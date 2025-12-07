import {CommonModule} from "@angular/common";
import {Component, OnInit, OnDestroy} from "@angular/core";
import {FormsModule} from "@angular/forms";
import {
  Observable,
  BehaviorSubject,
  combineLatest,
  EMPTY,
  timer,
  Subject,
} from "rxjs";
import {
  switchMap,
  map,
  catchError,
  startWith,
  takeUntil,
  scan,
} from "rxjs/operators";
import {
  MemberService,
  MemberIdLogsGet200Response,
  MemberIdLogsGet200ResponseLogsInner,
} from "../../../api";
import {MemberDeviceModule} from "../../../member-device/member-device.module";
import {MemberDetailService} from "../member-detail.service";

interface LogEntry {
  timestamp: Date;
  message: string;
  formattedMessage: string;
  rawLog: string;
}

interface LogsResponse {
  logs: LogEntry[];
  hasMore: boolean;
  total: number;
  isLoadMore?: boolean;
}

@Component({
  imports: [CommonModule, FormsModule, MemberDeviceModule],
  selector: "app-devices",
  templateUrl: "./devices.component.html",
  styleUrls: ["./devices.component.css"],
})
export class DevicesComponent implements OnInit, OnDestroy {
  private readonly destroy$ = new Subject<void>();
  private readonly refreshTrigger$ = new BehaviorSubject<void>(undefined);
  private readonly loadMoreTrigger$ = new Subject<void>();

  public getDhcp = false;
  public showLogs = false;
  public member$ = this.memberDetailService.member$;

  // Loading states
  public logsLoading$ = new BehaviorSubject<boolean>(false);
  public loadingMore$ = new BehaviorSubject<boolean>(false);
  public logsError$ = new BehaviorSubject<string | null>(null);

  // Logs data
  public logs$ = new BehaviorSubject<LogEntry[]>([]);
  public hasMoreLogs$ = new BehaviorSubject<boolean>(true);
  public currentOffset = 0;
  private readonly pageSize = 50;

  // Auto-refresh
  public autoRefresh = true;
  private readonly autoRefreshInterval = 10 * 1000; // 10 seconds

  constructor(
    private readonly memberService: MemberService,
    private readonly memberDetailService: MemberDetailService,
  ) {}

  ngOnInit(): void {
    this.setupLogsStream();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private setupLogsStream(): void {
    // Main logs stream
    const logsStream$ = combineLatest([
      this.member$,
      this.refreshTrigger$,
    ]).pipe(
      switchMap(([member]) => {
        if (!this.showLogs || !member || !member.id) {
          return EMPTY;
        }

        this.logsLoading$.next(true);
        this.logsError$.next(null);
        this.currentOffset = 0;

        return this.memberService
          .memberIdLogsGet(
            member.id,
            this.getDhcp,
            this.pageSize,
            this.currentOffset,
            "body",
          )
          .pipe(
            map((response) => {
              const data = response;
              return {
                logs: this.parseLogsResponse(data?.logs || []),
                hasMore: data?.hasMore || false,
                total: data?.total || 0,
              } as LogsResponse;
            }),
            catchError((error) => {
              console.error("Error loading logs:", error);
              this.logsError$.next("Failed to load logs");
              return EMPTY;
            }),
          );
      }),
    );

    // Load more logs stream
    const loadMoreStream$ = this.loadMoreTrigger$.pipe(
      switchMap(() => this.member$),
      switchMap((member) => {
        if (!member || !member.id || !this.hasMoreLogs$.value) {
          return EMPTY;
        }

        this.loadingMore$.next(true);
        this.currentOffset += this.pageSize;

        return this.memberService
          .memberIdLogsGet(
            member.id,
            this.getDhcp,
            this.pageSize,
            this.currentOffset,
            "body",
          )
          .pipe(
            map((response) => {
              const data = response;
              return {
                logs: this.parseLogsResponse(data?.logs || []),
                hasMore: data?.hasMore || false,
                total: data?.total || 0,
                isLoadMore: true,
              } as LogsResponse;
            }),
            catchError((error) => {
              console.error("Error loading more logs:", error);
              this.logsError$.next("Failed to load more logs");
              return EMPTY;
            }),
          );
      }),
    );

    // Combine initial load and load more
    const combinedLogsStream$ = logsStream$.pipe(
      startWith(null),
      scan((acc: LogEntry[], curr: LogsResponse | null) => {
        if (!curr) {
          return [];
        }
        if (curr.isLoadMore) {
          return [...acc, ...curr.logs];
        } else {
          return curr.logs;
        }
      }, []),
    );

    combinedLogsStream$.pipe(takeUntil(this.destroy$)).subscribe((logs) => {
      this.logs$.next(logs);
      this.logsLoading$.next(false);
      this.loadingMore$.next(false);
    });

    // Handle load more results
    loadMoreStream$.pipe(takeUntil(this.destroy$)).subscribe((result) => {
      this.hasMoreLogs$.next(result.hasMore);
      const currentLogs = this.logs$.value;
      this.logs$.next([...currentLogs, ...result.logs]);
      this.loadingMore$.next(false);
    });

    // Auto-refresh when enabled
    timer(0, this.autoRefreshInterval)
      .pipe(
        takeUntil(this.destroy$),
        switchMap(() => {
          if (this.autoRefresh && this.showLogs) {
            return this.refreshTrigger$.pipe(startWith(undefined));
          }
          return EMPTY;
        }),
      )
      .subscribe();
  }

  private parseLogsResponse(
    logs: MemberIdLogsGet200ResponseLogsInner[],
  ): LogEntry[] {
    return logs.map((log) => {
      const timestamp = new Date(log.timestamp || "");
      const message = log.message || "";

      return {
        timestamp,
        message,
        formattedMessage: this.formatLogMessage(message),
        rawLog: `${timestamp.toISOString()} ${message}`,
      };
    });
  }

  private formatLogMessage(message: string): string {
    let formatted = message;

    // Color coding for different log types
    if (message.includes("Login OK")) {
      formatted = formatted.replace(
        /Login OK[:]?/gi,
        '<span class="log-success">Login OK</span>',
      );
    } else if (
      message.includes("Login incorrect") ||
      message.includes("Password incorrect")
    ) {
      formatted = formatted.replace(
        /(Login incorrect|Password incorrect)/gi,
        '<span class="log-error">$1</span>',
      );
    } else if (message.includes("DHCP")) {
      formatted = formatted.replace(
        /DHCP/gi,
        '<span class="log-dhcp">DHCP</span>',
      );
    } else if (message.includes("Logout")) {
      formatted = formatted.replace(
        /Logout/gi,
        '<span class="log-info">Logout</span>',
      );
    }

    return formatted;
  }

  public toggleLogs(): void {
    this.showLogs = !this.showLogs;
    if (this.showLogs) {
      this.refreshLogs();
    }
  }

  public refreshLogs(): void {
    this.refreshTrigger$.next();
  }

  public loadMoreLogs(): void {
    if (this.hasMoreLogs$.value && !this.loadingMore$.value) {
      this.loadMoreTrigger$.next();
    }
  }

  public toggleDhcp(): void {
    this.getDhcp = !this.getDhcp;
    this.refreshLogs();
  }

  public toggleAutoRefresh(): void {
    this.autoRefresh = !this.autoRefresh;
  }

  public formatTimestamp(date: Date): string {
    return date.toLocaleString("fr-FR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  }
}
