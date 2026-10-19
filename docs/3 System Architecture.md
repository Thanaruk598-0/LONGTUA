# 3. System Architecture

## 3.1 Purpose

เอกสารฉบับนี้กำหนดสถาปัตยกรรมของระบบ LONGTUA — Personal Adaptive Planner เพื่ออธิบายโครงสร้างของระบบ ขอบเขตความรับผิดชอบของแต่ละส่วน การไหลของข้อมูล การติดต่อระหว่าง Mobile Application, Backend, AI/NLP, Validation, Planning Engine, Schedule Management, Notification และ Database รวมถึงข้อกำหนดด้าน Security, Reliability และ Deployment

Architecture นี้ใช้เป็นพื้นฐานร่วมกันสำหรับ:

* Database Design
* API Design
* AI/NLP Design
* Planning Engine Design
* Replanning Design
* UI/UX Implementation
* Testing
* Deployment

สถาปัตยกรรมของระบบออกแบบเป็น **Modular Monolith** โดยรวม Backend Modules ไว้ใน Application เดียว แต่แยก Responsibility และ Boundary ของแต่ละ Module อย่างชัดเจน

---

# 3.2 Architectural Goals

สถาปัตยกรรม LONGTUA มีเป้าหมายหลักดังนี้

### 3.2.1 Separation of Responsibilities

แยกหน้าที่ระหว่าง:

```text
User Interaction
AI / NLP
Validation / Normalization
Planning
Schedule Management
Notification
Persistence
```

เพื่อไม่ให้ Module ใดรับผิดชอบมากเกินขอบเขต

### 3.2.2 Human Control

ระบบต้องทำให้ User เป็นผู้ตัดสินใจขั้นสุดท้าย โดยผลของ AI หรือ Planning Engine ไม่สามารถเปลี่ยน Confirmed Schedule ได้โดยอัตโนมัติ

### 3.2.3 AI / Planner Separation

AI/NLP มีหน้าที่ตีความข้อมูล

Planning Engine มีหน้าที่จัดตาราง

ทั้งสองส่วนต้องไม่รวม Responsibility เข้าด้วยกัน

### 3.2.4 Adaptability

Architecture ต้องรองรับการสร้าง Schedule ใหม่เมื่อข้อมูลหรือสถานการณ์เปลี่ยน โดยไม่ต้องเปลี่ยนโครงสร้างระบบหลัก

### 3.2.5 Testability

AI/NLP และ Planning Engine ต้องสามารถทดสอบแยกจากกันด้วย Structured Input

### 3.2.6 Maintainability

AI Provider และ Implementation รายละเอียดภายในแต่ละ Module ต้องสามารถเปลี่ยนได้โดยไม่กระทบส่วนอื่นเกินความจำเป็น

---

# 3.3 Architectural Style

LONGTUA ใช้รูปแบบ:

> **Modular Monolith + REST API + Layered / Domain-Oriented Internal Modules**

Backend เป็น Application เดียว แต่แบ่งเป็น Modules ตาม Domain และ Responsibility

ภาพรวม:

```text
+-------------------------------------------------------+
|                 LONGTUA Mobile App                    |
|               React Native + Expo                     |
+-----------------------------+-------------------------+
                              |
                              | HTTPS / JSON
                              v
+-------------------------------------------------------+
|                LONGTUA Backend                       |
|                FastAPI Modular Monolith               |
|                                                       |
|  +----------------+  +------------------------------+ |
|  | API Layer      |  | Application / Orchestration  | |
|  +----------------+  +------------------------------+ |
|            |                    |                     |
|            +----------+---------+                     |
|                       |                               |
|     +-----------------+------------------+            |
|     |                 |                  |            |
|     v                 v                  v            |
|  AI / NLP      Validation /        Planning Core     |
|                Normalization             |            |
|                                           v           |
|                                   Schedule Mgmt       |
|                                           |           |
|                              +------------+--------+  |
|                              |                     |  |
|                              v                     v  |
|                        Persistence           Evaluation|
|                              |                      |  |
+------------------------------+----------------------+--+
                               |
                               v
                        +-------------+
                        | PostgreSQL  |
                        +-------------+

                       +------------------+
                       | AI Provider      |
                       | Gemini Primary   |
                       | Claude Alternative|
                       +------------------+
```

---

# 3.4 High-Level System Context

LONGTUA ประกอบด้วยองค์ประกอบหลัก 3 กลุ่ม

## 3.4.1 Client Layer

คือ Mobile Application ที่ User ใช้โดยตรง

Technology:

* React Native
* Expo
* TypeScript
* Expo Router
* TanStack Query
* Zustand
* expo-notifications
* expo-secure-store

Responsibility:

* รับ Input จาก User
* แสดง Calendar
* แสดง Planning Status
* แสดง Clarification
* แสดง Proposal
* รับ User Decision
* จัดการ Draft UI
* จัดการ Local Notification
* จัดเก็บ Client-side State ที่จำเป็น

Mobile Application **ไม่รับผิดชอบ Business Logic สำคัญของระบบ**

---

# 3.4.2 Application / Backend Layer

Backend ทำหน้าที่เป็นศูนย์กลางการประสานงานของระบบ

