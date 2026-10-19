# 18. Contract Freeze & Canonical Project Contracts

## 18.1 Purpose

เอกสารนี้ทำหน้าที่เป็น **Canonical Contract** ของ LONGTUA สำหรับใช้ร่วมกันระหว่าง Mobile, Backend, Database, AI/NLP, Planning Engine และ Figma ก่อนเริ่ม Implementation

เป้าหมายคือทำให้ทั้งสองผู้พัฒนาใช้คำจำกัดความเดียวกันในเรื่อง:

* Data Model
* Enum / Status
* API Request / Response
* Error Code
* State Transition
* Date / Time Format
* Schedule Version
* Proposal
* Planning Request
* Activity / Availability
* AI Output Boundary

หลักสำคัญ:

> **Contract คือข้อตกลงกลางระหว่าง module ไม่ใช่รายละเอียด implementation ภายใน module**

---

# 18.2 Contract Hierarchy

Contract ของ LONGTUA แบ่งเป็น:

```text
Domain Contract
      ↓
Data Contract
      ↓
API Contract
      ↓
State Contract
      ↓
UI Contract
      ↓
Implementation
```

โดย implementation ต้องไม่เปลี่ยน semantics ของ contract เอง

---

# 18.3 Canonical Naming Convention

## Backend / Database

ใช้:

```text
snake_case
```

ตัวอย่าง:

```text
planning_object_id
source_request_id
source_schedule_version_id
created_at
```

## API JSON

ใช้:

```text
camelCase
```

ตัวอย่าง:

```json
{
  "planningObjectId": "...",
  "sourceRequestId": "...",
  "createdAt": "..."
}
```

## TypeScript

ใช้:

```text
camelCase
```

สำหรับ variables/functions

และ:

```text
PascalCase
```

สำหรับ types/components

## Python

ใช้:

```text
snake_case
```

---

# 18.4 Identifier Contract

Entity ที่เป็น persistent resource ใช้ UUID

เช่น:

```text
userId
activityId
planningRequestId
proposalId
scheduleVersionId
availabilityRuleId
```

ห้ามใช้ database auto-increment integer เป็น public resource identifier ใน API

---

# 18.5 Date / Time Contract

ระบบใช้ ISO 8601 สำหรับ API

ตัวอย่าง datetime:

```text
2026-10-12T19:00:00+07:00
```

Date:

```text
2026-10-12
```

Time:

```text
19:00:00
```

หลักการ:

* datetime ต้องมี timezone information เมื่อเป็น timestamp ที่อ้างอิงเวลาจริง
* date-only ใช้เมื่อ user ให้เพียงวันที่
* unknown time ต้องไม่ถูกแทนด้วยค่า default โดยอัตโนมัติ
* notification datetime แยกจาก activity start datetime

---

# 18.6 Internal Planning Time

Planning Engine ใช้ integer minutes ภายใน bounded planning horizon

Concept:

```text
Absolute Datetime
       ↓
Planning Horizon Reference
       ↓
Integer Minutes
       ↓
CP-SAT
```

ระบบ API ไม่ expose internal minute offset เป็น business field

---

# 18.7 Planning Object Contract

Planning Object มีได้:

```text
ACTIVITY
CONTAINER
```

โดย Activity สามารถมี:

```text
TASK
EVENT
APPOINTMENT
MEETING
TRAVEL
OTHER
```

ความสัมพันธ์:

```text
objectType = ACTIVITY
→ activityType is required

objectType = CONTAINER
→ activityType = null
```

---

# 18.8 Activity Contract

Conceptual Activity:

```json
{
  "id": "uuid",
  "objectType": "ACTIVITY",
  "activityType": "TASK",
  "title": "อ่านหนังสือ",
  "description": null,
  "dateStart": "2026-10-12",
  "dateEnd": "2026-10-12",
  "startTime": "19:00:00",
  "endTime": "21:00:00",
  "durationMinutes": 120,
  "status": "ACTIVE"
}
```

Field semantics:

| Field             | Meaning                        |
| ----------------- | ------------------------------ |
| id                | Activity identifier            |
| objectType        | Planning object classification |
| activityType      | Activity subtype               |
| title             | Human-readable title           |
| description       | Optional details               |
| dateStart/dateEnd | Activity date range            |
| startTime/endTime | Explicit time range            |
| durationMinutes   | Execution duration             |
| status            | Activity lifecycle status      |

