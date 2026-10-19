# 13. Testing & Evaluation Design

## 13.1 Purpose

เอกสารนี้กำหนดแนวทางการทดสอบและประเมินผลของ LONGTUA ตั้งแต่ระดับ component ไปจนถึง End-to-End โดยมีเป้าหมายเพื่อให้:

1. ตรวจสอบว่าแต่ละ module ทำงานตาม specification
2. ตรวจสอบว่า AI/NLP สามารถแปลง Natural Language เป็น planning information ได้ถูกต้อง
3. ตรวจสอบว่า Planning Engine สร้างแผนที่สอดคล้องกับ Hard Constraints
4. ตรวจสอบว่า Re-planning สามารถปรับตารางเมื่อสถานการณ์เปลี่ยน
5. ตรวจสอบว่า Human-in-the-loop interaction ช่วยให้ผู้ใช้ได้แผนที่ตรงกับความต้องการ
6. วัดข้อจำกัดด้านประสิทธิภาพของระบบ
7. เชื่อมผลการทดสอบกับ Research Questions (RQ1–RQ4)
8. ใช้ผลการประเมินกำหนดขอบเขตการใช้งานของ MVP จากข้อมูลจริง แทนการกำหนดตัวเลขโดยไม่มี benchmark รองรับ

---

# 13.2 Testing Strategy

LONGTUA ใช้การทดสอบหลายระดับ:

```text id="z1h4ue"
Unit Tests
    ↓
Integration Tests
    ↓
Module / Service Tests
    ↓
API Tests
    ↓
End-to-End Tests
    ↓
Evaluation / Benchmark
    ↓
User Evaluation
```

แต่ละระดับมีวัตถุประสงค์ต่างกัน และไม่ควรใช้ End-to-End Test แทนการทดสอบระดับล่างทั้งหมด

---

# 13.3 Test Pyramid

แนวทางหลัก:

```text id="k8b7s0"
             E2E
            /   \
        Integration
       /           \
   Module / Service
   /               \
        Unit Tests
```

Unit Test จะมีจำนวนมากที่สุดและใช้ตรวจ logic ที่แยกเป็นส่วนได้

Integration Test ใช้ตรวจการทำงานร่วมกันระหว่าง module, database, AI adapter และ planning engine

E2E ใช้ตรวจ user flow สำคัญตั้งแต่ input จนถึง confirmed schedule

---

# 13.4 Test Environment

ควรแยก environment สำหรับ:

### Development

ใช้สำหรับพัฒนาและ debug

### Test

ใช้สำหรับ automated test และ integration test

### Demo / Production-like

ใช้สำหรับการทดลองระบบ end-to-end และการนำเสนอ

หลักการ:

```text id="i92h6b"
Environment
   ≠
Production Secrets
```

ห้ามใช้ credentials หรือข้อมูลลับจริงใน automated test

---

# 13.5 Testing Tools

## Mobile

* Jest
* jest-expo
* React Native Testing Library

ใช้สำหรับ:

* component behavior
* navigation-related logic
* local state
* form validation
* notification coordination behavior ที่สามารถ mock ได้

## Backend

* pytest

ใช้สำหรับ:

* unit test
* service test
* API test
* integration test
* planning-related tests

## Database

ใช้ PostgreSQL environment สำหรับ integration test เพื่อให้ behavior ใกล้เคียงกับระบบจริง

SQLite ไม่ควรถูกใช้เป็นตัวแทน PostgreSQL หาก behavior ที่ทดสอบขึ้นอยู่กับ feature เฉพาะของ PostgreSQL

---

# 13.6 Testing Scope by Module

| Module                     | Primary Test Type              |
| -------------------------- | ------------------------------ |
| Authentication             | Unit + Integration + API       |
| User / Settings            | Unit + API                     |
| Activity Management        | Unit + API + Integration       |
| Availability / Rules       | Unit + Integration             |
| AI / NLP                   | Unit + Module + Evaluation     |
| Validation / Normalization | Unit + Integration             |
| Planning Representation    | Unit + Integration             |
| Planning Core              | Unit + Integration + Benchmark |
| Proposal Management        | Unit + API + Integration       |
| Schedule Management        | Unit + API + Integration       |
| Re-planning                | Integration + Evaluation       |
| Notification Coordination  | Unit + Integration             |
| Mobile UI                  | Component + E2E                |
| End-to-End Flow            | E2E                            |

---

# 13.7 Unit Testing

Unit Test ใช้ตรวจ function หรือ module ที่มี logic ชัดเจนและสามารถ isolate ได้

ตัวอย่าง:

### Temporal Normalization

Input:

```text
"บ่ายสองโมง"
```

Expected:

```text
time = 14:00
time_type = EXACT
```

---

### Semantic Time Window

Input:

```text
"ช่วงบ่าย"
```

Expected:

```text
semantic_window = AFTERNOON
```

และใช้ user-defined Time Window เมื่อมี override

---

### Ambiguous Time

