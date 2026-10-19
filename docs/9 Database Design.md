# 9. Database Design

## 9.1 Purpose

เอกสารฉบับนี้กำหนดโครงสร้างฐานข้อมูลของ LONGTUA — Personal Adaptive Planner โดยแปลง Domain Model, Requirements, System Architecture, Planning Model, Replanning และ Schedule/Notification Design ให้เป็นโครงสร้างข้อมูลที่สามารถนำไปพัฒนาได้จริง

Database Design มีเป้าหมายเพื่อให้:

1. ข้อมูลของ User มีความถูกต้องและแยกตาม Ownership
2. Planning Objects และ Planning Rules สามารถนำไปใช้สร้าง Planning Model ได้
3. Planning Request และ Proposal สามารถติดตามย้อนหลังได้
4. Confirmed Schedule สามารถทำ Versioning และเก็บ Historical State ได้
5. Stale Proposal สามารถตรวจสอบได้
6. Database ไม่เก็บ State ที่ควรอยู่เฉพาะบน Mobile เช่น Local Notification Identifier
7. โครงสร้าง Database ไม่ผูกระบบเข้ากับ AI Provider หรือ Planning Algorithm มากเกินไป
8. Schema รองรับ MVP โดยไม่เพิ่ม Entity ที่ไม่จำเป็น

LONGTUA ใช้:

> **PostgreSQL**

เป็นฐานข้อมูลหลัก

และใช้:

* SQLAlchemy 2.x สำหรับ Data Access / ORM
* Alembic สำหรับ Database Migration

---

# 9.2 Database Design Principles

ฐานข้อมูลของ LONGTUA ใช้หลักการดังต่อไปนี้

### DB-PR-01 — User Ownership

ข้อมูลที่เป็น User-owned Resource ต้องสามารถตรวจสอบ Ownership ได้จาก Database Relationship

### DB-PR-02 — Immutable Schedule History

Schedule Version ที่สร้างแล้วต้องไม่ถูกแก้ไข

### DB-PR-03 — Current Schedule by Version

Current Schedule ไม่ต้องมี Table แยก แต่ระบุผ่าน Current Schedule Version

### DB-PR-04 — Proposal Is Separate

Proposal ต้องไม่ถูกเก็บรวมกับ Confirmed Schedule

### DB-PR-05 — Draft Is Not Persistent

Draft Schedule ของ Manual Editing ไม่จำเป็นต้องเป็น Database Entity ใน MVP

### DB-PR-06 — Notification Is Derived

Notification Instance ไม่ถูก Persist เป็น Backend Entity ใน MVP

### DB-PR-07 — Flexible Data in JSONB

ข้อมูลที่มีรูปแบบยืดหยุ่นหรือ Provider/Experiment-specific สามารถใช้ JSONB ได้ แต่ Core Domain State ต้องเก็บใน Typed Columns

### DB-PR-08 — Soft Delete for Referenced Objects

Planning Objects ที่มี Historical Reference ไม่ควรถูก Hard Delete

### DB-PR-09 — Database Is Not the Only Rule Layer

Database ต้อง enforce Invariants ที่เหมาะสม ส่วน Business Rules ที่ซับซ้อน เช่น Proposal State Transition ต้องถูกตรวจใน Application/Domain Layer

### DB-PR-10 — No Silent Data Loss

Database Schema และ Application ต้องไม่ถูกออกแบบให้ตัด Planning Object หรือ Constraint ออกเพียงเพื่อให้ระบบทำงานต่อ

---

# 9.3 Database Overview

MVP มีทั้งหมด **14 Tables**

```text
1.  users
2.  auth_sessions
3.  auth_tokens
4.  user_settings

5.  planning_objects
6.  container_memberships
7.  availability_rules
8.  planning_rules
9.  temporal_relations

10. planning_requests
11. proposals
12. proposal_items

13. schedule_versions
14. schedule_items
```

โครงสร้างแบ่งเป็น 5 กลุ่ม:

```text
Authentication
├── users
├── auth_sessions
└── auth_tokens

User Configuration
└── user_settings

Planning Domain
├── planning_objects
├── container_memberships
├── availability_rules
├── planning_rules
└── temporal_relations

Planning Process
├── planning_requests
├── proposals
└── proposal_items

Confirmed Schedule
├── schedule_versions
└── schedule_items
```

---

# 9.4 High-Level ERD

```text
                              +----------------+
                              |     users      |
                              +-------+--------+
                                      |
                    +-----------------+------------------+
                    |                 |                  |
                    v                 v                  v
           +----------------+ +----------------+ +----------------+
           | auth_sessions  | |  auth_tokens   | | user_settings  |
           +----------------+ +----------------+ +----------------+

                                      |
                                      |
                 +--------------------+--------------------+
                 |                    |                    |
                 v                    v                    v
       +------------------+ +-------------------+ +-------------------+
       | planning_requests | | planning_objects  | | availability_rules|
       +--------+---------+ +---------+---------+ +-------------------+
                |                     |
                |                     |
                |              +------+------+
                |              |             |
                |              v             v
                |      +----------------+ +-------------------+
                |      | container_     | | planning_rules   |
                |      | memberships    | +-------------------+
                |      +----------------+
                |
                |                     +-------------------+
                |                     | temporal_relations|
                |                     +-------------------+
                |
                v
       +-------------------+
       |     proposals     |
       +---------+---------+
                 |
                 v
       +-------------------+
       |  proposal_items   |
       +---------+---------+
                 |
                 |
                 v
       +-------------------+
       | schedule_versions |
       +---------+---------+
                 |
                 v
       +-------------------+
       |  schedule_items   |
       +-------------------+
```

---

# 9.5 Primary Key Convention

ทุก Table ใช้:

> `UUID`

เป็น Primary Key

รูปแบบ:

```text
id UUID PRIMARY KEY
```

เหตุผล:

* ลดการเดา ID
* รองรับ Distributed/External References ได้ดี
* เหมาะกับ API Resource Identifier
* แยก ID ระหว่าง Entity ได้ชัดเจน

---

# 9.6 Timestamp Convention

Timestamp ของ Backend ใช้:

> `TIMESTAMPTZ`

เพื่อรักษา Timezone-aware DateTime

เช่น:

```text
created_at
updated_at
deleted_at
expires_at
revoked_at
```

การแสดงผลใน Mobile สามารถแปลงเป็น Local Time ตาม User Timezone

---

# 9.7 User Timezone

User ต้องมี Timezone ที่ใช้สำหรับการตีความวันที่และเวลา

ตัวอย่าง:

```text
Asia/Bangkok
```

ควรใช้ IANA Time Zone Identifier

Timezone เป็นส่วนสำคัญต่อ:

* Relative Date
* Notification
* Recurring Availability
* Calendar
* Planning Horizon

---

# 9.8 Table 1 — users

## Purpose

เก็บข้อมูล Account และข้อมูลพื้นฐานของผู้ใช้

## Fields

| Field             | Type           | Null | Description            |
| ----------------- | -------------- | ---: | ---------------------- |
| id                | UUID           |   No | Primary Key            |
| email             | VARCHAR(320)   |   No | User Email             |
| password_hash     | TEXT           |   No | Argon2id Password Hash |
| display_name      | VARCHAR(100)   |  Yes | ชื่อแสดงผล             |
| timezone          | VARCHAR(64)    |   No | IANA Timezone          |
| status            | VARCHAR / ENUM |   No | Account Status         |
| email_verified_at | TIMESTAMPTZ    |  Yes | เวลายืนยัน Email       |
| created_at        | TIMESTAMPTZ    |   No | Creation Time          |
| updated_at        | TIMESTAMPTZ    |   No | Last Update            |

### Status

อย่างน้อย:

```text
ACTIVE
LOCKED
```

การลบบัญชีในอนาคตสามารถใช้ Soft Deletion Policy โดยไม่ต้องลบ Historical Schedule ที่จำเป็น

---

## Constraints

```text
PK(id)

UNIQUE(lower(email))
```

Email ต้องผ่าน Server-side Validation ก่อนบันทึก

---

# 9.9 Table 2 — auth_sessions

## Purpose

เก็บ Refresh Session ของ User แต่ละ Device/Session

## Fields

| Field               | Type        | Null | Description                   |
| ------------------- | ----------- | ---: | ----------------------------- |
| id                  | UUID        |   No | Primary Key                   |
| user_id             | UUID        |   No | FK → users                    |
| remember_me         | BOOLEAN     |   No | Remember Me State             |
| expires_at          | TIMESTAMPTZ |   No | Session Expiration            |
| absolute_expires_at | TIMESTAMPTZ |   No | Absolute Lifetime             |
| last_used_at        | TIMESTAMPTZ |  Yes | Last Refresh/Usage            |
| revoked_at          | TIMESTAMPTZ |  Yes | Revocation Time               |
| device_info         | JSONB       |  Yes | Non-sensitive Device Metadata |
| created_at          | TIMESTAMPTZ |   No | Creation Time                 |
| updated_at          | TIMESTAMPTZ |   No | Last Update                   |