---

# 18.9 Date-only Activity Contract

ตัวอย่าง:

```json
{
  "objectType": "ACTIVITY",
  "dateStart": "2026-10-12",
  "dateEnd": "2026-10-12",
  "startTime": null,
  "endTime": null,
  "durationMinutes": null
}
```

Valid state:

```text
Date = Known
Time = Unknown
Duration = Unknown
```

ห้ามตีความ:

```text
notification = 06:00
```

เป็น:

```text
activityStartTime = 06:00
```

---

# 18.10 Activity Lifecycle Contract

Activity lifecycle:

```text
ACTIVE
  │
  └── CANCELLED
```

การ delete ใช้ soft-delete mechanism:

```text
deletedAt != null
```

ไม่ใช้:

```text
SCHEDULED
UNSCHEDULED
```

เป็น Activity lifecycle state

Scheduling state สามารถ derive จาก Schedule Items

---

# 18.11 Container Contract

Container คือ planning object ที่เป็น larger temporal/context block และสามารถมี child activities

ตัวอย่าง:

```text
Workshop
14:00–17:00
```

ภายใน:

```text
Activity A
14:00–15:00

Activity B
15:30–16:30
```

Container membership เป็น structural relationship ผ่าน `container_memberships`

---

# 18.12 Container Membership Contract

ความสัมพันธ์:

```text
Container
   ↓
Child Activity
```

contract:

```text
containerId
childObjectId
```

หลักการ:

```text
start(container)
≤
start(child)

และ

end(child)
≤
end(container)
```

เมื่อเป็น containment relationship

---

# 18.13 Availability Contract

Availability Rule รองรับ:

```text
AVAILABLE
UNAVAILABLE
```

และ:

```text
ONE_TIME
RECURRING
```

ตัวอย่าง:

```json
{
  "kind": "AVAILABLE",
  "recurrenceType": "RECURRING",
  "daysOfWeek": [1, 2, 3, 4, 5],
  "startTime": "08:00:00",
  "endTime": "17:00:00"
}
```

---

# 18.14 Availability Semantics

### No Explicit Availability

Planner สามารถพิจารณาเวลาใน planning horizon ได้ โดยยังต้องเคารพ constraints อื่น

### Explicit Availability

Activity ต้องถูกวางใน Available period ที่เกี่ยวข้อง

### Overlapping Unavailability

เมื่อ:

```text
AVAILABLE
+
UNAVAILABLE
```

ให้:

```text
UNAVAILABLE wins
```

---

# 18.15 Planning Rule Contract

Planning Rule แบ่งเป็น:

```text
HARD
PREFERENCE
```

พร้อม:

```text
ruleType
parameters
```

เชิง semantic:

```text
HARD
→ Must satisfy

PREFERENCE
→ Optimize / Prefer
```

---

# 18.16 Temporal Relation Contract

รองรับ:

```text
BEFORE
AFTER
OVERLAP
```

ตัวอย่าง:

```json
{
  "sourceObjectId": "...",
  "targetObjectId": "...",
  "relationType": "BEFORE"
}
```

Temporal relation ไม่ได้แปลว่า planner ต้องยอมให้ activity overlap

ตัวอย่าง:

```text
OVERLAP relation
≠
execution overlap allowed
```

---

# 18.17 Planning Request Contract

Planning Request คือคำขอจาก user เพื่อให้ระบบ:

* เข้าใจ input
* clarify
* วางแผน
* re-plan
* สร้าง proposal

Conceptual structure:

```json
{
  "id": "uuid",
  "inputText": "พรุ่งนี้ตอนเย็นไปวิ่ง 1 ชั่วโมง",
  "status": "RECEIVED",
  "planningStart": "2026-10-12T00:00:00+07:00",
  "planningEnd": "2026-10-19T23:59:59+07:00",
  "parentRequestId": null
}
```

---

# 18.18 Planning Request Status

Canonical enum:

```text
RECEIVED
PROCESSING
NEEDS_CLARIFICATION
PLANNING
PROPOSED
FAILED
```

Transition:

```text
RECEIVED
   ↓
PROCESSING
   ├── NEEDS_CLARIFICATION
   │        ↓
   │     PROCESSING
   │
   ├── PLANNING
   │      ↓
   │   PROPOSED
   │
   └── FAILED
```

