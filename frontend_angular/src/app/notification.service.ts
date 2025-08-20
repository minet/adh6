import {Injectable} from "@angular/core";
import Swal from "sweetalert2";

export const Toast = Swal.mixin({
  toast: true,
  position: "bottom-end",
  showConfirmButton: false,
  timer: 1500,
  timerProgressBar: true,
});

@Injectable({
  providedIn: "root",
})
export class NotificationService {
  constructor() {}

  errorNotification(
    errorCode: number,
    title?: string,
    message?: string,
    timer?: number,
  ): void {
    let notifTitle = "";
    switch (errorCode) {
      case 400:
        notifTitle = "Bad Request";
        break;
      case 401:
        notifTitle = "Unauthenticated";
        break;
      case 403:
        notifTitle = "Unauthorize";
        break;
      case 404:
        notifTitle = "Not Found";
        break;
      case 500:
        notifTitle = "Internal server Error";

        void Toast.fire({
          title: notifTitle + " - " + title,
          text: message,
          icon: "error",
          timer: timer,
        });
    }
  }

  successNotification(title?: string, message?: string, timer?: number): void {
    void Toast.fire({
      title: title,
      text: message,
      icon: "success",
      timer: timer,
    });
  }
}