## Relationship

```text
users 1 ──── N auth_sessions
```

## Security

ไม่ควรเก็บ Refresh Token แบบ Plain Text

กรณีจำเป็นต้องเก็บ Token Reference ให้เก็บเป็น:

> Hash

---

# 9.10 Table 3 — auth_tokens

## Purpose

เก็บ One-Time Authentication Tokens เช่น:

* Email Verification
* Password Reset

## Fields

| Field      | Type           | Null | Description                 |
| ---------- | -------------- | ---: | --------------------------- |
| id         | UUID           |   No | Primary Key                 |
| user_id    | UUID           |   No | FK → users                  |
| session_id | UUID           |  Yes | Optional FK → auth_sessions |
| token_type | VARCHAR / ENUM |   No | Token Purpose               |
| token_hash | TEXT           |   No | Hashed Token                |
| expires_at | TIMESTAMPTZ    |   No | Expiration                  |
| used_at    | TIMESTAMPTZ    |  Yes | Usage Time                  |
| created_at | TIMESTAMPTZ    |   No | Creation Time               |

## Token Types

```text
EMAIL_VERIFICATION
PASSWORD_RESET
```

## Rules

Token ที่:

```text
used_at IS NOT NULL
```

ถือว่าใช้ไปแล้วและไม่สามารถใช้ซ้ำได้

Token ที่:

```text
expires_at < now()
```

ถือว่าหมดอายุ

---

# 9.11 Table 4 — user_settings

## Purpose

รวม User-level Settings ที่เกี่ยวข้องกับ Planning และ Notification

ไม่สร้าง Table แยกสำหรับ:

```text
time_window_settings
notification_settings
```

ใน MVP

## Fields

| Field                 | Type        | Null | Description                         |
| --------------------- | ----------- | ---: | ----------------------------------- |
| user_id               | UUID        |   No | PK + FK → users                     |
| time_window_overrides | JSONB       |   No | User Semantic Time Window Overrides |
| notification_defaults | JSONB       |   No | Notification Defaults               |
| created_at            | TIMESTAMPTZ |   No | Creation Time                       |
| updated_at            | TIMESTAMPTZ |   No | Last Update                         |

## Relationship

```text
users 1 ──── 1 user_settings
```

---

# 9.12 time_window_overrides JSONB

Conceptual Structure:

```json
{
  "MORNING": {
    "start": "06:00",
    "end": "12:00"
  },
  "AFTERNOON": {
    "start": "12:00",
    "end": "17:00"
  }
}
```

ไม่จำเป็นต้องมีทุก Window

หากไม่มีค่า:

```text
User Override
= absent
```

ให้ Fallback เป็น System Default

---

# 9.13 notification_defaults JSONB

Conceptual Structure:

```json
{
  "date_only": {
    "time": "06:00"
  },
  "time_specific": {
    "before_start_minutes": 60
  }
}
```

ค่าจริงควรผ่าน Schema Validation ก่อน Persist

---

# 9.14 Table 5 — planning_objects

## Purpose

เป็น Table หลักของ Domain สำหรับเก็บ:

```text
ACTIVITY
CONTAINER
```

ไม่สร้าง `activities` และ `containers` แยกกันใน MVP

## Fields

| Field                 | Type           | Null | Description                             |
| --------------------- | -------------- | ---: | --------------------------------------- |
| id                    | UUID           |   No | Primary Key                             |
| user_id               | UUID           |   No | FK → users                              |
| object_type           | VARCHAR / ENUM |   No | ACTIVITY / CONTAINER                    |
| activity_type         | VARCHAR / ENUM |  Yes | TASK / EVENT / ...                      |
| title                 | VARCHAR(255)   |   No | ชื่อกิจกรรม                             |
| description           | TEXT           |  Yes | รายละเอียด                              |
| status                | VARCHAR / ENUM |   No | ACTIVE / COMPLETED / CANCELLED          |
| date_start            | DATE           |   No | Logical Date Start                      |
| date_end              | DATE           |  Yes | Logical Date End                        |
| time_mode             | VARCHAR / ENUM |   No | Temporal Representation                 |
| start_at              | TIMESTAMPTZ    |  Yes | Concrete Start                          |
| end_at                | TIMESTAMPTZ    |  Yes | Concrete End                            |
| semantic_window       | VARCHAR / ENUM |  Yes | Semantic Time Window                    |
| duration_minutes      | INTEGER        |  Yes | Duration                                |
| duration_qualifier    | VARCHAR / ENUM |  Yes | EXACT / APPROXIMATE                     |
| deadline_at           | TIMESTAMPTZ    |  Yes | Deadline                                |
| notification_override | JSONB          |  Yes | Activity-specific Notification Override |
| source_request_id     | UUID           |  Yes | FK → planning_requests                  |
| deleted_at            | TIMESTAMPTZ    |  Yes | Soft Delete                             |
| created_at            | TIMESTAMPTZ    |   No | Creation Time                           |
| updated_at            | TIMESTAMPTZ    |   No | Last Update                             |

---

# 9.15 object_type

Allowed:

```text
ACTIVITY
CONTAINER
```

---

# 9.16 activity_type

Allowed:

```text
TASK
EVENT
APPOINTMENT
MEETING
TRAVEL
OTHER
```

`activity_type` ต้องเป็น `NULL` เมื่อ:

```text
object_type = CONTAINER
```

และต้องไม่เป็น `NULL` เมื่อ:

```text
object_type = ACTIVITY
```

ตาม Schema Policy

---

# 9.17 time_mode

สามารถแทน Temporal State หลัก เช่น:

```text
DATE_ONLY
EXACT
RANGE
SEMANTIC_WINDOW
APPROXIMATE
```

อย่างไรก็ตาม Original User Meaning และ Structured AI Output ไม่ควรถูกตีความจาก Database Column เพียงอย่างเดียว หากข้อมูลดังกล่าวมี Metadata เพิ่มเติมที่จำเป็น

---

# 9.18 Date-Only Representation

Date-only Activity เช่น:

> “พรุ่งนี้ซื้อของขวัญให้แฟน”

ควรเก็บ:

```text
date_start = 2026-10-05
start_at = NULL
end_at = NULL
```

และ:

```text
time_mode = DATE_ONLY
```

Notification Time สามารถมีค่า 06:00 โดยไม่ทำให้ `start_at` กลายเป็น 06:00

---

# 9.19 Concrete Time Representation

Timed Activity เช่น:

```text
09:00–11:00
```

เก็บ:

```text
start_at = ...
end_at = ...
time_mode = RANGE
```

หากเป็น Fixed Exact Time สามารถระบุ:

```text
time_mode = EXACT
```

ตาม Domain Policy

---

# 9.20 planning_objects Constraints

อย่างน้อยต้องมี:

```text
CHECK (
  (start_at IS NULL AND end_at IS NULL)
  OR
  (start_at IS NOT NULL AND end_at IS NOT NULL)
)

CHECK (
  end_at IS NULL
  OR end_at > start_at
)

CHECK (
  duration_minutes IS NULL
  OR duration_minutes > 0
)

CHECK (
  date_end IS NULL
  OR date_end >= date_start
)
```

และ:

```text
CHECK (
  (object_type = 'ACTIVITY' AND activity_type IS NOT NULL)
  OR
  (object_type = 'CONTAINER' AND activity_type IS NULL)
)
```

Cross-field consistency เช่นความสอดคล้องของ `date_start` กับ `start_at` ต้องตรวจทั้ง Application Layer และ Database ตามความเหมาะสม

---

# 9.21 Soft Delete

`planning_objects.deleted_at` ใช้สำหรับ Storage Lifecycle

ไม่ควรนำไปปะปนกับ:

```text
ACTIVE
COMPLETED
CANCELLED
```

ดังนั้น:

```text
Business Status
≠
Storage Deletion State
```

---

# 9.22 Table 6 — container_memberships

## Purpose

เก็บ Structural Relationship ระหว่าง:

```text
Container
↓
Child Activity
```

## Fields

| Field               | Type        | Null | Description           |
| ------------------- | ----------- | ---: | --------------------- |
| id                  | UUID        |   No | Primary Key           |
| container_object_id | UUID        |   No | FK → planning_objects |
| child_object_id     | UUID        |   No | FK → planning_objects |
| created_at          | TIMESTAMPTZ |   No | Creation Time         |

## Constraints

```text
UNIQUE(container_object_id, child_object_id)

CHECK(container_object_id <> child_object_id)
```

และ Application/Domain Layer ต้องตรวจ:

```text
container_object.object_type = CONTAINER
child_object.object_type = ACTIVITY
```