`COMPLETED` ไม่ใช้เป็น MVP state

---

# 18.19 Clarification Contract

เมื่อ status:

```text
NEEDS_CLARIFICATION
```

ระบบต้องมี clarification information ที่เพียงพอให้ Mobile แสดงคำถาม

Conceptual response:

```json
{
  "requestId": "...",
  "question": "คุณหมายถึง 6 โมงเช้าหรือ 6 โมงเย็น?",
  "options": [
    {
      "label": "06:00",
      "value": "06:00"
    },
    {
      "label": "18:00",
      "value": "18:00"
    }
  ]
}
```

Clarification ไม่ควรสร้างข้อมูลเองก่อน user response

---

# 18.20 Clarification Response Contract

Endpoint:

```text
POST /api/planning/requests/{id}/clarification-response
```

Conceptual request:

```json
{
  "answer": {
    "type": "OPTION",
    "value": "18:00"
  }
}
```

จากนั้น request กลับเข้าสู่ processing flow

---

# 18.21 Proposal Contract

Proposal ประกอบด้วย:

```text
Proposal
 └── Proposal Items
       ├── Candidate A
       ├── Candidate B
       └── Candidate C
```

จำนวน:

```text
1–3 candidates
```

---

# 18.22 Proposal Status

Canonical enum:

```text
PENDING
CONFIRMED
REJECTED
INVALIDATED
```

Transition:

```text
PENDING
 ├── CONFIRMED
 ├── REJECTED
 └── INVALIDATED
```

ไม่มี:

```text
EXPIRED
```

---

# 18.23 Candidate Contract

Candidate เป็น alternative schedule ภายใน Proposal

Field หลัก:

```json
{
  "planKey": "A",
  "items": [
    {
      "objectId": "...",
      "startTime": "2026-10-12T19:00:00+07:00",
      "endTime": "2026-10-12T21:00:00+07:00"
    }
  ]
}
```

`planKey`:

```text
A
B
C
```

ใช้ตามจำนวนจริงที่สร้างได้

---

# 18.24 Candidate Rules

Candidate ต้อง:

1. feasible
2. ผ่าน Hard Constraints
3. มี acceptable quality
4. มี meaningful difference หากมีหลาย candidate

ห้ามสร้าง dummy candidate

---

# 18.25 Proposal Source Version Contract

Proposal ต้องเก็บ:

```text
sourceScheduleVersionId
```

กรณีมี Current Schedule:

```text
sourceScheduleVersionId = currentScheduleVersionId
```

กรณี initial planning ที่ยังไม่มี confirmed schedule:

```text
sourceScheduleVersionId = null
```

---

# 18.26 Stale Proposal Contract

ก่อน Confirm:

```text
proposal.sourceScheduleVersionId
==
currentScheduleVersionId
```

จึง confirm ได้

ถ้าไม่ตรง:

```text
409 CONFLICT
```

และ error code:

```text
STALE_PROPOSAL
```

Current Schedule ต้องไม่เปลี่ยน

---

# 18.27 Schedule Version Contract

Schedule Version เป็น immutable snapshot

Conceptual:

```json
{
  "id": "uuid",
  "versionNumber": 6,
  "isCurrent": true
}
```

Invariant:

```text
Per User:
Current Version ≤ 1
```

เมื่อมี Confirmed Schedule:

```text
Version N
```

และเมื่อ confirm change:

```text
Version N+1
```

---

# 18.28 Schedule Item Contract

Schedule Item เป็น placement ของ Planning Object

เช่น:

```json
{
  "objectId": "...",
  "startTime": "2026-10-12T19:00:00+07:00",
  "endTime": "2026-10-12T21:00:00+07:00"
}
```

Schedule Item ไม่ใช่ Activity

ความสัมพันธ์:

```text
Activity
   ↕
Schedule Item
```

Activity = what

Schedule Item = when

---

# 18.29 Schedule Source-of-Truth Contract

Calendar ใช้:

```text
Current Confirmed Schedule
```

ไม่ใช้:

```text
Latest Proposal
```

ไม่ใช้:

```text
Local Draft
```

ดังนั้น:

```text
Calendar
   ↓
Current Schedule Version
```

---

# 18.30 Manual Edit Contract