Input:

```text
"6 โมง"
```

Expected:

```text
AMBIGUOUS
```

หาก context ไม่สามารถ resolve ได้

---

### Notification Policy

Date-only Activity:

```text
Activity Date = 2026-10-12
Activity Time = Unknown
```

Expected notification:

```text
2026-10-12 06:00
```

โดยไม่กำหนด Activity Start Time เป็น 06:00

---

### Conflict Detection

Activities:

```text
A = 09:00–10:00
B = 09:30–11:00
```

Expected:

```text
Conflict = true
```

แต่:

```text
Container = 09:00–17:00
Child = 13:00–15:00
```

Expected:

```text
Structural containment = valid
```

---

# 13.8 API Testing

API Test ต้องตรวจทั้ง:

* request validation
* response schema
* authentication
* authorization
* ownership
* status code
* error schema
* side effects
* idempotency ใน operation ที่กำหนด
* stale proposal protection

ตัวอย่าง:

```text id="2kw6c4"
POST /api/proposals/{id}/confirm
```

ต้องตรวจว่า:

1. ผู้ใช้เป็น owner ของ Proposal
2. Proposal ยังอยู่ในสถานะที่ confirm ได้
3. `source_schedule_version_id` ยังตรงกับ current schedule
4. proposal candidate ผ่าน validation
5. transaction สร้าง Schedule Version ใหม่
6. schedule version ใหม่ถูกตั้งเป็น current
7. proposal กลายเป็น CONFIRMED
8. notification synchronization สามารถดำเนินการต่อได้

---

# 13.9 Authentication Test Cases

ต้องครอบคลุมอย่างน้อย:

| Case                                              | Expected                          |
| ------------------------------------------------- | --------------------------------- |
| Register with valid data                          | Success                           |
| Duplicate email                                   | Rejected                          |
| Invalid login                                     | Rejected                          |
| Unverified account where verification is required | Rejected / limited                |
| Expired verification token                        | Rejected                          |
| Expired reset token                               | Rejected                          |
| Reused reset token                                | Rejected                          |
| Expired access token                              | Unauthorized                      |
| Valid refresh session                             | New access token                  |
| Revoked refresh session                           | Rejected                          |
| Logout                                            | Session revoked                   |
| Password change                                   | Existing refresh sessions revoked |

---

# 13.10 Authorization / Ownership Tests

ทุก endpoint ที่เข้าถึงข้อมูล user ต้องมี test ที่ตรวจว่า user หนึ่งไม่สามารถเข้าถึงข้อมูลของอีก user ได้

ตัวอย่าง:

```text id="v08k0f"
User A
  ↓
GET Activity owned by User B
  ↓
Access denied
```

ต้องทดสอบอย่างน้อยกับ:

* Activity
* Planning Request
* Proposal
* Schedule
* Availability
* Settings

เพื่อป้องกัน Broken Object Level Authorization

---

# 13.11 AI / NLP Testing Strategy

AI/NLP ไม่ควรประเมินจากความรู้สึกว่า output “ดูสมเหตุสมผล”

ต้องใช้ dataset ที่มี expected structured output หรือ expected decision เพื่อเปรียบเทียบผลลัพธ์

```text id="dq4m1b"
Input Text
    ↓
AI/NLP
    ↓
Structured Output
    ↓
Expected Output
    ↓
Metric
```

Dataset สามารถแบ่งเป็น:

1. manually authored cases
2. realistic user-style cases
3. synthetic edge cases
4. ambiguity cases
5. unsupported-input cases
6. difficult temporal cases

---

# 13.12 NLP Evaluation Dataset

แต่ละ record ควรมีอย่างน้อย:

```text id="sg2j2d"
Input Text
Expected Object Type
Expected Activity Type
Expected Title
Expected Date
Expected Time
Expected Duration
Expected Constraints
Expected Preferences
Expected Relations
Expected Clarification Decision
```

สำหรับ field ที่ไม่ควรมีค่า ให้ระบุเป็น:

```text
UNKNOWN
```

ไม่ใช่สร้าง expected value ขึ้นมาเพื่อให้ model ต้องตอบทุก field

---

# 13.13 NLP Metrics

## Precision

วัดสัดส่วนของ information ที่ระบบ extract แล้วถูกต้อง

```text
Precision =
Correct Extracted /
All Extracted
```

## Recall

วัดว่าสามารถ extract information ที่ควรได้ครบเพียงใด

```text
Recall =
Correct Extracted /
All Expected
```

## F1

```text
F1 =
2 × Precision × Recall /
(Precision + Recall)
```

ใช้กับ field ที่เหมาะสม เช่น:

* entity extraction
* relation extraction

---

# 13.14 Field-level Evaluation

ไม่ควรรวมทุก field เป็น metric เดียวตั้งแต่ต้น

อย่างน้อยควรแยก:

* Object Type
* Activity Type
* Date
* Start Time
* End Time
* Duration
* Constraint
* Preference
* Temporal Relation
* Clarification Decision

