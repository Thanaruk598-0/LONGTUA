# 14. Development & Implementation Specification

## 14.1 Purpose

เอกสารนี้กำหนดแนวทางการนำ System Design ของ LONGTUA ไปพัฒนาเป็นระบบจริง โดยมีเป้าหมายเพื่อ:

1. แปลง Architecture, Domain Model, API, Database, AI/NLP, Planning และ UI/UX ให้เป็น implementation structure ที่สอดคล้องกัน
2. กำหนดขอบเขตความรับผิดชอบของแต่ละ module ก่อนเริ่ม coding
3. กำหนดลำดับการพัฒนาเพื่อลด dependency และการแก้งานซ้ำ
4. กำหนด coding และ integration conventions
5. กำหนดวิธีเชื่อม Mobile, Backend, Database, AI Provider และ Planning Engine
6. กำหนด Definition of Done สำหรับแต่ละส่วน
7. เป็นพื้นฐานสำหรับการแตกเป็น Development Cards ในขั้นตอนถัดไป

เอกสารนี้ยังไม่กำหนดการแบ่งงานเป็นรายบุคคล และยังไม่ใช่ Sprint Plan โดยละเอียด

---

# 14.2 Implementation Principles

การพัฒนา LONGTUA ต้องยึดหลักดังต่อไปนี้

### 14.2.1 Design before implementation

Implementation ต้องอ้างอิงเอกสารที่กำหนดไว้แล้ว:

```text id="s5b3yq"
Requirements
    ↓
Domain
    ↓
Architecture
    ↓
AI / NLP
    ↓
Planning
    ↓
Re-planning
    ↓
Schedule / Notification
    ↓
Database
    ↓
API
    ↓
Security
    ↓
UI / UX
    ↓
Testing
    ↓
Implementation
```

หาก implementation พบว่ามี behavior ที่ design ยังไม่ครอบคลุม ต้องปรับ specification ก่อนสร้าง logic ใหม่ที่ขัดกับระบบเดิม

---

### 14.2.2 Single responsibility

แต่ละ module ต้องมี responsibility ชัดเจน

ตัวอย่าง:

```text id="4xj9ea"
AI / NLP
    = Understanding

Planning Core
    = Scheduling / Optimization

Schedule Management
    = Confirmed Schedule Lifecycle

Notification Coordination
    = Local Notification Synchronization
```

ไม่ควรนำ responsibility ของ module หนึ่งไปซ่อนไว้ในอีก module

---

### 14.2.3 Business logic must not depend on UI

กฎของ Planning และ Domain ต้องอยู่ใน Backend / domain layer ไม่ใช่ React component

ตัวอย่างที่ไม่ควรทำ:

```text id="y0j7mz"
React Component
   ↓
Calculate CP-SAT constraints
```

แนวทางที่ถูกต้อง:

```text id="3gq3qj"
React UI
   ↓
API
   ↓
Application Service
   ↓
Domain / Planning
```

---

### 14.2.4 AI output is untrusted input

AI output ต้องถูกมองเป็น external input แม้ AI จะเป็น provider ภายในระบบก็ตาม

```text id="x5v0af"
AI
 ↓
Schema Validation
 ↓
Domain Validation
 ↓
Normalization
 ↓
Planning Representation
```

ห้าม:

```text id="q7j5p4"
AI
 ↓
Database directly
```

หรือ:

```text id="k1s0rv"
AI
 ↓
Confirmed Schedule directly
```

---

### 14.2.5 Confirmed Schedule is authoritative

ในทุก implementation:

```text id="q3gh3h"
Proposal
≠
Confirmed Schedule
```

และ:

```text id="m5l5iy"
Confirmed Schedule
= Source of Truth
```

Calendar และ Notification ต้องอ้างอิง state นี้

---

# 14.3 Target Technology Stack

## Mobile

```text id="d6r9tv"
React Native
Expo
TypeScript
Expo Router
TanStack Query
Zustand
expo-notifications
expo-secure-store
```

Testing:

```text id="jthq9s"
Jest
jest-expo
React Native Testing Library
```

---

## Backend

```text id="95p7f1"
Python 3.14
FastAPI
Pydantic v2
SQLAlchemy 2.x
Alembic
pytest
OR-Tools CP-SAT
```

---

## Database

```text id="o5y7ie"
PostgreSQL
```

---

## AI Provider

Primary:

```text id="cbj6w3"
Google Gemini
```

Alternative:

```text id="b0m8oz"
Claude
```

การเรียก AI ต้องผ่าน provider abstraction

Exact model ID เป็น configuration ที่เลือกตาม implementation/evaluation context และไม่ควร hard-code ใน business logic

---

# 14.4 Repository Structure

MVP ควรแยก Mobile และ Backend ออกจากกันอย่างชัดเจน

ตัวอย่าง:

```text id="v0s4ta"
longtua/
│
├── mobile/
│   ├── app/
│   ├── src/
│   │   ├── components/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── stores/
│   │   ├── services/
│   │   ├── api/
│   │   ├── types/
│   │   ├── utils/
│   │   └── notifications/
│   ├── tests/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── application/
│   │   ├── auth/
│   │   ├── users/
│   │   ├── activities/
│   │   ├── planning/
│   │   ├── ai/
│   │   ├── validation/
│   │   ├── planner/
│   │   ├── proposals/
│   │   ├── schedules/
│   │   ├── availability/
│   │   ├── notifications/
│   │   ├── persistence/
│   │   └── core/
│   ├── tests/
│   ├── alembic/
│   ├── pyproject.toml
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
├── README.md
└── docs/
```

โครงสร้างจริงสามารถปรับชื่อ directory ได้ แต่ responsibility ของ module ต้องยังคงเหมือนใน Architecture Design

---

# 14.5 Backend Layering

Backend ใช้แนวคิด layered modular monolith

```text id="2r3cb8"
API / Router
    ↓
Application Service
    ↓
Domain / Business Logic
    ↓
Infrastructure / Persistence
```

