export type JobStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'PARTIALLY_COMPLETED' | 'FAILED';
export type CertificateStatus = 'PENDING' | 'GENERATED' | 'FAILED';

export interface Recipient {
  name: string;
  email: string;
}

export interface JobCreatePayload {
  event_name: string;
  event_date: string;
  recipients: Recipient[];
}

export interface JobStatusResponse {
  job_id: string;
  event_name: string;
  event_date: string;
  status: JobStatus;
  total_recipients: number;
  successful_count: number;
  failed_count: number;
  pending_count: number;
  progress_percentage: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface CertificateItem {
  id: string;
  recipient_name: string;
  recipient_email: string;
  certificate_number: string;
  status: CertificateStatus;
  download_url: string | null;
  error_message: string | null;
  created_at: string;
  generated_at: string | null;
}

export interface CertificateListResponse {
  job_id: string;
  total: number;
  certificates: CertificateItem[];
}