เพื่อให้รู้ว่า model ผิดจากส่วนใด

ตัวอย่าง:

```text
Date Extraction      F1 = ...
Time Extraction      F1 = ...
Duration Extraction  F1 = ...
Relation Extraction  F1 = ...
```

ค่าจริงจะรายงานจาก benchmark หลังสร้าง dataset

---

# 13.15 Structured Output Validity

ต้องวัดด้วยว่า AI ส่ง output ที่ตรง schema หรือไม่

Metric:

```text id="m75p6m"
Schema Validity Rate
=
Valid Outputs / All Outputs
```

ตัวอย่าง failure:

* missing required field
* wrong data type
* invalid enum
* malformed structure
* invalid time format

AI output ที่ schema invalid ต้องไม่เข้าสู่ Planning Engine โดยตรง

---

# 13.16 Unsupported Information Rate

ต้องประเมินว่าระบบสามารถหลีกเลี่ยงการ “เติมข้อมูลที่ผู้ใช้ไม่ได้ระบุ” ได้หรือไม่

ตัวอย่าง:

```text
User:
"พรุ่งนี้ไปซื้อของขวัญ"
```

ระบบไม่ควรสร้าง:

```text
Time = 10:00
Duration = 1 hour
```

หาก user ไม่ได้ระบุและไม่มี policy/context รองรับ

Metric สามารถรายงานเป็น:

```text
Unsupported Information Rate
=
Invented Planning-critical Values /
Relevant Test Cases
```

เป้าหมายเชิงคุณภาพของระบบคือควรมีค่านี้ต่ำที่สุดเท่าที่ทำได้

---

# 13.17 Clarification Decision Evaluation

ต้องแยกการวัด:

```text id="a7dn4m"
ควรถาม?
    ↓
ระบบถาม
```

ออกจาก:

```text
ระบบถาม
    ↓
คำถามนั้นถูกต้องหรือไม่?
```

อย่างน้อยต้องประเมิน:

* clarification required
* clarification not required
* selected clarification target

ตัวอย่าง:

```text
"พรุ่งนี้ 6 โมงไปวิ่ง"
```

ถ้า context ไม่พอ:

```text
Expected = ASK
```

แต่:

```text
"พรุ่งนี้ 6 โมงเช้าไปวิ่ง"
```

Expected:

```text
No clarification
```

---

# 13.18 AI / NLP Error Categories

ข้อผิดพลาดควรจัดกลุ่มเพื่อวิเคราะห์สาเหตุ:

```text id="s1qv02"
1. Object Detection Error
2. Attribute Extraction Error
3. Temporal Interpretation Error
4. Relation Error
5. Ambiguity Detection Error
6. Missing Information Decision Error
7. Unsupported Information Error
8. Schema Error
```

การรายงาน error category จะมีประโยชน์กว่าการรายงาน F1 เพียงค่าเดียว

---

# 13.19 Validation / Normalization Testing

หลัง AI output ต้องมี validation layer แยกจาก model

ต้องทดสอบ:

* enum validation
* date/time validation
* duration validation
* start/end consistency
* relation consistency
* unsupported value rejection
* planning object consistency
* user setting resolution
* notification rule resolution

ตัวอย่าง:

```text id="oox8dk"
AI Output
    ↓
Validation
    ↓
Normalization
    ↓
Planning Representation
```

AI ที่ตอบผิดแต่ validation จับได้ถือเป็น system behavior ที่ปลอดภัยกว่าการส่งข้อมูลผิดไป Planner

---

# 13.20 Planning Engine Testing

Planning Engine ต้องถูกทดสอบทั้ง correctness และ performance

---

# 13.21 Hard Constraint Correctness

ทุก solution ที่ระบบรายงานว่าสำเร็จต้องผ่าน Hard Constraint Validation

อย่างน้อยต้องทดสอบ:

### Fixed Time

```text
Activity = 14:00–15:00
```

ต้องถูกจัดตรงตาม fixed time

### Earliest Start

```text
start >= earliestStart
```

### Latest Start / Deadline

ต้องไม่เริ่มช้ากว่าที่กำหนด และต้องเสร็จภายใน deadline ตาม model

### Availability

Activity ต้องอยู่ในช่วง Available ที่กำหนด

### Unavailability

Activity ต้องไม่ชนช่วง Unavailable

### No-overlap

กิจกรรมที่ใช้ execution context เดียวกันห้าม overlap

### Precedence

```text
A BEFORE B
```

ต้องทำให้:

```text
end(A) <= start(B)
```

### Container Containment

```text
start(container) <= start(child)
end(child) <= end(container)
```

---

# 13.22 Solver Result Validation

ระบบต้องแยกผลจาก CP-SAT อย่างน้อย:

```text
OPTIMAL
FEASIBLE
INFEASIBLE
UNKNOWN
MODEL_INVALID
```

ต้องทดสอบแต่ละสถานการณ์

เมื่อ:

```text
INFEASIBLE
```

ระบบต้องไม่เปลี่ยนสถานะเป็น success เพียงเพื่อให้ UI มี schedule แสดง

---

# 13.23 Planning Objective Testing

Objective ต้องเคารพลำดับ:

```text id="v7d5ox"
1. Hard Feasibility
2. Explicit User Requirements
3. Preferences
4. Stability
5. Optional Activities
```

Test ต้องตรวจว่าระบบไม่เลือก schedule ที่ preference ดีกว่า แต่ละเมิด Hard Constraint

ตัวอย่าง:

```text
Plan A
Hard violations = 0
Preference score = lower

Plan B
Hard violations = 1
Preference score = higher
```

Expected:

```text
Plan A
```

---

# 13.24 Initial Planning vs Re-planning

ต้องมี test แยกสองกรณี

### Initial Planning

ไม่มี Current Schedule

```text
Stability objective = not applicable
```

### Re-planning

มี Current Schedule

```text
Stability = considered
```

และต้องตรวจว่า stability ไม่สามารถ override Explicit User Requirement หรือ Hard Constraint ได้

---

# 13.25 Re-planning Testing

Re-planning ต้องถูกทดสอบตาม trigger หลัก:

* New Activity
* Date Change
* Time Change
* Duration Change
* Deadline Change
* Availability Change
* Unavailability Change
* Cancellation
* User Feedback

แต่ละกรณีต้องตรวจ:

1. Change ถูกตรวจพบหรือไม่
2. Affected context ถูกระบุหรือไม่
3. Relevant planning horizon ถูกเลือกหรือไม่
4. Unaffected/past commitments ถูก preserve หรือไม่
5. Planner สามารถสร้าง solution ใหม่หรือไม่
6. Current Schedule ยังไม่เปลี่ยนก่อน Confirm หรือไม่

---

# 13.26 Re-planning Stability Evaluation

ให้ใช้:

```text
D = Σ |s_new(i) - s_old(i)|
```

เป็น operational measure สำหรับความเปลี่ยนแปลงของ start time

ค่า `D` ต่ำกว่า หมายถึง schedule มีการเปลี่ยนแปลงน้อยกว่าในมิติที่วัด

อย่างไรก็ตาม D ไม่ใช่ objective เดียวของ Re-planning

ต้องตรวจร่วมกับ:

* hard constraint preservation
* new requirement satisfaction
* feasibility
* schedule quality

---

# 13.27 Re-planning Metrics

อย่างน้อยควรรายงาน:

### Re-planning Success Rate

```text
Successful Replans /
All Replanning Cases
```

### Constraint Preservation

สัดส่วนของ Hard Constraints เดิมที่ยังคงถูกต้องหลัง Re-planning

### Runtime

เวลาตั้งแต่เริ่ม planning จนได้ solver result

### Number of Changed Activities

จำนวนกิจกรรมที่ถูกย้ายตำแหน่ง

### Start-time Deviation

```text
Σ |newStart - oldStart|
```

สำหรับกิจกรรมที่มี schedule เดิม

---

# 13.28 Proposal / Candidate Evaluation

Candidate ไม่ใช่ algorithm ที่ต้องมีจำนวนตายตัว

จึงต้องทดสอบกรณี:

```text
1 Candidate
2 Candidates
3 Candidates
```

และกรณี:

```text
No Meaningful Alternative
```

ต้องสามารถคืน 1 plan ได้ โดยไม่สร้าง dummy candidate เพื่อให้ครบ 3

---

# 13.29 Candidate Quality Evaluation

ควรประเมินอย่างน้อย:

### Feasibility

ทุก candidate ต้องผ่าน Hard Constraints

### Quality Retention

คุณภาพของ candidate ไม่ควรแย่ลงจนไม่สมเหตุสมผลเมื่อเทียบกับ best solution

### Diversity

Candidate ที่แสดงควรมีความแตกต่างที่ meaningful

เช่น:

```text
Plan A
เน้นทำงานช่วงเช้า

Plan B
เน้นทำงานช่วงบ่าย
```

ไม่ควรถือว่าเป็น diverse candidate หากต่างกันเพียงรายละเอียดที่ไม่มีความหมายต่อผู้ใช้

### Candidate Count

จำนวน candidate ที่คืนจริงต้องตรงกับจำนวนที่ system สามารถสร้างได้จริง

### Runtime

วัดผลกระทบจาก candidate generation ต่อเวลาโดยรวม

---

# 13.30 Schedule Version Testing

ต้องทดสอบ invariant สำคัญ:

```text id="1oy4u5"
Confirmed Schedule
      ↓
Confirm Change
      ↓
New Version
```

และ:

```text
Old Version = Immutable
```

ต้องตรวจว่า:

* version number เพิ่มขึ้น
* old version ไม่ถูก update
* มี current version เพียงหนึ่ง version
* schedule items ของแต่ละ version ถูกต้อง
* current version เปลี่ยนหลัง confirmation เท่านั้น