AI และ Planning เป็น module ภายใน application architecture ไม่ใช่ public API แยกออกจากระบบ

---

# 14.6 API Layer

API Layer รับผิดชอบ:

* routing
* authentication dependency
* authorization checks
* request parsing
* response serialization
* HTTP status mapping
* request ID / error handling

API Layer ไม่ควรมี algorithm ขนาดใหญ่

ตัวอย่าง:

```text id="vwq2nt"
POST /api/planning/requests
        ↓
PlanningRequestRouter
        ↓
PlanningApplicationService
```

ไม่ควรทำ:

```text id="zwm3k8"
Router
    ├── Call Gemini
    ├── Build CP-SAT model
    ├── Save DB
    └── Schedule notification
```

ทั้งหมดควรอยู่ใน Application / Domain modules ที่เหมาะสม

---

# 14.7 Application Service

Application Service เป็น orchestration layer

ตัวอย่าง Planning:

```text id="e7m9jo"
Planning Application Service
   ↓
Validate Request
   ↓
Load Relevant Context
   ↓
AI/NLP
   ↓
Validation / Normalization
   ↓
Planning Representation
   ↓
Planning Engine
   ↓
Proposal Creation
   ↓
Persist Result
```

Application Service มีหน้าที่ประสานงาน ไม่ใช่ถือรายละเอียด algorithm ทุกอย่างไว้ใน class เดียว

---

# 14.8 Domain Module Structure

แต่ละ domain module ควรมี responsibility แยกชัดเจน

### Activities

รับผิดชอบ:

* activity lifecycle
* activity validation
* activity CRUD behavior
* cancellation

### Availability

รับผิดชอบ:

* Available / Unavailable
* One-time / Recurring
* validation ของ rule

### Planning

รับผิดชอบ:

* planning request lifecycle
* orchestration
* clarification state

### AI

รับผิดชอบ:

* provider abstraction
* prompt / structured output
* AI response handling

### Validation / Normalization

รับผิดชอบ:

* semantic normalization
* domain safety
* temporal normalization

### Planner

รับผิดชอบ:

* planning representation → CP-SAT
* solve
* feasibility
* optimization
* candidate generation support

### Proposal

รับผิดชอบ:

* proposal lifecycle
* candidate data
* confirm / reject
* stale validation

### Schedule

รับผิดชอบ:

* schedule version
* schedule items
* manual confirmation
* immutable version creation

---

# 14.9 Database Implementation Order

Database ควรสร้างผ่าน Alembic migration ตาม dependency order:

```text id="j4w7lk"
1. users
2. auth_sessions / auth_tokens
3. user_settings
4. planning_requests
5. planning_objects
6. container_memberships
7. availability_rules
8. planning_rules
9. temporal_relations
10. proposals
11. proposal_items
12. schedule_versions
13. schedule_items
14. Final constraints / indexes / FK refinements
```

ต้องรักษาหลักการ:

```text id="4rj0vn"
Migration History
= Source of Database Schema Evolution
```

ไม่ควรแก้ production/test database schema ด้วย manual SQL แล้วปล่อยให้ migration history ไม่ตรงกัน

---

# 14.10 ORM / Schema Separation

ต้องแยก concept:

```text id="gyygp4"
Database Model
API Schema
Domain Model
```

ออกจากกันเมื่อจำเป็น

ไม่ควร expose SQLAlchemy model โดยตรงเป็น public API contract หากทำให้ internal schema กลายเป็น API contract โดยไม่ตั้งใจ

Pydantic schema ใช้สำหรับ request / response validation

---

# 14.11 Planning Representation Implementation

Planning Representation เป็น boundary ระหว่าง:

```text id="m4cbq5"
AI/NLP
      ↓
Planning Representation
      ↓
Planning Engine
```

Representation ต้องเป็น deterministic structure ที่ planner สามารถใช้ได้

ตัวอย่างแนวคิด:

```text id="l4yyql"
PlanningObject
ConstraintSet
PreferenceSet
RelationSet
AvailabilityContext
CurrentSchedule
PlanningWindow
```

Planning Engine ไม่ควรรับ raw natural language

---

# 14.12 AI Provider Adapter

AI ต้องผ่าน abstraction เช่น:

```text id="z0s0wj"
AIProvider
├── GeminiProvider
└── ClaudeProvider
```

Application Layer รู้เพียง interface ที่จำเป็น

ตัวอย่างแนวคิด:

```text id="n8eaqr"
PlanningExtractionResult
```

ไม่ควรให้ business logic ผูกกับ response format ของ provider ใด provider หนึ่ง

---

# 14.13 AI Configuration

Configuration ที่ควรแยกออกจาก source code:

```text id="4m9i6z"
AI_PROVIDER
AI_MODEL
AI_TIMEOUT
AI_TEMPERATURE / equivalent
PROMPT_VERSION
```

ค่าดังกล่าวไม่ควรถูก hard-code ใน module ที่มี business logic

Exact values ใช้ตาม deployment/evaluation configuration

---

# 14.14 Prompt Versioning

Prompt ที่ใช้ในระบบต้องสามารถระบุ version ได้ เช่น:

```text id="a4j17z"
planning-extraction-v1
feedback-interpretation-v1
```

เมื่อเปลี่ยน prompt อย่างมีนัยสำคัญ ต้องสามารถทราบได้ว่า evaluation result มาจาก prompt version ใด

---

# 14.15 AI Response Handling

ลำดับ implementation:

```text id="1b2f4v"
Raw AI Response
       ↓
Parse
       ↓
Schema Validation
       ↓
Domain Validation
       ↓
Normalization
       ↓
Accepted Representation
```

กรณี invalid:

```text id="o0bhqf"
Invalid AI Output
       ↓
Reject / Retry Policy
       ↓
Safe Failure
```

ห้ามนำ malformed result ไปสร้าง Schedule

---