Technology:

* Python 3.14
* FastAPI
* Pydantic v2
* SQLAlchemy 2.x
* Alembic

Responsibility:

* Authentication
* Authorization
* Request Validation
* Application Orchestration
* AI/NLP Integration
* Planning Orchestration
* Proposal Management
* Schedule Management
* Persistence
* Domain Rule Enforcement
* Error Handling

Backend เป็น Modular Monolith จึงสามารถเรียก Module ภายในโดยตรงได้ โดยไม่ต้องใช้ Network Call ระหว่าง Module

---

# 3.4.3 External / Infrastructure Layer

ประกอบด้วย:

### Database

PostgreSQL

ใช้สำหรับ:

* User Data
* Planning Objects
* Rules
* Requests
* Proposals
* Schedule Versions
* Schedule Items
* Authentication State

### AI Provider

Primary:

> Google Gemini

Alternative:

> Claude

การเรียก AI ต้องผ่าน Provider Adapter เพื่อป้องกันการผูก Business Logic เข้ากับ Provider รายใดรายหนึ่ง

### Planning Engine

ใช้:

> Google OR-Tools CP-SAT

เป็น Computational Core สำหรับ Constraint-Based Scheduling

---

# 3.5 Internal Backend Modules

Backend แบ่งเป็น Module หลักดังนี้

```text
1. Authentication
2. User / Settings
3. Planning Request
4. AI / NLP
5. Validation / Normalization
6. Planning Representation
7. Planning Core
8. Proposal Management
9. Schedule Management
10. Availability / Rules
11. Notification Coordination
12. Persistence
13. Evaluation / Metrics
```

รายละเอียดแต่ละ Module ดังนี้

---

# 3.6 Authentication Module

## Responsibility

* Register
* Login
* Refresh
* Logout
* Email Verification
* Password Reset
* Session Management
* Token Management

## Data

เกี่ยวข้องกับ:

```text
users
auth_sessions
auth_tokens
```

## Boundary

Authentication Module ต้องเป็นผู้ระบุ User Identity ที่ผ่านการ Authenticate แล้วให้ Application Layer

Module อื่นไม่ควรรับ `user_id` จาก Client เพื่อใช้เป็นแหล่งความจริงในการ Authorization

---

# 3.7 User / Settings Module

ดูแลข้อมูลที่ผู้ใช้กำหนดเป็น Personal Settings เช่น:

* Semantic Time Windows
* Notification Defaults

เกี่ยวข้องกับ:

```text
user_settings
```

Time Window และ Notification Policy ที่เป็น User-specific ต้องถูกอ่านผ่าน Module นี้

---

# 3.8 Planning Request Module

Planning Request เป็น Application-level object ที่ใช้ติดตามคำขอวางแผน

หน้าที่:

* รับ Planning Request
* สร้าง Request Context
* ติดตาม Processing State
* เก็บ Parent Request สำหรับ Clarification Flow
* เก็บ Planning Range
* เก็บ Processing Metrics

Lifecycle:

```text
RECEIVED
    ↓
PROCESSING
    ├── NEEDS_CLARIFICATION
    │       ↓
    │   PROCESSING
    │
    ├── COMPLETED
    └── FAILED
```

Planning Request Module เป็นตัวเชื่อมระหว่าง User Request กับ AI/NLP และ Planning Core

---

# 3.9 AI / NLP Module

AI/NLP Module เป็น **Understanding Layer**

หน้าที่:

```text
Natural Language
      ↓
Interpretation
      ↓
Structured Planning Information
```

ความสามารถหลัก:

* Event / Activity Extraction
* Planning Object Classification
* Activity Type Classification
* Temporal Information Extraction
* Temporal Relation Extraction
* Contextual Interpretation
* Ambiguity Detection
* Missing Information Detection
* Clarification Decision
* User Feedback Interpretation

AI/NLP อาจใช้โมเดลจาก External AI Provider แต่ Application ต้องไม่ผูก Domain Logic กับ Provider

---

# 3.10 AI Provider Adapter

เนื่องจากระบบใช้ AI Provider ภายนอก จึงต้องมี Adapter Layer

รูปแบบ:

```text
Application
    ↓
AI Service Interface
    ↓
Provider Adapter
   ├── Gemini Adapter
   └── Claude Adapter
```

Business Logic ไม่ควรเรียก Gemini SDK หรือ Claude SDK โดยตรง

ข้อดี:

* เปลี่ยน Provider ได้
* ทดสอบ AI Service ได้ง่าย
* ลด Vendor Lock-in
* ควบคุม Structured Output Contract ในชั้นเดียว

Primary Provider ใน MVP:

> Gemini

Alternative:

> Claude

Model ID จริงเป็น Configuration ที่ตรวจสอบและกำหนดใน Implementation/Evaluation

---

# 3.11 Validation / Normalization Module

AI Output ต้องไม่ถูกส่งเข้า Planning Engine โดยตรง

Flow:

```text
AI Output
   ↓
Schema Validation
   ↓
Domain Validation
   ↓
Normalization
   ↓
Planning Representation
```

หน้าที่:

### Schema Validation