---

# 9.23 Membership Semantics

Membership หมายถึง:

> Child Activity อยู่ภายใน Container

ไม่ควรสร้าง:

```text
temporal_relations
CONTAINS
WITHIN
```

ซ้ำอีกชุดสำหรับความสัมพันธ์เดียวกัน

ดังนั้น:

```text
container_memberships
= Structural Relationship

temporal_relations
= Generic Temporal Relationship
```

---

# 9.24 Table 7 — availability_rules

## Purpose

เก็บทั้ง:

```text
AVAILABLE
UNAVAILABLE
```

และรองรับ:

```text
ONE_TIME
RECURRING
```

ใน Table เดียว

## Fields

| Field           | Type           | Null | Description             |
| --------------- | -------------- | ---: | ----------------------- |
| id              | UUID           |   No | Primary Key             |
| user_id         | UUID           |   No | FK → users              |
| kind            | VARCHAR / ENUM |   No | AVAILABLE / UNAVAILABLE |
| recurrence_type | VARCHAR / ENUM |   No | ONE_TIME / RECURRING    |
| date_start      | DATE           |   No | Start Date              |
| date_end        | DATE           |  Yes | End Date                |
| days_of_week    | SMALLINT[]     |  Yes | Recurring Days          |
| start_time      | TIME           |   No | Window Start            |
| end_time        | TIME           |   No | Window End              |
| timezone        | VARCHAR(64)    |   No | Timezone Context        |
| created_at      | TIMESTAMPTZ    |   No | Creation Time           |
| updated_at      | TIMESTAMPTZ    |   No | Last Update             |

---

# 9.25 One-Time Rule

ตัวอย่าง:

> พรุ่งนี้ 10:00–12:00 ว่าง

```text
recurrence_type = ONE_TIME
date_start = tomorrow
date_end = tomorrow
days_of_week = NULL
```

---

# 9.26 Recurring Rule

ตัวอย่าง:

> จันทร์–ศุกร์ 08:00–17:00

```text
recurrence_type = RECURRING
days_of_week = [1,2,3,4,5]
start_time = 08:00
end_time = 17:00
```

รูปแบบตัวเลขของวันต้องถูกกำหนดเป็น Canonical Convention เดียวกันทั้งระบบ

---

# 9.27 Availability Rule Semantics

```text
kind = AVAILABLE
```

หมายถึง:

> Planner สามารถวาง Activity ในช่วงดังกล่าวได้

ขณะที่:

```text
kind = UNAVAILABLE
```

หมายถึง:

> Planner ห้ามวาง Activity ในช่วงดังกล่าว

---

# 9.28 availability_rules Validation

อย่างน้อย:

```text
kind IN ('AVAILABLE', 'UNAVAILABLE')

recurrence_type IN ('ONE_TIME', 'RECURRING')
```

สำหรับ:

```text
ONE_TIME
```

ต้องมี Date ที่ชัดเจน

สำหรับ:

```text
RECURRING
```

ต้องมี Recurrence Specification ที่ใช้ได้

รายละเอียด Cross-Midnight Validation ต้องทำที่ Domain/Application Layer เนื่องจาก Window สามารถคร่อมวันได้

---

# 9.29 Table 8 — planning_rules

## Purpose

เก็บ:

```text
HARD
PREFERENCE
```

ใน Table เดียว

เพื่อให้ Constraint และ Preference สามารถใช้ Domain Model ร่วมกัน

## Fields

| Field              | Type           | Null | Description            |
| ------------------ | -------------- | ---: | ---------------------- |
| id                 | UUID           |   No | Primary Key            |
| user_id            | UUID           |   No | FK → users             |
| planning_object_id | UUID           |  Yes | FK → planning_objects  |
| rule_kind          | VARCHAR / ENUM |   No | HARD / PREFERENCE      |
| rule_type          | VARCHAR / ENUM |   No | Rule Type              |
| priority           | INTEGER        |  Yes | Relative Rule Priority |
| parameters         | JSONB          |   No | Rule Parameters        |
| created_at         | TIMESTAMPTZ    |   No | Creation Time          |
| updated_at         | TIMESTAMPTZ    |   No | Last Update            |

`planning_object_id = NULL` สามารถใช้สำหรับ User-level Rule ที่ไม่ได้ผูกกับ Activity เดียว

---

# 9.30 Rule Types

อย่างน้อยรองรับแนวคิด:

```text
FIXED_TIME
EARLIEST_START
LATEST_START
TIME_WINDOW
DEADLINE
DURATION
AVAILABILITY
UNAVAILABILITY
PRECEDENCE
NO_OVERLAP
CONTAINER_CONTAINMENT
REQUIRED
OPTIONAL

PREFERRED_TIME_WINDOW
PREFERRED_ORDER
REST_GAP
OTHER_PREFERENCE
```

ไม่ได้หมายความว่าทุก Rule จะมี `rule_type` ที่ Planner ใช้ตรง ๆ เสมอไป บาง Rule สามารถ Normalize เป็น Canonical Constraint ก่อนสร้าง CP-SAT Model

---

# 9.31 parameters JSONB

ตัวอย่าง:

```json
{
  "window": "AFTERNOON"
}
```

หรือ:

```json
{
  "deadline": "2026-10-10T23:59:00+07:00"
}
```

หรือ:

```json
{
  "minimum_gap_minutes": 60
}
```

JSONB เหมาะกับ Rule ที่มี Parameters แตกต่างกัน แต่ต้องผ่าน Schema Validation ก่อนนำไปใช้

---

# 9.32 Rule Ownership

แม้ `planning_object_id` จะชี้ไปยัง User-owned Object แต่ `user_id` ใน Rule ยังถูกเก็บไว้เพื่อ:

* Ownership Check
* Query Efficiency
* Data Isolation
* Authorization

Application ต้องตรวจให้:

```text
planning_rules.user_id
==
planning_objects.user_id
```

เมื่อมี Object Reference

---

# 9.33 Table 9 — temporal_relations

## Purpose

เก็บ Temporal Relations ระหว่าง Planning Objects

## Fields

| Field          | Type           | Null | Description                |
| -------------- | -------------- | ---: | -------------------------- |
| id             | UUID           |   No | Primary Key                |
| user_id        | UUID           |   No | FK → users                 |
| from_object_id | UUID           |   No | FK → planning_objects      |
| to_object_id   | UUID           |   No | FK → planning_objects      |
| relation_type  | VARCHAR / ENUM |   No | BEFORE / AFTER / OVERLAP   |
| parameters     | JSONB          |  Yes | Optional Relation Metadata |
| created_at     | TIMESTAMPTZ    |   No | Creation Time              |

---

# 9.34 Temporal Relation Constraints

```text
CHECK(from_object_id <> to_object_id)

UNIQUE(
  from_object_id,
  to_object_id,
  relation_type
)
```

Relation Type:

```text
BEFORE
AFTER
OVERLAP
```

---

# 9.35 Canonical Relation

เพื่อให้ Planning Model ง่ายขึ้น:

```text
AFTER
```

สามารถ Normalize เป็น:

```text
BEFORE
```

โดยสลับ Source / Target

ตัวอย่าง:

```text
A AFTER B
```

สามารถ Normalize เป็น:

```text
B BEFORE A
```

Database สามารถเก็บความหมายที่ User ระบุ แต่ Planning Representation สามารถใช้ Canonical Relation ได้

---

# 9.36 OVERLAP Relation

`OVERLAP` เป็น Semantic Relation

ไม่ควรถูกตีความว่า:

> Activities สามารถทำพร้อมกันได้

การสร้าง No-Overlap เป็นหน้าที่ของ Planning Engine

---

# 9.37 Table 10 — planning_requests

## Purpose

เก็บคำขอที่ส่งเข้าสู่ Planning Workflow และใช้เป็น Trace สำหรับ AI / Planning / Replanning

## Fields

| Field              | Type           | Null | Description                                              |
| ------------------ | -------------- | ---: | -------------------------------------------------------- |
| id                 | UUID           |   No | Primary Key                                              |
| user_id            | UUID           |   No | FK → users                                               |
| parent_request_id  | UUID           |  Yes | FK → planning_requests                                   |
| request_type       | VARCHAR / ENUM |   No | INITIAL / REPLANNING / FEEDBACK / CLARIFICATION_RESPONSE |
| status             | VARCHAR / ENUM |   No | Request Lifecycle                                        |
| input_text         | TEXT           |   No | User Input                                               |
| reference_time     | TIMESTAMPTZ    |   No | Reference Date/Time                                      |
| planning_start     | TIMESTAMPTZ    |  Yes | Planning Range Start                                     |
| planning_end       | TIMESTAMPTZ    |  Yes | Planning Range End                                       |
| processing_time_ms | BIGINT         |  Yes | Processing Duration                                      |
| error_code         | VARCHAR(100)   |  Yes | Internal/Domain Error                                    |
| error_message      | TEXT           |  Yes | Non-sensitive Error Information                          |
| metadata           | JSONB          |  Yes | Diagnostics / Additional Metadata                        |
| created_at         | TIMESTAMPTZ    |   No | Creation Time                                            |
| updated_at         | TIMESTAMPTZ    |   No | Last Update                                              |

