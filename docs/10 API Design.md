# 10. API Design

## 10.1 Purpose

เอกสารฉบับนี้กำหนด REST API ของ LONGTUA — Personal Adaptive Planner เพื่อเป็น Contract ระหว่าง Mobile Application และ Backend

API เป็นช่องทางหลักสำหรับ:

* Authentication
* User Account
* Activity Management
* Planning Requests
* Clarification
* Feedback
* Proposal Review
* Schedule Retrieval
* Manual Schedule Validation / Confirmation
* Availability / Unavailability
* User Settings

API ต้องสอดคล้องกับ:

* Requirements
* Domain Model
* System Architecture
* AI/NLP Boundary
* Planning Engine Boundary
* Replanning Flow
* Database Design
* Schedule/Notification Design

---

# 10.2 API Design Principles

API ของ LONGTUA ใช้หลักการ:

### API-PR-01 — Resource-oriented

Endpoint ต้องสะท้อน Domain Resource และ Business Operation ที่ชัดเจน

### API-PR-02 — Application Boundary

API เรียก Application Layer ไม่เรียก Internal Component แบบตรง ๆ จาก Client

### API-PR-03 — No AI Endpoint Exposure

ไม่มี Public Endpoint เช่น:

```text
/api/ai/extract
```

สำหรับ Mobile

AI เป็น Internal Service ของ Backend

### API-PR-04 — No Planner Endpoint Exposure

ไม่มี Public Endpoint เช่น:

```text
/api/cp-sat/solve
```

Planner เป็น Internal Service

### API-PR-05 — Server-side Authorization

Authenticated User Identity มาจาก Auth Context ไม่ใช่จาก `userId` ที่ Client ส่งมาเพื่อกำหนด Ownership

### API-PR-06 — Proposal Before Confirmation

Planning API สร้าง Proposal ไม่เขียน Confirmed Schedule โดยตรง

### API-PR-07 — Explicit Confirmation

การเปลี่ยน Current Confirmed Schedule ต้องเกิดจาก Explicit Confirmation Operation

### API-PR-08 — Version-aware

Operations ที่เกี่ยวข้องกับ Schedule ต้องตรวจสอบ Schedule Version เพื่อป้องกัน Stale Update

### API-PR-09 — Idempotent Side Effects

Operation ที่สร้าง Side Effect สำคัญต้องรองรับ Idempotency

### API-PR-10 — Stable Error Contract

ทุก Error ที่ส่งกลับต้องใช้ Error Structure กลางของระบบ

---

# 10.3 API Base URL Structure

Base Path:

```text id="j0g4tu"
/api
```

ไม่มี:

```text id="zn7j7h"
/api/v1
```

ใน MVP

ตัวอย่าง:

```text id="w7chc1"
POST /api/planning/requests
```

---

# 10.4 Protocol

ใช้:

> HTTPS + JSON over HTTP

ใน Demo / Production

Request Body:

```text id="0da1jt"
application/json
```

Response Body:

```text id="tnf6aa"
application/json
```

---

# 10.5 Authentication Model

LONGTUA ใช้:

```text id="4m1j86"
Email + Password
```

Authentication ใช้:

```text id="99rsvs"
Short-lived Access Token
+
Refresh Session
```

Mobile ต้องเก็บ Token ที่เหมาะสมใน Secure Storage

เช่น `expo-secure-store`

---

# 10.6 Access Token

Access Token:

```text id="h6udbq"
Lifetime = 15 minutes
```

ใช้สำหรับ Protected API

Header:

```http id="9t4prx"
Authorization: Bearer <access_token>
```

Access Token หมดอายุ:

```text id="u2ycg8"
401 Unauthorized
```

Mobile สามารถใช้ Refresh Endpoint เพื่อต่อ Session ตาม Policy

---

# 10.7 Refresh Session

Refresh Session:

```text id="klxrf5"
Remember Me OFF
→ 7 days

Remember Me ON
→ 30 days
```

และมี Absolute Session Lifetime ตาม Security Policy

Refresh Session ถูกผูกกับ:

* User
* Session
* Device Context

---

# 10.8 Common Request Headers

Protected Requests:

```http id="ac54xn"
Authorization: Bearer <token>
Content-Type: application/json
```

สำหรับ Side-effecting Requests:

```http id="s7jqf8"
Idempotency-Key: <unique-key>
```

ตาม Operation ที่รองรับ

---

# 10.9 Common Response Headers

Backend สามารถส่ง:

```text id="0pxxvp"
X-Request-ID
```

หรือใช้ `requestId` ใน Error Body เป็น Canonical Trace Identifier

Implementation สามารถเลือกให้ Header และ Body มีค่าเดียวกัน

---

# 10.10 HTTP Status Codes

LONGTUA ใช้:

| Status | Meaning                             |
| ------ | ----------------------------------- |
| 200    | Successful Request                  |
| 201    | Resource Created                    |
| 204    | Successful Request without Body     |
| 400    | Bad Request                         |
| 401    | Authentication Required / Invalid   |
| 403    | Forbidden                           |
| 404    | Resource Not Found                  |
| 409    | Conflict / Version / State Conflict |
| 422    | Schema / Semantic Validation Error  |
| 429    | Rate Limit                          |
| 500    | Internal Server Error               |
| 503    | Service / Dependency Unavailable    |

ความหมายของ `404` และ `403` สำหรับ Ownership-sensitive Resources สามารถกำหนดโดย Security Policy เพื่อหลีกเลี่ยง Resource Enumeration

---

# 10.11 Common Error Format

ทุก Error ใช้:

```json id="f1v4yl"
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {},
    "requestId": "request-id"
  }
}
```

---

# 10.12 Error Code Convention

Error Code ใช้ตัวพิมพ์ใหญ่และ `_`

ตัวอย่าง:

```text id="b5jzqd"
INVALID_REQUEST
VALIDATION_ERROR
UNAUTHORIZED
FORBIDDEN
RESOURCE_NOT_FOUND
CONFLICT
STALE_PROPOSAL
NO_FEASIBLE_PLAN
PLANNING_NOT_READY
PLANNING_HORIZON_EXCEEDED
PLANNING_OBJECT_LIMIT_EXCEEDED
SOLVER_UNKNOWN
MODEL_INVALID
AI_PROVIDER_UNAVAILABLE
AI_OUTPUT_INVALID
CLARIFICATION_REQUIRED
INVALID_SCHEDULE
SCHEDULE_CONFLICT
INVALID_NOTIFICATION_SETTING
RATE_LIMITED
INTERNAL_ERROR
SERVICE_UNAVAILABLE
```

---

# 10.13 Error Details

`details` ใช้สำหรับ Data ที่ช่วยให้ Client แก้ปัญหาได้

ตัวอย่าง Validation:

```json id="x4zxc7"
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request contains invalid fields.",
    "details": {
      "fields": {
        "duration_minutes": [
          "must be greater than 0"
        ]
      }
    },
    "requestId": "abc123"
  }
}
```

ไม่ควรใส่:

* Password
* Token
* AI Secret
* Database Credential
* Sensitive Internal Stack Trace

ลงใน Error Response

---

# 10.14 Authentication Endpoints

## POST /api/auth/register

สร้างบัญชีใหม่

### Request

```json id="fuk68f"
{
  "email": "user@example.com",
  "password": "password",
  "displayName": "User"
}
```

### Response

```text id="prp6gu"
201 Created
```

Conceptual Response:

```json id="bo5wa2"
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "displayName": "User",
    "emailVerified": false
  }
}
```

ระบบไม่ควรคืน Password Hash

---

# 10.15 POST /api/auth/login

เข้าสู่ระบบ

### Request

```json id="7e0m37"
{
  "email": "user@example.com",
  "password": "password",
  "rememberMe": true
}
```

### Response

```text id="842nul"
200 OK
```

Conceptual:

```json id="qac926"
{
  "accessToken": "jwt",
  "expiresIn": 900,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "displayName": "User"
  }
}
```

Refresh Session ต้องถูกจัดการอย่างปลอดภัยตาม Client/Server Authentication Design

---

# 10.16 POST /api/auth/refresh

ต่ออายุ Access Token

### Request

ขึ้นอยู่กับ Refresh Token/session delivery mechanism ของ Implementation