ตรวจสอบโครงสร้างของ AI Output

### Domain Validation

ตรวจสอบความถูกต้องตาม Domain Rule

### Normalization

เช่น:

```text
“ช่วงบ่าย”
    ↓
AFTERNOON
    ↓
User Time Window / System Default
    ↓
Concrete Time Range
```

หรือ:

```text
“พรุ่งนี้”
    ↓
Reference Time
    ↓
Concrete Date
```

Module นี้มีหน้าที่ป้องกันข้อมูลที่ผิดหรือข้อมูลที่ AI สร้างขึ้นโดยไม่ถูกต้องไม่ให้เข้าสู่ Planning Core

---

# 3.12 Planning Representation Module

เป็น Boundary ระหว่าง Understanding และ Scheduling

AI/NLP ส่ง:

> Structured Planning Information

Validation/Normalization แปลงเป็น:

> Planning Representation

ซึ่งเป็นรูปแบบกลางที่ Planning Engine ใช้งานได้

ตัวอย่างเชิงแนวคิด:

```text
Natural Language
     ↓
AI Interpretation
     ↓
{
  Activity,
  Date,
  Time,
  Duration,
  Deadline,
  Constraints,
  Preferences,
  Relations
}
     ↓
Planning Representation
     ↓
CP-SAT
```

Planning Representation ต้องไม่ขึ้นอยู่กับ Prompt หรือรูปแบบ Response ของ AI Provider

---

# 3.13 Planning Core

Planning Core เป็น **Scheduling / Optimization Layer**

ใช้ Google OR-Tools CP-SAT

หน้าที่:

* สร้าง Decision Variables
* สร้าง Hard Constraints
* สร้าง Preferences / Objective
* ตรวจ Feasibility
* Solve
* Candidate Generation
* Replanning

Planning Core รับเฉพาะ Structured Planning Representation

ไม่รับ:

* Raw Natural Language
* Prompt
* AI Response แบบดิบ
* User Interface State

---

# 3.14 Planning Objective Hierarchy

Planning Core ใช้ลำดับความสำคัญ:

```text
1. Hard Constraints
        ↓
2. Explicit User Requirements
        ↓
3. Preferences
        ↓
4. Stability
        ↓
5. Optional Activities
```

ความหมายคือ:

> Feasibility มาก่อน Quality

และ:

> Stability ไม่ควรทำให้ Requirement ใหม่ของ User ถูกละเลย

ใน Initial Planning ยังไม่มี Existing Schedule ที่ต้องรักษา จึงไม่จำเป็นต้องให้ Stability เป็น Objective หลัก

ใน Replanning จึงนำ Existing Schedule มาใช้เป็น Stability Reference

---

# 3.15 Planning Horizon

Planning Horizon เป็นขอบเขตเวลาที่ Planning Engine ใช้ในการคำนวณแต่ละครั้ง

ต้องแยกออกจาก:

> Calendar Data Range

กล่าวคือ:

```text
Calendar
= เก็บ/ดูข้อมูลได้ระยะยาว

Planning Horizon
= ขอบเขตการคำนวณของ CP-SAT
```

ตัวอย่าง:

```text
Activity
15 February
```

สามารถมีอยู่ใน Calendar แม้ Planning Operation ปัจจุบันจะทำงานในช่วง January

เมื่อมีการแก้ Activity ดังกล่าวและมีผลต่อ Schedule ระบบอาจกำหนด Affected Replanning Horizon ใหม่ตามบริบท

---

# 3.16 Proposal Management Module

Planning Core ไม่เขียน Confirmed Schedule โดยตรง

Flow:

```text
Planning Core
      ↓
Candidate(s)
      ↓
Proposal Management
      ↓
Proposal
      ↓
User Review
```

Proposal Status:

```text
PENDING
CONFIRMED
REJECTED
INVALIDATED
```

Proposal ต้องเก็บ Source Schedule Version เพื่อป้องกัน Stale Proposal

---

# 3.17 Schedule Management Module

Schedule Management รับผิดชอบ:

* Current Schedule
* Schedule Version
* Schedule Item
* Confirmation
* Manual Confirmation
* Historical Schedule

Model:

```text
Confirmed Schedule
      ↓
Schedule Version N
      ↓
Schedule Items
```

เมื่อมีการเปลี่ยน:

```text
Version N
   ↓
User Confirmation
   ↓
Version N+1
```

Schedule Version เดิมต้องไม่ถูกแก้ไข

---

# 3.18 Draft Schedule

Manual Editing จะไม่แก้ Confirmed Schedule โดยตรง

Flow:

```text
Confirmed Schedule
       ↓
Draft
       ↓
Manual Edit
       ↓
Validate
   ├── Conflict
   └── Valid
           ↓
        Confirm
           ↓
    New Schedule Version
```

Draft เป็น Client/Application State ใน MVP และไม่จำเป็นต้อง Persist เป็น Database Entity

เหตุผลคือ Draft ยังไม่ถือเป็น Confirmed State

---

# 3.19 Replanning Module

Replanning เป็นกระบวนการที่ใช้ Existing Schedule ร่วมกับข้อมูลใหม่

Input:

```text
Current Schedule
+
Changed Information
+
Current Constraints
+
New Requirements
+
Preferences
```

Flow:

```text
Change
   ↓
Impact Detection
   ↓
Affected Context
   ↓
Affected Horizon
   ↓
Freeze Past / Unaffected Context
   ↓
Rebuild Planning Model
   ↓
CP-SAT Solve
   ↓
Proposal
```

MVP ใช้:

> Full model rebuild + re-solve

แต่ทำเฉพาะใน bounded affected horizon

---

# 3.20 Stability Handling

ใน Replanning ระบบต้องพยายามลดการเปลี่ยนแปลงที่ไม่จำเป็นใน Existing Schedule

Operational Metric:

```text
D = Σ |s_new(i) - s_old(i)|
```

โดย:

* `s_new(i)` = Start Time ใหม่
* `s_old(i)` = Start Time เดิม

ค่า `D` ใช้เป็นตัววัด Schedule Change / Stability

Stability เป็น Objective ลำดับหลัง Requirement และ Preference

---

# 3.21 Candidate Generation

Candidate Generation เป็นหน้าที่ของ Planning Core

ไม่ใช่หน้าที่ของ AI

Flow:

```text
CP-SAT / Planning
       ↓
Feasible Solutions
       ↓
Candidate Selection
       ↓
Candidate A / B / C
```

Candidate Count:

```text
1 ≤ Candidate Count ≤ 3
```

แต่จำนวนจริงอาจเป็น 1, 2 หรือ 3

ระบบต้องสร้าง Candidate เพิ่มเมื่อ:

* มีหลาย Feasible Solution
* มีคุณภาพที่ยอมรับได้
* มีความแตกต่างอย่างมีความหมาย

ไม่ต้องสร้าง Candidate เทียม

กรณี Schedule ถูกกำหนดตายตัว ระบบสามารถส่งเพียงหนึ่ง Candidate ได้

---

# 3.22 Schedule and Notification Boundary

Notification ไม่ใช่ Source of Truth

```text
Confirmed Schedule
        ↓
Notification Derivation
        ↓
Local Notification
```

ดังนั้น:

```text
Proposal
   X
   ↓
Notification

Confirmed Schedule
   ✓
   ↓
Notification
```

Notification Instance อยู่ฝั่ง Mobile และไม่ต้องถูก Persist เป็น Backend Entity ใน MVP

---

# 3.23 Local Notification Architecture

Mobile Application ใช้:

> `expo-notifications`

สำหรับ Local Notification

Backend มีหน้าที่ส่ง Schedule State ที่ได้รับการยืนยันแล้ว

Mobile รับผิดชอบ:

* สร้าง Local Notification
* ยกเลิก Notification เดิม
* สร้าง Notification ใหม่
* จัดการ Device-specific Notification Identifier

ตัวอย่าง:

```text
Confirmed Schedule
09:00 Activity
Notification = 08:00
      ↓
Schedule changed
      ↓
12:00 Activity
      ↓
Cancel old local notification
      ↓
Schedule new local notification
```

Backend ไม่จำเป็นต้องรู้ Local Notification Identifier ของแต่ละ Device

---

# 3.24 Persistence Layer

Persistence Layer ทำหน้าที่แปลง Domain/Application State ไปยัง PostgreSQL

Technology:

* SQLAlchemy 2.x
* Alembic
* PostgreSQL

หลักการ:

> Business Logic ไม่ควรขึ้นอยู่กับ SQL ที่กระจายอยู่ทั่วระบบ

Database เป็น Persistent Source สำหรับ User-Owned Data และ Historical Schedule

---

# 3.25 Database Boundary

14 ตารางหลัก:

```text
users
auth_sessions
auth_tokens
user_settings

planning_objects
container_memberships
availability_rules
planning_rules
temporal_relations

planning_requests
proposals
proposal_items

schedule_versions
schedule_items
```

แต่ Architecture ไม่ควรผูก Module ทุกตัวเข้ากับทุก Table โดยตรง

ตัวอย่าง:

```text
Planning Core
    ↓
Planning Model
    ↓
Application Layer
    ↓
Repositories / Persistence
    ↓
PostgreSQL
```

ไม่ควรเป็น:

```text
Planning Core
    ↓
SQLAlchemy Model โดยตรงทุกจุด
```

---

# 3.26 API Layer

API Layer เป็น Boundary ระหว่าง Mobile และ Backend

Technology:

> FastAPI + JSON over HTTPS

Base Path:

```text
/api
```

ไม่มี `/v1` ใน MVP

API Layer รับผิดชอบ:

* Authentication
* Request Parsing
* Schema Validation
* Calling Application Services
* Response Formatting
* Error Mapping

API Layer ไม่ควรฝัง Planning Algorithm หรือ AI Prompt Logic โดยตรง

---

# 3.27 Application / Orchestration Layer

Application Layer เชื่อม Domain Modules เข้าด้วยกัน

ตัวอย่าง:

```text
POST /api/planning/requests
        ↓
Planning Application Service
        ↓
AI/NLP
        ↓
Validation
        ↓
Planning Representation
        ↓
Planning Core
        ↓
Proposal Management
        ↓
Response
```