Manual edit เริ่มจาก:

```text
Current Schedule Version
```

mobile เก็บ:

```text
Local Draft
```

จากนั้น:

```text
Draft
 ↓
Validate
 ↓
Confirm
```

Draft ไม่ถูก persist เป็น Schedule Version ใน MVP

---

# 18.31 Manual Validation Contract

Endpoint:

```text
POST /api/schedule/validate
```

มีหน้าที่:

```text
Validate only
```

ไม่มี side effect:

```text
No Schedule Version creation
No Current Version update
No Notification scheduling
```

---

# 18.32 Manual Confirm Contract

Endpoint:

```text
POST /api/schedule/manual-confirm
```

ต้องส่ง:

```text
expectedCurrentScheduleVersionId
```

เพื่อป้องกัน stale Draft

หาก current version เปลี่ยน:

```text
409 CONFLICT
STALE_SCHEDULE_DRAFT
```

---

# 18.33 Manual Confirmation State Flow

```text
Current Version N
      ↓
Mobile Draft
      ↓
Validate
      ↓
Valid
      ↓
Manual Confirm
      ↓
Create Version N+1
      ↓
Version N+1 = Current
```

กรณี invalid:

```text
Draft
 ↓
Conflict
 ↓
Confirm Disabled
```

---

# 18.34 Planning-affecting Change Contract

การเปลี่ยนต่อไปนี้ถือว่ากระทบ planning:

```text
Date
Start Time
End Time
Duration
Deadline
Fixed Time
Planning-related Constraint
```

Flow:

```text
Change Request
      ↓
Planning / Re-planning
      ↓
Proposal
      ↓
User Confirm
      ↓
Commit Change
```

---

# 18.35 Non-planning Change Contract

การเปลี่ยนทั่วไปที่ไม่กระทบ scheduling เช่น:

```text
Title
Description
Non-planning Metadata
```

สามารถ update ได้โดยตรง

โดยไม่จำเป็นต้องสร้าง Proposal

---

# 18.36 Activity Change Transaction Contract

สำหรับ planning-affecting activity change:

```text
BEGIN
   ↓
Validate Proposal
   ↓
Create New Schedule Version
   ↓
Apply Activity Change
   ↓
Commit
```

หากไม่สำเร็จ:

```text
Rollback
```

เพื่อไม่ให้:

```text
Activity
≠
Confirmed Schedule
```

---

# 18.37 Availability Change Contract

หาก Availability / Unavailability change ไม่กระทบ current schedule:

```text
Save directly
```

หากกระทบ current schedule:

```text
Change
 ↓
Re-planning
 ↓
Proposal
 ↓
Confirm
 ↓
Apply rule + schedule change
```

---

# 18.38 Feedback Contract

Endpoint:

```text
POST /api/planning/feedback
```

Feedback เป็น user input ที่อาจใช้:

```text
modify preference
modify constraint
modify placement requirement
request different plan
```

Flow:

```text
Feedback
 ↓
AI Interpretation
 ↓
Validation
 ↓
Planning Modification
 ↓
Re-planning
 ↓
New Proposal
```

Feedback ไม่แก้ Confirmed Schedule โดยตรง

---

# 18.39 Re-planning Contract

Trigger:

```text
New Activity
Date Change
Time Change
Duration Change
Deadline Change
Availability Change
Unavailability Change
Cancellation
User Feedback
```

Flow:

```text
Current Schedule
      +
New Information
      ↓
Affected Context
      ↓
Bounded Horizon
      ↓
Rebuild Model
      ↓
Re-solve
      ↓
Proposal
```

---

# 18.40 Re-planning Stability Contract

เมื่อมี Current Schedule ให้พิจารณา:

```text
D = Σ |newStart(i) - oldStart(i)|
```

แต่ priority:

```text
Hard Constraint
>
Explicit Requirement
>
Preference
>
Stability
>
Optional Activity
```

---

# 18.41 AI Output Contract

AI/NLP output ต้องเป็น structured representation

Conceptual:

```json
{
  "planningObjects": [],
  "constraints": [],
  "preferences": [],
  "relations": [],
  "clarification": null
}
```

AI output:

```text
untrusted input
```

จึงต้องผ่าน:

```text
Schema Validation
→
Domain Validation
→
Normalization
```

---