---

# 13.31 Stale Proposal Testing

Scenario:

```text id="h6d8r7"
Schedule Version 5 = Current

Proposal A
source_schedule_version_id = 5
```

จากนั้นมีการ Confirm อีก Proposal:

```text
Schedule Version 6 = Current
```

เมื่อพยายาม Confirm Proposal A:

```text
Expected:
409 / stale-related error
```

และ:

```text
Schedule Version 6
```

ต้องไม่ถูกเปลี่ยนโดย stale Proposal

---

# 13.32 Manual Edit Testing

ต้องครอบคลุม:

### Valid Draft

```text
Draft
→ Validate
→ Valid
→ Confirm
```

Expected:

```text
New Schedule Version
```

### Conflicting Draft

```text
Draft
→ Validate
→ Conflict
```

Expected:

```text
Confirm disabled
Current Schedule unchanged
```

### Cancel / Back

การออกจาก Draft โดยไม่ Confirm ต้องไม่แก้ Current Schedule

---

# 13.33 Notification Testing

Notification เป็น derived state จาก Confirmed Schedule

ต้องทดสอบ:

### Date-only

```text
Activity Date = D
Notification = D 06:00
```

### Timed Activity

```text
Start = 14:00
Default Notification = 13:00
```

### Activity Override

Activity-level setting ต้อง override global default

### Reschedule

```text
09:00 → 12:00
```

ต้อง:

```text
Cancel old notification
Schedule new notification
```

### Proposal

Proposal ต้องไม่สร้าง notification

### Rejected Proposal

Rejected Proposal ต้องไม่เปลี่ยน notification

### Notification Failure

Schedule ต้องยังคง Confirmed

---

# 13.34 Mobile UI Testing

UI component tests ควรตรวจ behavior มากกว่า visual pixel matching

ตัวอย่าง:

### Button State

Confirm button:

```text
Valid Draft → Enabled
Conflict → Disabled
Stale Proposal → Disabled
```

### Clarification

เมื่อ backend ส่ง:

```text
NEEDS_CLARIFICATION
```

UI ต้องนำไปยัง clarification state

### Empty Calendar

ไม่มี schedule:

```text
Empty State
```

### Error

Backend failure:

```text
Error State
```

และต้องมี retry action ตามบริบท

---

# 13.35 End-to-End Test Scenarios

อย่างน้อยควรมี E2E scenario หลักดังนี้

## E2E-01 Initial Planning

```text
Login
→ AI Input
→ Processing
→ Planning
→ Proposal
→ Confirm
→ Calendar Updated
```

Expected:

* Schedule Version ใหม่ถูกสร้าง
* Calendar แสดง Confirmed Schedule
* Notification ถูก synchronize

---

## E2E-02 Ambiguous Input

```text
AI Input
→ Ambiguity Detected
→ Clarification
→ User Answer
→ Planning
→ Proposal
→ Confirm
```

---

## E2E-03 No Feasible Plan

```text
AI Input
→ Planning
→ INFEASIBLE
→ Error / Constraint Explanation
```

Expected:

```text
Current Schedule unchanged
```

---

## E2E-04 Feedback Re-planning

```text
Proposal
→ Feedback
→ Re-planning
→ New Proposal
→ Confirm
```

---

## E2E-05 Manual Edit Conflict

```text
Calendar
→ Edit
→ Create Conflict
→ Confirm Disabled
→ Fix Conflict
→ Confirm
```

---

## E2E-06 Activity Rescheduling

```text
Confirmed Activity
→ Change Time
→ Re-planning / Manual Draft
→ Confirm
→ Notification Rescheduled
```

---

## E2E-07 Stale Proposal

```text
Proposal A
→ Another Change Confirmed
→ Proposal A becomes stale
→ Attempt Confirm
→ Rejected
```

Expected:

```text
Current Schedule unchanged
```

---

# 13.36 Error-path Coverage

Testing ต้องไม่เน้นเฉพาะ Happy Path

ทุก critical flow ต้องมีอย่างน้อย:

```text
Success
Failure
Validation Error
Conflict
Unauthorized
Not Found
Stale State
Timeout / Unavailable
```

ตัวอย่าง Planning:

```text
Input
 ↓
 ├── Success → Proposal
 ├── Clarification → Ask User
 ├── Infeasible → Explain Conflict
 ├── Unsupported → Reject Safely
 └── Service Error → Retry / Error
```

---

# 13.37 Property / Invariant Testing

บาง behavior ควรทดสอบเป็น invariant มากกว่าทดสอบเฉพาะ input/output คู่เดียว

ตัวอย่าง:

### Schedule Invariant

ทุก Confirmed Schedule ต้องไม่มี Hard Constraint violation

### Version Invariant

มี Current Schedule Version ได้เพียงหนึ่ง version ต่อ user

### Proposal Invariant

Proposal ที่อ้างอิง schedule version เก่าต้องไม่สามารถถูก Confirm ได้หลัง current version เปลี่ยน

