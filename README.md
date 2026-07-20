<div align="center">

# Enterprise Delivery Intelligence Platform (EDIP)
### *Turning software delivery data into executive decisions.*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](#)
[![SQLite](https://img.shields.io/badge/Database-3NF_Compliance-lightgrey.svg?style=for-the-badge&logo=sqlite&logoColor=white)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](#)
[![Status](https://img.shields.io/badge/Status-Enterprise_Architecture-success.svg?style=for-the-badge)](#)

</div>

---

## Monday Morning at 9:00 AM
The CIO walks into the Weekly Delivery Review.

She asks:
> *"Why did Release 24.3 slip by two weeks?"*

Nobody has an answer.
The Business Analyst checks Jira. The Project Manager opens Excel. Engineering exports another CSV. QA has a separate tracker. Requirements are scattered in Word documents, and approvals are buried in email threads.

Three hours later, Leadership still doesn't know:
* Which requirement caused the delay.
* Who approved the late change.
* Why UAT failed three times.
* How much business value was lost.

**EDIP exists to answer those questions in minutes, not hours.**

---

## 🎯 What a Business Analyst Actually Does
A high-level Business Analyst doesn't just "gather requirements"—they govern the entire delivery lifecycle. This platform mathematically models those exact responsibilities:

| BA Responsibility | EDIP Module |
| :--- | :--- |
| **Gather requirements** | Requirements Workspace |
| **Trace changes & scope creep** | Version Intelligence / Volatility Engine |
| **UAT coordination** | Test Analytics & First-Pass Yield |
| **Stakeholder approvals** | Approval Engine & SLA Tracker |
| **Executive reporting** | Delivery Intelligence Dashboard |
| **Process improvement** | Bottleneck Analytics |

---

## 📊 Core Analytical Capabilities
EDIP ingests massive amounts of historical delivery data across thousands of requirements, analyzing state transitions, version volatility, and approval SLAs to mathematically quantify delivery health.

**EDIP delivers insights via:**
1. **Requirement Volatility Indexing:** Flagging teams that constantly change requirements post-approval (Scope Creep).
2. **Approval Bottleneck Analysis:** Tracking exactly which Business Sponsors are slowing down the delivery pipeline.
3. **UAT First-Pass Yield:** Measuring engineering quality by tracking how many test cycles (rework) a requirement undergoes.
4. **Compliance Traceability:** An immutable Audit Ledger mapping Business Rules -> User Stories -> Test Cases.

---

## 📸 Executive Dashboards (Demo)

### The CIO Killer Dashboard
*Quickly identify release health, projects at risk, and predicted delays.*
> **[Insert Screenshot 1 Here: Executive Release Health showing the 74/100 score and the ₹8.4 Cr value at risk]**

### Delivery Bottleneck Analysis
*Identify which sponsors and departments are causing SLA breaches.*
> **[Insert Screenshot 2 Here: SLA Breach & Approval Delay Analysis highlighting the worst offending sponsor]**

### UAT Defect Heatmap
*Track First-Pass Yield and engineering rework cycles.*
> **[Insert Screenshot 3 Here: Top 20 Requirements with Highest Rework]**

---

## 🏛️ Enterprise Architecture

The platform is designed using **Clean Architecture** principles. The Analytics Engine is entirely decoupled from the presentation layer and the database, allowing for isolated testing of business rules.

```mermaid
flowchart TD
    subgraph Presentation Layer
        UI[Streamlit Executive BI Dashboard]
    end

    subgraph Core Analytics Engine (Application Layer)
        VolEng[Volatility Analysis Engine]
        SLAEng[SLA Breach Engine]
        TraceEngine[Traceability & Compliance Engine]
    end

    subgraph Infrastructure Layer
        SQLite[(Enterprise SQLite DB 3NF)]
    end

    UI --> VolEng
    UI --> SLAEng
    UI --> TraceEngine
    VolEng --> SQLite
    SLAEng --> SQLite
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

## 📈 Business Impact (Before vs. After)

| Problem Area | Before EDIP | After EDIP |
| :--- | :--- | :--- |
| **Approvals** | Status scattered across email threads | Centralized, 1-click digital signature workflow |
| **Visibility** | Manual release reporting via Excel | Automated executive dashboard updated in real-time |
| **Traceability** | Difficult to map code to business rules | End-to-end, bi-directional requirement lineage |
| **Delivery Delays** | Discovered late (usually during release) | Early bottleneck detection and SLA tracking |
| **Governance** | Reactive (fixing broken releases) | Proactive delivery insights and volatility metrics |

---

## 🚀 Quick Start (Running the Platform)

### 1. Initialize the Enterprise Database
This script generates the 3NF SQLite database, enforces Foreign Key constraints, and populates the system with 500+ historical requirements containing simulated delays and volatility.
```bash
python infrastructure/database.py
```

### 2. Launch the Executive Portal
This spins up the Streamlit Business Intelligence application.
```bash
python -m streamlit run presentation/app.py
```

---

## 📚 Engineering & Business Documentation
Comprehensive artifacts detailing the delivery methodology are located in the `/docs` directory:
- [Business Discovery Report](docs/Business_Discovery_Report.md): The "As-Is" McKinsey-style analysis.
- [Requirements Engineering (BRD/FRD)](docs/Requirements_Engineering.md): The formal Business & Functional specifications.
- [Enterprise Architecture & ADRs](docs/Enterprise_Architecture.md): Architectural Decision Records.
- [Data Design & Normalization](docs/Data_Design.md): ERD and Audit strategies.

---
<div align="center">
  <i>Engineered for Enterprise Delivery Intelligence</i>
</div>
