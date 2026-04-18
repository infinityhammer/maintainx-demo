import { Aircraft } from './aircraft';

export type WorkOrderPriority = 'low' | 'normal' | 'high' | 'critical';
export type WorkOrderStatus =
  | 'open'
  | 'in_progress'
  | 'awaiting_parts'
  | 'complete'
  | 'cancelled';

export interface WorkOrder {
  id: number;
  aircraft_id: number;
  title: string;
  description?: string;
  priority: WorkOrderPriority;
  status: WorkOrderStatus;
  assigned_to?: string;
  created_at: string;
  updated_at?: string;
  aircraft?: Aircraft;
}