### Response

```text id="iw0u9o"
200 OK
```

คืน Access Token ใหม่

หาก Session:

* Expired
* Revoked
* Invalid

ให้:

```text id="3v88zt"
401 Unauthorized
```

---

# 10.17 POST /api/auth/logout

Logout

### Request

```text id="q5j8aj"
Idempotency-Key
```

เมื่อจำเป็น

### Behavior

* Revoke Refresh Session
* Clear / invalidate associated Device Session ตาม Policy
* Access Token ฝั่ง Client ถูกลบ

### Response

```text id="r5djzy"
204 No Content
```

---

# 10.18 GET /api/auth/me

คืนข้อมูล User ที่ Authenticated อยู่

### Response

```json id="9h5kz5"
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "displayName": "User",
    "timezone": "Asia/Bangkok"
  }
}
```

User ID มาจาก Auth Context

---

# 10.19 POST /api/auth/verify-email

ใช้ Email Verification Token

ตัวอย่าง:

```json id="fuif2a"
{
  "token": "one-time-token"
}
```

หากสำเร็จ:

```text id="nrncnv"
200 OK
```

Token ต้องใช้ได้เพียงครั้งเดียวและมี Expiration

---

# 10.20 POST /api/auth/forgot-password

Request Password Reset

```json id="m7hbdg"
{
  "email": "user@example.com"
}
```

ระบบควรระวัง User Enumeration และสามารถตอบด้วยข้อความเชิง Generic

---

# 10.21 POST /api/auth/reset-password

ตั้ง Password ใหม่

```json id="6b3n2t"
{
  "token": "one-time-token",
  "newPassword": "new-password"
}
```

เมื่อสำเร็จ:

* Password ถูกเปลี่ยน
* Existing Refresh Sessions ถูก Revoke ตาม Policy

---

# 10.22 Activity Endpoints

```text id="kg5gka"
GET    /api/activities
POST   /api/activities
GET    /api/activities/{id}
PATCH  /api/activities/{id}
POST   /api/activities/{id}/cancel
DELETE /api/activities/{id}
```

---

# 10.23 GET /api/activities

คืนรายการ Activity ของ Authenticated User

รองรับ Query Parameters เช่น:

```text id="0cvjtx"
from
to
status
type
page
pageSize
```

ตัวอย่าง:

```http id="jp6evn"
GET /api/activities?from=2026-10-01&to=2026-10-31&page=1&pageSize=50
```

---

# 10.24 Activity List Response

```json id="f2az3c"
{
  "items": [
    {
      "id": "uuid",
      "objectType": "ACTIVITY",
      "activityType": "TASK",
      "title": "ทำรายงาน",
      "status": "ACTIVE",
      "dateStart": "2026-10-05",
      "startAt": null,
      "endAt": null,
      "durationMinutes": 120
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 50,
    "totalItems": 1,
    "totalPages": 1
  }
}
```

---

# 10.25 POST /api/activities

สร้าง Activity แบบ Manual

### Request

Conceptual:

```json id="v6cg72"
{
  "activityType": "TASK",
  "title": "ทำรายงาน",
  "description": "รายงานวิชา ...",
  "dateStart": "2026-10-05",
  "dateEnd": null,
  "startAt": null,
  "endAt": null,
  "durationMinutes": 120,
  "deadlineAt": "2026-10-05T23:59:00+07:00",
  "notificationOverride": null
}
```

`userId` ไม่อยู่ใน Request Body

### Response

```text id="g7m6fd"
201 Created
```

---

# 10.26 POST /api/activities — Behavior

การสร้าง Activity แบบ Manual:

```text id="efg1ps"
Validate
 ↓
Create Planning Object
 ↓
Persist
```

การสร้าง Activity ไม่ควรสร้าง Confirmed Schedule Placement โดยอัตโนมัติ เว้นแต่ API Operation ถูกออกแบบให้สร้างทั้งสอง State อย่างชัดเจน

ดังนั้น Default Behavior คือ:

> Create Activity ≠ Automatically Schedule Activity

หากต้องการวางลง Schedule ให้ใช้ Planning Flow / Manual Confirmation ตาม Policy

---

# 10.27 GET /api/activities/{id}

คืนรายละเอียด Activity ที่ User เป็นเจ้าของ

หากไม่พบหรือ User ไม่มีสิทธิ์ตาม Resource Visibility Policy:

```text id="j8bm71"
404 Not Found
```

หรือ Policy ที่เหมาะสม

---

# 10.28 PATCH /api/activities/{id}

แก้ไข Activity

รองรับ Partial Update

ตัวอย่าง:

```json id="p0u6vw"
{
  "durationMinutes": 120,
  "deadlineAt": "2026-10-05T20:00:00+07:00"
}
```

หลัง Update Backend ต้องทำ:

```text id="pq2yv9"
Validate
 ↓
Persist Activity Change
 ↓
Determine Planning Impact
 ↓
If Current Schedule affected
    → Replanning flow
```

แต่ต้องไม่:

```text id="rrw1bt"
silently modify Current Schedule
```

---

# 10.29 Activity Update Impact

Response สามารถระบุได้ว่า:

```json id="0mp8fd"
{
  "activity": {},
  "planningImpact": {
    "affected": true,
    "replanningRequired": true
  }
}
```

รายละเอียดจริงขึ้นกับ Application Contract

จุดสำคัญคือการแจ้ง Impact ไม่ได้หมายความว่า Schedule ถูกเปลี่ยนแล้ว

---

# 10.30 POST /api/activities/{id}/cancel

Cancel Activity เป็น Explicit Business Operation

### Response

```text id="9f7r87"
200 OK
```

Conceptual:

```json id="l4l0b7"
{
  "activity": {
    "id": "uuid",
    "status": "CANCELLED"
  },
  "planningImpact": {
    "affected": true,
    "replanningRequired": true
  }
}
```

Current Schedule ยังไม่เปลี่ยนจนกว่ากระบวนการ Replanning จะสร้าง Proposal และ User Confirm

---

# 10.31 DELETE /api/activities/{id}

ใช้สำหรับ Soft Delete ของ Planning Object

### Response

```text id="bjgij7"
204 No Content
```

การ Delete:

* ไม่ Hard Delete Historical References
* ไม่ลบ Historical Schedule Version
* ต้องพิจารณา Planning Impact ถ้า Activity มีผลต่อ Current Schedule

---

# 10.32 Planning Endpoints

```text id="j5s0je"
POST /api/planning/requests
POST /api/planning/requests/{id}/clarification-response
POST /api/planning/feedback
```

Planning Endpoint เป็น High-level Application API

ไม่เปิด Internal AI หรือ CP-SAT Endpoint

---

# 10.33 POST /api/planning/requests

สร้าง Planning Request จาก Natural Language

### Request

```json id="m5jho9"
{
  "inputText": "พรุ่งนี้ช่วงบ่ายอยากทำรายงานสองชั่วโมง",
  "referenceTime": "2026-10-04T10:00:00+07:00"
}
```

`referenceTime` สามารถให้ Client ส่งตาม Context ของ Operation แต่ Server ต้อง Validate และควบคุม Timezone Policy ตาม Security/Consistency Design

ในบาง Implementation สามารถให้ Server เป็นผู้กำหนด Reference Time จาก Request Time เพื่อความสอดคล้อง

### Response

หากระบบต้องประมวลผลต่อ:

```text id="ryzmkc"
201 Created
```

หรือ:

```text id="w9xymv"
200 OK
```

ขึ้นกับ Implementation Contract

Conceptual:

```json id="hxfh5r"
{
  "request": {
    "id": "uuid",
    "status": "PROCESSING"
  }
}
```

---

# 10.34 Planning Request Processing

หลังสร้าง Request:

```text id="sfvpdo"
RECEIVED
   ↓
PROCESSING
```

จากนั้น:

```text id="hk1g4h"
PROCESSING
├── NEEDS_CLARIFICATION
├── COMPLETED
└── FAILED
```

หาก Processing เสร็จพร้อม Proposal:

```text id="2ifk0m"
request.status = COMPLETED
proposal = available
```

---

# 10.35 Planning Request Response States

Client ต้องสามารถแยก State:

```text id="m22h5e"
PROCESSING
```

