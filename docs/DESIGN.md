# Onboard Atlas – Technical Design

## 1. Project Overview

Onboard Atlas is a multi-tenant, AI-powered HR policy assistant designed for HR consultancies that manage HR operations for multiple startups.

Each company has its own HR policies, including leave, expenses, onboarding, and performance management. The system aims to provide accurate answers from the correct company's handbook while preventing unauthorized access to another company's information.

The current implementation provides a FastAPI backend integrated with Google's Gemini API, including automatic model fallback and token usage tracking.

## 2. Technology Stack

| Component | Technology |
|---|---|
| Backend API | Python, FastAPI |
| LLM | Google Gemini API |
| Configuration | Pydantic Settings |
| Request validation | Pydantic |
| Usage tracking | Python, threading Lock |
| Containerization | Docker |
| Testing | Pytest, HTTPX |
| Code quality | Ruff |
| Planned database | PostgreSQL |
| Planned vector search | pgvector |
| Planned UI | Streamlit |

## 3. System Architecture

### Current implementation

Client → FastAPI → Request Validation → Gemini LLM → Response + Token Usage → Client

The application uses a primary Gemini model and automatically attempts a fallback model if the primary model fails.

### Planned RAG architecture

User → Authentication → Tenant and Role Verification → PostgreSQL Row-Level Security → Tenant-filtered Vector Search → Relevant Handbook Chunks → Gemini LLM → Answer with Document Citations

Every document chunk will contain tenant and access-control metadata. Tenant filtering must happen before retrieved content is passed to the LLM.

## 4. API Endpoints

### 4.1 GET /health

Purpose: Checks whether the API application is running.

Response:

```json
{
  "status": "ok",
  "app": "onboard-atlas",
  "environment": "local"
}
```

This endpoint does not call Gemini or a database.

### 4.2 POST /ask

Purpose: Accepts a question and generates an answer using Gemini.

Request:

```json
{
  "question": "Explain what an HR policy handbook is in simple words."
}
```

Validation:
- Question must contain at least 3 characters.
- Maximum question length is 5000 characters.

Response:

```json
{
  "answer": "An HR policy handbook is a guidebook containing company rules and policies.",
  "model_used": "gemini-3.8-flash",
  "input_tokens": 12,
  "output_tokens": 289,
  "total_tokens": 972
}
```

The answer and token values above illustrate the response structure; actual values depend on the Gemini response.

If both configured models fail, the API returns HTTP 503 with a generic AI-service error message.

Note: The current endpoint sends the question directly to Gemini. Handbook retrieval, tenant authorization, and source citations are not implemented yet.

### 4.3 GET /usage

Purpose: Returns accumulated API usage statistics.

Example response:

```json
{
  "total_requests": 1,
  "total_input_tokens": 12,
  "total_output_tokens": 289,
  "total_tokens": 972,
  "estimated_cost_usd": 0.000550875,
  "models": {
    "gemini-3.8-flash": {
      "requests": 1,
      "input_tokens": 12,
      "output_tokens": 289,
      "total_tokens": 972,
      "estimated_cost_usd": 0.000550875
    }
  }
}
```

Usage is tracked separately for each model.

The current tracker:
- Counts successful requests.
- Tracks input, output, and total tokens.
- Calculates estimated API cost.
- Uses a thread lock to protect updates.
- Stores usage in memory, so statistics reset when the application restarts.

The configured model prices are estimates and must be updated when the applicable API pricing changes.

## 5. Gemini Integration and Fallback

The application uses the Google Gen AI Python SDK.

Configured models:

- Primary: gemini-3.8-flash
- Fallback: gemini-3.5-flash-lite

Workflow:

1. Receive a question through POST /ask.
2. Validate the request using Pydantic.
3. Call the primary Gemini model.
4. If the primary model fails or returns an empty answer, attempt the fallback model.
5. Extract the generated answer and token usage.
6. Record usage and estimated cost.
7. Return the structured response.

If both models fail, the application returns HTTP 503.

## 6. Configuration and Environment Variables

Sensitive configuration is stored in a local `.env` file.