Application Layer จึงทำหน้าที่:

> “ประสานกระบวนการ”

ไม่ใช่:

> “รับผิดชอบทุก Business Rule”

Business Rule ที่สำคัญควรอยู่ใน Domain/Service ที่เหมาะสม

---

# 3.28 End-to-End Data Flow

## 3.28.1 Initial Planning

```text
+--------+
| User   |
+----+---+
     |
     | Natural Language
     v
+-----------------+
| Mobile App      |
+--------+--------+
         |
         | HTTPS
         v
+-------------------------+
| API / Application Layer |
+-----------+-------------+
            |
            v
+-----------------+
| AI / NLP        |
+--------+--------+
         |
         v
+-------------------------+
| Validation / Normalize  |
+-----------+-------------+
            |
            v
+-------------------------+
| Planning Representation |
+-----------+-------------+
            |
            v
+-----------------+
| Planning Core   |
| CP-SAT          |
+--------+--------+
         |
         v
+-----------------+
| Candidate(s)    |
+--------+--------+
         |
         v
+-----------------+
| Proposal        |
+--------+--------+
         |
         v
+-----------------+
| User Review     |
+--------+--------+
         |
         +------ Reject
         |
         +------ Feedback
         |
         +------ Edit
         |
         +------ Confirm
                        |
                        v
              +------------------+
              | Schedule Version |
              +--------+---------+
                       |
                       v
              +------------------+
              | Local Notification|
              +------------------+
```

---

# 3.29 Clarification Flow

```text
Natural Language
      ↓
AI / NLP
      ↓
Ambiguity / Missing Critical Info
      ↓
Planning Request
      ↓
NEEDS_CLARIFICATION
      ↓
User Answer
      ↓
Parent Request Context
      ↓
AI / NLP
      ↓
Validation
      ↓
Planning
      ↓
Proposal
```

ตัวอย่าง:

```text
“พรุ่งนี้ 6 โมงไปวิ่ง”
            ↓
      Ambiguous Time
            ↓
“หมายถึง 06:00 หรือ 18:00?”
            ↓
         User Answer
```

AI ต้องไม่เดาเมื่อ Ambiguity มีผลต่อ Planning

---

# 3.30 Replanning Data Flow

```text
Current Confirmed Schedule
             +
       New User Input
             |
             v
      Impact Detection
             |
             v
      Affected Context
             |
             v
      Replanning Horizon
             |
             v
   Planning Representation
             |
             v
       Planning Core
             |
             v
       New Proposal
             |
             v
        User Review
             |
        +----+----+
        |         |
      Reject    Confirm
                    |
                    v
            Schedule Version N+1
```

---

# 3.31 Feedback Flow

Feedback เป็น Input เพิ่มเติมที่สามารถนำไปสู่ Replanning

```text
Proposal
   ↓
User Feedback
   ↓
AI / NLP
   ↓
Structured Requirement / Preference
   ↓
Validation
   ↓
Replanning
   ↓
New Proposal
```

ตัวอย่าง:

> “ขอเลื่อนอ่านหนังสือไปช่วงเย็น และไม่อยากให้กระทบเวลานอน”

AI/NLP ทำหน้าที่แปลงข้อความเป็น structured requirement/preference

Planning Engine เป็นผู้ตัดสินใจว่าจะจัดเวลาอย่างไร

---

# 3.32 Authentication and Authorization Flow

```text
User
 ↓
Login
 ↓
Backend
 ↓
Verify Credentials
 ↓
Create Session / Token
 ↓
Access Protected Endpoint
 ↓
Authentication
 ↓
Authorization / Ownership Check
 ↓
Business Operation
```

Ownership ต้องตรวจสอบฝั่ง Server

Client ไม่สามารถกำหนดว่า Resource ใดเป็นของตนเองเพียงแค่ส่ง `userId`

---

# 3.33 Confirmed Schedule State Transition

เฉพาะ Explicit Confirmation เท่านั้นที่สามารถสร้าง Schedule Version ใหม่

```text
Proposal PENDING
       |
       | User Confirm
       v
Proposal CONFIRMED
       |
       v
New Schedule Version
       |
       v
Current Schedule
       |
       v
Notification Derivation
```

กรณี Reject:

```text
Proposal PENDING
       |
       | User Reject
       v
Proposal REJECTED
```

กรณี Proposal ถูกทำให้ไม่สามารถใช้งานได้:

```text
Proposal PENDING
       |
       v
Proposal INVALIDATED
```

---

# 3.34 Stale Proposal Protection

เพื่อป้องกัน Proposal ที่สร้างจาก Schedule Version เก่า

```text
Current Schedule = V3

Proposal P
Source Schedule Version = V3
        ↓
Schedule changed
        ↓
Current Schedule = V4
        ↓
Try Confirm P
        ↓
Version mismatch
        ↓
Reject Confirmation
```

ดังนั้น Proposal ไม่สามารถเขียนทับ Current Schedule ที่ใหม่กว่าได้

---

# 3.35 Error Handling Architecture

Error ถูกจัดเป็นชั้นดังนี้:

```text
Client Error
     ↓
Schema Validation Error
     ↓
Domain Validation Error
     ↓
Authentication / Authorization Error
     ↓
AI Provider Error
     ↓
AI Output Validation Error
     ↓
Planning Error
     ↓
Database Error
     ↓
Infrastructure Error
```

API ใช้ Error Structure กลาง:

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

หลักการคือ:

* Error ต้องมี Code
* Message ต้องสื่อความหมาย
* Details ใช้เมื่อจำเป็น
* `requestId` ใช้สำหรับ Trace

---

# 3.36 AI Failure Boundary

หาก AI Provider:

* Timeout
* Unavailable
* Return Invalid Output
* Return Unsupported Structure

ระบบต้อง **ไม่ส่งผลดังกล่าวเข้า Planning Engine**

Flow:

```text
AI Provider
     ↓
Failure / Invalid Output
     ↓
AI Service Error
     ↓
Application Error Handling
     ↓
Planning not executed
```

ระบบไม่ควร fallback ด้วยการสร้างข้อมูลเองโดยไม่มีหลักฐาน

Alternative Provider สามารถถูกใช้ผ่าน Provider Adapter ตาม Policy ที่กำหนด

---

# 3.37 Planning Failure Boundary

Planning Engine อาจพบ:

* No Feasible Plan
* Solver Timeout
* Solver Unknown / Failure
* Horizon Exceeded
* Object Limit Exceeded

ระบบต้องไม่:

* Relax Hard Constraint แบบเงียบ ๆ
* ตัด Activity แบบเงียบ ๆ
* ส่ง Partial Plan ทั้งที่ Operation ต้องการ Complete Result

หาก Operation ไม่สามารถสร้างผลลัพธ์ที่ถูกต้องได้ ให้คืน Failure State ที่เหมาะสม

---

# 3.38 Transaction Boundary

การประมวลผลที่ใช้เวลานาน เช่น AI และ CP-SAT ไม่ควรถูกทำภายใน Database Transaction เดียวกับการ Confirm Schedule

ตัวอย่างที่เหมาะสม:

```text
Create Planning Request
        ↓
AI / NLP
        ↓
Planning
        ↓
Proposal
```

และเมื่อ User Confirm:

```text
BEGIN TRANSACTION
      ↓
Validate Proposal Version
      ↓
Create New Schedule Version
      ↓
Create Schedule Items
      ↓
Update Proposal
      ↓
COMMIT
```

หลักการนี้ช่วยลดเวลาที่ Database Transaction ถูกเปิดค้างไว้

---

# 3.39 Concurrency Considerations

ระบบต้องรองรับกรณี User หรือ Client หลาย Operation เกิดใกล้เคียงกัน เช่น:

```text
Proposal A created
      ↓
Schedule changed
      ↓
Proposal B created
      ↓
User tries to confirm Proposal A
```

Proposal A ต้องถูกตรวจสอบ Source Schedule Version ก่อน Confirm

ระบบจึงใช้:

> Version-based Consistency / Stale Proposal Protection

เพื่อป้องกันการเขียนทับ Current Schedule

---

# 3.40 Security Architecture

Security ถูกออกแบบแบบ Layered

```text
Mobile
  ↓
HTTPS
  ↓
Authentication
  ↓
Authorization
  ↓
Input Validation
  ↓
Business Rules
  ↓
Persistence Authorization
```

หลักการเพิ่มเติม:

* Password Hashing ด้วย Argon2id
* Access Token อายุจำกัด
* Refresh Session
* Secure Token Storage บน Mobile
* Secret อยู่ Backend
* Database Credentials ไม่อยู่ Mobile
* AI API Key ไม่อยู่ Mobile
* Rate Limiting
* Ownership Check
* ไม่มี Sensitive Data ใน Log โดยไม่จำเป็น

---

# 3.41 Mobile Security Boundary

Mobile Application ใช้ `expo-secure-store` สำหรับข้อมูล Token ที่ต้องเก็บในอุปกรณ์

Mobile ไม่ควรมี:

* Database Credential
* AI API Key
* Server Secret
* JWT Signing Secret

การตัดสินใจสำคัญด้าน Authorization ต้องเกิดฝั่ง Server

---

# 3.42 Performance Architecture

LONGTUA ไม่แก้ Performance ด้วยการจำกัด Calendar Data Range

แต่ใช้:

```text
Long-range Data Storage
        +
Relevant Object Selection
        +
Bounded Planning Horizon
        +
Solver Time Limit
        +
Pagination
        +
AI Context Limiting
```

Concept:

```text
Calendar
┌──────────────────────────────────────────┐
│ Long-range Data                          │
│                                          │
│   ┌──────── Planning Horizon ────────┐   │
│   │ Objects used by CP-SAT            │   │
│   └──────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

ไม่จำเป็นต้องส่งข้อมูลทั้ง Calendar ให้ AI หรือ CP-SAT ทุกครั้ง

---

# 3.43 AI Context Boundary

AI ควรได้รับเฉพาะ Context ที่เกี่ยวข้อง เช่น:

* Relevant Activities
* Relevant Constraints
* User Settings ที่จำเป็น
* Planning Request Context
* Pending Clarification Context

ไม่ควรส่ง:

> Entire Database

หรือ

> Entire Conversation History

โดยไม่มีเหตุผล

การจำกัด Context ช่วยทั้งด้าน Performance, Privacy และลดความเสี่ยงจากข้อมูลที่ไม่เกี่ยวข้อง

---

# 3.44 Evaluation Boundary

Evaluation ไม่ควรฝังอยู่ใน Production Business Logic

แต่ระบบต้อง expose ข้อมูลหรือ Metrics ที่จำเป็นสำหรับการประเมิน เช่น:

* Extraction Accuracy
* Precision / Recall / F1
* Feasibility
* Constraint Violation
* Deadline Satisfaction
* Preference Satisfaction
* Runtime
* Candidate Diversity
* Schedule Change
* Interaction Effort

Architecture:

```text
Production Flow
       ↓
Operational Metrics / Event Data
       ↓
Evaluation Layer
       ↓
Experiment Dataset / Analysis
```

Evaluation ต้องสามารถแยกออกจากการทำงานหลักของ Production System ได้

---

# 3.45 Deployment Architecture

MVP ใช้ Architecture แบบง่ายและสามารถ Deploy ได้จริงโดยไม่เพิ่ม Infrastructure ที่ไม่จำเป็น

```text
                  Internet
                     |
                     v
             +---------------+
             | Mobile Client |
             +-------+-------+
                     |
                  HTTPS
                     |
                     v
             +---------------+
             | FastAPI       |
             | Backend       |
             +---+-------+---+
                 |       |
                 |       +------------------+
                 |                          |
                 v                          v
          +-------------+            +-------------+
          | PostgreSQL  |            | AI Provider |
          +-------------+            +-------------+
                 |
                 v
          Persistent Data
```

Planning Engine อยู่ภายใน Backend:

```text
FastAPI Backend
      |
      +-- AI/NLP
      +-- Validation
      +-- Planning Core (CP-SAT)
      +-- Schedule Management
      +-- Persistence