หมายถึง:

> ระบบกำลังทำงาน

```text id="abgdty"
NEEDS_CLARIFICATION
```

หมายถึง:

> User ต้องตอบข้อมูลเพิ่ม

```text id="8u0qpo"
COMPLETED
```

หมายถึง:

> มีผลลัพธ์ให้ User Review

```text id="txwp1l"
FAILED
```

หมายถึง:

> Request ไม่สามารถดำเนินการต่อได้

---

# 10.36 POST /api/planning/requests/{id}/clarification-response

ใช้ตอบ Clarification ที่เกิดขึ้นกับ Planning Request

### Request

```json id="6r8kva"
{
  "responseText": "หกโมงเย็น"
}
```

### Response

```text id="g7sv3a"
202 Accepted
```

หรือ `200 OK` ตาม Processing Model

Conceptual:

```json id="9da1f6"
{
  "request": {
    "id": "new-request-id",
    "parentRequestId": "original-request-id",
    "status": "PROCESSING"
  }
}
```

การตอบ Clarification ต้องรักษา Context ของ Request เดิม

---

# 10.37 Clarification Example

Original:

```text id="oj3vqv"
POST /api/planning/requests

“พรุ่งนี้ 6 โมงไปวิ่ง”
```

Request:

```text id="a2modu"
status = NEEDS_CLARIFICATION
```

ระบบถาม:

> “หมายถึง 06:00 หรือ 18:00?”

User:

```text id="k5tkyd"
POST /api/planning/requests/{id}/clarification-response

{
  "responseText": "18:00"
}
```

จากนั้น:

```text id="7jbyvd"
PROCESSING
   ↓
PLANNING
   ↓
PROPOSAL
```

---

# 10.38 Clarification Does Not Create Schedule Directly

Clarification Response:

```text id="1g1yzn"
→ Input Update
```

ไม่ใช่:

```text id="rqaj6m"
→ Schedule Update
```

ดังนั้น Confirmed Schedule ยังไม่เปลี่ยน

---

# 10.39 POST /api/planning/feedback

รับ Feedback จาก User เพื่อใช้ในการปรับแผน

### Request

```json id="l1u2w7"
{
  "proposalId": "uuid",
  "feedbackText": "ขอเลื่อนอ่านหนังสือไปช่วงเย็น และอยากให้กระทบกิจกรรมอื่นน้อยที่สุด"
}
```

### Response

```text id="h4yzcw"
202 Accepted
```

Conceptual:

```json id="qtlfan"
{
  "planningRequest": {
    "id": "uuid",
    "status": "PROCESSING"
  }
}
```

ระบบสามารถสร้าง Replanning Request ภายในที่มี:

```text id="2pjo8u"
parent_request_id
```

เชื่อมกับ Context เดิมตาม Application Policy

---

# 10.40 Feedback Flow

```text id="tlovgm"
Proposal
 ↓
User Feedback
 ↓
POST /api/planning/feedback
 ↓
AI/NLP
 ↓
Structured Requirement / Preference
 ↓
Validation
 ↓
Replanning
 ↓
New Proposal
```

Feedback ไม่สามารถเปลี่ยน Confirmed Schedule โดยตรง

---

# 10.41 Feedback Without Actionable Information

เช่น User ส่ง:

> “ไม่ชอบแผนนี้”

อาจยังไม่มี Requirement ที่สามารถนำไป Replan ได้

ระบบสามารถ:

```text id="6dmoij"
Request Clarification
```

แทนการเดาว่า User ต้องการอะไร

ตัวอย่าง:

> “ต้องการเปลี่ยนช่วงเวลา กิจกรรม หรือมีข้อจำกัดเพิ่มเติมไหม?”

---

# 10.42 Proposal Endpoints

```text id="yz39rb"
GET  /api/proposals/{id}
POST /api/proposals/{id}/confirm
POST /api/proposals/{id}/reject
```

---

# 10.43 GET /api/proposals/{id}

คืน Proposal พร้อม Candidate(s)

ตัวอย่าง:

```json id="0kp86r"
{
  "id": "proposal-uuid",
  "status": "PENDING",
  "candidateCount": 2,
  "sourceScheduleVersionId": "version-uuid",
  "candidates": [
    {
      "planKey": "A",
      "items": []
    },
    {
      "planKey": "B",
      "items": []
    }
  ]
}
```

---

# 10.44 Candidate Response

Candidate:

```json id="v8g9n7"
{
  "planKey": "A",
  "items": [
    {
      "planningObjectId": "uuid",
      "startAt": "2026-10-04T13:00:00+07:00",
      "endAt": "2026-10-04T15:00:00+07:00"
    }
  ],
  "summary": {
    "requirementSatisfaction": 1.0,
    "preferenceSatisfaction": 0.8,
    "stabilityScore": 0.9
  }
}
```

ตัวเลข Score ที่แสดงให้ User จริงจะต้องถูกกำหนดแยกจาก Internal Evaluation Metrics และไม่ควรสร้างตัวเลขที่ไม่มีนิยามที่ชัดเจน

---

# 10.45 POST /api/proposals/{id}/confirm

Confirm Candidate ที่ User เลือก

### Request

```json id="j0qgqn"
{
  "planKey": "A"
}
```

Header:

```text id="jbi69y"
Idempotency-Key: <unique-key>
```

---

# 10.46 Proposal Confirmation Preconditions

ก่อน Confirm:

```text id="41c19a"
1. Authenticate User
2. Authorize Proposal Ownership
3. Status = PENDING
4. Candidate exists
5. Source Schedule Version is current
6. Candidate passes validation
7. Candidate has no Hard Constraint violation
```

หากไม่ผ่าน:

```text id="fdpoac"
409 Conflict
```

หรือ:

```text id="e4w0xl"
422 Unprocessable Entity
```

ตามลักษณะ Error

---

# 10.47 Stale Proposal Response

ถ้า:

```text id="b0zq0k"
Proposal Source = V3
Current Schedule = V4
```

Response:

```text id="qk8s4g"
409 Conflict
```

```json id="p6qw9y"
{
  "error": {
    "code": "STALE_PROPOSAL",
    "message": "The proposal was created from an outdated schedule version.",
    "details": {
      "sourceScheduleVersionId": "v3",
      "currentScheduleVersionId": "v4"
    },
    "requestId": "abc123"
  }
}
```

ห้ามสร้าง V5 จาก Proposal ที่อ้างอิง V3

---

# 10.48 Successful Proposal Confirmation

เมื่อ Confirm สำเร็จ:

```text id="vj1loz"
Proposal
→ CONFIRMED

Schedule Version
→ V(n+1)
```

และ:

```text id="1g63jy"
V(n)
→ is_current = FALSE

V(n+1)
→ is_current = TRUE
```

### Response

```text id="9mkrzo"
200 OK
```

Conceptual:

```json id="h7p8yp"
{
  "proposal": {
    "id": "proposal-uuid",
    "status": "CONFIRMED"
  },
  "scheduleVersion": {
    "id": "new-version-uuid",
    "versionNumber": 4,
    "isCurrent": true
  }
}
```

---

# 10.49 POST /api/proposals/{id}/reject

Reject Proposal

### Request

```json id="ra9o7q"
{
  "reason": "เวลาไม่สะดวก"
}
```

`reason` สามารถเป็น Optional ตาม UX Policy

### Response

```text id="t8rj84"
200 OK
```

Proposal:

```text id="w6i7ez"
PENDING
→ REJECTED
```

Current Schedule:

```text id="7kdggk"
unchanged
```

Notification:

```text id="v8i7qs"
unchanged
```

---

# 10.50 Reject Does Not Change Schedule

เมื่อ User Reject:

```text id="9zqxyo"
Proposal rejected
```

ไม่ควร:

* เปลี่ยน Current Schedule
* สร้าง Schedule Version ใหม่
* ยกเลิก Notification ปัจจุบัน
* สร้าง New Schedule โดยอัตโนมัติ

---

# 10.51 Schedule Endpoints

```text id="i3c7lz"
GET  /api/schedule
POST /api/schedule/validate
POST /api/schedule/manual-confirm
```

---

# 10.52 GET /api/schedule

คืน Current Confirmed Schedule

รองรับ:

```text id="y9sq60"
from
to
```

เพื่อให้ Mobile ดึงเฉพาะช่วงที่ต้องแสดง

ตัวอย่าง:

```http id="s8viuk"
GET /api/schedule?from=2026-10-04T00:00:00+07:00&to=2026-10-05T00:00:00+07:00
```

---

# 10.53 Schedule Response

```json id="n3bzxm"
{
  "scheduleVersion": {
    "id": "uuid",
    "versionNumber": 4,
    "isCurrent": true
  },
  "items": [
    {
      "id": "schedule-item-uuid",
      "planningObjectId": "activity-uuid",
      "startAt": "2026-10-04T14:00:00+07:00",
      "endAt": "2026-10-04T16:00:00+07:00"
    }
  ]
}
```

---

# 10.54 GET /api/schedule — Date-only Activity

Date-only Activity ที่ไม่มี Schedule Placement ไม่ควรถูกสร้างเป็น:

```text id="72h9eo"
06:00–07:00
```

เพียงเพราะ Notification Default

API สามารถคืน Date-only Activities แยกจาก Scheduled Items เช่น:

```json id="6kq9f6"
{
  "items": [],
  "unscheduled": [
    {
      "planningObjectId": "uuid",
      "date": "2026-10-05",
      "title": "ซื้อของขวัญ"
    }
  ]
}
```

หรือใช้ Separate Field ใน Schedule Response Contract

---

# 10.55 POST /api/schedule/validate

ใช้ Validate Draft Schedule

### Request

```json id="9x1d4d"
{
  "baseScheduleVersionId": "version-uuid",
  "items": [
    {
      "planningObjectId": "activity-a",
      "startAt": "2026-10-04T14:00:00+07:00",
      "endAt": "2026-10-04T16:00:00+07:00"
    },
    {
      "planningObjectId": "activity-b",
      "startAt": "2026-10-04T15:00:00+07:00",
      "endAt": "2026-10-04T17:00:00+07:00"
    }
  ]
}
```

---

# 10.56 Schedule Validation Response — Valid

```json id="sw9d1i"
{
  "valid": true,
  "conflicts": []
}
```

---

# 10.57 Schedule Validation Response — Conflict

```json id="4e9o8y"
{
  "valid": false,
  "conflicts": [
    {
      "type": "NO_OVERLAP",
      "objectIds": [
        "activity-a",
        "activity-b"
      ],
      "message": "Activities overlap."
    }
  ]
}
```

Response Status สามารถเป็น:

```text id="t5d5wk"
200 OK
```

แม้ Schedule จะ Invalid เนื่องจาก API เองทำงานสำเร็จและคืน Validation Result

หรือใช้ `422` หาก Contract นิยาม Invalid Draft เป็น Semantic Validation Error

ต้องกำหนดรูปแบบเดียวกันใน Implementation

---

# 10.58 POST /api/schedule/manual-confirm

Confirm Draft Schedule

### Request

```json id="kqatn4"
{
  "baseScheduleVersionId": "version-uuid",
  "items": [
    {
      "planningObjectId": "activity-a",
      "startAt": "2026-10-04T14:00:00+07:00",
      "endAt": "2026-10-04T16:00:00+07:00"
    }
  ]
}
```

Header:

```text id="y9y2et"
Idempotency-Key: <unique-key>
```

---

# 10.59 Manual Confirmation Preconditions

1. User authenticated
2. User owns Objects
3. Base Schedule Version ยังเป็น Current ตาม Policy
4. Draft ผ่าน Validation
5. ไม่มี Hard Conflict
6. Items มีข้อมูลถูกต้อง
7. User explicitly confirms

---

# 10.60 Manual Confirmation Success

Response:

```text id="v1ecgw"
200 OK
```

Conceptual:

```json id="yuq23r"
{
  "scheduleVersion": {
    "id": "new-version-uuid",
    "versionNumber": 5,
    "isCurrent": true
  }
}
```

Historical Version เดิมยังคงอยู่

---

# 10.61 Manual Confirmation Stale Base

ถ้า:

```text id="8n6k3g"
Draft Base = V4
Current = V5
```

Response:

```text id="ah3frh"
409 Conflict
```

Code:

```text id="1q7g8w"
STALE_SCHEDULE_VERSION
```

Draft ต้องไม่สามารถเขียนทับ V5 ได้

---

# 10.62 Manual Validation Does Not Commit

```text id="o4x2cd"
POST /api/schedule/validate
```

ทำเพียง:

```text id="p2y5c8"
Validate Draft
```

ไม่:

```text id="4jepu3"
Create Schedule Version
```

ดังนั้น Validate และ Confirm เป็นคนละ Operation

---

# 10.63 Availability Endpoints

```text id="f0wz13"
GET    /api/availability
POST   /api/availability
PATCH  /api/availability/{id}
DELETE /api/availability/{id}
```

ใช้ Table:

```text id="8x0mq3"
availability_rules
```

รองรับทั้ง:

```text id="9arg1k"
AVAILABLE
UNAVAILABLE
```

และ:

```text id="jm7wr8"
ONE_TIME
RECURRING
```

---

# 10.64 GET /api/availability

Query:

```text id="o0q4ea"
kind
from
to
page
pageSize
```

ตัวอย่าง:

```http id="r28aez"
GET /api/availability?kind=AVAILABLE&from=2026-10-01&to=2026-10-31
```

---

# 10.65 POST /api/availability

### One-time Example

```json id="n5r2he"
{
  "kind": "UNAVAILABLE",
  "recurrenceType": "ONE_TIME",
  "dateStart": "2026-10-05",
  "dateEnd": "2026-10-05",
  "startTime": "13:00",
  "endTime": "15:00",
  "timezone": "Asia/Bangkok"
}
```

### Recurring Example

```json id="s2vwy5"
{
  "kind": "AVAILABLE",
  "recurrenceType": "RECURRING",
  "daysOfWeek": [1,2,3,4,5],
  "startTime": "08:00",
  "endTime": "17:00",
  "timezone": "Asia/Bangkok"
}
```

---

# 10.66 Availability Mutation Impact

เมื่อแก้ไข Availability/Unavailability:

```text id="2pa6ec"
Persist Change
       ↓
Determine Current Schedule Impact
       ↓
If affected
    → Replanning
```

ระบบไม่ควรแก้ Current Schedule โดยอัตโนมัติ

---

# 10.67 DELETE /api/availability/{id}

ลบ Availability Rule

หาก Rule ถูกใช้ใน Historical Planning Context:

* ต้องพิจารณา Historical Trace
* ไม่ควรทำให้ Historical Schedule Version เปลี่ยน

การลบสามารถเป็น Hard Delete ได้หากไม่มี Historical FK ที่จำเป็น หรือใช้ Soft Delete ตาม Implementation Policy แต่ไม่ควรทำลายข้อมูลย้อนหลังที่จำเป็นต่อ Evaluation

---

# 10.68 Settings Endpoints

```text id="6h9x2f"
GET   /api/settings/time-windows
PATCH /api/settings/time-windows

GET   /api/settings/notifications
PATCH /api/settings/notifications
```

ทั้งสอง Endpoint ใช้ `user_settings` เป็น Persistence Layer

---

# 10.69 GET /api/settings/time-windows

Response:

```json id="pb61xi"
{
  "systemDefaults": {
    "LATE_NIGHT": {
      "start": "00:00",
      "end": "06:00"
    },
    "MORNING": {
      "start": "06:00",
      "end": "09:00"
    },
    "LATE_MORNING": {
      "start": "09:00",
      "end": "12:00"
    },
    "NOON": {
      "start": "12:00",
      "end": "13:00"
    },
    "AFTERNOON": {
      "start": "13:00",
      "end": "16:00"
    },
    "EVENING": {
      "start": "16:00",
      "end": "19:00"
    },
    "NIGHT": {
      "start": "19:00",
      "end": "24:00"
    }
  },
  "overrides": {
    "AFTERNOON": {
      "start": "12:00",
      "end": "17:00"
    }
  }
}
```

System Default สามารถแสดงให้ Mobile รู้เพื่อใช้ Presentation/Settings UI

---

# 10.70 PATCH /api/settings/time-windows

User สามารถ Update เฉพาะ Override ที่ต้องการ