Example `.env.example`:

```env
APP_NAME=onboard-atlas
ENVIRONMENT=local
GEMINI_API_KEY=your_api_key_here
GEMINI_PRIMARY_MODEL=gemini-3.8-flash
GEMINI_FALLBACK_MODEL=gemini-3.5-flash-lite
```

The actual API key must never be committed to Git or included in the Docker image.

## 7. Database Design – Planned

PostgreSQL with pgvector is planned for storing handbook content, tenant information, and vector embeddings.

The following tables are proposed. They are not yet implemented in the current application.

### 7.1 tenants

Stores information about client companies.

| Column | Description |
|---|---|
| tenant_id | Primary key |
| tenant_name | Company name |
| created_at | Creation timestamp |

### 7.2 users

Stores users belonging to each tenant.

| Column | Description |
|---|---|
| user_id | Primary key |
| tenant_id | Foreign key referencing tenants |
| name | User name |
| email | User email |
| role | Employee, Manager, or HR Admin |

### 7.3 documents

Stores handbook document metadata.

| Column | Description |
|---|---|
| document_id | Primary key |
| tenant_id | Foreign key referencing tenants |
| document_name | Handbook filename |
| source_url | Original document location |
| created_at | Upload timestamp |

### 7.4 document_chunks

Stores extracted handbook text and vector embeddings.

| Column | Description |
|---|---|
| chunk_id | Primary key |
| document_id | Foreign key referencing documents |
| tenant_id | Tenant identifier |
| page_number | Original handbook page |
| heading | Section heading |
| content | Extracted text |
| embedding | Vector representation |

### 7.5 hr_requests – Planned

Stores leave, expense, and other HR requests.

| Column | Description |
|---|---|
| request_id | Primary key |
| tenant_id | Tenant identifier |
| user_id | Request creator |
| request_type | Leave, Expense, or Other |
| status | Pending, Approved, or Rejected |
| approved_by | Approving manager or HR administrator |
| created_at | Request timestamp |

## 8. Security and Tenant Isolation – Planned

Tenant isolation is a core requirement of Onboard Atlas.

Planned security measures:

1. Every user belongs to a specific tenant.
2. Every handbook document and chunk contains a tenant_id.
3. User roles include Employee, Manager, and HR Admin.
4. PostgreSQL Row-Level Security (RLS) enforces tenant-level access restrictions.
5. Tenant filtering occurs before vector search.
6. Manager-only and HR-admin-only information requires additional role checks.
7. Unauthorized cross-tenant requests must be rejected.

Security evaluation target:

- 100 adversarial prompts.
- Zero cross-tenant information leaks.

These controls are design requirements and have not yet been implemented or security-tested in the current API prototype.

## 9. Error Handling

| Scenario | Expected behavior |
|---|---|
| Invalid question | HTTP 422 validation error |
| Missing Gemini API key | AI service failure |
| Primary model failure | Attempt fallback model |
| Both models fail | HTTP 503 |
| Empty Gemini response | Attempt fallback model |
| Unknown model pricing | Usage recording error |

## 10. Testing and Deployment

Current testing:
- Pytest for the health endpoint.
- Ruff for code quality checks.
- Docker image build.
- Docker container execution.
- Health endpoint tested inside Docker.
- Gemini question-answering tested inside Docker.
- Usage endpoint tested inside Docker.

CI uses GitHub Actions for automated Ruff and Pytest checks.

Deployment to a public hosting provider is planned.

## 11. Future Development

1. Integrate PostgreSQL and pgvector.
2. Implement user authentication and role-based authorization.
3. Implement tenant-level Row-Level Security.
4. Collect and process GitLab and PostHog handbook datasets.
5. Implement document parsing, chunking, and embedding generation.
6. Implement tenant-filtered RAG retrieval.
7. Return answers with document and page citations.
8. Implement leave and expense request workflows.
9. Add streaming, timeouts, and retry handling.
10. Deploy the application and publish its live API link.

---

**Project:** Onboard Atlas  
**Backend:** FastAPI + Gemini  
**Current version:** 0.3.0