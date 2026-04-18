import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { WorkOrder } from '../models/work-order';

@Injectable({ providedIn: 'root' })
export class WorkOrderService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/work-orders`;

  getAll(filters?: { status?: string; aircraft_id?: number }): Observable<WorkOrder[]> {
    let params = new HttpParams();
    if (filters?.status) {
      params = params.set('status', filters.status);
    }
    if (filters?.aircraft_id != null) {
      params = params.set('aircraft_id', String(filters.aircraft_id));
    }
    return this.http.get<WorkOrder[]>(this.base, { params });
  }

  getById(id: number): Observable<WorkOrder> {
    return this.http.get<WorkOrder>(`${this.base}/${id}`);
  }

  create(data: Partial<WorkOrder>): Observable<WorkOrder> {
    return this.http.post<WorkOrder>(this.base, data);
  }

  update(id: number, data: Partial<WorkOrder>): Observable<WorkOrder> {
    return this.http.patch<WorkOrder>(`${this.base}/${id}`, data);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