ตัวอย่าง:

```json id="xandxu"
{
  "overrides": {
    "AFTERNOON": {
      "start": "12:00",
      "end": "17:00"
    }
  }
}
```

ระบบต้อง Validate ก่อน Persist

---

# 10.71 Time Window Validation

ตรวจ:

* Valid Time
* Start ≠ End ตาม Rule
* Full-Day Partition Validation เมื่อ User กำหนด Complete Custom Partition ตาม Policy
* No invalid overlapping Custom Windows เมื่อเป็น Full-Day Partition
* Canonical Window Name

หากเป็น Partial Override:

```text id="o0xtgs"
Missing Window
→ Fallback System Default
```

---

# 10.72 GET /api/settings/notifications

Response:

```json id="eygfqx"
{
  "systemDefaults": {
    "dateOnly": {
      "time": "06:00"
    },
    "timeSpecific": {
      "beforeStartMinutes": 60
    }
  },
  "overrides": {
    "dateOnly": null,
    "timeSpecific": null
  }
}
```

---

# 10.73 PATCH /api/settings/notifications

ตัวอย่าง:

```json id="4k0h3n"
{
  "overrides": {
    "dateOnly": {
      "time": "08:00"
    },
    "timeSpecific": {
      "beforeStartMinutes": 30
    }
  }
}
```

ระบบต้อง Validate:

```text id="jq2lfz"
beforeStartMinutes >= 0
notification time valid
```

และ Notification Time ที่ได้จริงต้องสอดคล้องกับ Activity Start ตาม Notification Policy

---

# 10.74 Notification Setting Impact

เมื่อ User เปลี่ยน Notification Default:

```text id="b7g7yi"
Settings Change
       ↓
Find Current Scheduled Activities
       ↓
Apply only to Activities without Activity Override
       ↓
Mobile Notification Synchronization
```

ไม่ต้อง Replan Schedule เพราะ Notification Policy ไม่ใช่ Scheduling Constraint

---

# 10.75 API and Notification Boundary

Backend Settings API:

```text id="bopvwx"
stores Policy
```

Mobile:

```text id="rulxgc"
derives Local Notification
```

Backend ไม่มี:

```text id="kxz47f"
notification_instances
```

ใน MVP

---

# 10.76 API and Candidate Generation

ไม่มี Endpoint:

```text id="z8cys2"
/api/candidates/generate
```

โดยตรง

เพราะ Candidate Generation เป็น Internal Planning Capability

Client ขอ:

```text id="4k84z8"
/api/planning/requests
```

แล้วได้รับ:

```text id="0b93sy"
Proposal
```

พร้อม Candidate(s)

---

# 10.77 API and AI Boundary

ไม่มี:

```text id="g6m6ph"
/api/ai/extract
```

AI Flow:

```text id="7smne0"
POST /api/planning/requests
        ↓
Application
        ↓
AI / NLP
        ↓
Validation
        ↓
Planning
```

Client ไม่จำเป็นต้องรู้ Prompt หรือ AI Provider

---

# 10.78 API and CP-SAT Boundary

ไม่มี:

```text id="3xzq08"
/api/cp-sat/solve
```

Planner ถูกเรียกโดย Application Service

Client รู้เพียง:

```text id="0v8v6a"
Planning Request
→ Proposal
```

---

# 10.79 API Idempotency

Operations ที่มี Side Effect สำคัญ:

```text id="8uop9m"
POST /api/auth/logout
POST /api/planning/requests
POST /api/planning/requests/{id}/clarification-response
POST /api/planning/feedback
POST /api/proposals/{id}/confirm
POST /api/proposals/{id}/reject
POST /api/schedule/manual-confirm
POST /api/activities/{id}/cancel
```

สามารถกำหนดให้รองรับ `Idempotency-Key` ตาม Risk/Implementation

อย่างน้อยควรบังคับใช้กับ:

```text id="8byhiw"
Planning Request
Proposal Confirmation
Manual Confirmation
```

---

# 10.80 Idempotency Behavior

ตัวอย่าง:

```text id="c8z1pl"
POST /api/proposals/P1/confirm
Idempotency-Key: X
```

Request ซ้ำด้วย Key เดิมและ Payload เดิม:

```text id="7f7stu"
→ Return original result
```

ไม่สร้าง Schedule Version ใหม่

หากใช้ Key เดิมแต่ Payload แตกต่าง:

```text id="8er0v0"
409 Conflict
```

เช่น:

```text id="xt2v2i"
IDEMPOTENCY_KEY_REUSED
```

---

# 10.81 Request Validation

Validation 3 ระดับ:

```text id="hga0zd"
1. HTTP / JSON Schema
       ↓
2. Domain Validation
       ↓
3. Business Rule Validation
```

ตัวอย่าง:

```text id="v8n6gx"
durationMinutes = -10
```

ระดับ Schema / Domain:

```text id="o18un3"
422
```

แต่:

```text id="cezmzd"
Proposal Source Version != Current Version
```

เป็น:

```text id="nx0f5e"
409
```

---

# 10.82 DateTime Representation

API ใช้:

> ISO 8601 Date-Time

ตัวอย่าง:

```text id="0rha9b"
2026-10-04T14:00:00+07:00
```

ควรมี Timezone Offset หรือ Canonical Timezone ตาม Field Semantics

Date-only:

```text id="s5htks"
2026-10-04
```

ไม่ควรเติม Midnight แล้วตีความเป็น DateTime

---

# 10.83 Timezone Policy

Timezone สำคัญสำหรับ:

* Calendar
* Planning
* Recurring Availability
* Relative Date
* Notification

API ต้องไม่ถือว่า:

```text id="10j7xa"
Date + Time
```

ไม่มี Timezone Context

User Timezone สามารถอ้างอิงจาก:

```text id="1j13hr"
users.timezone
```

และ Rule-specific Timezone จาก:

```text id="m9dv4f"
availability_rules.timezone
```

ตาม Domain Policy

---

# 10.84 Pagination Contract

List APIs ใช้:

```text id="8k3g8x"
page
pageSize
```

Response:

```json id="x5dl3x"
{
  "items": [],
  "pagination": {
    "page": 1,
    "pageSize": 50,
    "totalItems": 120,
    "totalPages": 3
  }
}
```

ตัวเลข Default / Maximum `pageSize` ต้องกำหนดจาก Performance Benchmark และ API Operational Policy

---

# 10.85 API Filtering

Filtering ต้องจำกัดตาม User Ownership

เช่น:

```text id="0lgvst"
GET /api/activities?status=ACTIVE
```

Backend ต้องเติม:

```text id="e4flte"
authenticated_user_id
```

เอง

Client ไม่ต้องส่ง:

```text id="yg2f9u"
userId
```

เพื่อระบุ Owner

---

# 10.86 Authorization Rules

### User Resource

User ต้องเข้าถึงได้เฉพาะของตนเอง

### Proposal

ต้องเป็นของ User

### Schedule Version

ต้องเป็นของ User

### Planning Object

ต้องเป็นของ User

### Availability

ต้องเป็นของ User

### Planning Rule

ต้องเป็นของ User

### Temporal Relation

Objects ต้นทางและปลายทางต้องเป็นของ User เดียวกัน

---

# 10.87 Resource Enumeration Protection

สำหรับ Resource ที่ User ไม่มีสิทธิ์ ระบบสามารถตอบ:

```text id="4g0y1d"
404 Not Found
```

แทนการบอกว่า Resource มีอยู่แต่ User ไม่มี Permission

Policy นี้ช่วยลดการเปิดเผยข้อมูลของ Users อื่น

---

# 10.88 API and Proposal Lifecycle

API ต้องเคารพ:

```text id="5k7lto"
PENDING
  ├── CONFIRMED
  ├── REJECTED
  └── INVALIDATED
```

### Confirm

เฉพาะ `PENDING`

### Reject

เฉพาะ `PENDING`

### Invalidated

ไม่สามารถ Confirm

### Confirmed

ไม่สามารถ Confirm ซ้ำ

### Rejected

ไม่สามารถ Confirm

---

# 10.89 Proposal Confirmation Rules

`POST /api/proposals/{id}/confirm` ต้อง:

```text id="8l39il"
Check Authentication
 ↓
Check Ownership
 ↓
Check Proposal Status
 ↓
Check Candidate
 ↓
Check Source Schedule Version
 ↓
Validate Candidate
 ↓
Create New Schedule Version
 ↓
Update Proposal
 ↓
Commit
```

ทั้งหมดต้องอยู่ใน Transaction ที่เหมาะสม

---

# 10.90 Schedule Version Transaction

Conceptually:

```text id="yq7vug"
BEGIN
   |
   +-- Verify Current Version
   |
   +-- Create New Version
   |
   +-- Create Schedule Items
   |
   +-- Update Old Version
   |
   +-- Update Proposal
   |
COMMIT
```

หลัง Commit:

```text id="rvl9pk"
Mobile Notification Synchronization
```

เกิดภายนอก Transaction

---

# 10.91 API and Draft Schedule

Draft ไม่ต้องมี Resource ID แบบ Persistent ใน Database

Mobile สามารถเก็บ:

```text id="lptqbb"
Draft State
```

ใน Client State

เมื่อ Validate:

```text id="b8ld6l"
Send Draft
→ POST /api/schedule/validate
```

เมื่อ Confirm:

```text id="x7r7m9"
Send Draft
→ POST /api/schedule/manual-confirm
```

---

# 10.92 Draft Concurrency

Manual Confirmation ต้องส่ง:

```text id="f95ren"
baseScheduleVersionId
```

เพื่อบอกว่า Draft นี้สร้างจาก Schedule Version ใด

หาก Current Version เปลี่ยน:

```text id="z26cdx"
409 Conflict
```

ต้องโหลด Current Schedule ใหม่และให้ User review Draft อีกครั้งตาม UX Policy

---

# 10.93 API and Replanning

ไม่มี:

```text id="20zq0k"
/api/replanning
```

แยกใน MVP

Replanning ถูก Trigger ผ่าน:

* Activity Update
* Activity Cancellation
* Availability Change
* Planning Request
* Feedback

แล้ว Application Layer เป็นผู้ตัดสินใจว่าจะเข้าสู่ Replanning หรือไม่

---

# 10.94 Replanning API Flow

ตัวอย่าง:

```text id="h5i6ga"
PATCH /api/activities/A
        ↓
Application
        ↓
Impact Detection
        ↓
Affected Context
        ↓
Replanning
        ↓
Proposal
```

Client ไม่จำเป็นต้องเรียก Solver เอง

---

# 10.95 Long-range Activity Update

Activity ที่อยู่ไกลจาก Current Date ยังเรียก:

```text id="0tngeb"
PATCH /api/activities/{id}
```

ได้

Planning Horizon ไม่ควรถูกใช้เป็น API CRUD Permission Boundary

กล่าวคือ:

```text id="4u4erp"
Outside Planning Horizon
≠
Cannot Edit
```

---

# 10.96 Error Handling — AI Failure

ถ้า AI Provider:

```text id="3si6ya"
Timeout
Unavailable
Invalid Output
```

API สามารถคืน:

```text id="9x35jn"
503 Service Unavailable
```

หรือ:

```text id="kl65kg"
422 Unprocessable Entity
```

ตามสาเหตุ

ตัวอย่าง:

```json id="1sq1pf"
{
  "error": {
    "code": "AI_PROVIDER_UNAVAILABLE",
    "message": "Planning could not be processed because the AI service is unavailable.",
    "details": {},
    "requestId": "abc123"
  }
}
```

ไม่ส่ง Provider Secret หรือ Stack Trace

---

# 10.97 Error Handling — No Feasible Plan

หาก Planner ยืนยันว่าไม่มี Feasible Solution:

API สามารถคืน:

```text id="vd4wjw"
200 OK
```

พร้อม Planning Result State:

```json id="py8jnv"
{
  "request": {
    "id": "uuid",
    "status": "COMPLETED"
  },
  "result": {
    "status": "NO_FEASIBLE_PLAN"
  }
}
```

หรือใช้ Error Response ตาม API Contract

สิ่งสำคัญคือ Client ต้องแยก:

> “ระบบทำงานเสร็จ แต่ไม่มี Feasible Plan”

ออกจาก:

> “ระบบทำงานผิดพลาด”

---

# 10.98 Error Handling — Solver Unknown

หาก Solver คืน `UNKNOWN` และไม่มี Feasible Result:

```text id="r2wb0j"
503
```

หรือ Domain-specific `500/503`

โดย Response ต้องไม่เรียกว่า `NO_FEASIBLE_PLAN`

---

# 10.99 Error Handling — Model Invalid

หาก Planner สร้าง Invalid Model:

```text id="uvp6yh"
500 Internal Server Error
```

เช่น:

```json id="l9e10f"
{
  "error": {
    "code": "MODEL_INVALID",
    "message": "The planning model could not be processed.",
    "details": {},
    "requestId": "abc123"
  }
}
```

รายละเอียด Internal Solver ต้องถูกซ่อนจาก Client หากไม่จำเป็น

---

# 10.100 API and Unsupported Feature

หาก User Request ขอ Feature ที่ MVP ไม่รองรับ:

```text id="ai7q48"
Unsupported
```

เช่น Real-time Traffic Route Optimization

API สามารถคืน Structured Application Result เช่น:

```json id="9yr4c3"
{
  "request": {
    "id": "uuid",
    "status": "FAILED"
  },
  "error": {
    "code": "UNSUPPORTED_FEATURE",
    "message": "This planning capability is not supported."
  }
}
```

ไม่ควรเปลี่ยน Request ให้เป็น Approximation โดยไม่ได้รับความยินยอม

---

# 10.101 API and Missing Information

หาก AI/NLP พบ Missing Information ที่จำเป็น:

```text id="f1v09b"
Planning Request
→ NEEDS_CLARIFICATION
```

ไม่ควรตอบ:

```text id="j3qg79"
422
```

เพียงเพราะข้อมูลยังไม่ครบ หากระบบสามารถ Clarify ได้

---

# 10.102 API and Clarification

Client ต้องสามารถใช้ Request State เพื่อแสดง:

```text id="a4wm1q"
status = NEEDS_CLARIFICATION
```

พร้อมข้อมูลคำถามใน Response Contract

ตัวอย่าง:

```json id="6ipgw5"
{
  "request": {
    "id": "uuid",
    "status": "NEEDS_CLARIFICATION"
  },
  "clarification": {
    "question": "6 โมงหมายถึง 06:00 หรือ 18:00?"
  }
}
```

---

# 10.103 API Request Lifecycle

```text id="tg1sl0"
POST /planning/requests
        ↓
201
        ↓
PROCESSING
        |
        +--> NEEDS_CLARIFICATION
        |       |
        |       v
        |   POST clarification-response
        |       |
        |       v
        |   PROCESSING
        |
        +--> COMPLETED
        |       |
        |       v
        |    Proposal
        |
        +--> FAILED
```

---

# 10.104 API and User Decision

Proposal API แยก User Decision ออกจาก Planning

```text id="fnxy28"
Planner
 ↓
Proposal

User
 ↓
Confirm / Reject / Feedback
```

API จึงไม่ควรใช้:

```text id="k4bsmm"
POST /api/planning/requests
```

เพื่อหมายความว่า:

> “สร้างและยืนยันตารางให้เลย”

Request และ Confirmation เป็นคนละ State Transition

---

# 10.105 API Security Rules

ทุก Protected Endpoint ต้อง:

1. Validate Access Token
2. Resolve Authenticated User
3. Validate Ownership
4. Validate Input
5. Execute Domain Operation

ห้ามเชื่อ:

```text id="g0zgiv"
userId
```

จาก Request Body ว่าเป็น Owner

---

# 10.106 API Rate Limiting

Rate Limit ควรใช้กับอย่างน้อย:

```text id="1i3r3w"
Login
Register
Forgot Password
Planning Requests
Clarification
Feedback
Proposal Confirmation
```

ค่าจริงเป็น Operational Configuration และต้องปรับตาม Performance/Security Testing

เมื่อเกิน:

```text id="r5q7f6"
429 Too Many Requests
```

---

# 10.107 API Idempotency and Retry

Client สามารถ Retry Request ที่ network failure ได้โดยไม่สร้าง Duplicate Side Effect หากใช้ Idempotency Key ตาม Contract