---

# 9.38 Request Lifecycle

```text
RECEIVED
   ↓
PROCESSING
   ├── NEEDS_CLARIFICATION
   │       ↓
   │   PROCESSING
   ├── COMPLETED
   └── FAILED
```

Status เป็น Application State และต้องเปลี่ยนตาม State Machine

---

# 9.39 parent_request_id

ใช้สำหรับ Clarification Flow:

```text
Request A
   ↓
NEEDS_CLARIFICATION
   ↓
User Response
   ↓
Request B
parent_request_id = Request A
```

ทำให้สามารถ Trace ว่าคำตอบของ User เกี่ยวข้องกับ Planning Request ใด

ไม่จำเป็นต้องสร้าง `clarifications` Table แยกใน MVP

---

# 9.40 planning_start / planning_end

สอง Field นี้ใช้ระบุ:

> Planning Range ที่ Operation นี้ตั้งใจให้ Planner พิจารณา

ไม่ใช่:

> Calendar Data Range

และไม่ใช่:

> Activity Date Range

---

# 9.41 Table 11 — proposals

## Purpose

เก็บผลลัพธ์ที่ส่งให้ User Review ก่อนเปลี่ยน Confirmed Schedule

## Fields

| Field                      | Type           | Null | Description            |
| -------------------------- | -------------- | ---: | ---------------------- |
| id                         | UUID           |   No | Primary Key            |
| user_id                    | UUID           |   No | FK → users             |
| planning_request_id        | UUID           |   No | FK → planning_requests |
| source_schedule_version_id | UUID           |  Yes | FK → schedule_versions |
| status                     | VARCHAR / ENUM |   No | Proposal Lifecycle     |
| candidate_count            | SMALLINT       |   No | 1–3                    |
| selected_plan_key          | CHAR(1)        |  Yes | Selected Candidate     |
| metadata                   | JSONB          |  Yes | Metrics / Diagnostics  |
| created_at                 | TIMESTAMPTZ    |   No | Creation Time          |
| reviewed_at                | TIMESTAMPTZ    |  Yes | Review Time            |
| confirmed_at               | TIMESTAMPTZ    |  Yes | Confirmation Time      |
| invalidated_at             | TIMESTAMPTZ    |  Yes | Invalidation Time      |

---

# 9.42 Proposal Status

ใช้:

```text
PENDING
CONFIRMED
REJECTED
INVALIDATED
```

ไม่มี:

```text
EXPIRED
```

ตาม Design Freeze

---

# 9.43 source_schedule_version_id

Field นี้ใช้สำหรับ Replanning / Stale Proposal Protection

ตัวอย่าง:

```text
Current Schedule = V3

Proposal P
source_schedule_version_id = V3
```

เมื่อ Current กลายเป็น V4:

```text
P.source = V3
Current = V4
```

Proposal P ถือว่า Stale

Initial Planning ที่ไม่มี Existing Confirmed Schedule สามารถมีค่า:

```text
NULL
```

---

# 9.44 Candidate Count

ต้อง:

```text
1 ≤ candidate_count ≤ 3
```

Candidate Count ไม่ได้หมายความว่า Proposal ต้องมี Candidate 3 ชุด

---

# 9.45 selected_plan_key

ก่อน Confirm:

```text
NULL
```

เมื่อ User เลือก Candidate:

```text
A
B
หรือ
C
```

ต้องสอดคล้องกับ Candidate ที่มีอยู่จริง

Cross-table Validation นี้เป็น Application Transaction Rule มากกว่า Database CHECK เพียงอย่างเดียว

---

# 9.46 Table 12 — proposal_items

## Purpose

เก็บ Schedule Placement ของแต่ละ Candidate ภายใน Proposal

Concept:

```text
Proposal
├── Plan A
│   ├── Activity A
│   ├── Activity B
│   └── Activity C
├── Plan B
│   ├── Activity A
│   └── Activity C
└── Plan C
    └── ...
```

## Fields

| Field              | Type        | Null | Description                 |
| ------------------ | ----------- | ---: | --------------------------- |
| id                 | UUID        |   No | Primary Key                 |
| proposal_id        | UUID        |   No | FK → proposals              |
| plan_key           | CHAR(1)     |   No | A / B / C                   |
| planning_object_id | UUID        |   No | FK → planning_objects       |
| start_at           | TIMESTAMPTZ |   No | Proposed Start              |
| end_at             | TIMESTAMPTZ |   No | Proposed End                |
| metadata           | JSONB       |  Yes | Optional Placement Metadata |
| created_at         | TIMESTAMPTZ |   No | Creation Time               |

---

# 9.47 proposal_items Constraints

```text
UNIQUE(
  proposal_id,
  plan_key,
  planning_object_id
)

CHECK(plan_key IN ('A', 'B', 'C'))

CHECK(end_at > start_at)
```

Candidate ที่ไม่ Schedule Optional Activity สามารถไม่มี `proposal_item` สำหรับ Activity นั้น

---

# 9.48 Candidate vs Proposal in Database

Database แยก:

```text
proposals
= Proposal Container

proposal_items
= Candidate Schedule Placements
```

ดังนั้นไม่ต้องสร้าง:

```text
candidate_plans
```

เป็น Table แยก

เหตุผลคือ Candidate มี Life Cycle แค่ภายใน Proposal

---

# 9.49 Table 13 — schedule_versions

## Purpose

เก็บ Immutable Snapshot ของ Confirmed Schedule

## Fields

| Field               | Type           | Null | Description            |
| ------------------- | -------------- | ---: | ---------------------- |
| id                  | UUID           |   No | Primary Key            |
| user_id             | UUID           |   No | FK → users             |
| version_number      | BIGINT         |   No | Version Number         |
| is_current          | BOOLEAN        |   No | Current Version Flag   |
| confirmation_source | VARCHAR / ENUM |   No | PROPOSAL / MANUAL      |
| source_request_id   | UUID           |  Yes | FK → planning_requests |
| created_at          | TIMESTAMPTZ    |   No | Version Creation Time  |

---

# 9.50 Schedule Version Uniqueness

ต้องมี:

```text
UNIQUE(user_id, version_number)
```

และ:

```text
UNIQUE(user_id)
WHERE is_current = TRUE
```

ทำให้ User หนึ่งคนมี Current Schedule Version ได้เพียงหนึ่ง Version

---

# 9.51 Schedule Version Immutability

หลังจาก Version ถูก Commit แล้ว:

```text
version_number
created_at
confirmation_source
source_request_id
```

ไม่ควรถูกแก้

และ `schedule_items` ที่อยู่ภายใต้ Version นั้นต้องไม่ถูก Update/Delete ใน Normal Business Flow

---

# 9.52 Current Schedule

ไม่สร้าง:

```text
current_schedules
```

Table

แต่ใช้:

```text
schedule_versions.is_current = TRUE
```

เป็นตัวระบุ Current Version

ตัวอย่าง:

```text
V1  is_current = FALSE
V2  is_current = FALSE
V3  is_current = TRUE
```

---

# 9.53 Table 14 — schedule_items

## Purpose

เก็บ Placement ของ Planning Object ภายใน Confirmed Schedule Version

## Fields

| Field               | Type        | Null | Description                 |
| ------------------- | ----------- | ---: | --------------------------- |
| id                  | UUID        |   No | Primary Key                 |
| schedule_version_id | UUID        |   No | FK → schedule_versions      |
| planning_object_id  | UUID        |   No | FK → planning_objects       |
| start_at            | TIMESTAMPTZ |   No | Confirmed Start             |
| end_at              | TIMESTAMPTZ |   No | Confirmed End               |
| metadata            | JSONB       |  Yes | Optional Placement Metadata |
| created_at          | TIMESTAMPTZ |   No | Creation Time               |

---

# 9.54 schedule_items Constraints

```text
UNIQUE(
  schedule_version_id,
  planning_object_id
)

CHECK(end_at > start_at)
```

Schedule Item เป็น Placement ของ Object ใน Version

ดังนั้น:

```text
planning_object
≠
schedule_item
```

---

# 9.55 Date-Only Activity in Schedule

Date-only Activity สามารถอยู่ใน Calendar ได้โดยไม่ต้องมี `schedule_item` ที่มี Start/End Time

กล่าวคือ:

```text
planning_object
date_start = known
start_at = NULL
```

สามารถแสดงใน:

```text
All Day / Unscheduled
```