### Notification Invariant

ไม่มี notification จาก unconfirmed proposal

### Ownership Invariant

Object ของ user A ต้องไม่ถูกเข้าถึงโดย user B

### AI Safety Invariant

Planning-critical values ที่ไม่มีหลักฐานจาก user input/context ต้องไม่ถูกสร้างโดยระบบอย่างเงียบ ๆ

---

# 13.38 Test Data Design

Test data ต้องสะท้อนทั้ง normal cases และ edge cases

แบ่งอย่างน้อยเป็น:

```text
Normal
Boundary
Ambiguous
Missing
Unsupported
Conflict
Dense Schedule
Sparse Schedule
Recurring
Date-only
Fixed-time
Replanning
```

ตัวอย่าง Boundary:

* activity duration ต่ำมาก
* activity ติดขอบ planning horizon
* activity จบพอดีกับ deadline
* availability จบพอดีกับ activity start
* unavailability เริ่มพอดีกับ activity end

เพื่อให้รองรับ semantics แบบ half-open interval:

```text
[start, end)
```

เช่น:

```text
A = 09:00–10:00
B = 10:00–11:00
```

ต้องไม่ถือว่า overlap กัน

---

# 13.39 Dataset Split for AI Evaluation

Dataset สำหรับ AI evaluation ควรแยกเป็น:

```text
Training / Prompt Development
Validation / Tuning
Final Evaluation
```

ชุด Final Evaluation ต้องไม่ถูกใช้เพื่อปรับ prompt/model configuration ระหว่าง development

เพื่อไม่ให้ผล evaluation สะท้อนการ tune กับข้อมูลทดสอบโดยตรง

---

# 13.40 Evaluation Reproducibility

เมื่อทำการประเมิน AI และ Planning Engine ต้องเก็บ configuration ที่เกี่ยวข้อง เช่น:

* model/provider
* prompt version
* schema version
* system configuration
* Time Window configuration
* Planning Engine configuration
* dataset version
* evaluation date
* randomization / seed เมื่อมี
* software version

เพื่อให้ผลที่ได้สามารถตรวจสอบย้อนหลังได้

---

# 13.41 Performance Benchmark

Performance Benchmark ใช้เพื่อหา practical system limit ของ MVP

ตัวแปรหลัก:

```text
Planning Horizon
×
Activity Count
×
Candidate Count
```

ตัวอย่าง workload:

```text
Horizon:
1 day
3 days
7 days
14 days

Activities:
10
25
50
100

Candidates:
1
2
3
```

ตัวเลขที่ใช้จริงต้องถูกปรับตามขนาดระบบที่สามารถทดสอบได้ ไม่กำหนดเป็น requirement ตายตัวก่อนมีข้อมูล benchmark

---

# 13.42 Performance Metrics

อย่างน้อยเก็บ:

### Planning Runtime

เวลาที่ใช้ตั้งแต่ planner เริ่มรับ model จนได้ solver result

### End-to-End Planning Time

รวม:

```text
AI/NLP
+
Validation
+
Planning
+
Proposal Preparation
```

### Memory Usage

ใช้ดู resource consumption ของ backend/process

### Success Rate

วัดว่าสามารถสร้าง solution ได้ใน workload แต่ละขนาดหรือไม่

### Quality

วัดคุณภาพตาม objective/model ที่กำหนด

---

# 13.43 Performance Result

ควรรายงานในรูปแบบตารางหรือกราฟ เช่น:

| Horizon | Activities | Candidates | Success | Runtime | Quality |
| ------- | ---------: | ---------: | ------: | ------: | ------: |
| 1 day   |         10 |          1 |       … |       … |       … |
| 3 days  |         25 |          1 |       … |       … |       … |
| 7 days  |         50 |          2 |       … |       … |       … |
| 14 days |        100 |          3 |       … |       … |       … |

จากข้อมูลนี้จึงกำหนด practical MVP boundary ได้อย่างมีหลักฐาน

---

# 13.44 Ablation Testing

เพื่อประเมินว่ากลไกแต่ละส่วนมีผลต่อผลลัพธ์หรือไม่ ควรมี controlled comparison

ตัวอย่าง:

### Preference Ablation

```text
Planning
vs
Planning + Preferences
```

วัด:

* preference satisfaction
* overall quality
* feasibility
* runtime

---

### Stability Ablation

```text
Re-planning
vs
Re-planning + Stability
```

วัด:

* start-time deviation
* changed activities
* requirement satisfaction

---

### Feedback Ablation

```text
Initial Proposal
vs
Proposal + User Feedback + Replanning
```

วัด requirement satisfaction และ alignment

---

# 13.45 Human-in-the-loop Evaluation

HITL ต้องประเมินทั้งผลลัพธ์และ interaction

ตัวชี้วัดหลัก:

### Requirement Satisfaction

ผู้ใช้ได้แผนที่ตรงกับ requirement หรือไม่

