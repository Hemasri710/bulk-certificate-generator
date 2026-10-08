# AEREO Internship Assignment - Interview Preparation Notes

This document contains a **2-Minute Project Elevator Pitch** and answers to **20 Technical Interview Questions** designed to help you confidently present and defend this system during your interview for the Software Development Engineer Intern role at AEREO, Bengaluru.

---

## 🎤 2-Minute Spoken Project Pitch

> "Hi! I built the **Bulk Certificate Generator API**, an asynchronous backend service designed to handle high-volume certificate generation requests reliably and without blocking client applications.
>
> The core problem I solved is that rendering PDF documents is CPU and I/O intensive. If done synchronously during an API request, bulk operations with hundreds of recipients cause HTTP request timeouts and server memory spikes.
>
> To solve this, I designed a layered architecture using **FastAPI, SQLAlchemy 2.0, PostgreSQL, and ReportLab**. When a client POSTs a bulk request:
> 1. Pydantic v2 validates all recipient names and email addresses.
> 2. The job and certificate metadata are initialized in PostgreSQL with a `PENDING` status.
> 3. The API immediately returns an HTTP 201 Created with a unique `job_id`, delegating the heavy rendering to **FastAPI BackgroundTasks**.
>
> A crucial feature I implemented is **Fault-Tolerant Failure Isolation**. Each certificate is generated inside its own `try/except` block. If one recipient's record fails to render due to invalid data or rendering errors, it is marked as `FAILED` with an error traceback saved in the DB, while processing continues uninterrupted for the remaining recipients. The job finishes gracefully as `PARTIALLY_COMPLETED`.
>
> Clients can query real-time job progress percentages via a dedicated status endpoint, and generated certificates can be retrieved securely using path-traversal-protected download routes.
>
> The codebase includes comprehensive Pytest unit tests, Alembic migrations, Docker Compose configuration, and a clean React Admin Dashboard."

---

## 💡 20 Technical Q&A for Interviewers

### 1. Why did you choose FastAPI over Flask or Django?
FastAPI was selected because:
- **High Performance**: Built on top of Starlette and Pydantic, making it one of the fastest Python frameworks available.
- **Native Async & Background Tasks**: Built-in support for asynchronous request handling and background execution (`BackgroundTasks`).
- **Data Validation**: Pydantic v2 integrates seamlessly for automatic request body parsing, schema validation, and error formatting.
- **Automated OpenAPI Documentation**: Generates interactive Swagger docs (`/docs`) out of the box.

### 2. Why PostgreSQL?
PostgreSQL provides ACID compliance, strong data integrity constraints (foreign keys, unique indexes), and excellent performance under concurrent read/write workloads. Since generation job statuses and certificate audit logs require strict persistence, a relational database is ideal.

### 3. Why SQLAlchemy 2.0?
SQLAlchemy 2.0 introduces modern Python type-hinting support (`Mapped`, `mapped_column`), unified `select()` syntax, and clean separation between ORM session management and low-level SQL execution. It allows us to decouple business services from raw SQL queries.

### 4. Why FastAPI `BackgroundTasks`?
`BackgroundTasks` allows us to offload non-blocking tasks to Python thread/event loops right after returning the HTTP 201 response. For single-server deployments or internship assignments, it eliminates the need to run and manage external broker services like Redis and worker daemons like Celery.

### 5. Why not Celery for this assignment?
Celery requires a message broker (Redis or RabbitMQ) and separate worker processes. Adding Celery would introduce unnecessary infrastructure complexity for a local assignment. However, the system is designed modularly so `BackgroundTasks` can be swapped for a Celery task function with minimal changes.

### 6. How does bulk processing work under the hood?
When a bulk payload arrives:
1. `JobService.create_bulk_job` creates 1 `GenerationJob` record and $N$ `Certificate` records in `PENDING` state inside a single database transaction.
2. The endpoint returns `201 Created`.
3. `JobService.process_job_background` fetches the pending certificate records and generates PDF files sequentially or in bounded batches.

### 7. How does failure isolation work?
Inside the background worker loop, each recipient's PDF generation call is wrapped in a `try...except` block:
```python
try:
    PDFCertificateGenerator.generate_certificate(...)
    cert_repo.mark_generated(cert.id, file_path)
    job_repo.increment_counts(job_id, is_success=True)
except Exception as e:
    cert_repo.mark_failed(cert.id, error_message=str(e))
    job_repo.increment_counts(job_id, is_success=False)
```
If an exception occurs, only that specific certificate status changes to `FAILED`. The loop proceeds to the next recipient.

### 8. How is progress percentage calculated?
```python
processed_count = successful_count + failed_count
progress_percentage = round((processed_count / total_recipients) * 100, 2)
```
If `total_recipients` is 0, progress is safely set to `100.0%` to prevent division-by-zero errors.

