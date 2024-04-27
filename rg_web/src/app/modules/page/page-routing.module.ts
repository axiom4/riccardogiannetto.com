import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { PageComponent } from './components/page/page.component';

const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: "/404" },
  { path: ':tag', component: PageComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class PageRoutingModule { }