# 14.16 Clarification Implementation

Planning Request ต้องรองรับ state:

```text id="9a8fa3"
RECEIVED
PROCESSING
NEEDS_CLARIFICATION
PLANNING
PROPOSED
COMPLETED
FAILED
```

สถานะจริงสามารถปรับตาม API implementation ได้ แต่ต้องคง semantic เดิม

เมื่อ `NEEDS_CLARIFICATION`:

```text id="udczq2"
Backend
 ↓
Question
 ↓
Mobile
 ↓
User Answer
 ↓
Clarification Response API
 ↓
Continue Planning
```

Clarification context ต้องเชื่อมกลับกับ original planning request

---

# 14.17 Planning Engine Implementation

Planning Engine ควรแยกเป็นขั้น:

```text id="3xejhr"
Build Model
    ↓
Apply Variables
    ↓
Apply Hard Constraints
    ↓
Apply Preferences
    ↓
Apply Stability (Replanning)
    ↓
Solve
    ↓
Extract Solution
    ↓
Validate Solution
```

Planner ไม่ควรรู้เรื่อง HTTP, React หรือ database transaction โดยตรง

---

# 14.18 Solver Model Rules

Implementation ต้องรักษา:

* integer minute representation
* half-open interval semantics
* explicit duration
* hard constraints
* preference objective
* stability objectiveใน Re-planning
* bounded planning horizon

ไม่มีการแปลงเวลาเป็น fixed 15-minute slots โดยอัตโนมัติ หากไม่ใช่ requirement ของ model

---

# 14.19 Solver Result Handling

ผล CP-SAT ต้องถูก map เป็น internal result อย่างชัดเจน:

```text id="u0jv7s"
OPTIMAL
FEASIBLE
INFEASIBLE
UNKNOWN
MODEL_INVALID
```

Application layer จึงค่อยแปลงเป็น API-level outcome

ตัวอย่าง:

```text id="r9v6jx"
INFEASIBLE
    ↓
No Feasible Plan
```

ไม่ควรส่ง raw solver status ให้ Mobile เป็น business behavior ทั้งหมดโดยตรง

---

# 14.20 Solution Validation

แม้ CP-SAT จะ return feasible result ระบบต้อง validate solution อีกครั้งตาม Domain Rules

```text id="f7g1oe"
Solver Solution
      ↓
Independent Validation
      ↓
Valid
```

หรือ:

```text id="3ka6o2"
Solver Solution
      ↓
Validation Failure
      ↓
System Error / Unsafe Result
```

ห้ามสร้าง Confirmed Schedule จาก solution ที่ validation ไม่ผ่าน

---

# 14.21 Candidate Generation

Candidate generation อยู่หลัง successful solving

```text id="p8c2v7"
Feasible Solution
      ↓
Candidate Generation
      ↓
Candidate Validation
      ↓
Proposal
```

หลักการ:

* อาจได้ 1 candidate
* อาจได้ 2 candidates
* อาจได้ 3 candidates
* ไม่สร้าง dummy candidate
* Candidate ต้องมี meaningful difference
* ทุก candidate ต้อง feasible

---

# 14.22 Re-planning Implementation

Re-planning MVP ใช้:

```text id="j7j1e6"
Change Detection
      ↓
Affected Context
      ↓
Bounded Planning Horizon
      ↓
Rebuild Planning Model
      ↓
Solve
      ↓
Compare with Current Schedule
      ↓
Proposal
```

Planner สามารถ rebuild model ใหม่ได้ แต่ต้อง preserve สิ่งที่ไม่ควรถูกเปลี่ยนตาม Re-planning Rules

---

# 14.23 Current Schedule Integration

เมื่อ Re-planning:

```text id="j4tt8x"
Current Schedule
      ↓
Load Existing Placements
      ↓
Determine Movable / Frozen
      ↓
Planning Model
```

Stability:

```text id="1w9csl"
D = Σ |newStart - oldStart|
```

ต้องใช้ร่วมกับ Hard Constraint และ Explicit Requirement ไม่ใช่แทนที่

---

# 14.24 Proposal Implementation

Proposal มี lifecycle:

```text id="5d7e2s"
PENDING
  │
  ├── CONFIRMED
  │
  └── REJECTED

PENDING
  ↓
INVALIDATED
```

Proposal ต้องเก็บ:

```text id="h7o5nj"
source_schedule_version_id
```

เพื่อ stale check

---

# 14.25 Proposal Confirmation Transaction

การ Confirm Proposal เป็น critical transaction

ลำดับ:

```text id="u3v2h0"
BEGIN TRANSACTION
   ↓
Lock / Validate Current Schedule State
   ↓
Check Proposal State
   ↓
Check source_schedule_version_id
   ↓
Validate Candidate
   ↓
Create New Schedule Version
   ↓
Create Schedule Items
   ↓
Mark Previous Current = false
   ↓
Mark New Version = current
   ↓
Mark Proposal = CONFIRMED
   ↓
COMMIT
```

หากขั้นตอนสำคัญล้มเหลว ต้องไม่ทิ้งฐานข้อมูลไว้ใน state ครึ่งหนึ่ง

Notification synchronization ทำหลังจาก confirmed state ถูก commit ตาม design

---

# 14.26 Manual Edit Implementation

Manual Edit:

```text id="s6v0nq"
Confirmed Schedule
      ↓
Mobile Draft
      ↓
Validation API
      ↓
Valid
      ↓
Manual Confirm API
      ↓
New Schedule Version
```

Draft ไม่จำเป็นต้อง persist ใน backend ใน MVP

---

# 14.27 Manual Validation

`POST /api/schedule/validate`:

* รับ draft representation
* ตรวจ Hard Constraints
* ไม่ commit schedule
* ไม่สร้าง Schedule Version
* ไม่สร้าง notification

`POST /api/schedule/manual-confirm`:

* validate อีกครั้ง
* create new version
* update current version
* return new confirmed state