กรณี:

```text id="x9ssj2"
Client sends confirm
→ server processes
→ network timeout
```

Client Retry ด้วย Key เดิม:

```text id="yqk8d6"
→ server returns original result
```

ไม่สร้าง Schedule Version เพิ่ม

---

# 10.108 API Caching

GET APIs ที่เหมาะสมสามารถใช้ HTTP caching / Client caching ตาม Policy

ตัวอย่าง:

```text id="aaxk64"
GET /api/schedule
GET /api/activities
GET /api/settings/time-windows
```

แต่ Current Schedule ต้องมี Version Information เพื่อช่วย Client รู้ว่าข้อมูลเปลี่ยนหรือไม่

---

# 10.109 Schedule Version in Response

Schedule-related Responses ควรมี:

```json id="mwofj2"
{
  "scheduleVersion": {
    "id": "uuid",
    "versionNumber": 4,
    "isCurrent": true
  }
}
```

เพื่อช่วย Mobile:

* Cache Invalidation
* Concurrency Detection
* Synchronization
* Notification Synchronization

---

# 10.110 API and Mobile Notification Sync

เมื่อ Confirm สำเร็จ:

```text id="rwot44"
POST /api/proposals/{id}/confirm
        ↓
New Schedule Version
        ↓
Response
        ↓
Mobile
        ↓
Update Calendar
        ↓
Update Local Notifications
```

Backend ไม่ส่ง Local Notification ID กลับมาใน MVP

---

# 10.111 Notification Sync Data

Mobile สามารถใช้:

```text id="xk098u"
scheduleVersion
scheduleItems
notification policy
activity override
```

เพื่อคำนวณ Local Notification

Mapping:

```text id="2v9sau"
scheduleItemId
→ localNotificationId
```

เป็น Local State

---

# 10.112 API Consistency for Date-only

Activity:

```text id="qp7zzq"
dateStart = 2026-10-05
startAt = null
```

ต้องไม่ถูกเปลี่ยนเป็น:

```text id="ve77m4"
startAt = 2026-10-05T06:00:00
```

โดย API เพียงเพราะ Notification Default = 06:00

---

# 10.113 API Consistency for Notification

Activity:

```text id="e5g91b"
startAt = 09:00
notification = 08:00
```

API ต้องสามารถแยก:

```text id="zr37bp"
startAt
```

ออกจาก:

```text id="fsb4q7"
notificationOverride
```

อย่างชัดเจน

---

# 10.114 API Schema vs Internal Domain Model

API DTO ไม่จำเป็นต้องมี Structure เหมือน Database ORM Model 100%

ตัวอย่าง:

```text id="nqv8y9"
API DTO
→ designed for client communication

Domain Model
→ designed for business logic

ORM Model
→ designed for persistence
```

ควรมี Mapping:

```text id="qf0v0c"
API DTO
 ↓
Application / Domain
 ↓
Persistence
```

เพื่อไม่ให้ Database Schema รั่วออกเป็น API Contract โดยตรง

---

# 10.115 API Versioning Policy

MVP ใช้:

```text id="n7n3py"
/api
```

ไม่มี `/v1`

หากอนาคตมี Breaking Change ที่ Contract เดิมไม่สามารถรองรับได้ สามารถพิจารณา:

```text id="m7ep8z"
/api/v2
```

โดยตัวอย่างเหตุผลที่อาจนำไปสู่ Version ใหม่:

* Planning Algorithm เปลี่ยน Contract อย่างมีนัยสำคัญ
* Planning Representation เพิ่มข้อมูลที่ไม่ Backward Compatible
* Request/Response Structure เปลี่ยนแบบ Breaking
* Authentication Contract เปลี่ยน
* Client Compatibility ต้องรองรับสอง Version พร้อมกัน

การเพิ่ม `/v2` ไม่ได้ขึ้นกับการเปลี่ยน CP-SAT ภายในเพียงอย่างเดียว หาก Internal Algorithm เปลี่ยนแต่ API Contract เดิมยังรองรับได้ ก็ไม่จำเป็นต้องสร้าง API Version ใหม่

---

# 10.116 API Contract Compatibility

การเปลี่ยนแปลงแบ่ง:

### Non-breaking

* เพิ่ม Optional Response Field
* เพิ่ม Optional Request Field
* เพิ่ม Error Detail ที่ Client เดิมไม่จำเป็นต้องอ่าน
* Internal Algorithm Change ที่ไม่เปลี่ยน Contract

### Breaking

* ลบ Field
* เปลี่ยน Field Meaning
* เปลี่ยน Data Type
* เปลี่ยน Required Field
* เปลี่ยน State Semantics
* เปลี่ยน Confirmation Behavior

Breaking Change อาจต้องใช้ API Version ใหม่

---

# 10.117 API Endpoint Summary

## AUTH

```text id="u0j4vh"
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh
POST   /api/auth/logout
GET    /api/auth/me
POST   /api/auth/verify-email
POST   /api/auth/forgot-password
POST   /api/auth/reset-password
```

## ACTIVITIES

```text id="dzca2o"
GET    /api/activities
POST   /api/activities
GET    /api/activities/{id}
PATCH  /api/activities/{id}
POST   /api/activities/{id}/cancel
DELETE /api/activities/{id}
```

## PLANNING

```text id="a9o5k5"
POST   /api/planning/requests
POST   /api/planning/requests/{id}/clarification-response
POST   /api/planning/feedback
```

## PROPOSALS

```text id="u5xj15"
GET    /api/proposals/{id}
POST   /api/proposals/{id}/confirm
POST   /api/proposals/{id}/reject
```

## SCHEDULE

```text id="zu3n12"
GET    /api/schedule
POST   /api/schedule/validate
POST   /api/schedule/manual-confirm
```

## AVAILABILITY

```text id="8l5b4n"
GET    /api/availability
POST   /api/availability
PATCH  /api/availability/{id}
DELETE /api/availability/{id}
```

## SETTINGS

```text id="2y7c6q"
GET    /api/settings/time-windows
PATCH  /api/settings/time-windows
GET    /api/settings/notifications
PATCH  /api/settings/notifications
```

---

# 10.118 Endpoint Responsibility Matrix

| Endpoint                |                   AI/NLP |                  Planner | Schedule Write | User Confirmation |
| ----------------------- | -----------------------: | -----------------------: | -------------: | ----------------: |
| POST planning/requests  |                 Internal |                 Internal |              ❌ |                 ❌ |
| clarification-response  |                 Internal |                 Internal |              ❌ |                 ❌ |
| planning/feedback       |                 Internal |                 Internal |              ❌ |                 ❌ |
| proposals/{id}          |                          |                          |              ❌ |                   |
| proposals/{id}/confirm  |                          |                          |              ✅ |                 ✅ |
| proposals/{id}/reject   |                          |                          |              ❌ |                 ✅ |
| schedule/validate       |                          |        Domain Validation |              ❌ |                 ❌ |
| schedule/manual-confirm |                          |                          |              ✅ |                 ✅ |
| activities PATCH        | Possible Internal Impact | Possible Internal Replan |    Conditional |          ❌ direct |
| availability PATCH      |                          | Possible Internal Replan |    Conditional |          ❌ direct |
| settings PATCH          |                          |                          |              ❌ |                 ✅ |

`Conditional` หมายถึงอาจสร้าง Proposal/Replanning Context แต่ไม่สามารถเปลี่ยน Current Schedule โดยไม่มี Confirmation

---

# 10.119 Endpoint → Database Mapping

| API Group    | Main Tables                                           |
| ------------ | ----------------------------------------------------- |
| Auth         | users, auth_sessions, auth_tokens                     |
| Activities   | planning_objects                                      |
| Planning     | planning_requests, planning_objects, rules, relations |
| Proposals    | proposals, proposal_items                             |
| Schedule     | schedule_versions, schedule_items                     |
| Availability | availability_rules                                    |
| Settings     | user_settings                                         |

API ไม่ควร expose Table Structure โดยตรง

---

# 10.120 Complete Planning API Flow