### 9. How are PDF certificates generated using ReportLab?
`PDFCertificateGenerator` creates a landscape A4 canvas (`841.89 x 595.27` points). It draws custom decorative outer/inner borders, corner accents, organization title, recipient name, event details, issue date, certificate ID, and signature blocks using `reportlab.platypus.SimpleDocTemplate` and custom `ParagraphStyle`.

### 10. How are file downloads secured against Path Traversal attacks?
Arbitrary file paths are never accepted directly from client requests. The download endpoint accepts only a `certificate_id` UUID, looks up the registered `file_path` in PostgreSQL, and verifies safety via:
```python
def is_safe_path(base_directory, target_file):
    base = Path(base_directory).resolve()
    target = Path(target_file).resolve()
    return base in target.parents or base == target
```
If `target_file` resolves outside `storage/certificates/`, access is rejected.

### 11. Can you explain your Database Schema?
We have two primary tables:
- `generation_jobs`: Tracks the overall job metadata (`event_name`, `status`, `total_recipients`, `successful_count`, `failed_count`, timestamps).
- `certificates`: Foreign key to `generation_jobs.id` (`ON DELETE CASCADE`), storing `recipient_name`, `recipient_email`, unique `certificate_number`, `status`, `file_path`, and `error_message`.
Indexes are created on `job_id`, `recipient_email`, `status`, and `certificate_number`.

### 12. Explain the layered architecture.
- **Routes (`api/routes`)**: Handles HTTP requests/responses and input validation.
- **Services (`services/`)**: Contains pure business logic (job state transitions, PDF generation triggering).
- **Repositories (`repositories/`)**: Encapsulates SQLAlchemy database queries.
- **Models & Schemas (`models/`, `schemas/`)**: Defines ORM database tables and Pydantic validation DTOs.

### 13. How is error handling structured across the API?
We implemented custom FastAPI exception handlers for HTTP exceptions, validation errors (`RequestValidationError`), and unhandled 500 errors. All error responses return a standardized JSON structure:
```json
{
  "error": {
    "code": "JOB_NOT_FOUND",
    "message": "Generation job with ID 'xyz' was not found."
  }
}
```

### 14. What is your automated testing strategy?
We use `pytest` with an isolated SQLite in-memory database (`sqlite:///:memory:`). We test:
- Request validation (invalid email, blank fields, empty arrays).
- Job creation and status calculations.
- Asynchronous background worker execution.
- Failure handling (mocking ReportLab failure for specific recipients).
- Certificate PDF streaming and download headers.

### 15. What are the scalability limitations of the current setup?
- **In-Memory Background Tasks**: `BackgroundTasks` uses Python thread pools on a single server instance. If the server crashes mid-job, pending tasks in memory are lost.
- **Local File Storage**: PDF files are saved to local disk, which won't share across multiple load-balanced server instances.

### 16. How would you replace `BackgroundTasks` with Celery/Redis for production?
1. Configure a Celery app connected to Redis (`redis://localhost:6379/0`).
2. Convert `process_job_background` into a `@celery.task`.
3. In `POST /api/v1/jobs/`, invoke `process_job_background.delay(job_id)`.
4. Run Celery workers independently (`celery -A tasks worker --loglevel=info`).

### 17. How would you scale this system if traffic increased 10x (e.g., 500,000 certificates/day)?
1. **Distributed Queue**: Use SQS or RabbitMQ + Celery.
2. **Object Storage**: Store generated PDFs in Amazon S3 or Google Cloud Storage instead of local disk. Generate pre-signed S3 URLs for downloads.
3. **Database Read Replicas**: Use PostgreSQL primary for writes and read replicas for status querying.
4. **Horizontal Worker Scaling**: Deploy autoscale worker nodes on Kubernetes (KEDA).

### 18. What security vulnerabilities did you consider?
- **Path Traversal / Arbitrary File Read**: Mitigated via path resolution checks.
- **SQL Injection**: Mitigated via SQLAlchemy parameterized queries.
- **Data Pollution**: Mitigated via Pydantic input sanitization and length bounds.
- **Exposing Internal Stack Traces**: Disabled detailed stack trace exposure in production HTTP responses.

### 19. How would you deploy this project to production?
- Containerize using Docker and host on AWS ECS / EKS or DigitalOcean App Platform.
- Use Managed PostgreSQL (AWS RDS).
- Put NGINX or Cloudflare in front as a Reverse Proxy with SSL/TLS termination and rate limiting.

### 20. What questions might an interviewer ask about your code?
- *Question*: "Why did you use strings for UUIDs in SQLite and Postgres?"
  - *Answer*: Using `String(36)` with `uuid.uuid4()` guarantees cross-database compatibility between PostgreSQL and SQLite without dialect-specific type conversions.