### Task Completion

ผู้ใช้สามารถดำเนิน flow จนได้ Confirmed Schedule หรือไม่

### Interaction Effort

วัดจำนวน interaction ที่ต้องใช้ เช่น:

* clarification responses
* edits
* feedback actions

ไม่ควรตีความว่า interaction น้อยที่สุดดีเสมอไป เพราะ clarification ที่จำเป็นช่วยลดความผิดพลาดได้

### Proposal Acceptance

```text
Accepted Proposals /
Presented Proposals
```

### Usability / Satisfaction

สามารถเก็บด้วย questionnaire ที่เหมาะสมกับการทดลองของโครงงาน

---

# 13.46 Human Evaluation Scenarios

ผู้ทดสอบควรได้รับ scenario ที่ครอบคลุม:

```text
1. Initial Planning
2. Ambiguous Time
3. Date-only Activity
4. Hard Conflict
5. Availability Conflict
6. Re-planning
7. User Feedback
8. Manual Edit
```

จากนั้นให้ทำ task ตาม scenario โดยไม่จำเป็นต้องสอนวิธีใช้ละเอียดเกินไป เพื่อวัด behavior ของ UI จริง

---

# 13.47 End-to-End Evaluation

End-to-End ประเมิน flow:

```text id="s0dw7a"
Natural Language
      ↓
AI/NLP
      ↓
Validation
      ↓
Planning
      ↓
Proposal
      ↓
Human Review
      ↓
Confirmed Schedule
      ↓
Notification
```

Metrics สามารถรวม:

* NLP correctness
* feasibility
* requirement satisfaction
* planning runtime
* user interaction effort
* confirmation rate
* notification correctness

---

# 13.48 Research Question Mapping

| Research Question | Evaluation                                                                                |
| ----------------- | ----------------------------------------------------------------------------------------- |
| RQ1               | E1: NLP extraction, schema validity, clarification accuracy, unsupported information rate |
| RQ2               | E2: Feasibility, constraint violations, deadline satisfaction, preference satisfaction    |
| RQ3               | E3: Re-planning success, constraint preservation, runtime, schedule stability             |
| RQ4               | E4/E5: Candidate quality, feedback impact, requirement satisfaction, interaction effort   |

---

# 13.49 Evaluation Groups

งานประเมินระบบสามารถแบ่งเป็น:

```text
E1 NLP Understanding
E2 Initial Planning
E3 Re-planning
E4 Candidate / Proposal
E5 Human-in-the-loop
E6 End-to-End
```

โดยแต่ละ evaluation ต้องมี:

```text
Objective
Dataset / Scenario
Metric
Procedure
Expected Result
```

เพื่อให้สามารถอธิบายในรายงานโครงงานได้อย่างเป็นระบบ

---

# 13.50 Pass / Fail Criteria

ไม่ควรกำหนดว่า “ทุก metric ต้อง 100%” เพราะ NLP และ optimization มีธรรมชาติแตกต่างกัน

จึงควรกำหนด:

### Correctness-critical invariants

ต้องผ่าน เช่น:

* Hard Constraint violation ใน Confirmed Schedule
* unauthorized access
* stale Proposal confirmation
* invalid schedule confirmation
* notification จาก unconfirmed Proposal

### Quality Metrics

ให้รายงานค่าที่วัดได้จริง เช่น:

* Precision
* Recall
* F1
* feasibility rate
* preference satisfaction
* replanning stability
* runtime

และใช้ผลจริงในการอภิปรายจุดแข็ง/ข้อจำกัดของระบบ

---

# 13.51 Critical Safety / Consistency Tests

ก่อน Demo หรือ Release Candidate ต้องผ่านอย่างน้อย:

```text id="pl3o8n"
[ ] Confirmed Schedule ไม่มี Hard Constraint violation
[ ] Proposal ที่ stale ไม่สามารถ Confirm ได้
[ ] Reject Proposal ไม่แก้ Current Schedule
[ ] Draft ที่ conflict ไม่สามารถ Confirm ได้
[ ] AI ไม่สามารถแก้ Confirmed Schedule โดยตรง
[ ] Proposal ไม่สร้าง notification
[ ] Confirmed Schedule change sync notification ได้
[ ] User A เข้าถึงข้อมูลของ User B ไม่ได้
[ ] Current Schedule มีได้เพียงหนึ่ง version
[ ] Historical Schedule Version ไม่ถูกแก้ไข
```

---

# 13.52 Regression Testing

เมื่อแก้ระบบส่วนหนึ่ง ต้อง rerun test ที่เกี่ยวข้องเพื่อป้องกัน regression

ตัวอย่าง:

ถ้าแก้ Planning Model:

```text
Planning Unit Tests
→ Constraint Tests
→ Replanning Tests
→ Proposal Tests
→ E2E Planning Tests
```

ถ้าแก้ Notification Policy:

```text
Notification Unit Tests
→ Schedule Integration Tests
→ Reschedule Tests
→ E2E Notification Tests
```