Validation ซ้ำตอน Confirm เป็น requirement เพื่อป้องกัน stale / tampered client state

---

# 14.28 Schedule Version Implementation

Schedule Version ต้องเป็น immutable snapshot

เมื่อ Confirm:

```text id="71rrcc"
Version N
      ↓
Version N+1
```

Version N ไม่ถูก update ให้กลายเป็น Version N+1

Database ต้องรักษา invariant:

```text id="ohf5hh"
Per User
Current Versions = 1
```

---

# 14.29 Notification Coordination Implementation

Notification logic อยู่ Mobile-side coordination layer

```text id="i0xqlm"
Confirmed Schedule API
      ↓
Mobile
      ↓
Calculate Effective Notification
      ↓
Cancel Obsolete Notification
      ↓
Schedule New Local Notification
```

Backend ไม่ต้องเก็บ device-specific notification instance ใน MVP

---

# 14.30 Notification Identity

Local notification ID เป็น device-local identifier

ดังนั้น backend ไม่ควรใช้ notification ID เป็น primary business identifier

Mobile ควรเก็บ mapping ที่จำเป็นเพื่อให้สามารถ:

* cancel
* reschedule
* rebuild notification state

จาก Confirmed Schedule ปัจจุบันได้

---

# 14.31 Mobile State Management

แบ่ง responsibility:

### TanStack Query

ใช้สำหรับ:

* server state
* API data
* caching
* refetch
* mutation state

### Zustand

ใช้สำหรับ:

* local UI state
* temporary flow state
* draft state
* selected date/view
* planning interaction state ที่ไม่เหมาะกับ server cache

ไม่ควรใช้ Zustand เป็น duplicate database ของ backend โดยไม่จำเป็น

---

# 14.32 Local Draft State

Draft ที่ต้องยังไม่ commit เช่น:

* Manual Schedule Edit
* Form input
* Candidate modifications

ควรถูกเก็บใน local state

เมื่อ user ออกจาก flow โดยไม่ได้ Confirm:

```text id="v0e0qj"
Draft discarded
Current Schedule unchanged
```

---

# 14.33 Mobile API Layer

ไม่ควรกระจาย `fetch` / HTTP calls ไปตาม component ต่าง ๆ

โครงสร้าง:

```text id="8e8d0s"
Screen
  ↓
Feature Hook / Mutation
  ↓
API Service
  ↓
HTTP Client
```

เช่น:

```text id="t4u1g9"
useConfirmProposal()
   ↓
proposalApi.confirm()
   ↓
HTTP Client
```

---

# 14.34 UI Implementation from Figma

Figma เป็น visual reference สำหรับ implementation

ลำดับ:

```text id="z1y7ra"
Behavior Specification
      ↓
Figma
      ↓
Component Structure
      ↓
Screen Implementation
```

หาก Figma มี visual decision ที่ขัดกับ behavior specification ให้ยึด behavior/domain/API contract ก่อน

---

# 14.35 Component Strategy

ควรแยก:

```text id="m7r2j7"
Shared Components
    +
Feature Components
    +
Screen Components
```

ตัวอย่าง Shared:

* Button
* Input
* Modal
* Bottom Sheet
* Loading
* Error State
* Empty State

Feature-specific:

* Calendar Event Card
* Proposal Candidate Card
* Conflict Banner
* Clarification Question
* Schedule Comparison

ไม่ควร abstract component มากเกินไปก่อนพบ reuse จริง

---

# 14.36 Calendar Implementation

Calendar View ต้องแยก presentation ตามระดับ:

```text id="4g8f8y"
Year View
Month View
Day View
```

Day Timeline ใช้ Confirmed Schedule

Date-only Activities:

```text id="j2s4mn"
All Day / Unscheduled
```

ไม่ควร map notification default 06:00 เป็น Activity placement

---

# 14.37 Planning Flow Implementation

Mobile flow:

```text id="82hf5z"
Input
 ↓
Submit
 ↓
Loading / Processing
 ↓
Clarification OR Proposal OR Failure
```

หลัง Proposal:

```text id="zqv2m2"
Review
 ├── Confirm
 ├── Reject
 └── Feedback
```

การทำ navigation ต้องรักษา state ของ Planning Request เพื่อให้ user กลับมา review ได้อย่างถูกต้อง

---

# 14.38 Error Mapping

Backend มี common error schema:

```json
{
  "error": {
    "code": "...",
    "message": "...",
    "details": {},
    "requestId": "..."
  }
}
```

Mobile ต้อง map error code ไปยัง behavior ที่เหมาะสม

ตัวอย่าง:

```text id="m6z7rv"
STALE_PROPOSAL
→ Stale Proposal UI

NO_FEASIBLE_PLAN
→ Planning Failure UI

VALIDATION_ERROR
→ Form / Constraint Error

UNAUTHORIZED
→ Authentication Flow

NETWORK_ERROR
→ Retry UI
```

ไม่ควรพึ่งข้อความ error เพียงอย่างเดียวในการตัดสิน behavior

---

# 14.39 Request / Response Contract Discipline

API contract ต้องเป็น shared agreement ระหว่าง Mobile และ Backend

ก่อน implementation ของ feature ใหม่ต้องมี:

```text id="zz1s6x"
Endpoint
Request Schema
Response Schema
Error Cases
State Transition
```

จึงจะเริ่ม implement ได้

ห้ามให้ Mobile เดา response structure แล้วค่อยแก้ backend ตามภายหลัง

---

# 14.40 Idempotency

Operation ที่มี side effect สำคัญควรรองรับ Idempotency-Key ตาม API Design

อย่างน้อย:

```text id="jnsp0j"
POST /api/planning/requests
POST /api/proposals/{id}/confirm
POST /api/schedule/manual-confirm
```

เพื่อป้องกัน duplicate operation จาก retry/network condition

ตัวอย่าง:

```text id="9f0pme"
Confirm ถูกส่ง 2 ครั้ง
      ↓
Server
      ↓
เกิด Schedule Version ใหม่เพียงครั้งเดียว
```

---

# 14.41 Transaction Boundaries

Critical operations ต้องใช้ transaction ตามความเหมาะสม เช่น:

### Confirm Proposal

```text id="k6y2mp"
Proposal
+
Schedule Version
+
Schedule Items
```

### Manual Confirm

```text id="x8s7er"
New Version
+
Schedule Items
+
Current Version Transition
```

Database state ต้องไม่เหลือ partially committed operation

---

# 14.42 Environment Configuration

Environment อย่างน้อย:

```text id="v8xt3m"
Development
Test
Demo / Production-like
```

ตัวแปรสำคัญ:

```text id="1un3zo"
DATABASE_URL
JWT_SECRET
AI_PROVIDER
AI_MODEL
AI_API_KEY
CORS_ORIGINS
ENVIRONMENT
```

Secrets ต้องอยู่ใน environment / secret manager ที่เหมาะสม และไม่มี secret ใน Git

---

# 14.43 Docker Development

Backend และ PostgreSQL ควรสามารถรันใน local development ได้ผ่าน Docker Compose

แนวคิด:

```text id="5qep9s"
docker compose up
      ↓
Backend
PostgreSQL
```

ต้องมี:

* health check
* persistent DB volume ตามความเหมาะสม
* environment configuration
* migration workflow

---

# 14.44 Migration Workflow

เมื่อแก้ schema:

```text id="n5p7f4"
Modify Model
   ↓
Generate / Write Migration
   ↓
Review Migration
   ↓
Run Migration
   ↓
Run Tests
```

ห้ามแก้ schema production โดยตรงแล้วค่อยสร้าง migration ย้อนหลัง

---

# 14.45 Health Check

Backend ต้องมี:

```text id="2l38d7"
GET /api/health
```

ใช้ตรวจ basic application availability

Health check ควรแยกจาก business API และไม่เปิดเผยข้อมูลลับ

---

# 14.46 Logging

Logging ต้องช่วย debug แต่ไม่เปิดเผยข้อมูล sensitive

ควรมี:

* request ID
* endpoint
* status
* timing
* error category
* relevant internal identifier

ไม่ควร log:

* passwords
* JWT / refresh tokens
* AI API keys
* database credentials
* sensitive user data ที่ไม่จำเป็น
* raw prompt/response หากมีข้อมูลที่ไม่ควรเก็บ

---

# 14.47 Observability Baseline

MVP ไม่จำเป็นต้องมีระบบ observability ขนาดใหญ่

อย่างน้อยควรวัด:

```text id="13f5cn"
API response time
Planning time
AI processing time
Database errors
Planning failures
Notification synchronization failures
```

ข้อมูลเหล่านี้มีประโยชน์ต่อ E6 และ Performance Benchmark

---

# 14.48 Coding Standards

## Backend

ควรใช้:

* type hints
* Pydantic validation
* consistent naming
* service boundaries
* small testable functions
* explicit exception mapping

## Mobile

ควรใช้:

* TypeScript strictness ที่เหมาะสม
* typed API models
* reusable hooks
* feature-based organization
* explicit loading/error states

ไม่ควรใช้ `any` เพื่อแก้ type error โดยไม่มีเหตุผล

---

# 14.49 Naming Conventions

ต้องเลือก convention เดียวและใช้ทั้ง project

ตัวอย่าง:

Backend:

```text id="4qk8nh"
snake_case
```

TypeScript:

```text id="t4h3yi"
camelCase
```

Types / Components:

```text id="4xy3xq"
PascalCase
```

API JSON field names ต้องเป็น contract ที่ตกลงแล้ว ไม่เปลี่ยนตาม database naming โดยอัตโนมัติ

---

# 14.50 Git Workflow

ทุก feature ควรพัฒนาบน branch แยก

ตัวอย่าง:

```text id="y9m6fz"
main
  │
  ├── feat/auth
  ├── feat/activity
  ├── feat/planning
  ├── feat/proposal
  └── feat/calendar
```

Pull Request ควรอธิบาย:

* What changed
* Why
* Related requirement/design
* Test performed
* Known limitation

---

# 14.51 Commit Convention

Commit ควรสื่อ intent

ตัวอย่าง:

```text id="32r8dr"
feat: add activity creation API
fix: prevent stale proposal confirmation
test: add replanning stability cases
refactor: separate AI provider adapter
```

ไม่ควรรวม feature ใหญ่หลาย unrelated changes ใน commit เดียวจน review ยาก

---

# 14.52 Implementation Order

ลำดับพัฒนาที่แนะนำ:

```text id="2r7n6q"
Phase 1
Project Foundation
    ↓
Phase 2
Database + Auth
    ↓
Phase 3
Activity + Availability
    ↓
Phase 4
Planning Representation + Validation
    ↓
Phase 5
AI/NLP
    ↓
Phase 6
Planning Engine
    ↓
Phase 7
Proposal + Schedule Version
    ↓
Phase 8
Re-planning
    ↓
Phase 9
Notification Coordination
    ↓
Phase 10
Calendar / Main UI Integration
    ↓
Phase 11
End-to-End Integration
    ↓
Phase 12
Evaluation / Benchmark
```

อย่างไรก็ตาม Mobile UI สามารถพัฒนา Figma/component skeleton แบบขนานกับ Backend ได้ ตราบใดที่ API contract และ behavior ไม่ถูกสมมติขึ้นเอง

---

# 14.53 Phase 1 — Project Foundation

เป้าหมาย:

* repository
* project initialization
* environment configuration
* code quality tools
* Docker Compose
* CI baseline
* base navigation
* FastAPI application
* PostgreSQL connection
* `/health`

Definition of Done:

```text id="v9x0t2"
[ ] Mobile runs
[ ] Backend runs
[ ] Database connects
[ ] Environment separation exists
[ ] Health check works
[ ] Basic CI passes
```

