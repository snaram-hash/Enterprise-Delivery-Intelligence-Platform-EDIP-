# Phase 4: Enterprise Architecture
**Project:** Enterprise Requirements & Decision Management Platform (ERDMP)
**Role:** Solution Architect

---

## 1. Architectural Philosophy
The ERDMP is designed strictly around **Clean Architecture (Onion Architecture)** principles. We must completely decouple the Domain Logic (the state-machine rules governing requirement lifecycles) from the Infrastructure (Database) and Presentation (UI) layers. This ensures that the core business rules are testable entirely in isolation, without needing a UI or a database connection.

---

## 2. C4 Architecture Model (Container Level)

```mermaid
flowchart TD
    subgraph Presentation Layer
        UI[Streamlit Web App]
        API[FastAPI / Direct Python API]
    end

    subgraph Core Application Layer (Use Cases)
        ReqManager[Requirement Manager]
        AppFlow[Approval Workflow Engine]
        TraceEngine[Traceability Engine]
    end

    subgraph Domain Layer (Enterprise Logic)
        StateMach[State Machine Validator]
        Entities[Requirement & User Story Objects]
    end

    subgraph Infrastructure Layer
        SQLite[(Enterprise SQLite DB)]
        AuditLog[Audit Logging Service]
        Export[CSV/Jira Exporter]
    end

    UI --> API
    API --> ReqManager
    API --> AppFlow
    API --> TraceEngine
    ReqManager --> StateMach
    AppFlow --> StateMach
    StateMach --> Entities
    ReqManager --> SQLite
    AppFlow --> AuditLog
```

---

## 3. Modular Folder Structure
The repository will follow a professional, enterprise-grade Python directory structure:

```text
Enterprise_Requirements_Platform/
│
├── core/                        # Domain Layer (Zero Dependencies)
│   ├── entities.py              # Requirement, UserStory, Testcase dataclasses
│   └── state_machine.py         # Rules for transitioning (Draft -> Approved)
│
├── application/                 # Use Cases / Application Layer
│   ├── requirement_service.py   # CRUD and validation for requirements
│   ├── approval_service.py      # Digital signature and workflow routing
│   └── traceability_service.py  # Generating the hierarchy mapping
│
├── infrastructure/              # Infrastructure Layer
│   ├── database.py              # SQLite connection and ORM mapping
│   ├── audit_logger.py          # Immutable logging of all state changes
│   └── exporters.py             # CSV/Jira export adapters
│
├── presentation/                # UI Layer
│   ├── app.py                   # Streamlit Main Entry
│   ├── pages/                   # Separate views (Dashboard, UAT, Traceability)
│   └── components.py            # Reusable UI widgets
│
├── tests/                       # Pytest Suite
├── docs/                        # MkDocs Portal (BRDs, Handbooks, Architecture)
├── requirements.txt
└── README.md
```

---

## 4. Security & Permissions Model

### 4.1 Role-Based Access Control (RBAC)
Although the MVP will use simulated session states in Streamlit, the architecture enforces strict RBAC at the `application` layer:
- **`role: admin`**: Can configure system-wide settings and override locked states in emergencies.
- **`role: sponsor`**: Can only view dashboards and execute `approve()` or `reject()` methods on assigned requirements. Cannot author requirements.
- **`role: ba`**: Can author requirements, transition states from `Draft` to `PendingReview`, and link User Stories. Cannot approve their own requirements.
- **`role: engineer`**: Can view approved requirements, write technical comments, and execute the technical sign-off `approve()` method.

### 4.2 Immutable Audit Trail
Every time a Requirement object changes state (e.g., `PendingReview` -> `Approved`), the `approval_service.py` must push a payload to the `audit_logger.py`. This table in SQLite is strictly append-only (no UPDATE or DELETE statements allowed on this table by application logic).

---

## 5. Architecture Decision Record (ADR)

### ADR 001: Use of SQLite vs PostgreSQL
**Context:** We need a relational database to store Requirements, User Stories, and Audit Logs. Enterprise apps typically use PostgreSQL.
**Decision:** We will use SQLite with WAL (Write-Ahead Logging) enabled.
**Justification:** This project is a portfolio showcase intended to be easily downloadable and runnable by Hiring Managers and Recruiters on their local machines. Forcing a recruiter to spin up a Dockerized PostgreSQL instance adds immense friction. SQLite achieves the relational integrity (Foreign Keys) required for our ERD without the setup overhead.
**Consequences:** We cannot handle high-concurrency writes, but for a local portfolio demonstration, concurrency is not a requirement.

### ADR 002: Streamlit vs React/Next.js
**Context:** We need a Presentation layer to demonstrate the ERDMP workflows.
**Decision:** We will use Streamlit (Python).
**Justification:** The core value of this project is demonstrating *Business Analysis and Backend Architecture* (State Machines, Traceability). Writing thousands of lines of React/CSS dilutes the focus and wastes development time on frontend cosmetics rather than business logic. Streamlit allows us to build a data-heavy, professional UI rapidly using pure Python, keeping the codebase unified.
**Consequences:** UI customization is constrained, but sufficient for an enterprise internal tool aesthetic.

---

### Next Steps
Upon approval of the architectural constraints, folder structure, and ADRs, we will transition to **Phase 5: Product Design**, where the Senior UX Designer will map out the specific screens, navigation, and user journey for the Streamlit application.