# 18.42 AI Unknown Contract

ถ้า AI ไม่ทราบค่า:

```text
null / UNKNOWN
```

ตาม schema ที่กำหนด

ห้าม AI:

```text
guess silently
```

ตัวอย่าง:

```text
"พรุ่งนี้ไปซื้อของขวัญ"
```

ต้องไม่สร้าง:

```text
duration = 60
startTime = 10:00
```

โดยไม่มีหลักฐาน

---

# 18.43 AI Ambiguous Contract

หากข้อมูลมีหลาย interpretation ที่มีผลต่อ planning:

```text
AMBIGUOUS
```

และระบบควรสร้าง clarification request

ตัวอย่าง:

```text
"6 โมง"
```

เมื่อไม่สามารถ resolve:

```text
06:00
vs
18:00
```

---

# 18.44 Semantic Time Contract

Canonical semantic values:

```text
LATE_NIGHT
MORNING
LATE_MORNING
NOON
AFTERNOON
EVENING
NIGHT
```

User-defined windows สามารถ override default

AI:

```text
"ช่วงบ่าย"
→
AFTERNOON
```

Normalization:

```text
AFTERNOON
→
User-defined / Default Time Range
```

---

# 18.45 Constraint Contract

Hard Constraint examples:

```text
FIXED_TIME
EARLIEST_START
LATEST_START
DEADLINE
TIME_WINDOW
AVAILABILITY
UNAVAILABILITY
PRECEDENCE
CONTAINMENT
NO_OVERLAP
```

Preference examples:

```text
PREFERRED_TIME
PREFERRED_ORDER
STABILITY
OPTIONAL_PRIORITY
```

รายละเอียด rule parameters อยู่ใน `planning_rules.parameters`

---

# 18.46 Error Contract

ทุก API error ใช้โครงสร้าง:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {},
    "requestId": "uuid"
  }
}
```

Client ต้องใช้ `code` สำหรับ behavior และใช้ `message` สำหรับ display

ห้ามใช้ message เป็น machine-readable contract

---

# 18.47 Canonical Error Codes

## Authentication

```text
INVALID_CREDENTIALS
UNAUTHORIZED
SESSION_EXPIRED
INVALID_TOKEN
TOKEN_REVOKED
```

## Authorization

```text
FORBIDDEN
RESOURCE_NOT_FOUND
```

## Validation

```text
VALIDATION_ERROR
INVALID_DATE_RANGE
INVALID_TIME_RANGE
INVALID_DURATION
INVALID_PLANNING_OBJECT
```

## Planning

```text
CLARIFICATION_REQUIRED
NO_FEASIBLE_PLAN
PLANNING_FAILED
UNSUPPORTED_INPUT
AI_OUTPUT_INVALID
```

## Proposal / Schedule

```text
STALE_PROPOSAL
INVALID_PROPOSAL
SCHEDULE_CONFLICT
STALE_SCHEDULE_DRAFT
INVALID_SCHEDULE
```

## System

```text
RATE_LIMITED
SERVICE_UNAVAILABLE
INTERNAL_ERROR
```

รายการสามารถขยายได้เมื่อ implementation พบ business case ที่จำเป็น แต่ไม่ควรสร้าง error code ซ้ำความหมายเดิม

---

# 18.48 HTTP Status Mapping

Canonical mapping:

| HTTP | Meaning                               |
| ---- | ------------------------------------- |
| 200  | Success                               |
| 201  | Resource created                      |
| 204  | Success without response body         |
| 400  | Invalid request / malformed operation |
| 401  | Authentication required/failed        |
| 403  | Authenticated but not authorized      |
| 404  | Resource not found / ownership policy |
| 409  | State conflict / stale state          |
| 422  | Semantic validation failure           |
| 429  | Rate limited                          |
| 500  | Internal server error                 |
| 503  | Service unavailable                   |

---

# 18.49 Idempotency Contract

Operation ที่มี critical side effects ต้องรองรับ `Idempotency-Key`

ขั้นต่ำ:

```text
POST /api/planning/requests
POST /api/proposals/{id}/confirm
POST /api/schedule/manual-confirm
```

หลัก:

```text
Same Idempotency-Key
+
Same User
+
Same Endpoint
→
Must not create duplicate side effect
```

---

# 18.50 Ownership Contract

Client ห้ามกำหนด ownership เอง

ห้ามรับ:

```json
{
  "userId": "another-user"
}
```

เพื่อใช้เปลี่ยนเจ้าของ resource

Backend derive user:

```text
Authenticated Session
↓
Current User
↓
Resource Ownership
```

---

# 18.51 Security-sensitive Fields

Client ไม่สามารถควบคุม field ระดับ system เช่น:

```text
userId
isCurrent
versionNumber
proposalStatus
scheduleVersionId
createdAt
updatedAt
```

เว้นแต่ endpoint นั้นระบุเป็น read-only response data

---

# 18.52 Notification Contract

Notification เป็น derived state ของ:

```text
Confirmed Schedule
```

Policy:

```text
Activity Override
>
Global User Setting
>
System Default
```

Defaults:

```text
Date-only → 06:00
Timed → 1 hour before start
```

---

# 18.53 Notification Sync Contract

เมื่อ Current Schedule เปลี่ยน:

```text
Old Effective Notifications
      ↓
