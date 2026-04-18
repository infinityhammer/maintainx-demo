import { Routes } from '@angular/router';

import { AircraftListComponent } from './components/aircraft-list/aircraft-list.component';
import { WorkOrderDetailComponent } from './components/work-order-detail/work-order-detail.component';
import { WorkOrderListComponent } from './components/work-order-list/work-order-list.component';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'work-orders' },
  { path: 'work-orders', component: WorkOrderListComponent },
  { path: 'work-orders/:id', component: WorkOrderDetailComponent },
  { path: 'aircraft', component: AircraftListComponent },
];