```text id="qf8zo4"
POST /api/planning/requests
          |
          v
     Planning Request
          |
          v
       AI / NLP
          |
          v
 Validation / Normalize
          |
          +---- Clarification
          |         |
          |         v
          |   POST clarification-response
          |         |
          |         v
          |      Continue
          |
          v
      Planning Core
          |
          v
       Proposal
          |
     GET /proposals/{id}
          |
          v
       User Review
       /         \
   Reject       Confirm
      |            |
      v            v
  REJECTED      New Version
                   |
                   v
             Current Schedule
                   |
                   v
            Local Notification
```

---

# 10.121 Complete Replanning API Flow

```text id="jpy0fi"
Changed Activity / Feedback / Constraint
               |
               v
        API Operation
               |
               v
        Impact Detection
               |
               v
          Replanning
               |
               v
        New Proposal
               |
               v
     GET /api/proposals/{id}
               |
               v
           User Review
               |
               v
      POST /confirm
               |
               v
       New Schedule Version
               |
               v
     Mobile Notification Sync
```

---

# 10.122 API Invariants

```text id="s1h1he"
API-INV-01
Authenticated identity comes from Auth Context.

API-INV-02
Client cannot set resource ownership using userId in request body.

API-INV-03
AI is not exposed as a public extraction endpoint.

API-INV-04
CP-SAT is not exposed as a public solve endpoint.

API-INV-05
Planning creates Proposal, not Confirmed Schedule.

API-INV-06
Only Explicit User Confirmation can create a new Current Schedule Version.

API-INV-07
Rejected Proposal cannot modify Current Schedule.

API-INV-08
Stale Proposal cannot override Current Schedule.

API-INV-09
Manual Draft must be validated before confirmation.

API-INV-10
Invalid Draft cannot be confirmed.

API-INV-11
Schedule Version must be version-aware.

API-INV-12
Historical Schedule Versions are immutable.

API-INV-13
Notification instances are not persisted as Backend Business Resources.

API-INV-14
Date-only Activity does not receive a fake Activity Start Time from Notification Default.

API-INV-15
Planning Horizon does not limit Calendar CRUD operations.

API-INV-16
Errors use a common response structure.

API-INV-17
Side-effecting operations use Idempotency where required.

API-INV-18
Server validates ownership for every User-owned resource.

API-INV-19
AI/Planner failures do not silently create Invalid Schedule.

API-INV-20
Unsupported features are not silently approximated.
```

---

# 10.123 API Design Rationale

## Rationale 1 — No /v1 in MVP

ลด Complexity ของ API Contract ในช่วง Senior Project และเปิดทางให้ Version ใหม่เกิดเมื่อมี Breaking Change จริง ไม่ใช่เพียงเพราะ Internal Algorithm มีการเปลี่ยน

## Rationale 2 — No /ai/extract

ทำให้ Client พึ่งพา Business Flow แทนการผูกเข้ากับ Internal AI Implementation

## Rationale 3 — No /cp-sat/solve

ทำให้ Planning Algorithm เป็น Internal Capability และสามารถเปลี่ยน Solver ภายในโดยไม่จำเป็นต้องเปลี่ยน Mobile Contract

## Rationale 4 — Proposal as Boundary

รักษา Human-in-the-Loop และแยก Proposed State จาก Confirmed State

## Rationale 5 — Manual Validate + Confirm

ป้องกันการ Commit Draft ที่มี Conflict

## Rationale 6 — Schedule Version in Confirmation

ป้องกัน Concurrent / Stale Updates

## Rationale 7 — User ID From Auth

ลดความเสี่ยงจาก Broken Object Level Authorization และ Ownership Mistakes

## Rationale 8 — Local Notification Outside Backend Resource Model

ลด Dependency ระหว่าง API กับ Device-specific Notification State

---

# 10.124 API Documentation Standard

Endpoint ทุกตัวที่นำไป Implementation ต้องมีข้อมูลอย่างน้อย:

```text id="3f1qx2"
HTTP Method
Path
Authentication
Authorization
Request Headers
Path Parameters
Query Parameters
Request Body
Validation Rules
Business Rules
Response Status
Response Body
Error Codes
Idempotency
Side Effects
Database Impact
```

เพื่อให้สามารถนำไปสร้าง OpenAPI Specification ใน Implementation Phase ได้โดยไม่ต้องตีความใหม่

---

# 10.125 OpenAPI Generation

FastAPI สามารถสร้าง OpenAPI Schema จาก Request/Response Models ได้ใน Implementation

อย่างไรก็ตาม:

> OpenAPI เป็น Implementation Artifact

ส่วน Domain Rules และ Business Rules ต้องยังคงอ้างอิงจาก Design Documentation ฉบับนี้

---

# 10.126 API Testing Strategy

API ต้องมีการทดสอบอย่างน้อย:

### Authentication

* Valid Login
* Invalid Password
* Expired Token
* Revoked Session
* Ownership

### Activities

* CRUD
* Cancel
* Soft Delete
* Invalid Data
* Planning Impact

### Planning

* Normal Request
* Clarification
* No Feasible Plan
* AI Failure
* Unsupported Request

### Proposal

* Get
* Confirm
* Reject
* Stale Proposal
* Duplicate Confirm

### Schedule

* Get Current
* Validate Draft
* Conflict
* Manual Confirm
* Stale Base Version

### Availability

* One-time
* Recurring
* Available
* Unavailable
* Invalid Time

### Settings

* Time Windows
* Notification Defaults
* Override

---

# 10.127 Security Test Cases

อย่างน้อยต้องทดสอบ:

```text id="0g1tqz"
User A → access User B Activity
User A → access User B Proposal
User A → confirm User B Proposal
User A → modify User B Schedule
Client sends fake userId
Expired Token
Revoked Token
Replay Idempotency Key
Stale Proposal Confirmation
```

ทุกกรณีต้องไม่ทำให้ User สามารถเข้าถึงหรือแก้ข้อมูลของ User อื่นได้

---

# 10.128 Performance Test Cases

API Performance Benchmark ต้องทดสอบอย่างน้อย:

```text id="tgedws"
Activity List
Schedule Range Query
Planning Request
Proposal Retrieval
Confirmation
Availability Query
```

โดยเฉพาะ Planning API ต้องแยก:

```text id="xd9z3a"
API Response Time
```

ออกจาก:

```text id="so9x91"
AI Processing Time
Planning Solver Time
Database Time
```

เพื่อวิเคราะห์ Bottleneck ได้

---

# 10.129 Final API Architecture

```text id="74sl2j"
                     MOBILE APP
                         |
                         | HTTPS / JSON
                         v
                +------------------+
                |     API Layer    |
                +---------+--------+
                          |
                          v
                +------------------+
                | Application Layer|
                +---------+--------+
                          |
        +-----------------+------------------+
        |                 |                  |
        v                 v                  v
    AI / NLP        Schedule / Domain    Planning Core
        |                 |                  |
        |                 |                  |
        +-----------------+------------------+
                          |
                          v
                   Persistence Layer
                          |
                          v
                     PostgreSQL
```

API Layer จึงเป็น Boundary ระหว่าง Mobile และระบบภายใน โดยไม่เปิดรายละเอียด Internal Implementation ออกมาโดยไม่จำเป็น

---

# 10.130 Final API Principle

API ของ LONGTUA ใช้หลัก:

> **The client asks the system to understand, plan, review, and commit — but the client never directly controls the internal AI or Planning Engine.**

หรือในรูปแบบของระบบ:

```text id="1h0jii"
Request
  ↓
Understand
  ↓
Validate
  ↓
Plan
  ↓
Propose
  ↓
User Decides
  ↓
Commit
```

ทำให้ API สอดคล้องกับหลักใหญ่ของ LONGTUA:

```text id="s5dx3u"
AI
= Understand

Planner
= Compute

API
= Orchestrate / Expose

Proposal
= Present

User
= Decide

Schedule Version
= Commit

Notification
= Derive
```

และทุก Endpoint ต้องรักษา Invariants เดิมของระบบ โดยเฉพาะ:

> **AI ไม่จัดตารางโดยตรง**
> **Planner ไม่เปลี่ยน Confirmed Schedule โดยตรง**
> **Proposal ไม่เท่ากับ Confirmed Schedule**
> **Explicit User Confirmation เท่านั้นที่สร้าง Current Schedule Version ใหม่**