Cancel
      ↓
New Effective Notifications
      ↓
Schedule
```

backend ไม่ถือ local notification ID เป็น business identity

Mobile เป็น owner ของ local notification instance

---

# 18.54 Notification Safety Contract

ห้าม:

```text
Proposal
→
Notification
```

ห้าม:

```text
Draft
→
Notification
```

ต้องเป็น:

```text
Confirmed Schedule
→
Notification
```

---

# 18.55 Figma Contract

Figma ต้องสะท้อน canonical states:

```text
Planning Request
Proposal
Draft
Confirmed Schedule
Conflict
Clarification
Error
```

Figma ไม่ควรสร้าง state ใหม่ที่ไม่มี backend/domain semantics

ตัวอย่างเช่นไม่ควรมี:

```text
AUTO_CONFIRMED
```

เพราะ MVP ไม่มี behavior นี้

---

# 18.56 UI Action Contract

Critical actions:

```text
Confirm
Reject
Cancel
Delete
Retry
Feedback
```

ต้องมี behavior ที่ตรงกับ backend state

เช่น:

```text
STALE_PROPOSAL
→
Confirm Disabled
```

และ:

```text
Draft Conflict
→
Confirm Disabled
```

---

# 18.57 Contract Compatibility Rule

การแก้ contract แบ่งเป็น:

### Non-breaking

เช่น:

* เพิ่ม optional response field
* เพิ่ม internal implementation
* เพิ่ม logging
* optimize database query

ไม่จำเป็นต้องสร้าง API version ใหม่

### Breaking

เช่น:

* rename required field
* change field type
* change endpoint semantics
* remove required response field
* incompatible state transition

ต้องพิจารณา API versioning หรือ coordinated migration

---

# 18.58 API Version Rule

MVP:

```text
/api/...
```

ยังไม่มี:

```text
/api/v1/...
```

ใช้ `/api/v2` เมื่อเกิด breaking contract change จริง

การเปลี่ยน:

```text
CP-SAT implementation
AI model
Prompt
Database indexing
Internal architecture
```

ไม่ถือเป็น API breaking change โดยตัวมันเอง

---

# 18.59 Contract Testing

ทั้ง Mobile และ Backend ต้องทดสอบ contract

อย่างน้อย:

```text
Request matches schema
Response matches schema
Error matches schema
Enum values match
Nullable fields match
Date/time formats match
```

สำหรับ critical endpoint ต้องมี integration test

---

# 18.60 Canonical Endpoint Contract

## Authentication

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
POST /api/auth/logout
GET  /api/auth/me
POST /api/auth/verify-email
POST /api/auth/forgot-password
POST /api/auth/reset-password
```

## Activities

```text
GET    /api/activities
POST   /api/activities
GET    /api/activities/{id}
PATCH  /api/activities/{id}
POST   /api/activities/{id}/cancel
DELETE /api/activities/{id}
```

## Planning

```text
POST /api/planning/requests
POST /api/planning/requests/{id}/clarification-response
POST /api/planning/feedback
```

## Proposal

```text
GET  /api/proposals/{id}
POST /api/proposals/{id}/confirm
POST /api/proposals/{id}/reject
```

## Schedule

```text
GET  /api/schedule
POST /api/schedule/validate
POST /api/schedule/manual-confirm
```

