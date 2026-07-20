<div align="center">

# Enterprise Requirements & Decision Management Platform (ERDMP)
### *Centralizing the Complete Business Analysis Lifecycle*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](#)
[![SQLite](https://img.shields.io/badge/Database-3NF_Compliance-lightgrey.svg?style=for-the-badge&logo=sqlite&logoColor=white)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](#)
[![Status](https://img.shields.io/badge/Status-Enterprise_Architecture-success.svg?style=for-the-badge)](#)

</div>

---

## 🎯 Executive Summary
The **Enterprise Requirements & Decision Management Platform (ERDMP)** is an internal capability product designed to solve a massive structural inefficiency within Fortune 500 companies: the fragmented management of Business Requirements.

When a multinational enterprise processes 300+ major change requests per quarter using scattered Word documents, Excel sheets, and email threads, the result is extreme approval gridlock, duplicated requirements, and failed compliance audits. 

**ERDMP replaces this chaos by providing:**
1. A single source of truth for authoring Business Requirements.
2. A strict State-Machine Engine enforcing digital signature approvals.
3. A bi-directional Requirement Traceability Matrix (RTM) linking Business Rules to User Stories to Test Cases.
4. An immutable Audit Ledger tracking every state change for regulatory compliance.

*(Note: This platform sits strictly upstream of Sprint Execution. It feeds approved requirements into execution tools like Jira, it does not replace them).*

---

## 🏛️ Enterprise Architecture

The platform is designed using **Clean Architecture** principles. The core domain logic (state transitions and traceability mapping) is entirely decoupled from the presentation layer and the database, allowing for isolated testing of business rules.

```mermaid
flowchart TD
    subgraph Presentation Layer
        UI[Streamlit Web App]
    end

    subgraph Core Application Layer (Use Cases)
        ReqManager[Requirement Manager]
        AppFlow[Approval Workflow Engine]
        TraceEngine[Traceability Engine]
    end

    subgraph Infrastructure Layer
        SQLite[(Enterprise SQLite DB 3NF)]
        AuditLog[Audit Logging Service]
    end

    UI --> ReqManager
    UI --> AppFlow
    UI --> TraceEngine
    ReqManager --> SQLite
    AppFlow --> AuditLog
```

### The "Soft Delete" Versioning Strategy
To ensure engineers never build against "ghost-edited" specifications, ERDMP utilizes Type 2 Slowly Changing Dimensions. When a Business Analyst edits an `Approved` requirement, the system does not overwrite the row. It marks the existing row as inactive, inserts a new row with `Version + 0.1`, and forces the status back to `Draft`.

---

## 📊 Core Platform Capabilities

### 1. The Executive Approval Workflow
Business Sponsors (VPs/Directors) require zero training to use the platform. They access a dedicated "My Approvals Queue" which summarizes the Business Value, Acceptance Criteria, and Technical Impact of a requirement, allowing them to digitally sign with one click.

### 2. Bi-Directional Traceability
The platform automatically generates a hierarchical tree proving that every engineered feature maps back to an approved Business Rule. The system actively flags **Compliance Exceptions** (e.g., a User Story that lacks UAT Test Cases).

### 3. The Immutable Ledger
Every state change (Draft ➔ Pending ➔ Approved) is cryptographically stamped in an append-only `audit_logs` table, ready for instant export during a regulatory audit.

---

## 🚀 Quick Start (Running the Platform)

### 1. Initialize the Enterprise Database
This script generates the 3NF SQLite database, enforces Foreign Key constraints, and populates the system with mock users (Sponsors, BAs, Engineers) and mock requirements.
```bash
python infrastructure/database.py
```

### 2. Launch the Executive Portal
This spins up the Streamlit application.
```bash
python -m streamlit run presentation/app.py
```

---

## 📚 Engineering & Business Documentation
Comprehensive artifacts detailing the 10-phase delivery methodology are located in the `/docs` directory:
- [Business Discovery Report](docs/Business_Discovery_Report.md): The "As-Is" McKinsey-style analysis.
- [Requirements Engineering (BRD/FRD)](docs/Requirements_Engineering.md): The formal Business & Functional specifications.
- [Enterprise Architecture & ADRs](docs/Enterprise_Architecture.md): Architectural Decision Records.
- [Data Design & Normalization](docs/Data_Design.md): ERD and Audit strategies.

---
<div align="center">
  <i>Engineered for Enterprise Requirements Management</i>
</div>