แทนการสร้าง Fake Schedule Item เช่น:

```text
06:00–07:00
```

เพียงเพราะ Notification ถูกตั้งไว้ 06:00

---

# 9.56 Notification Data Is Not Stored

Database ไม่มี:

```text
notification_instances
```

และไม่มี:

```text
local_notification_id
```

เพราะ Local Notification Identifier เป็น Device-side State

Backend เก็บเพียง:

```text
Schedule
+
Notification Default
+
Activity Override
```

Mobile จัดการ:

```text
Schedule Item ID
→ Local Notification ID
```

---

# 9.57 Relationship Cardinality

## users

```text
users 1 ──── N auth_sessions
users 1 ──── N auth_tokens
users 1 ──── 1 user_settings

users 1 ──── N planning_objects
users 1 ──── N availability_rules
users 1 ──── N planning_rules
users 1 ──── N temporal_relations
users 1 ──── N planning_requests
users 1 ──── N proposals
users 1 ──── N schedule_versions
```

## Planning Objects

```text
planning_requests 1 ──── N planning_objects

planning_objects
      N
      │
      ├──── container_memberships ──── N
      │
      ├──── planning_rules ─────────── N
      │
      └──── temporal_relations ─────── N
```

## Proposal

```text
planning_requests 1 ──── N proposals

proposals 1 ──── N proposal_items
```

## Schedule

```text
schedule_versions 1 ──── N schedule_items
```

---

# 9.58 Foreign Key Policy

Foreign Keys ต้องใช้เพื่อรักษา Referential Integrity

ตัวอย่าง:

```text
planning_objects.user_id
    → users.id
```

```text
proposals.planning_request_id
    → planning_requests.id
```

```text
proposal_items.proposal_id
    → proposals.id
```

```text
schedule_items.schedule_version_id
    → schedule_versions.id
```

---

# 9.59 ON DELETE Policy

ไม่ควรใช้:

```text
ON DELETE CASCADE
```

แบบกว้าง ๆ กับ Historical Schedule Data

โดยเฉพาะ:

```text
schedule_versions
schedule_items
proposals
proposal_items
```

เพราะอาจทำให้ Historical Records สูญหาย

สำหรับ Planning Objects ที่มี Historical Reference ควรใช้:

```text
Soft Delete
```

แทน Hard Delete

---

# 9.60 Planning Object Ownership

การ Query Planning Object ต้องมีเงื่อนไข:

```text
WHERE planning_objects.user_id = authenticated_user_id
```

เสมอสำหรับ User-facing Operations

ไม่อนุญาตให้ Client ระบุ Owner แล้ว Server เชื่อข้อมูลนั้นโดยตรง

---

# 9.61 Cross-Entity Ownership

เมื่อ Object A เชื่อมกับ Object B ผ่าน:

```text
container_memberships
planning_rules
temporal_relations
```

ระบบต้องตรวจว่า Objects ทั้งหมดเป็นของ User เดียวกัน

ตัวอย่าง:

```text
Container.user_id
==
Child.user_id
```

ห้ามสร้าง Cross-user Relationship

---

# 9.62 Database Constraints Summary

Constraints สำคัญที่ต้องมี:

### User

```text
UNIQUE(lower(email))
```

### User Settings

```text
UNIQUE(user_id)
```

### Planning Objects

```text
date_end >= date_start
end_at > start_at
duration_minutes > 0
object/activity consistency
```

### Container Membership

```text
container != child
UNIQUE(container, child)
```

### Temporal Relations

```text
from != to
UNIQUE(from, to, relation)
```

### Proposals

```text
candidate_count BETWEEN 1 AND 3
```

### Proposal Items

```text
plan_key IN A/B/C
UNIQUE(proposal, plan_key, object)
end_at > start_at
```

### Schedule Versions

```text
UNIQUE(user, version_number)
UNIQUE(user) WHERE is_current = TRUE
```

### Schedule Items

```text
UNIQUE(version, object)
end_at > start_at
```

---

# 9.63 Index Strategy

Index ต้องสร้างตาม Query Pattern ไม่ใช่สร้างทุก Column

## users

```text
UNIQUE INDEX lower(email)
```

## auth_sessions

```text
INDEX(user_id)
INDEX(user_id, revoked_at)
INDEX(expires_at)
```

## auth_tokens

```text
UNIQUE(token_hash)
INDEX(user_id, token_type)
INDEX(expires_at)
```

## planning_objects

```text
INDEX(user_id)
INDEX(user_id, status)
INDEX(user_id, date_start)
INDEX(user_id, date_start, date_end)
INDEX(source_request_id)
```

สำหรับ Soft Delete สามารถใช้ Partial Index ที่:

```text
WHERE deleted_at IS NULL
```

เมื่อ Query ส่วนใหญ่ต้องการ Active Objects

---

# 9.64 Availability Index

```text
INDEX(user_id, kind)
INDEX(user_id, recurrence_type)
INDEX(user_id, date_start)
```

---

# 9.65 Planning Rules Index

```text
INDEX(user_id, rule_kind)
INDEX(user_id, planning_object_id)
INDEX(planning_object_id, rule_type)
```

---

# 9.66 Temporal Relation Index

```text
INDEX(from_object_id)
INDEX(to_object_id)
INDEX(user_id)
```

เพื่อรองรับ Dependency / Impact Analysis

---

# 9.67 Planning Request Index

```text
INDEX(user_id, created_at)
INDEX(user_id, status)
INDEX(parent_request_id)
INDEX(user_id, request_type)
```

---

# 9.68 Proposal Index

```text
INDEX(user_id, status)
INDEX(planning_request_id)
INDEX(source_schedule_version_id)
```

---

# 9.69 Proposal Items Index

```text
INDEX(proposal_id, plan_key)
INDEX(planning_object_id)
```

Unique Constraint:

```text
(proposal_id, plan_key, planning_object_id)
```

ทำหน้าที่เป็นทั้ง Integrity และ Index

---

# 9.70 Schedule Version Index

```text
INDEX(user_id, created_at)
INDEX(user_id, is_current)
UNIQUE(user_id, version_number)
```

Partial Unique:

```text
UNIQUE(user_id)
WHERE is_current = TRUE
```

---

# 9.71 Schedule Items Index

```text
INDEX(schedule_version_id)
INDEX(planning_object_id)
INDEX(schedule_version_id, start_at)
```

เพื่อรองรับ Calendar Query

---

# 9.72 Calendar Query Pattern

Calendar Current View สามารถ Query:

```text
Current Schedule Version
        ↓
Schedule Items
        ↓
Start / End Range
```

Conceptually:

```text
SELECT schedule_items
FROM current_schedule_version
WHERE start_at < range_end
  AND end_at > range_start
```

พร้อมดึง Date-only Planning Objects ที่เกี่ยวข้องแยกต่างหาก

---

# 9.73 Current Schedule Query

ไม่ต้อง Query ทุก Version

Flow:

```text
users
 ↓
schedule_versions
WHERE is_current = TRUE
 ↓
schedule_items
```

---

# 9.74 Planning Object Query

Planning Engine ไม่ควร:

```text
SELECT * FROM planning_objects
```

ทั้ง Database

แต่ควรเลือก:

```text
Relevant User
+
Relevant Date / Horizon
+
Relevant Status
+
Related Constraints
```

ตาม Planning Context

---

# 9.75 Replanning Data Selection

Replanning ต้องดึง:

```text
Current Schedule
+
Affected Planning Objects
+
Related Constraints
+
Temporal Relations
+
Availability / Unavailability
+
New Planning Request
```

ไม่จำเป็นต้องอ่านข้อมูลทั้งหมด

---

# 9.76 Historical Data

Historical Data ที่ต้องรักษา:

```text
Planning Objects
Historical Schedule Versions
Historical Proposal Information
Planning Requests
```

โดยเฉพาะ Schedule Version ไม่ควรถูกแก้เพื่อสะท้อน Current State

---

# 9.77 Version Example

สมมติ:

```text
V1
Study = 14:00–16:00
```

ต่อมา Replanning แล้ว User Confirm:

```text
V2
Study = 16:00–18:00
```

Database:

```text
schedule_versions
V1 is_current = FALSE
V2 is_current = TRUE
```

และ:

```text
schedule_items

V1 → Study 14:00–16:00
V2 → Study 16:00–18:00
```

V1 ไม่ถูก Update เป็น 16:00–18:00

---

# 9.78 Stale Proposal Verification

เมื่อ User Confirm Proposal:

ระบบต้องตรวจ:

```text
Proposal.source_schedule_version_id
==
Current Schedule Version ID
```

ถ้า:

```text
NULL
```

กรณี Initial Planning สามารถ Confirm ได้ตาม Policy

ถ้าไม่ตรง:

```text
STALE_PROPOSAL
```