```

ไม่จำเป็นต้องแยกเป็น Microservices ใน MVP

---

# 3.46 Development Environment

Development ใช้:

* Git
* Docker Compose
* Python
* PostgreSQL
* FastAPI
* React Native / Expo

Docker Compose ใช้จัดการอย่างน้อย:

```text
backend
postgres
```

AI Provider เรียกผ่าน External API

Mobile ใช้ Expo สำหรับ Development และ Demo

---

# 3.47 Testing Environment

ควรแยก Testing Concern ออกจาก Development

Backend:

* pytest
* API Integration Tests
* Domain Tests
* Planning Tests
* AI Adapter Tests

Mobile:

* Jest
* jest-expo
* React Native Testing Library

Planning Core ต้องสามารถทดสอบด้วย Mock / Structured Input โดยไม่ต้องพึ่ง AI Provider

---

# 3.48 Demo / Production Environment

Demo/Production ต้องมีอย่างน้อย:

* HTTPS
* Environment-based Configuration
* Production Database
* AI Provider Configuration
* Health Check
* Application Logs
* Error Monitoring ตามความเหมาะสม
* Database Backup ตามความเหมาะสม

Mobile Demo รองรับ:

* iPhone ผ่าน Expo Go
* Android APK

Architecture Backend เดียวกัน

---

# 3.49 Environment Configuration

Configuration ที่แตกต่างกันระหว่าง Environment ต้องไม่ Hard-code ใน Source Code

ตัวอย่าง:

```text
DATABASE_URL
JWT_SECRET
AI_PROVIDER
AI_API_KEY
ENVIRONMENT
CORS_ORIGINS
SOLVER_TIME_LIMIT
```

ใช้ Environment Variables

และมี:

```text
.env.example
```

ใน Repository โดยไม่มี Secret จริง

---

# 3.50 Health Check

Backend ต้องมี Health Endpoint:

```text
GET /api/health
```

ใช้สำหรับตรวจสอบว่า Application ทำงานอยู่

Health Check ไม่ควรเปิดเผย Secret หรือ Sensitive Information

---

# 3.51 Architecture Rules

ต่อไปนี้เป็น **Architecture Invariants** ของ LONGTUA

### Rule 1 — UI Does Not Understand Planning

Mobile UI ไม่รับผิดชอบ Natural Language Interpretation หรือ CP-SAT Logic

### Rule 2 — AI Does Not Schedule

AI/NLP ไม่สามารถกำหนด Final Schedule

### Rule 3 — Planner Does Not Interpret NLP

Planning Core รับ Structured Planning Representation เท่านั้น

### Rule 4 — AI Does Not Access Database Directly

AI Provider ไม่มีสิทธิ์เข้าถึง PostgreSQL โดยตรง

### Rule 5 — Planner Does Not Access UI Directly

Planning Core คืน Structured Result ผ่าน Application Layer

### Rule 6 — Proposed ≠ Confirmed

Proposal ต้องถูกแยกจาก Current Confirmed Schedule

### Rule 7 — Explicit Confirmation

Confirmed Schedule เปลี่ยนได้จาก Explicit User Confirmation เท่านั้น

### Rule 8 — Notification Source

Notification สร้างจาก Confirmed Schedule เท่านั้น

### Rule 9 — Hard Constraint Integrity

Hard Constraints ไม่ถูก Relaxed โดยอัตโนมัติ

### Rule 10 — Ownership

Server เป็นผู้ตัดสิน Ownership และ Authorization

### Rule 11 — Historical Immutability

Historical Schedule Version แก้ไขไม่ได้

### Rule 12 — Stale Proposal Protection

Proposal ที่อ้างอิง Schedule Version เก่าต้องไม่สามารถ Override Current Schedule

### Rule 13 — No Dummy Candidates

จำนวน Candidate ไม่ใช่เป้าหมายในตัวเอง

### Rule 14 — Long-range Calendar

Calendar Data Range ต้องไม่ถูกจำกัดด้วย Planning Horizon

### Rule 15 — Contextual Replanning

Replanning Horizon ต้องกำหนดจาก Affected Context

---

# 3.52 Technology Stack

## Mobile

| Component        | Technology                                      |
| ---------------- | ----------------------------------------------- |
| Framework        | React Native                                    |
| Platform Tooling | Expo                                            |
| Language         | TypeScript                                      |
| Navigation       | Expo Router                                     |
| Server State     | TanStack Query                                  |
| Client State     | Zustand                                         |
| Notifications    | expo-notifications                              |
| Secure Storage   | expo-secure-store                               |
| Testing          | Jest + jest-expo + React Native Testing Library |

## Backend

| Component  | Technology             |
| ---------- | ---------------------- |
| Language   | Python 3.14            |
| Framework  | FastAPI                |
| Validation | Pydantic v2            |
| ORM        | SQLAlchemy 2.x         |
| Migration  | Alembic                |
| Testing    | pytest                 |
| Planning   | Google OR-Tools CP-SAT |

## Database

| Component | Technology |
| --------- | ---------- |
| Database  | PostgreSQL |

## AI

| Role        | Provider         |
| ----------- | ---------------- |
| Primary     | Google Gemini    |
| Alternative | Claude           |
| Integration | Provider Adapter |

---

# 3.53 Architectural Decision Summary

| Decision             | Choice                  | Reason                                       |
| -------------------- | ----------------------- | -------------------------------------------- |
| Backend Architecture | Modular Monolith        | เหมาะกับ MVP และลด Infrastructure Complexity |
| API Style            | REST + JSON             | เหมาะกับ Mobile ↔ Backend                    |
| API Base Path        | `/api`                  | ลด Versioning Complexity ใน MVP              |
| Planning             | CP-SAT                  | รองรับ Constraint-based Scheduling           |
| AI Integration       | Provider Adapter        | ลด Vendor Lock-in                            |
| Database             | PostgreSQL              | รองรับ Structured + JSONB Data               |
| Mobile               | React Native + Expo     | Cross-platform Development                   |
| Calendar             | Internal Calendar       | ลด External Dependency                       |
| Notification         | Local Notification      | เหมาะกับ MVP                                 |
| Schedule State       | Immutable Version       | รองรับ History และ Stale Protection          |
| Replanning           | Full Rebuild + Re-solve | ลดความซับซ้อนของ MVP                         |
| Async Queue          | ไม่ใช้ใน MVP            | เพิ่มเมื่อ Benchmark แสดงความจำเป็น          |
| Microservices        | ไม่ใช้ใน MVP            | ไม่จำเป็นต่อ Scope ปัจจุบัน                  |

---

# 3.54 Architecture Summary

สถาปัตยกรรมของ LONGTUA สามารถสรุปได้ดังนี้:

```text
                        USER
                         |
                         v
              +---------------------+
              |   Mobile App        |
              | React Native + Expo  |
              +----------+----------+
                         |
                      HTTPS
                         |
                         v
              +---------------------+
              | FastAPI Backend      |
              | Modular Monolith     |
              +----------+----------+
                         |
                 Application Layer
                         |
       +-----------------+------------------+
       |                 |                  |
       v                 v                  v
   AI / NLP        Validation         Planning Core
       |            / Normalize             |
       |                 |                  |
       +-----------------+------------------+
                         |
                         v
                Proposal Management
                         |
                +--------+--------+
                |                 |
             Reject           Confirm
                                  |
                                  v
                         Schedule Management
                                  |
                                  v
                         Schedule Version
                                  |
                                  v
                       Local Notification
                         
                         |
                         v
                    PostgreSQL
```

หัวใจของ Architecture คือการแยก **Understanding, Planning และ Decision** ออกจากกัน:

```text
AI / NLP
= Understand

Planning Core
= Compute

User
= Decide
```

และหลักการนี้ยังคงเป็นแกนเดียวกันกับทุก Lifecycle ของ LONGTUA ตั้งแต่ Initial Planning, Clarification, Proposal, Manual Edit ไปจนถึง Adaptive Replanning

จึงทำให้ Architecture รองรับทั้ง Core Requirements ของโครงการและการประเมินผล RQ1–RQ4 ได้ โดยไม่จำเป็นต้องเพิ่ม Autonomous Decision-Making เข้ามาในระบบ