---

# 14.54 Phase 2 — Database + Authentication

Implement:

* users
* auth sessions
* auth tokens
* user settings
* register
* login
* refresh
* logout
* email verification
* password reset
* password security
* ownership middleware

Definition of Done:

* auth flows work
* token lifecycle works
* unauthorized access blocked
* tests pass
* migration reproducible

---

# 14.55 Phase 3 — Activity + Availability

Implement:

* planning objects
* activity CRUD
* cancellation
* availability rules
* recurring availability
* unavailability
* validation

Definition of Done:

* user can create activity
* date-only activity works
* timed activity works
* availability can be stored
* ownership enforced
* conflict-related validation available

---

# 14.56 Phase 4 — Planning Representation + Validation

Implement domain structures for:

* planning objects
* constraints
* preferences
* temporal relations
* time semantics
* unknown
* ambiguous
* unsupported
* normalized time/duration

Definition of Done:

* domain input can be transformed into planner-ready representation
* invalid structures rejected
* no invented planning-critical values
* unit tests cover edge cases

---

# 14.57 Phase 5 — AI/NLP

Implement:

* provider abstraction
* Gemini adapter
* alternative provider adapter structure
* prompt templates
* structured output
* parsing
* schema validation
* clarification decision
* feedback interpretation

Definition of Done:

* natural language can produce structured planning information
* invalid AI output is rejected safely
* provider can be switched through configuration
* evaluation dataset can be executed reproducibly

---

# 14.58 Phase 6 — Planning Engine

Implement:

* CP-SAT model builder
* variable generation
* hard constraints
* preferences
* initial planning
* solution extraction
* independent validation
* no-feasible-plan handling
* candidate generation support

Definition of Done:

* feasible test cases produce valid schedules
* infeasible cases are correctly identified
* Hard Constraint violations cannot appear in accepted solution
* solver status is handled correctly

---

# 14.59 Phase 7 — Proposal + Schedule

Implement:

* proposal creation
* proposal items
* candidate display data
* confirm
* reject
* schedule version
* current version handling
* stale proposal detection

Definition of Done:

```text id="i2m4s0"
Planning
 ↓
Proposal
 ↓
Confirm
 ↓
New Schedule Version
 ↓
Calendar-ready Schedule
```

Confirmed Schedule must only change through valid confirmation

---

# 14.60 Phase 8 — Re-planning

Implement triggers:

* new activity
* date/time change
* duration change
* deadline change
* availability change
* unavailability
* cancellation
* feedback

Implement:

* impact detection
* affected horizon
* current schedule loading
* stability
* full model rebuild
* new proposal

Definition of Done:

* current schedule remains unchanged before confirm
* valid replan produces proposal
* infeasible replan leaves current state unchanged
* stale protection works

---

# 14.61 Phase 9 — Notification Coordination

Implement Mobile-side:

* notification policy
* effective notification calculation
* scheduling
* cancellation
* rescheduling
* rebuild from current schedule

Definition of Done:

```text id="st1uh7"
Confirmed Schedule
→ Notification
```

and never:

```text id="7tpw2v"
Proposal
→ Notification
```

---

# 14.62 Phase 10 — Calendar / Main UI Integration

Implement:

* Year
* Month
* Day
* Today
* Activity Detail
* Manual Activity
* AI Planning
* Clarification
* Proposal
* Feedback
* Re-planning
* Manual Edit
* Conflict
* Availability
* Settings

Definition of Done:

ทุก major UI flow มี:

```text id="b4z7kq"
Default
Loading
Empty
Error
Disabled
Success
```

และ planning flow มี:

```text id="e4e8m9"
Clarification
Proposal
Confirmed
Rejected
Stale
Conflict
```

ตามความเกี่ยวข้อง

---

# 14.63 Phase 11 — End-to-End Integration

รวมระบบทั้งหมด:

```text id="96g7w2"
Mobile
 ↓
API
 ↓
Application
 ↓
AI
 ↓
Validation
 ↓
Planner
 ↓
Proposal
 ↓
Schedule
 ↓
Mobile
 ↓
Notification
```

ต้องทดสอบทั้ง happy path และ failure path

---

# 14.64 Phase 12 — Evaluation / Benchmark

หลัง core implementation stable:

```text id="7kq2y5"
E1 NLP
E2 Initial Planning
E3 Re-planning
E4 Candidates
E5 HITL
E6 End-to-End
Performance Benchmark
```

ต้อง freeze evaluation configuration ก่อน Final Evaluation เพื่อป้องกันการปรับระบบตามผล test set เดียวกัน

---

# 14.65 Parallel Development Rule

เนื่องจากมีผู้พัฒนา 2 คน สามารถทำงาน parallel ได้ แต่ต้องลด shared dependency

หลักการ:

```text id="1f4w3d"
Shared Contract
      ↓
Parallel Implementation
      ↓
Integration
```

ตัวอย่าง:

```text id="9jr1ah"
Person A
Backend / Database / API

Person B
Mobile / Figma / UI
```

แต่ก่อนเริ่ม implementation ที่เชื่อมกันต้องตกลง:

* API request
* API response
* field names
* error codes
* state names

ไม่ควรให้ทั้งสองคนสร้าง contract คนละแบบแล้วค่อย merge ภายหลัง

---

# 14.66 Shared Boundary Documents

ก่อนแบ่งงานแต่ละ feature ต้องอ้างอิง:

```text id="5bz5kw"
Requirements
API Contract
Database Design
Domain Model
UI Behavior
Test Cases
```

สิ่งเหล่านี้เป็น shared source of truth

Code ไม่ควรกลายเป็น source of truth แรกของ requirement

---

# 14.67 Definition of Ready

Task ก่อนเริ่ม implementation ควรมีข้อมูลอย่างน้อย:

```text id="o7q7ue"
Feature
Purpose
Input
Output
Dependencies
API Contract
Database Impact
UI Impact
Validation Rules
Test Cases
```