และห้ามสร้าง New Schedule Version จาก Proposal นั้น

---

# 9.79 Confirmation Transaction

Proposal Confirmation ควรเขียน Database ภายใน Transaction เดียว:

```text
BEGIN
    ↓
Validate Proposal State
    ↓
Validate Source Schedule Version
    ↓
Determine Selected Candidate
    ↓
Create New Schedule Version
    ↓
Create Schedule Items
    ↓
Update Proposal = CONFIRMED
    ↓
Set New Version = CURRENT
    ↓
Set Old Version = NOT CURRENT
    ↓
COMMIT
```

Local Notification ไม่อยู่ใน Transaction นี้

---

# 9.80 Manual Confirmation Transaction

สำหรับ Draft:

```text
BEGIN
    ↓
Validate Draft
    ↓
Create New Schedule Version
    ↓
Create Schedule Items
    ↓
Set New Version = CURRENT
    ↓
COMMIT
```

Draft เองไม่ถูก Persist เป็น Table ใน MVP

---

# 9.81 Current Version Update

ใน Transaction เดียวกันต้องป้องกันไม่ให้เกิด:

```text
0 Current Versions
```

หรือ:

```text
2 Current Versions
```

Database Partial Unique Index ช่วยป้องกันกรณี:

```text
2 × is_current = TRUE
```

แต่ Application Transaction ต้องจัดการ State Transition ให้ถูกต้องด้วย

---

# 9.82 Proposal Confirmation Race

ถ้ามี Request สองรายการพยายาม Confirm Proposal พร้อมกัน:

```text
Request A
Request B
```

ต้องมี Concurrency Control เช่น:

* Transaction Isolation
* Row Lock
* Version Check

เพื่อไม่ให้สร้าง Schedule Version ซ้ำจาก Confirmation เดียวกัน

การเลือกวิธี Implementation เป็น Technical Detail แต่ผลลัพธ์ต้องรักษา:

```text
One valid confirmation
→ One new current version
```

---

# 9.83 Idempotency

Operations ที่มี Side Effect สำคัญ เช่น:

```text
Planning Request
Proposal Confirmation
Manual Schedule Confirmation
```

ควรรองรับ:

> `Idempotency-Key`

โดยรายละเอียดของ Idempotency Storage สามารถอยู่ใน Application/Infrastructure Layer และไม่จำเป็นต้องเพิ่ม Table ลงใน 14-table Domain Schema หาก Implementation สามารถใช้กลไกอื่นที่ปลอดภัยได้

---

# 9.84 JSONB Usage Policy

JSONB ใช้กับข้อมูลที่:

* Parameters มีหลายรูปแบบ
* Diagnostics
* Metadata
* Provider-specific Data
* Notification Override
* User Settings

แต่ไม่ควรใช้ JSONB แทน Field หลักที่ต้อง:

* Query บ่อย
* Index
* Join
* Constraint
* Ownership Check

ตัวอย่าง:

```text
title
status
user_id
start_at
end_at
```

ควรเป็น Typed Column

ไม่ควรเก็บรวมใน:

```text
metadata JSONB
```

---

# 9.85 Core Data vs Metadata

ตัวอย่าง:

### Core

```text
proposal.status
proposal.candidate_count
schedule_version.version_number
schedule_item.start_at
planning_object.status
```

ต้องเป็น Typed Column

### Metadata

```text
solver diagnostics
AI provider metadata
benchmark information
debug information
```

สามารถใช้:

```text
JSONB
```

ได้

---

# 9.86 What Is Not Stored in Database

ใน MVP ไม่สร้าง Tables สำหรับ:

```text
candidate_plans
clarifications
planning_modifications
ai_processing_records
notification_instances
current_schedules
separate_time_window_settings
separate_notification_settings
```

เหตุผล:

### candidate_plans

Candidate อยู่ภายใน Proposal → `proposal_items`

### clarifications

Clarification เป็น State ของ Planning Request → `planning_requests.parent_request_id`

### planning_modifications

Application/Planning Process State ไม่จำเป็นต้อง Persist ทุก Intermediate Step

### ai_processing_records

ไม่จำเป็นต่อ Core Domain MVP

### notification_instances

Device-side Local Notification State

### current_schedules

Current = `schedule_versions.is_current`

### settings

รวมอยู่ใน `user_settings`

---

# 9.87 Database and AI Boundary

AI Provider ไม่สามารถเข้าถึง PostgreSQL โดยตรง

Flow:

```text
Mobile
 ↓
Backend
 ↓
AI / NLP
 ↓
Structured Output
 ↓
Validation
 ↓
Database / Planning
```

AI ไม่มี Database Credentials

---

# 9.88 Database and Planning Boundary

Planning Engine ไม่ควร Query Database โดยกระจาย SQL ไปทั่ว Solver Logic

Flow:

```text
Database
 ↓
Repository / Data Access
 ↓
Application / Domain Mapping
 ↓
Planning Representation
 ↓
Planning Core
```

Planner รับ Structured Planning Representation

---

# 9.89 Database and Notification Boundary

Database:

```text
Confirmed Schedule
Notification Policy
Notification Override
```

Mobile:

```text
Local Notification ID
Scheduled Local Notification
Permission / Device State
```

จึงไม่มี Persistence Contract สำหรับ Device Notification Instance ใน MVP

---

# 9.90 Soft Delete Policy

สำหรับ `planning_objects`:

```text
deleted_at = NULL
```

หมายถึง Active Storage Record

หาก:

```text
deleted_at IS NOT NULL
```

ถือว่า Soft Deleted

Historical Schedule Version ที่อ้างถึง Object ดังกล่าวยังคงอ่านได้

---

# 9.91 Completed / Cancelled vs Deleted

สามสถานะนี้ต่างกัน:

```text
COMPLETED
= Business Activity เสร็จแล้ว

CANCELLED
= User ยกเลิก Activity

DELETED
= Storage Record ถูก Soft Delete
```

ห้ามใช้แทนกัน

---

# 9.92 Database Migration Structure

MVP ใช้ Alembic และแบ่ง Migration เป็น 9 Revisions ตามลำดับ Dependency:

### Revision 1 — Users

```text
users
```

### Revision 2 — Authentication

```text
auth_sessions
auth_tokens
```

### Revision 3 — User Settings

```text
user_settings
```

### Revision 4 — Planning Requests

```text
planning_requests
```

รวม:

```text
parent_request_id
planning_start
planning_end
processing_time_ms
```

### Revision 5 — Planning Objects

```text
planning_objects
```

รวม:

```text
source_request_id
```

### Revision 6 — Planning Relations

```text
container_memberships
availability_rules
planning_rules
temporal_relations
```

### Revision 7 — Proposals

```text
proposals
proposal_items
```

อาจสร้าง `source_schedule_version_id` เป็น Nullable Column ก่อน โดยยังไม่สร้าง Foreign Key ถ้า Schedule Table ยังไม่มี

### Revision 8 — Schedule

```text
schedule_versions
schedule_items
```

### Revision 9 — Final Constraints / Cross-References / Indexes

เพิ่ม:

```text
proposals.source_schedule_version_id
→ schedule_versions.id
```

พร้อม:

* Partial Current Version Unique Index
* Final CHECK Constraints
* Cross-table Foreign Keys
* Performance Indexes

แนวทางนี้หลีกเลี่ยง Circular/Dependency Problem ใน Migration Order

---

# 9.93 Migration Principles

ทุก Migration ต้อง:

1. Reversible เมื่อเหมาะสม
2. ไม่ทำลาย Historical Data
3. ตรวจสอบ Referential Integrity
4. ทำงานตาม Dependency Order
5. แยก Schema Change ออกจาก Data Migration เมื่อเป็นไปได้

---

# 9.94 Seed Data

System-level Default Data เช่น Semantic Time Windows สามารถกำหนดผ่าน:

* Application Configuration
* Version-controlled Seed / Migration Data

แต่ User Override ต้องอยู่ใน:

```text
user_settings
```

ไม่ควร Copy System Default ทุกค่าเข้า User Row หากไม่จำเป็น

---

# 9.95 System Default vs User Override in Database

ตัวอย่าง:

System:

```text
AFTERNOON = 13:00–16:00
```

User ไม่มี Override:

```text
user_settings.time_window_overrides
= {}
```

Application:

```text
use System Default
```

User Override:

```text
AFTERNOON = 12:00–17:00
```

Application:

```text
use User Override
```

Database จึงเก็บเฉพาะ Override ที่ User กำหนด

---

# 9.96 Notification Default Storage

System Default เช่น:

```text
Date-only = 06:00
Time-specific = 60 min
```

ไม่จำเป็นต้องสร้าง Row ต่อ User สำหรับทุกค่า

User Settings เก็บเฉพาะค่าที่ User Override

Application Resolution:

```text
Activity Override
      ↓
if absent
      ↓
User Default Override
      ↓
if absent
      ↓
System Default
```

---

# 9.97 Database Integrity for Notification

Database ต้องสามารถตรวจว่า:

```text
notification_override
```

มี Schema ถูกต้องในระดับ Application

แต่การตัดสินว่า Notification Time Valid หรือไม่ เช่น:

```text
notification <= activity_start
```

ควร Validate ใน Application/Domain Layer เนื่องจากข้อมูลอาจอยู่คนละ Entity/Policy

---

# 9.98 Database Integrity for Planning

Database สามารถตรวจได้:

```text
end > start
duration > 0
date_end >= date_start
```

แต่ไม่ควรพยายามใส่ CP-SAT Logic ลง Database Constraint

ตัวอย่าง:

```text
“Activity ห้าม overlap”
```

ไม่ควรแก้ด้วย PostgreSQL CHECK Constraint

เพราะเป็น Scheduling Rule ที่ต้องประเมินข้ามหลาย Rows และขึ้นกับ Domain Context

---

# 9.99 Database Responsibility vs Application Responsibility

| Rule                         |      DB | Application |
| ---------------------------- | ------: | ----------: |
| UUID PK                      |       ✅ |             |
| FK Integrity                 |       ✅ |             |
| Unique Email                 |       ✅ |           ✅ |
| start < end                  |       ✅ |           ✅ |
| duration > 0                 |       ✅ |           ✅ |
| Object Type consistency      |       ✅ |           ✅ |
| User Ownership               |         |           ✅ |
| Proposal Lifecycle           |         |           ✅ |
| Stale Proposal               |         |           ✅ |
| Candidate Quality            |         |           ✅ |
| CP-SAT Feasibility           |         |           ✅ |
| Hard Constraint Satisfaction |         |           ✅ |
| Notification Synchronization |         |           ✅ |
| Schedule Version Transition  | Partial |           ✅ |
| Historical Immutability      | Partial |           ✅ |

---

# 9.100 Historical Immutability Enforcement

Database สามารถช่วยป้องกันโดย:

* ไม่เปิด Update/Delete ผ่าน Application Repository
* ใช้ Database Permission ที่เหมาะสมใน Production
* ใช้ Transaction Policy
* ตรวจ Version State

แต่ MVP ไม่จำเป็นต้องสร้าง PostgreSQL Trigger ที่ซับซ้อนสำหรับทุก Historical Table หาก Application Layer สามารถ enforce ได้อย่างถูกต้องและมี Automated Tests

อย่างไรก็ตาม:

> Historical Version ต้องถือว่า Immutable ใน Domain Contract แม้ Database Engine จะอนุญาต SQL UPDATE โดยตรง

---

# 9.101 Schedule Version Creation

การสร้าง Version ใหม่ต้อง:

1. อ่าน Current Version
2. Validate Source
3. สร้าง Version Number ถัดไป
4. สร้าง Schedule Items
5. เปลี่ยน Current Flag
6. Commit ภายใน Transaction

ตัวอย่าง:

```text
Current = V3

Create:
V4

Set:
V3.is_current = FALSE
V4.is_current = TRUE
```

---

# 9.102 Version Number Allocation

Version Number เป็น Sequence ต่อ User:

```text
V1
V2
V3
...
```

ต้องไม่ reuse Number เดิมหลังจาก Version ถูกสร้างแล้ว

ดังนั้น:

```text
UNIQUE(user_id, version_number)
```

เป็น Integrity Requirement

วิธีการ Generate Version Number ต้องรองรับ Concurrent Confirmation และไม่ทำให้เกิด Duplicate Version

---

# 9.103 Proposal-to-Version Trace

แม้ MVP ไม่จำเป็นต้องมี FK จาก Schedule Version กลับไป Proposal หากจะหลีกเลี่ยง Dependency Cycle แต่สามารถ Trace ผ่าน:

```text
Schedule Version
→ source_request_id
→ planning_requests
→ proposals
```

ร่วมกับ:

```text
Proposal
→ source_schedule_version_id
```

ทำให้สามารถอธิบาย Replanning Provenance ได้โดยไม่ต้องเพิ่ม Table ใหม่

---

# 9.104 Database State Example

## Initial Planning

```text
planning_requests
   R1 = COMPLETED

proposals
   P1 = CONFIRMED

schedule_versions
   V1 = CURRENT

schedule_items
   Study = 14:00–16:00
```

## Replanning

```text
planning_requests
   R2 = COMPLETED

proposals
   P2
   source_schedule_version_id = V1

schedule_versions
   V1 = FALSE
   V2 = CURRENT
```

Historical State:

```text
V1
Study = 14:00–16:00
```

Current:

```text
V2
Study = 16:00–18:00
```

---

# 9.105 Database State Example — Stale Proposal

```text
Current Schedule = V2

Proposal P2
source_schedule_version_id = V1
```

เมื่อ User พยายาม Confirm:

```text
P2.source = V1
Current = V2

V1 != V2
```

ระบบต้อง:

```text
Reject Confirmation
```

และสามารถเปลี่ยน:

```text
P2.status = INVALIDATED
```

ตาม Application Policy

---

# 9.106 Database State Example — Date-Only Activity

```text
planning_objects

title = "ซื้อของขวัญให้แฟน"
date_start = 2026-10-05
time_mode = DATE_ONLY
start_at = NULL
end_at = NULL
```

และ:

```text
user_settings
notification_defaults.date_only.time = "06:00"
```

ผล:

```text
Calendar
→ All Day / Unscheduled

Notification
→ 06:00
```

06:00 ไม่ถูกเก็บเป็น Activity Start

---

# 9.107 Database State Example — Time-specific Activity

```text
planning_objects

title = "ประชุม"
start_at = 2026-10-05 09:00+07
end_at   = 2026-10-05 10:00+07
time_mode = RANGE
```

System Default:

```text
60 min before
```

Mobile:

```text
Notification = 08:00
```

ไม่มี `notification_instances` ใน Database

---

# 9.108 Database State Example — User Override

```text
planning_objects
notification_override =
{
  "before_start_minutes": 30
}
```

แม้ System Default:

```text
60
```

Effective Notification:

```text
30 min before
```

---

# 9.109 Database Query Boundary for AI

AI/NLP ไม่ควรได้รับ Raw Database Models

Application ควรสร้าง:

```text
Relevant AI Context
```

จาก:

```text
planning_objects
planning_rules
availability_rules
temporal_relations
planning_requests
user_settings
```

แล้วส่ง Structured Context ให้ AI

---

# 9.110 Database Query Boundary for Planner

Planner ควรได้รับ:

```text
Planning Representation
```

ที่สร้างจาก:

```text
Database
+
Current Request
+
Context
+
Normalization
```

ไม่ใช่:

```text
SQLAlchemy ORM Objects
```

โดยตรง

---

# 9.111 Performance Considerations

Database ต้องรองรับ:

### Long-range Calendar Storage

Activity สามารถเก็บระยะยาว

### Bounded Planning

Planner อ่านเฉพาะ Relevant Horizon

### Pagination

List APIs ต้องไม่ดึงข้อมูลทั้งหมดพร้อมกัน

### Indexing

ใช้ Date/User/Status/Version Index

### Connection Pool

Backend ใช้ PostgreSQL Connection Pool

---

# 9.112 Calendar Query Strategy

สำหรับ Month/Day View:

```text
1. Get Current Schedule Version
2. Query Schedule Items in Requested Date Range
3. Query Date-only Planning Objects in Requested Date Range
4. Combine for Presentation
```

ไม่ต้อง Query Historical Versions

---

# 9.113 Planning Object Date Range

Activity สามารถมี Date Range ที่ยาวกว่าหนึ่งวันในกรณีที่ Domain รองรับ เช่น Container หรือ Travel

แต่ Schedule Placement ต้องปฏิบัติตาม:

```text
start_at
end_at
```

และ Planning Rules

---

# 9.114 Schedule Item Placement Integrity

Schedule Item ต้องอยู่ใน Logical Date Range ของ Planning Object เมื่อ Object มี Date Boundary ที่กำหนด

ตัวอย่าง:

```text
Activity Date = 10 October
Schedule Item = 11 October
```

ถือเป็น Domain Error เว้นแต่ Object ถูกกำหนดให้ข้ามวันได้ตาม Policy

---

# 9.115 Container Placement Integrity

Container และ Child Activity ต้องสอดคล้องกัน:

```text
Child Start >= Container Start
Child End <= Container End
```

การตรวจนี้เป็น Planning / Domain Constraint

ไม่ใช่เพียง DB Foreign Key

---

# 9.116 Data Retention

Historical Schedule และ Planning Request ควรถูกเก็บตามขอบเขตโครงการและข้อกำหนดการทดลอง

