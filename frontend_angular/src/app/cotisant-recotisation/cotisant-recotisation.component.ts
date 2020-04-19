import { Component, OnInit } from '@angular/core';


@Component({
  selector: 'app-cotisant-recotisation',
  templateUrl: './cotisant-recotisation.component.html',
  styleUrls: ['./cotisant-recotisation.component.css']
})
export class CotisantRecotisationComponent implements OnInit {
  date: number;
  constructor() { }

  ngOnInit() {
  }

  public setDate(nb: number) {
    const today = new Date();
    today.setMonth(today.getMonth() + nb);
    return today;
  }

}