หากยังตอบไม่ได้ว่า feature ทำงานอย่างไร ไม่ควรรีบเริ่ม coding

---

# 14.68 Definition of Done

Feature ถือว่า Done เมื่อ:

```text id="9o5h3e"
[ ] Requirement implemented
[ ] Domain behavior correct
[ ] API contract correct
[ ] Database changes migrated
[ ] Validation implemented
[ ] Error paths handled
[ ] Tests added
[ ] Relevant integration tests pass
[ ] Security/ownership checked
[ ] UI state handled
[ ] No critical regression
```

สำหรับ feature ที่เกี่ยวกับ Schedule ต้องเพิ่ม:

```text id="2r3b0q"
[ ] Confirmed Schedule consistency checked
[ ] Schedule version behavior checked
[ ] Notification impact checked
```

---

# 14.69 Definition of Done for AI Features

AI-related feature ต้องเพิ่ม:

```text id="j1n7pj"
[ ] Structured schema defined
[ ] Invalid output handled
[ ] Unsupported info handled
[ ] Clarification behavior defined
[ ] Provider configuration separated
[ ] Prompt version identified
[ ] Test dataset available
[ ] Evaluation metric defined
```

---

# 14.70 Definition of Done for Planning Features

Planning-related feature ต้องเพิ่ม:

```text id="f5c0ah"
[ ] Hard constraints tested
[ ] Edge cases tested
[ ] Solver status handled
[ ] Solution independently validated
[ ] Infeasible case handled
[ ] Current schedule preservation checked
[ ] Runtime measurable
```

---

# 14.71 Definition of Done for Re-planning

Re-planning feature ต้องเพิ่ม:

```text id="79wq2a"
[ ] Trigger defined
[ ] Affected context defined
[ ] Horizon defined
[ ] Stability behavior defined
[ ] Current Schedule preserved before confirm
[ ] New Proposal created
[ ] Stale protection tested
[ ] Notification synchronization tested
```

---

# 14.72 Definition of Done for UI

UI feature ต้องมี:

```text id="lv8m0a"
[ ] Figma reference
[ ] Default state
[ ] Loading state
[ ] Empty state where applicable
[ ] Error state
[ ] Disabled state where applicable
[ ] Navigation flow
[ ] API loading behavior
[ ] API failure behavior
[ ] Accessibility baseline
```

---

# 14.73 Integration Order

การรวม module ควรทำตาม dependency:

```text id="25ktdl"
Database
   ↓
Repository
   ↓
Domain
   ↓
Application Service
   ↓
API
   ↓
Mobile API Client
   ↓
UI
```

AI/Planner integration:

```text id="cycq37"
AI Adapter
   ↓
Planning Representation
   ↓
Planner
   ↓
Proposal
   ↓
Schedule
```

Notification:

```text id="p1n7fm"
Confirmed Schedule
   ↓
Mobile Notification Coordinator
```

---

# 14.74 No Premature Optimization

MVP ไม่ควรเริ่มจาก:

* microservices
* distributed queue
* Kubernetes
* complex caching
* event sourcing
* separate planning service
* autonomous AI agent

เว้นแต่ benchmark หรือ implementation evidence แสดงว่าจำเป็นจริง

แนวทางหลัก:

```text id="4t7jgu"
Simple Correct Architecture
        ↓
Measure
        ↓
Identify Bottleneck
        ↓
Optimize Only When Needed
```

---

# 14.75 Performance-aware Implementation

แม้จะไม่ optimize ล่วงหน้า แต่ module ที่มีผลต่อ performance ต้องวัดเวลาไว้ตั้งแต่ implementation

อย่างน้อย:

```text id="qkkxm0"
AI Processing Time
Validation Time
Planning Time
Database Time
API Total Time
```

เพื่อรองรับ Performance Benchmark ในภายหลัง

---

# 14.76 Security-aware Implementation

ทุก feature ต้องตรวจ:

* Authentication
* Authorization
* Ownership
* Input validation
* Secret handling
* Logging safety
* Rate limiting ตาม endpoint
* AI input safety
* transaction correctness

Security ไม่ควรถูกเลื่อนไปเป็นขั้นตอนสุดท้ายหลัง feature ทั้งหมดเสร็จ

---

# 14.77 Data Integrity Rules in Code

Critical invariants ต้องสามารถถูก enforce ทั้งระดับ:

```text id="n73v02"
Application
+
Database
```

ตัวอย่าง:

### Current Version

Application:

```text id="a0o1wy"
only one current version
```

Database:

```text id="c57s5q"
partial unique constraint
```

### Proposal

Application ตรวจ stale

และ database transaction ต้องป้องกัน inconsistent confirmation state

---

# 14.78 Feature Dependency Map

```text id="j0xop7"
Authentication
    ↓
Activities
    ↓
Availability / Rules
    ↓
Planning Representation
    ↓
AI / NLP
    ↓
Planning Engine
    ↓
Proposal
    ↓
Schedule
    ↓
Re-planning
    ↓
Notifications
    ↓
E2E
```

Calendar UI สามารถเริ่มทำก่อน Planning เสร็จได้ โดยใช้ mock API หรือ fixture ใน development แต่ต้องไม่สร้าง business behavior แตกต่างจาก specification

---

# 14.79 Mocking Strategy

ระหว่างพัฒนา สามารถ mock:

* AI Provider
* Planning Engine
* API responses
* Notification API

เพื่อให้พัฒนา Mobile และ Backend แบบขนานได้

แต่ก่อนเข้าสู่ Final Integration:

```text id="xkz1cy"
Mock
 ↓
Real Implementation
 ↓
Integration Test
```

ต้องมีการเปลี่ยนเป็น real component

ไม่ควรใช้ mock ในผล Final Evaluation

---

# 14.80 Test Data Fixtures

ควรสร้าง reusable fixtures สำหรับ:

* user
* activities
* availability
* constraints
* current schedule
* proposals
* schedule versions
* clarification cases

