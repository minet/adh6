import {inject, Injectable} from "@angular/core";
import {forkJoin, map, Observable, of, switchMap} from "rxjs";
import {MemberFilter, MemberService} from "../api";
import {ComboboxOption} from "./combobox.component";

@Injectable({providedIn: "root"})
export class MemberSuggestionsService {
  private readonly memberService = inject(MemberService);

  search(
    terms: string,
    filter: MemberFilter | undefined,
    maxResults: number,
    valueField: "username" | "id" = "username",
  ): Observable<ComboboxOption[]> {
    const query = terms.trim();
    if (query.length < 2) {
      return of([]);
    }
    return this.memberService
      .memberGet(maxResults + 1, 0, query, filter, "response")
      .pipe(
        switchMap((response) => {
          const ids = response.body ?? [];
          const total = Number(
            response.headers.get("x-total-count") ?? ids.length,
          );
          // Same privacy threshold as the list: never expose names for broad searches.
          if (
            !Number.isFinite(total) ||
            total < 0 ||
            total > maxResults ||
            ids.length > maxResults ||
            ids.length === 0
          ) {
            return of([]);
          }
          return forkJoin(
            ids.map((id) =>
              this.memberService
                .memberIdGet(id, ["username", "firstName", "lastName"])
                .pipe(map((member) => ({...member, id}))),
            ),
          ).pipe(
            map((members) =>
              members
                .filter((member) => Boolean(member.username))
                .map((member) => ({
                  value: valueField === "id" ? member.id : member.username!,
                  label: [
                    member.username,
                    [member.firstName, member.lastName]
                      .filter(Boolean)
                      .join(" "),
                  ]
                    .filter(Boolean)
                    .join(" : "),
                })),
            ),
          );
        }),
      );
  }
}