## Availability

```text
GET    /api/availability
POST   /api/availability
PATCH  /api/availability/{id}
DELETE /api/availability/{id}
```

## Settings

```text
GET   /api/settings/time-windows
PATCH /api/settings/time-windows

GET   /api/settings/notifications
PATCH /api/settings/notifications
```

---

# 18.61 Endpoint Responsibility Rule

Public API ต้อง expose business operation

ไม่ expose internal implementation

ดังนั้นไม่มี:

```text
/api/ai/extract
/api/cp-sat/solve
```

ใน MVP

แต่มี:

```text
/api/planning/requests
```

ซึ่ง backend orchestrates:

```text
AI
→
Validation
→
Planning
→
Proposal
```

---

# 18.62 Contract Freeze Checklist

ก่อนเริ่ม implementation ต้องยืนยัน:

```text
[ ] Domain terminology frozen
[ ] Entity identifiers frozen
[ ] Enum values frozen
[ ] API paths frozen
[ ] Request fields frozen
[ ] Response fields frozen
[ ] Error schema frozen
[ ] Error codes frozen
[ ] Date/time format frozen
[ ] Proposal state frozen
[ ] Planning Request state frozen
[ ] Schedule Version semantics frozen
[ ] Notification semantics frozen
[ ] Ownership rules frozen
[ ] Stale protection frozen
[ ] Manual edit flow frozen
```

---

# 18.63 Change Control After Freeze

หลังจาก Contract Freeze:

การเปลี่ยน contract ต้องมี:

```text
Change Proposal
      ↓
Impact Analysis
      ↓
Affected Documents
      ↓
API / DB / UI Impact
      ↓
Test Impact
      ↓
Approve
      ↓
Update Contract
```

ห้ามแก้ API หรือ state กลาง ๆ ระหว่าง coding โดยไม่ตรวจผลกระทบ

---

# 18.64 Frozen vs Implementation-defined

สิ่งที่ **Freeze แล้ว**:

```text
Domain semantics
API endpoints
Core state
Core enums
Field meaning
Source of truth
Transaction behavior
Stale protection
Notification policy
Architecture boundary
```

สิ่งที่ **ยัง Implementation-defined**:

```text
Exact class names
Exact file names
Internal helper functions
Internal database query strategy
UI pixel values
Exact prompt wording
Exact AI model ID
Benchmark limits
```

เพื่อไม่ให้ contract แข็งจนขัดขวาง implementation detail ที่ไม่ควรเป็น public concern

---

# 18.65 Definition of Contract Freeze Complete

Contract Freeze ถือว่าเสร็จเมื่อ:

1. Mobile สามารถ implement API client โดยไม่ต้องเดา field
2. Backend สามารถ implement endpoint โดยไม่ต้องเดา behavior
3. Database สามารถ implement schema โดยไม่ต้องเดา domain semantics
4. Figma สามารถสร้าง states ตาม canonical state model
5. Test case สามารถอ้างอิง enum และ state ได้โดยตรง
6. Critical consistency rules ไม่มี ambiguity ที่ยังไม่ได้ตัดสินใจ

---

# 18.66 Final Canonical Flow

```text
User
 ↓
Mobile
 ↓
Business API
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
 ├── Confirm
 ├── Reject
 └── Feedback
       ↓
    Re-planning
       ↓
  New Proposal
       ↓
    Confirm
       ↓
Confirmed Schedule Version
       ↓
Mobile Calendar
       ↓
Local Notifications
```

---

# 18.67 Final Contract Principle

LONGTUA ใช้หลัก:

> **One system, one semantic contract.**

ทุกส่วนต้องตีความ entity เดียวกันแบบเดียวกัน:

```text
Activity
Proposal
Candidate
Draft
Schedule Version
Planning Request
Availability
Notification
```

และต้องรักษา invariant:

```text
Proposal ≠ Confirmed Schedule

Draft ≠ Confirmed Schedule

Notification ≠ Schedule

AI Output ≠ Trusted Planning Data
```

เมื่อ Contract Freeze เสร็จ:

```text
Design
   ↓
Contract
   ↓
Figma
   ↓
Task Breakdown
   ↓
Implementation
```

จึงสามารถเข้าสู่การพัฒนาจริงได้โดยลดการตีความซ้ำระหว่างทีม