เพื่อให้ test case แต่ละชุดไม่ต้องสร้างข้อมูลซ้ำทั้งหมด

---

# 14.81 Demo Data

Demo data ต้องแยกจาก production/evaluation dataset

ควรมี scenario ที่สามารถแสดง:

```text id="q9vlb8"
1. Initial Plan
2. Multiple Candidates
3. Conflict
4. Re-planning
5. Notification Update
```

แต่ Demo data ต้องไม่ถูกนำไปใช้เป็นหลักฐานของ Evaluation

---

# 14.82 Development Milestone

Milestone ที่สำคัญ:

### M1 — Foundation Ready

Application และ database สามารถรันได้

### M2 — CRUD Ready

Activity / Availability / Auth ทำงาน

### M3 — AI Ready

Natural Language → Structured Representation

### M4 — Planner Ready

Structured Representation → Feasible Schedule

### M5 — HITL Ready

Proposal → Review → Confirm / Feedback

### M6 — Adaptive Ready

Change → Re-planning → New Proposal

### M7 — Product Flow Ready

Calendar + Notification + Settings

### M8 — Evaluation Ready

E1–E6 + Benchmark พร้อมรัน

---

# 14.83 Minimum Viable Vertical Slice

ก่อนพัฒนา feature จำนวนมาก ควรทำ vertical slice ให้ end-to-end ทำงานได้ก่อน

Target:

```text id="0u7pve"
User
 ↓
Login
 ↓
Natural Language
 ↓
AI
 ↓
Validation
 ↓
CP-SAT
 ↓
Proposal
 ↓
Confirm
 ↓
Schedule
 ↓
Calendar
 ↓
Notification
```

Vertical slice นี้ช่วยตรวจ architecture ตั้งแต่ต้นก่อนที่แต่ละ module จะถูกพัฒนาแยกจน integration ยาก

---

# 14.84 Recommended First Vertical Slice

Scenario:

> “พรุ่งนี้ตอน 19:00 อ่านหนังสือ 2 ชั่วโมง”

Expected:

```text id="y6l4rj"
Input
 ↓
AI/NLP
 ↓
Activity
Date = tomorrow
Start = 19:00
Duration = 2h
 ↓
Validation
 ↓
Planning
 ↓
Proposal
 ↓
Confirm
 ↓
Schedule Version
 ↓
Day View
 ↓
Notification
```

จากนั้นค่อยเพิ่ม:

```text id="v5j0t4"
Ambiguity
Availability
Conflict
Multiple Candidate
Feedback
Re-planning
Manual Edit
```

---

# 14.85 Implementation Risk Control

ความเสี่ยงหลักระหว่าง coding:

### AI Output Instability

แก้ด้วย:

* schema validation
* prompt versioning
* provider abstraction
* evaluation dataset

### Planner Complexity

แก้ด้วย:

* แยก representation
* unit tests
* small constraint modules
* benchmark

### Mobile/Backend Contract Drift

แก้ด้วย:

* API contract
* typed schemas
* integration test

### Notification Inconsistency

แก้ด้วย:

* Confirmed Schedule as source of truth
* deterministic notification sync

### Schedule Corruption

แก้ด้วย:

* immutable versions
* transactions
* stale check
* independent validation

---

# 14.86 Implementation Anti-patterns

ห้าม:

```text id="6c4jve"
UI
 ↓
Direct DB logic
```

ห้าม:

```text id="0p5g6v"
AI
 ↓
Direct Schedule Update
```

ห้าม:

```text id="7drj9x"
Proposal
 ↓
Automatically Confirm
```

ห้าม:

```text id="3gjn8f"
Notification
 ↓
Used as Schedule Source
```

ห้าม:

```text id="k7sk3y"
Invalid AI Output
 ↓
CP-SAT
```

ห้าม:

```text id="w9t3uo"
Failed Re-planning
 ↓
Overwrite Current Schedule
```

---

# 14.87 Final Implementation Flow

เมื่อระบบถูก implement จริง ให้มองเป็น pipeline:

```text id="cs17mm"
User
 ↓
Mobile UI
 ↓
API
 ↓
Application Service
 ↓
AI / NLP
 ↓
Validation / Normalization
 ↓
Planning Representation
 ↓
Planning Engine
 ↓
Proposal
 ↓
User Review
 ↓
Confirm
 ↓
Schedule Version
 ↓
Mobile Calendar
 ↓
Notification Coordination
```

เมื่อมีการเปลี่ยนแปลง:

```text id="e1ovx6"
Current Schedule
 ↓
Change
 ↓
Re-planning
 ↓
New Proposal
 ↓
User Review
 ↓
Confirm
 ↓
New Schedule Version
 ↓
Notification Sync
```

---

# 14.88 Final Development Principle

การ implementation ของ LONGTUA ต้องไม่เริ่มจาก “เขียนทุกอย่างให้ใช้งานได้ก่อน แล้วค่อยจัด architecture”

แต่ต้องเป็น:

```text id="gq7xgq"
Understand
   ↓
Specify
   ↓
Contract
   ↓
Implement
   ↓
Test
   ↓
Integrate
   ↓
Measure
   ↓
Improve
```

และในส่วนที่มีความเสี่ยงสูง:

```text id="k9a7s0"
AI
+
Planning
+
Re-planning
+
Schedule Consistency
```

ต้องมี test และ validation ตั้งแต่ implementation แรก ไม่ใช่เพิ่มหลังจากระบบเสร็จ

เป้าหมายของเอกสารนี้คือทำให้เมื่อเริ่ม Coding แล้ว ทั้งสองคนสามารถตอบได้ชัดเจนว่า:

> **“Feature นี้อยู่ module ไหน, รับอะไร, ส่งอะไร, เปลี่ยน state อะไร, ต้องผ่าน validation อะไร และจะรู้ได้อย่างไรว่ามันเสร็จแล้ว”**
