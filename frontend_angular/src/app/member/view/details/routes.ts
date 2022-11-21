import { Route } from "@angular/router";

export const ROUTES: Route[] = [
  { 
    path: '', 
    loadComponent: () => import('./details.component').then(m => m.DetailsComponent),
    children: [
      { path: 'comment', loadComponent: () => import('./member-comment-edit/member-comment-edit.component').then(m => m.MemberCommentEditComponent) }
    ]
  },
];