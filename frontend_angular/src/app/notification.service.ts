import { Injectable } from '@angular/core';
import Swal from 'sweetalert2';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private Toast = Swal.mixin({
    toast: true,
    position: 'bottom-end',
    showConfirmButton: false,
    timer: 1500,
    timerProgressBar: true,
  })

  constructor() { }

  errorNotification(errorCode: number, title?: string, message?: string, timer?: number): void {
    let notifTitle = "";
    switch (errorCode) {
      case 400:
        notifTitle = "Bad Request"
      case 401:
        notifTitle = "Unauthenticated"
      case 403:
        notifTitle = "Unauthorize"
      case 404:
        notifTitle = "Not Found"
      case 500:
        notifTitle = "Internal server Error"

        this.Toast.fire({
          title: notifTitle + " - " + title,
          text: message,
          icon: 'error',
          timer: timer
        })
    }
  }

  successNotification(title?: string, message?: string, timer?: number): void {
    this.Toast.fire({
      title: title,
      text: message,
      icon: 'success',
      timer: timer
    })
  }
}