MVP ไม่กำหนด Automatic Purge ที่อาจลบข้อมูลย้อนหลังโดยไม่ตั้งใจ

---

# 9.117 Backup Considerations

อย่างน้อย Demo/Production Database ควรมี:

* Backup Strategy
* Restore Test
* Migration Version Tracking

โดย Backup/Restore เป็น Deployment Concern และไม่ได้เพิ่ม Table สำหรับ Backup ลงใน Domain Schema

---

# 9.118 Database Security

Database Credentials:

```text
Backend Only
```

ไม่อยู่ใน Mobile

Database ต้องไม่ expose Public Access โดยไม่จำเป็น

และ Backend ต้องใช้ Least Privilege เท่าที่ Infrastructure รองรับ

---

# 9.119 Database Migration and Application Compatibility

Database Migration ต้องคำนึงถึง:

```text
Application Version
↔
Database Schema Version
```

โดย Migration ต้องถูก Run ก่อน Feature ที่ต้องใช้ Schema ใหม่จะถูก Enable

สำหรับ MVP ไม่จำเป็นต้องมี Zero-downtime Migration Architecture ที่ซับซ้อน

---

# 9.120 Complete Table Summary

|  # | Table                 | Purpose                             |
| -: | --------------------- | ----------------------------------- |
|  1 | users                 | Account / Ownership                 |
|  2 | auth_sessions         | Refresh Sessions                    |
|  3 | auth_tokens           | One-time Auth Tokens                |
|  4 | user_settings         | Time Window + Notification Defaults |
|  5 | planning_objects      | Activity / Container                |
|  6 | container_memberships | Container → Child                   |
|  7 | availability_rules    | Available / Unavailable             |
|  8 | planning_rules        | Hard / Preference                   |
|  9 | temporal_relations    | BEFORE / AFTER / OVERLAP            |
| 10 | planning_requests     | Planning Workflow                   |
| 11 | proposals             | Reviewable Plan                     |
| 12 | proposal_items        | Candidate Placements                |
| 13 | schedule_versions     | Immutable Confirmed Snapshot        |
| 14 | schedule_items        | Confirmed Placements                |

---

# 9.121 Database Invariants

```text
DB-INV-01
Every user-owned resource belongs to one user.

DB-INV-02
Users have unique normalized email addresses.

DB-INV-03
Each user has at most one user_settings row.

DB-INV-04
Planning Object type and Activity Type must be consistent.

DB-INV-05
Start and End must both exist or both be absent.

DB-INV-06
End must be later than Start.

DB-INV-07
Duration must be positive when present.

DB-INV-08
Date ranges cannot run backwards.

DB-INV-09
Container cannot contain itself.

DB-INV-10
Temporal Relation cannot reference the same Object.

DB-INV-11
Proposal candidate count is 1–3.

DB-INV-12
Proposal status follows the defined lifecycle.

DB-INV-13
Each proposal plan/object pair has at most one placement.

DB-INV-14
Each user has at most one Current Schedule Version.

DB-INV-15
Schedule Version numbers are unique per user.

DB-INV-16
Historical Schedule Versions are immutable.

DB-INV-17
Each schedule version/object pair has at most one placement.

DB-INV-18
Draft state is not persisted as confirmed schedule.

DB-INV-19
Notification instances are not persistent backend entities in MVP.

DB-INV-20
Deleting a planning object must not destroy historical schedule data.

DB-INV-21
Cross-user domain relationships are prohibited.

DB-INV-22
Stale proposals cannot become a new Current Schedule Version.

DB-INV-23
Database does not silently remove planning-critical data.
```

---

# 9.122 Database Design Rationale

## Rationale 1 — 14 Tables

ลดจำนวน Table จาก Design รุ่นก่อน เพื่อให้ MVP สามารถพัฒนาและดูแลได้ง่าย โดยยังรักษา Domain Separation ที่จำเป็น

## Rationale 2 — planning_objects

รวม Activity และ Container เพราะทั้งสองเป็น Planning Object เดียวกันในระดับ Abstraction แต่ใช้ `object_type` แยก Semantic

## Rationale 3 — Combined Rule Tables

รวม:

```text
Availability / Unavailability
Hard / Preference
```

เพื่อหลีกเลี่ยง Table ที่แยกมากเกินไปแต่มีโครงสร้างคล้ายกัน

## Rationale 4 — Proposal Items

Candidate ไม่จำเป็นต้องเป็น Persistent Entity แยก เพราะมี Lifecycle อยู่ภายใน Proposal

## Rationale 5 — Schedule Version

รองรับ Historical State, Stale Protection และ Replanning Evaluation

## Rationale 6 — No Current Schedule Table

Current State สามารถ derive จาก `schedule_versions.is_current`

## Rationale 7 — No Notification Table

Notification เป็น Device-derived State ใน MVP และไม่ใช่ Business Source of Truth

## Rationale 8 — JSONB

ใช้ JSONB เฉพาะส่วนที่โครงสร้างเปลี่ยนแปลงได้ เช่น Rule Parameters, Settings, Diagnostics และ Overrides

## Rationale 9 — Soft Delete

รักษา Historical References โดยไม่สูญเสีย Domain Objects

---

# 9.123 Database ↔ Domain Mapping

```text
Domain Concept
        ↓
Database Representation

User
→ users

Activity / Container
→ planning_objects

Container Membership
→ container_memberships

Availability / Unavailability
→ availability_rules

Hard Constraint / Preference
→ planning_rules

Temporal Relation
→ temporal_relations

Planning Request
→ planning_requests

Proposal
→ proposals

Candidate Placement
→ proposal_items

Confirmed Schedule
→ schedule_versions + schedule_items

Notification
→ NOT persisted as entity
```

---

# 9.124 Database ↔ Architecture Mapping

```text
Authentication Module
→ users
→ auth_sessions
→ auth_tokens

Settings Module
→ user_settings

Planning Domain
→ planning_objects
→ container_memberships
→ availability_rules
→ planning_rules
→ temporal_relations

Planning Workflow
→ planning_requests
→ proposals
→ proposal_items

Schedule Management
→ schedule_versions
→ schedule_items
```

ไม่มี Module ใดควรเข้าถึงทุก Table โดยไม่มีเหตุผล

---

# 9.125 Database ↔ Research Traceability

Database รองรับ Evaluation ได้ดังนี้:

### RQ1

```text
planning_requests
planning_objects
planning_rules
temporal_relations
```

ใช้ตรวจ Structured Planning Information

### RQ2

```text
planning_rules
availability_rules
proposals
schedule_versions
schedule_items
```

ใช้วัด Constraint / Preference Satisfaction

### RQ3

```text
planning_requests
proposals
schedule_versions
schedule_items
```

ใช้เปรียบเทียบ Before / After Replanning

### RQ4

```text
planning_requests.parent_request_id
proposals
schedule_versions
```

ใช้ Trace Feedback → Replanning → New Proposal → Confirmed Version

---

# 9.126 What Database Does Not Decide

Database ไม่เป็นผู้ตัดสิน:

* Feasible Schedule
* Best Candidate
* Preference Satisfaction
* Clarification Decision
* Replanning Scope
* Candidate Diversity
* User Confirmation
* Notification Timing Policy Resolution

สิ่งเหล่านี้เป็น Responsibility ของ Application / AI / Planning / Mobile Layer ตาม Architecture

---

# 9.127 Database Design Summary

Database ของ LONGTUA ถูกออกแบบให้รองรับ Lifecycle:

```text
User
 ↓
Planning Request
 ↓
Planning Objects + Rules
 ↓
Proposal
 ↓
Candidate Items
 ↓
User Confirmation
 ↓
Schedule Version
 ↓
Schedule Items
```

เมื่อเกิดการเปลี่ยนแปลง:

```text
Current Schedule Version
        ↓
New Planning Request
        ↓
Replanning
        ↓
New Proposal
        ↓
User Confirmation
        ↓
New Schedule Version
```

โดย Historical Version เดิมไม่ถูกแก้

---

# 9.128 Final Database Principle

หลักการสำคัญของ Database LONGTUA คือ:

> **Database เก็บ State ที่เป็นความจริงของระบบและข้อมูลที่จำเป็นต่อการ Trace แต่ไม่เก็บหรือบังคับ Logic ของ AI และ Scheduling ที่ควรอยู่ใน Application/Planning Layer**

จึงเกิดการแยกชัดเจน:

```text
Database
= Persist

AI
= Understand

Validation
= Verify

Planner
= Compute

Proposal
= Propose

User
= Confirm

Schedule Version
= Commit

Notification
= Derive
```

และทำให้ Database สามารถรองรับทั้ง Initial Planning, Human-in-the-Loop, Replanning, Schedule Versioning และ Evaluation ของ LONGTUA ได้โดยไม่ต้องเพิ่ม Entity ที่อยู่นอก MVP
