import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { Aircraft } from '../models/aircraft';

@Injectable({ providedIn: 'root' })
export class AircraftService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/aircraft`;

  getAll(filters?: { status?: string }): Observable<Aircraft[]> {
    let params = new HttpParams();
    if (filters?.status) {
      params = params.set('status', filters.status);
    }
    return this.http.get<Aircraft[]>(this.base, { params });
  }

  getById(id: number): Observable<Aircraft> {
    return this.http.get<Aircraft>(`${this.base}/${id}`);
  }

  create(data: Partial<Aircraft>): Observable<Aircraft> {
    return this.http.post<Aircraft>(this.base, data);
  }

  update(id: number, data: Partial<Aircraft>): Observable<Aircraft> {
    return this.http.patch<Aircraft>(`${this.base}/${id}`, data);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