---

# 13.53 Continuous Integration

เมื่อ repository และ development workflow พร้อม ระบบควรให้ automated test ทำงานเมื่อมี code change

อย่างน้อย:

```text id="q07vxb"
Commit / Pull Request
        ↓
Lint / Type Check
        ↓
Unit Tests
        ↓
Integration Tests
        ↓
Build / Test
```

E2E และ benchmark ที่มีค่าใช้จ่ายสูงสามารถแยกเป็น pipeline ตามความเหมาะสมของ project infrastructure

---

# 13.54 Test Case Documentation

Test case แต่ละตัวควรระบุ:

```text
Test ID
Title
Purpose
Precondition
Input
Procedure
Expected Result
Actual Result
Status
```

ตัวอย่าง:

```text
PLN-001
Title: Prevent overlapping fixed activities

Precondition:
Two activities are fixed at overlapping times

Input:
A = 10:00–11:00
B = 10:30–11:30

Expected:
No feasible schedule
or valid alternative if one exists
```

---

# 13.55 Defect Severity

Bug สามารถแบ่งตามผลกระทบ:

### Critical

กระทบ correctness/security/consistency โดยตรง

เช่น:

* Confirm แล้ว schedule ผิด Hard Constraint
* User เห็นข้อมูล user อื่น
* stale Proposal แก้ current schedule ได้

### Major

กระทบ core functionality แต่ยังมี workaround

เช่น:

* Re-planning ไม่ทำงานในบางกรณี
* clarification flow ค้าง

### Minor

UI หรือ behavior ที่ไม่กระทบ core correctness

เช่น:

* indicator ไม่แสดงบางสถานการณ์
* ข้อความบางส่วนไม่ชัดเจน

---

# 13.56 Test Completion Criteria

Feature สำคัญถือว่าพร้อมเข้าสู่ integration/demo เมื่อ:

1. Unit tests ผ่าน
2. Integration tests ที่เกี่ยวข้องผ่าน
3. API contract ผ่าน
4. Critical invariants ผ่าน
5. Relevant E2E scenario ผ่าน
6. ไม่มี Critical defect ที่ยังเปิดอยู่
7. Behavior ตรงกับ Requirements / Domain / API / UI specification

---

# 13.57 Final Evaluation Workflow

กระบวนการประเมินทั้งโครงการ:

```text id="amj3xd"
Finalize System
      ↓
Freeze Evaluation Configuration
      ↓
Prepare Dataset
      ↓
Run E1 NLP
      ↓
Run E2 Initial Planning
      ↓
Run E3 Re-planning
      ↓
Run E4 Candidate Evaluation
      ↓
Run E5 HITL Evaluation
      ↓
Run E6 End-to-End
      ↓
Run Performance Benchmark
      ↓
Analyze Results
      ↓
Answer RQ1–RQ4
```

---

# 13.58 Relationship with Other Documents

Testing Design ต้อง trace กลับไปยังเอกสารก่อนหน้า:

```text
Requirements
    ↓
Domain Model
    ↓
AI/NLP Design
    ↓
Planning Engine
    ↓
Re-planning
    ↓
Schedule / Notification
    ↓
Database / API / Security
    ↓
UI / UX
    ↓
Testing & Evaluation
```

ดังนั้น Test Case ไม่ควรถูกสร้างแยกจาก system design แต่ควรถูก derive จาก behavior และ invariants ที่ถูกกำหนดไว้แล้ว

---

# 13.59 Final Testing Principle

หลักการสำคัญของการทดสอบ LONGTUA คือ:

> **ไม่เพียงทดสอบว่าระบบ “ทำงานได้” แต่ต้องทดสอบว่าระบบ “ทำงานถูกต้องตามข้อกำหนด”**

โดยเฉพาะในส่วน Planning และ AI/NLP ต้องแยกให้ชัดเจนระหว่าง:

```text
AI ถูกต้อง
≠
Schedule ถูกต้อง
```

และ:

```text
Schedule หาได้
≠
Schedule เหมาะกับผู้ใช้
```

ดังนั้น evaluation ของ LONGTUA ต้องครอบคลุมทั้ง:

```text
Understanding
+
Feasibility
+
Adaptation
+
User Alignment
+
System Correctness
+
Performance
```

ผลลัพธ์สุดท้ายควรสามารถตอบได้อย่างเป็นหลักฐานว่า:

1. ระบบเข้าใจ Natural Language ได้ดีเพียงใด
2. ระบบสร้างแผนที่ feasible ภายใต้ constraints ได้หรือไม่
3. ระบบปรับแผนเมื่อสถานการณ์เปลี่ยนได้ดีเพียงใด
4. Feedback ของผู้ใช้ช่วยให้แผนดีขึ้นหรือไม่
5. ระบบมี practical limit อยู่ที่ workload ระดับใด
6. มีข้อผิดพลาดหรือข้อจำกัดใดที่ยังคงอยู่ใน MVP
