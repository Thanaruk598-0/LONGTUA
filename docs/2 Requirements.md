# 2. Requirements Specification

## 2.1 Purpose

เอกสารฉบับนี้กำหนด Functional Requirements, Non-Functional Requirements, Domain Rules และขอบเขตของระบบ LONGTUA — Personal Adaptive Planner เพื่อใช้เป็นข้อกำหนดกลางสำหรับการออกแบบระบบ การออกแบบฐานข้อมูล การออกแบบ API การพัฒนา Mobile Application การพัฒนา AI/NLP การสร้าง Planning Engine การทดสอบ และการประเมินผลระบบ

Requirements ในเอกสารนี้ใช้เป็น **Source of Truth** สำหรับการพัฒนาระบบภายในขอบเขตของ MVP โดยรายละเอียดระดับ Implementation เช่น ชื่อตัวแปร โครงสร้าง JSON ภายใน หรือวิธีการเขียน Code สามารถเปลี่ยนได้ตราบใดที่ไม่ทำให้ Requirement ที่กำหนดไว้เสียไป

---

# 2.2 System Actors

## 2.2.1 User

User คือผู้ใช้งานหลักของระบบ และเป็นผู้ควบคุมผลลัพธ์ด้านการวางแผน

User สามารถ:

* สร้างและจัดการ Activity
* กำหนด Availability และ Unavailability
* ระบุข้อจำกัดและ Preferences
* ส่งข้อความภาษาธรรมชาติให้ระบบ
* ตอบคำถาม Clarification
* ตรวจสอบ Proposal
* Confirm หรือ Reject Proposal
* แก้ไข Schedule ผ่าน Draft
* ส่ง Feedback เพื่อให้ระบบปรับแผน

หลักการสำคัญคือ **User เป็น Final Decision Maker**

ระบบจึงไม่ถือว่าผลจาก AI หรือ Planning Engine เป็นคำสั่งให้เปลี่ยนตารางโดยอัตโนมัติ

---

## 2.2.2 AI / NLP Component

AI/NLP เป็น System Component สำหรับทำความเข้าใจ Input ของ User

AI/NLP มีหน้าที่ เช่น:

* Extract Activity Information
* Identify Planning Object Type
* Identify Activity Type
* Extract Date / Time / Duration
* Interpret Semantic Time Window
* Extract Temporal Relations
* Detect Ambiguity
* Detect Missing Planning-Critical Information
* Process User Feedback

AI/NLP **ไม่มีหน้าที่ตัดสินใจจัดตาราง**

---

## 2.2.3 Planning Engine

Planning Engine เป็น System Component สำหรับสร้าง Schedule ภายใต้ Planning Model

หน้าที่หลัก ได้แก่:

* สร้าง Planning Representation
* ประมวลผล Hard Constraints
* ประมวลผล Preferences
* ตรวจสอบ Feasibility
* หา Schedule
* สร้าง Candidate Alternatives เมื่อเหมาะสม
* Re-plan เมื่อได้รับข้อมูลหรือสถานการณ์ใหม่

Planning Engine **ไม่มีหน้าที่ตีความ Natural Language**

---

# 2.3 Functional Requirements

---

# 2.3.1 Authentication and Account Management

### FR-AUTH-01 — User Registration

ระบบต้องอนุญาตให้ผู้ใช้สร้างบัญชีด้วย Email และ Password

### FR-AUTH-02 — User Login

ระบบต้องอนุญาตให้ผู้ใช้เข้าสู่ระบบด้วยข้อมูลบัญชีที่ถูกต้อง

### FR-AUTH-03 — Access Token

ระบบต้องออก Access Token สำหรับการเข้าถึง Protected Resources ตาม Authentication Policy

### FR-AUTH-04 — Refresh Session

ระบบต้องรองรับการต่ออายุ Access Token ผ่าน Refresh Session โดยไม่ต้อง Login ใหม่ภายในอายุ Session ที่กำหนด

### FR-AUTH-05 — Remember Me

ระบบต้องรองรับตัวเลือก Remember Me ตาม Authentication Policy ของระบบ

### FR-AUTH-06 — Logout

ระบบต้องอนุญาตให้ผู้ใช้ Logout และต้องทำให้ Session ที่เกี่ยวข้องไม่สามารถใช้ต่อได้ตาม Policy

### FR-AUTH-07 — Email Verification

ระบบต้องรองรับการยืนยัน Email สำหรับบัญชีที่ต้องการ Verification

### FR-AUTH-08 — Password Reset

ระบบต้องรองรับกระบวนการขอ Reset Password และตั้ง Password ใหม่ผ่าน One-Time Token

### FR-AUTH-09 — Password Security

ระบบต้องไม่จัดเก็บ Password แบบ Plain Text และต้องใช้ Password Hashing ตาม Security Policy

### FR-AUTH-10 — Ownership Authorization

ระบบต้องตรวจสอบว่าผู้ใช้มีสิทธิ์เข้าถึงหรือแก้ไขข้อมูลของตนเองก่อนดำเนินการกับ Protected Resource ทุกครั้ง

---

# 2.3.2 Activity Management

### FR-ACT-01 — Create Activity Manually

ผู้ใช้ต้องสามารถสร้าง Activity โดยไม่ต้องผ่าน AI/NLP

### FR-ACT-02 — View Activities

ผู้ใช้ต้องสามารถดู Activity ของตนเองได้

### FR-ACT-03 — View Activity Detail

ผู้ใช้ต้องสามารถดูรายละเอียดของ Activity แต่ละรายการได้

### FR-ACT-04 — Update Activity

ผู้ใช้ต้องสามารถแก้ไขข้อมูลของ Activity ที่ตนเองเป็นเจ้าของได้

### FR-ACT-05 — Cancel Activity

ผู้ใช้ต้องสามารถยกเลิก Activity ได้โดยไม่ทำลาย Historical Reference ที่จำเป็นต่อระบบ

### FR-ACT-06 — Soft Delete

ระบบต้องรองรับการ Soft Delete สำหรับข้อมูล Planning Object เพื่อป้องกันการสูญเสียข้อมูลที่ยังมีความสัมพันธ์กับ Historical Records

### FR-ACT-07 — Activity Information

Activity ต้องสามารถเก็บข้อมูลที่จำเป็นต่อการวางแผน เช่น:

* Title
* Description
* Activity Type
* Date
* Start Time
* End Time
* Duration
* Deadline
* Notification Override
* Status
* Source Request

ตามเงื่อนไขของข้อมูลแต่ละ Activity

### FR-ACT-08 — Date-Only Activity

ระบบต้องรองรับ Activity ที่มีวันที่แต่ยังไม่มีเวลาเริ่มต้นหรือช่วงเวลาที่แน่นอน

### FR-ACT-09 — Fixed-Time Activity

ระบบต้องรองรับ Activity ที่มีเวลาที่กำหนดตายตัว

### FR-ACT-10 — Planning-Relevant Update Detection

เมื่อ Activity ถูกแก้ไข ระบบต้องสามารถจำแนกได้ว่าการเปลี่ยนแปลงนั้นกระทบกระบวนการจัดตารางหรือไม่

ตัวอย่างการเปลี่ยนแปลงที่อาจกระทบ Planning ได้แก่:

* Duration
* Fixed Time
* Date
* Deadline
* Planning Constraint
* Preference
* Container Membership
* Cancellation

ในขณะที่การแก้ข้อมูลเชิงคำอธิบาย เช่น Title เพียงอย่างเดียว โดยทั่วไปไม่ควรทำให้เกิด Replanning หากไม่ได้เปลี่ยนข้อมูลที่ใช้ในการ Scheduling

---

# 2.3.3 Planning Object Management

### FR-OBJ-01 — Planning Object

ระบบต้องรองรับ Planning Object อย่างน้อย 2 ประเภท:

* Activity
* Container

### FR-OBJ-02 — Activity Types

Activity ต้องรองรับประเภทที่กำหนดใน MVP ได้แก่:

* TASK
* EVENT
* APPOINTMENT
* MEETING
* TRAVEL
* OTHER

### FR-OBJ-03 — Container

ระบบต้องรองรับ Container สำหรับแทนกรอบกิจกรรมหรือ Commitment ขนาดใหญ่ที่สามารถประกอบด้วย Child Activities

### FR-OBJ-04 — Container Membership

ระบบต้องสามารถกำหนดความสัมพันธ์ระหว่าง Container และ Child Activity ได้

### FR-OBJ-05 — Container Exclusivity

Container ใน MVP ถือเป็น Exclusive Commitment ดังนั้น Activity ที่ไม่ใช่ Child ของ Container ไม่ควรถูกจัดให้อยู่ในช่วงเวลาที่ Container ครอบคลุม

### FR-OBJ-06 — Child Containment

Child Activity ที่เป็นสมาชิกของ Container ต้องสามารถถูกจำกัดให้อยู่ภายในช่วงเวลาของ Container ตาม Relationship ที่กำหนด

### FR-OBJ-07 — Overlap Semantics

ระบบต้องแยกระหว่าง:

* Temporal overlap ที่ใช้บอกความสัมพันธ์ของเวลา
* Scheduling overlap ที่ถือเป็น Conflict

ดังนั้นการมี `OVERLAP` เป็น Temporal Relation ไม่ได้หมายความว่า Planning Engine สามารถจัด Activity ให้ทำพร้อมกันได้

Concurrent / Multitasking ไม่อยู่ใน MVP

---

# 2.3.4 Availability and Unavailability

### FR-AV-01 — Availability

ผู้ใช้ต้องสามารถกำหนดช่วงเวลาที่อนุญาตให้ Planner นำ Activity ไปจัดวางได้

### FR-AV-02 — Unavailability

ผู้ใช้ต้องสามารถกำหนดช่วงเวลาที่ไม่สามารถจัด Activity ได้

### FR-AV-03 — One-Time Rule

ระบบต้องรองรับ Availability / Unavailability แบบเกิดขึ้นครั้งเดียว

### FR-AV-04 — Recurring Rule

ระบบต้องรองรับ Availability / Unavailability แบบเกิดซ้ำตามวันที่กำหนด

ตัวอย่าง:

> Monday–Friday, 08:00–17:00

### FR-AV-05 — Availability Does Not Consume Execution Capacity

Availability ต้องไม่ถูกถือว่าเป็น Activity และไม่สร้าง Scheduling Conflict เพียงเพราะมี Activity อยู่ภายในช่วง Availability

### FR-AV-06 — Unavailability as Hard Constraint

Unavailability ต้องถูกนำไปพิจารณาเป็น Hard Constraint สำหรับการจัด Activity

---

# 2.3.5 Natural Language Planning Request

### FR-PLN-01 — Natural Language Input

ผู้ใช้ต้องสามารถส่งข้อความภาษาธรรมชาติเพื่อร้องขอการวางแผนได้

### FR-PLN-02 — Structured Information Extraction

ระบบต้องสามารถแปลงข้อความให้เป็น Structured Planning Information

### FR-PLN-03 — Planning Object Classification

ระบบต้องสามารถจำแนกว่า Input หมายถึง Activity หรือ Container ตามบริบท

### FR-PLN-04 — Activity Type Classification

ระบบต้องสามารถระบุ Activity Type ที่เหมาะสมจากข้อมูลที่ผู้ใช้ให้มา

### FR-PLN-05 — Temporal Information Extraction

ระบบต้องรองรับการทำความเข้าใจข้อมูลด้านเวลา เช่น:

* Date
* Exact Time
* Time Range
* Duration
* Deadline
* Semantic Time Window
* Approximate Time / Duration
* Relative Time

### FR-PLN-06 — Temporal Relation Extraction

ระบบต้องสามารถระบุ Temporal Relation ที่ระบบรองรับ เช่น:

* BEFORE
* AFTER
* OVERLAP

### FR-PLN-07 — Reference Time

การตีความวันและเวลาที่สัมพันธ์กับคำ เช่น “พรุ่งนี้”, “อาทิตย์หน้า” ต้องอ้างอิง Reference Time ที่มีทั้ง Date และ Time ตามบริบทของคำขอ

### FR-PLN-08 — No Unsupported Invention

ระบบต้องไม่สร้างข้อมูล Planning-Critical เช่น เวลา วันที่ หรือระยะเวลา ที่ไม่มีข้อมูลรองรับจาก Input หรือ Context ที่ระบบอนุญาตให้ใช้

### FR-PLN-09 — Contextual Interpretation

ระบบต้องสามารถใช้ Relevant Context ในการตีความ Input เมื่อจำเป็น โดยไม่ต้องส่งข้อมูลทั้งหมดของระบบหรือประวัติการสนทนาไปยัง AI โดยอัตโนมัติ

### FR-PLN-10 — Structured Output

ผลจาก AI/NLP ต้องถูกส่งออกในรูปแบบ Structured Schema ที่สามารถตรวจสอบและนำไปใช้กับ Planning Engine ได้

---

# 2.3.6 Unknown, Missing and Ambiguous Information

### FR-AMB-01 — Unknown Information

ระบบต้องสามารถแยกข้อมูลที่ยังไม่ทราบออกจากข้อมูลที่มีค่าแน่นอน

### FR-AMB-02 — Ambiguous Information

ระบบต้องสามารถตรวจจับข้อมูลที่สามารถตีความได้มากกว่าหนึ่งแบบ

### FR-AMB-03 — Missing Information

ระบบต้องสามารถตรวจจับข้อมูลที่จำเป็นต่อการวางแผนแต่ยังไม่ได้รับมา

### FR-AMB-04 — Clarification Decision

ระบบต้องตัดสินใจขอ Clarification เมื่อความกำกวม หรือข้อมูลที่ขาดหาย ส่งผลต่อการตีความหรือความเป็นไปได้ในการจัดตาราง

### FR-AMB-05 — No Unnecessary Clarification

ระบบไม่ควรถาม Clarification สำหรับข้อมูลที่ยังไม่จำเป็นต่อการดำเนินการในขั้นตอนปัจจุบัน

ตัวอย่าง:

> “พรุ่งนี้ไปซื้อของขวัญให้แฟน”

สามารถเก็บเป็น Date-Only Activity ได้โดยไม่จำเป็นต้องถามเวลาในทันที หากยังไม่ต้องนำไปวางลงช่วงเวลาเฉพาะ

### FR-AMB-06 — Clarification Response

ผู้ใช้ต้องสามารถตอบคำถาม Clarification และให้ระบบนำคำตอบกลับเข้าสู่ Planning Context เดิมได้

### FR-AMB-07 — Clarification Context

Clarification ต้องสัมพันธ์กับ Planning Request เดิม โดยไม่ต้องสร้างทรัพยากร Clarification แยกเป็น Entity ใน MVP

---

# 2.3.7 Validation and Normalization

### FR-VAL-01 — Schema Validation

ระบบต้องตรวจสอบว่า AI Output มีโครงสร้างตรงตาม Schema ที่กำหนด

### FR-VAL-02 — Domain Validation

ระบบต้องตรวจสอบความถูกต้องตาม Domain Rule ก่อนข้อมูลเข้าสู่ Planning Engine

### FR-VAL-03 — Temporal Normalization

ระบบต้องแปลง Temporal Information ที่อยู่ในรูปแบบ Semantic ให้เป็น Concrete Planning Time ตาม Time Window Policy

### FR-VAL-04 — Exact Time Preservation

Exact Time ที่ผู้ใช้ระบุอย่างชัดเจนต้องไม่ถูกแทนที่ด้วย Time Window โดยไม่จำเป็น

### FR-VAL-05 — Approximate Qualifier

Approximate Time หรือ Approximate Duration ต้องคง Qualifier ว่าข้อมูลดังกล่าวเป็นค่าประมาณ

### FR-VAL-06 — Duration Validation

Duration ที่นำเข้าสู่ Planning Engine ต้องเป็นค่าที่สามารถใช้งานเชิง Scheduling ได้ และต้องผ่าน Domain Validation

### FR-VAL-07 — Date and Time Validation

ระบบต้องตรวจสอบความสอดคล้องของ Date, Start Time และ End Time

### FR-VAL-08 — Invalid Output Handling

หาก AI ส่ง Structured Output ที่ไม่ผ่าน Validation ระบบต้องไม่ส่งข้อมูลดังกล่าวเข้าสู่ Planning Engine โดยตรง

---

# 2.3.8 Time Window

### FR-TW-01 — System Default Windows

ระบบต้องมี System Default Semantic Time Windows ดังนี้:

| Semantic Window | Default     |
| --------------- | ----------- |
| LATE_NIGHT      | 00:00–06:00 |
| MORNING         | 06:00–09:00 |
| LATE_MORNING    | 09:00–12:00 |
| NOON            | 12:00–13:00 |
| AFTERNOON       | 13:00–16:00 |
| EVENING         | 16:00–19:00 |
| NIGHT           | 19:00–24:00 |

### FR-TW-02 — User Override

ผู้ใช้ต้องสามารถกำหนด Override ให้กับ Semantic Time Window บางประเภทได้

### FR-TW-03 — Default Fallback

หากผู้ใช้ไม่ได้กำหนด Override สำหรับ Window ใด ระบบต้องใช้ System Default ของ Window นั้น

### FR-TW-04 — Global Setting

Time Window Configuration เป็น User-level Global Setting ไม่ใช่ค่าที่แตกต่างกันในแต่ละ Activity

### FR-TW-05 — Valid Configuration

ระบบต้องไม่อนุญาต Configuration ที่ขัดกับ Validation Rules เช่น เวลาเริ่มต้นและสิ้นสุดไม่ถูกต้อง หรือการกำหนด Full-Day Partition ที่มีช่องว่างหรือซ้อนกันเมื่อ Policy กำหนดว่าต้องครอบคลุมทั้งวัน

---

# 2.3.9 Planning Constraints and Preferences

### FR-RULE-01 — Hard Constraint

ระบบต้องรองรับ Rule ประเภท Hard Constraint ซึ่งต้องไม่ถูกละเมิดใน Feasible Schedule

### FR-RULE-02 — Preference

ระบบต้องรองรับ Preference ซึ่งเป็น Soft Requirement ที่ใช้ประเมินคุณภาพของ Schedule

### FR-RULE-03 — Rule Classification

แต่ละ Rule ต้องสามารถระบุได้ว่าเป็น:

* HARD
* PREFERENCE

### FR-RULE-04 — Constraint Types

ระบบต้องรองรับ Constraint ที่จำเป็นต่อ MVP เช่น:

* Fixed Time
* Earliest Start
* Time Window
* Deadline
* Availability
* Unavailability
* Duration
* Precedence
* Container Containment
* Context-dependent No-Overlap

### FR-RULE-05 — Preference Handling

Preference ต้องไม่ทำให้ Hard Constraint ถูกละเมิด

### FR-RULE-06 — Requirement Priority

ระบบต้องให้ความสำคัญตามลำดับ:

```text
Hard Constraints
      ↓
Explicit User Requirements
      ↓
Preferences
      ↓
Stability
      ↓
Optional Activities
```

### FR-RULE-07 — No Silent Relaxation

ระบบต้องไม่ลดหรือผ่อน Hard Constraint โดยอัตโนมัติเพื่อให้ได้คำตอบ

### FR-RULE-08 — No Feasible Plan

หากไม่สามารถสร้าง Schedule ที่ผ่าน Hard Constraints ได้ ระบบต้องแจ้งสถานะ `NO_FEASIBLE_PLAN` แทนการสร้างตารางที่ผิดเงื่อนไข

---

# 2.3.10 Initial Planning

### FR-IP-01 — Planning Request

ระบบต้องสามารถนำ Structured Planning Information ไปสร้าง Planning Request

### FR-IP-02 — Relevant Object Selection

ระบบต้องเลือกเฉพาะ Planning Objects, Rules และ Context ที่เกี่ยวข้องกับการวางแผนในครั้งนั้นเข้าสู่ Planning Model

### FR-IP-03 — Planning Horizon

แต่ละ Planning Operation ต้องมี Planning Horizon ที่กำหนดขอบเขตการคำนวณของ Planning Engine

### FR-IP-04 — Calendar Independence

Planning Horizon เป็นขอบเขตการคำนวณ ไม่ใช่ขอบเขตของการเก็บ Activity หรือการแสดง Calendar

### FR-IP-05 — Feasibility

ผลลัพธ์ของ Initial Planning ต้องเป็น Feasible Schedule หรือแจ้งว่าไม่มี Feasible Plan

### FR-IP-06 — Candidate Count

ระบบอาจสร้าง Candidate จำนวน 1–3 ชุด ตามความเหมาะสมของผลลัพธ์

### FR-IP-07 — Meaningful Alternatives

ระบบต้องสร้าง Candidate เพิ่มเมื่อมีแผนที่เป็นไปได้และมีความแตกต่างที่มีความหมาย ไม่ใช่สร้าง Alternative แบบเทียมเพื่อให้ครบจำนวน

### FR-IP-08 — Fixed Schedule

หากข้อกำหนดกำหนดเวลาหรือช่วงเวลาตายตัวจนไม่เหลือทางเลือกที่มีความหมาย ระบบสามารถสร้าง Candidate เพียง 1 ชุดได้

### FR-IP-09 — Stability in Initial Planning

Initial Planning ไม่ต้องบังคับใช้ Stability เป็น Objective หลักเมื่อยังไม่มี Existing Confirmed Schedule ที่ต้องรักษา

---

# 2.3.11 Candidate and Proposal

### FR-PROP-01 — Proposal Creation

ระบบต้องนำผลจาก Planning Engine ไปสร้าง Proposal สำหรับ User Review

### FR-PROP-02 — Candidate

Candidate หมายถึงหนึ่งทางเลือกของ Schedule

### FR-PROP-03 — Proposal

Proposal หมายถึงผลลัพธ์ที่ส่งให้ผู้ใช้ตรวจสอบ และสามารถประกอบด้วย Candidate 1–3 ชุด

### FR-PROP-04 — Proposal Status

Proposal ต้องรองรับสถานะ:

* PENDING
* CONFIRMED
* REJECTED
* INVALIDATED

### FR-PROP-05 — Proposal Review

ผู้ใช้ต้องสามารถตรวจสอบรายละเอียดของ Proposal และ Candidate ที่อยู่ภายในได้

### FR-PROP-06 — Confirm

ผู้ใช้ต้องสามารถ Confirm Candidate ที่ต้องการได้

### FR-PROP-07 — Reject

ผู้ใช้ต้องสามารถ Reject Proposal ได้

### FR-PROP-08 — Feedback

ผู้ใช้ต้องสามารถส่ง Feedback เกี่ยวกับ Proposal เพื่อใช้ประกอบการปรับแผนได้

### FR-PROP-09 — No Direct Confirmation by AI

AI และ Backend Process ต้องไม่สามารถเปลี่ยน Proposal เป็น Confirmed Schedule โดยปราศจาก Explicit User Confirmation

### FR-PROP-10 — Stale Proposal Protection

Proposal ที่สร้างจาก Schedule Version ที่ไม่ใช่ Current Version ต้องไม่สามารถถูก Confirm ได้

### FR-PROP-11 — Confirmed Proposal

Proposal ที่ Confirm แล้วต้องไม่สามารถถูก Confirm ซ้ำจนสร้าง Schedule Version ซ้ำโดยไม่ถูกต้อง

### FR-PROP-12 — Invalidated Proposal

Proposal ที่ถูก Invalidated ต้องไม่สามารถนำไป Confirm ได้

---

# 2.3.12 Human-in-the-Loop and Feedback

### FR-HITL-01 — User Review

ทุก Planning Proposal ต้องผ่านขั้นตอน User Review ก่อนกลายเป็น Confirmed Schedule

### FR-HITL-02 — User Choice

ระบบต้องให้ User สามารถ:

* Confirm
* Reject
* Edit
* Give Feedback

### FR-HITL-03 — Feedback-driven Replanning

เมื่อ Feedback ของ User เปลี่ยน Requirement หรือ Preference ที่มีผลต่อ Planning ระบบต้องสามารถนำ Feedback ไปสร้าง Replanning Request ได้

### FR-HITL-04 — User Control

การตอบสนองของ AI ต่อ Feedback ต้องจบด้วย Proposal ใหม่ ไม่ใช่การแก้ Confirmed Schedule โดยอัตโนมัติ

---

# 2.3.13 Replanning

### FR-REP-01 — Change Detection

ระบบต้องสามารถตรวจจับการเปลี่ยนแปลงที่อาจกระทบ Current Schedule

### FR-REP-02 — Impact Classification

ระบบต้องจำแนกว่าการเปลี่ยนแปลงมีผลต่อ Schedule หรือไม่

### FR-REP-03 — Affected Context

ระบบต้องระบุ Planning Objects และ Constraints ที่เกี่ยวข้องกับการเปลี่ยนแปลง

### FR-REP-04 — Affected Replanning Horizon

ระบบต้องกำหนด Replanning Horizon ให้เหมาะกับบริบทของการเปลี่ยนแปลง

### FR-REP-05 — Unaffected Preservation

Past และ Unaffected Schedule Items ต้องไม่ถูกเปลี่ยนโดยไม่จำเป็น

### FR-REP-06 — Replanning Model

MVP ต้องรองรับการสร้าง Planning Model ใหม่และ Solve ใหม่สำหรับ Replanning

### FR-REP-07 — Requirement Preservation

Replanning ต้องพิจารณา Requirement ใหม่ร่วมกับ Existing Constraints ที่ยังมีผล

### FR-REP-08 — Stability

Replanning ต้องสามารถพิจารณาความแตกต่างจาก Existing Schedule เพื่อหลีกเลี่ยงการเปลี่ยนแปลงที่ไม่จำเป็น

### FR-REP-09 — Proposal-based Replanning

ผลจาก Replanning ต้องกลับมาเป็น Proposal ก่อน Confirmed Schedule จะเปลี่ยน

### FR-REP-10 — No Autonomous Change

ระบบต้องไม่เปลี่ยน Confirmed Schedule โดยอัตโนมัติจากผล Replanning

### FR-REP-11 — Long-range Modification

Activity ที่อยู่นอก Normal Planning Horizon ยังต้องสามารถถูกแก้ไขหรือยกเลิกได้ โดยระบบไม่ถือว่า Calendar Data Range เท่ากับ Planning Horizon

### FR-REP-12 — Horizon Exceeded

หากการ Replanning ต้องใช้ขอบเขตเกิน System Limit ระบบต้องแจ้งให้ผู้ใช้ทราบแทนการตัดข้อมูลหรือผ่อน Constraint แบบเงียบ ๆ

---

# 2.3.14 Manual Schedule Editing

### FR-EDIT-01 — Draft Schedule

การแก้ไข Confirmed Schedule ด้วยตนเองต้องเกิดผ่าน Draft State

### FR-EDIT-02 — Temporary Conflict

Draft สามารถมี Conflict ชั่วคราวระหว่างการแก้ไขได้

### FR-EDIT-03 — Draft Validation

ระบบต้อง Validate Draft ก่อน Confirm

### FR-EDIT-04 — Conflict Detection

ระบบต้องตรวจจับ Hard Conflict ใน Draft

### FR-EDIT-05 — Confirm Blocking

ระบบต้องไม่อนุญาตให้ User Confirm Draft ที่ยังมี Hard Conflict

### FR-EDIT-06 — Manual Confirmation

Draft ที่ผ่าน Validation ต้องสามารถถูก Confirm และกลายเป็น Schedule Version ใหม่

### FR-EDIT-07 — Historical Preservation

การ Manual Edit ต้องไม่แก้ไข Historical Schedule Version เดิม

---

# 2.3.15 Schedule Versioning

### FR-SCH-01 — Confirmed Schedule

ระบบต้องมีแนวคิด Current Confirmed Schedule สำหรับ User

### FR-SCH-02 — Immutable Version

Schedule Version ที่ถูกสร้างแล้วต้องไม่ถูกแก้ไขย้อนหลัง

### FR-SCH-03 — New Version on Confirmation

ทุกการเปลี่ยน Confirmed Schedule ผ่าน Proposal Confirmation หรือ Manual Confirmation ต้องสร้าง Schedule Version ใหม่

### FR-SCH-04 — Current Version

ผู้ใช้แต่ละคนต้องมี Current Schedule Version ได้เพียงหนึ่ง Version

### FR-SCH-05 — Historical Versions

ระบบต้องเก็บ Historical Versions ตามขอบเขตที่กำหนด เพื่อให้สามารถตรวจสอบสถานะก่อนหน้าได้

### FR-SCH-06 — Schedule Item

Schedule Item ต้องเป็นผลจากการนำ Activity ไปวางใน Schedule และต้องไม่ถูกตีความว่าเป็น Activity Entity เดียวกัน

---

# 2.3.16 Calendar

### FR-CAL-01 — Calendar Views

ระบบต้องรองรับอย่างน้อย:

* Year View
* Month View
* Day View

### FR-CAL-02 — Day Timeline

Day View ต้องแสดงข้อมูลในลักษณะ Time-based Timeline

### FR-CAL-03 — All-Day / Unscheduled

Activity ที่มีเพียง Date แต่ยังไม่มีเวลาที่จัดวาง ต้องแสดงในพื้นที่ All Day / Unscheduled และไม่ควรถูกตีความว่าเริ่มต้นตาม Notification Time

### FR-CAL-04 — Today Navigation

ระบบต้องมีช่องทางให้ผู้ใช้กลับไปยังวันที่ปัจจุบันได้โดยสะดวก

### FR-CAL-05 — Activity Creation

ผู้ใช้ต้องสามารถเริ่มต้นการสร้าง Activity จาก Calendar ได้

### FR-CAL-06 — Internal Calendar

Calendar ของ LONGTUA เป็น Calendar ภายในระบบ

### FR-CAL-07 — External Calendar Exclusion

MVP ไม่รองรับการ Sync กับ Apple Calendar, Google Calendar หรือ Device Calendar

---

# 2.3.17 Notification

### FR-NOTI-01 — Confirmed Schedule as Source

Notification ต้องสร้างจาก Confirmed Schedule เท่านั้น

### FR-NOTI-02 — Date-Only Notification Default

Activity ที่มีวันที่แต่ไม่มีเวลาต้องใช้ Date-Only Notification Default ของระบบ

### FR-NOTI-03 — Time-Specific Notification Default

Activity ที่มีเวลาชัดเจนต้องใช้ Time-Specific Notification Default ของระบบตาม Notification Policy

### FR-NOTI-04 — User Notification Settings

ผู้ใช้ต้องสามารถแก้ไข Notification Defaults ได้

### FR-NOTI-05 — Activity Override

Activity เฉพาะรายการต้องสามารถมี Notification Override ที่มี Priority สูงกว่า System Default

### FR-NOTI-06 — Notification Time Constraint

Notification Time ต้องไม่อยู่หลัง Activity Start Time

### FR-NOTI-07 — Schedule Change

เมื่อ Confirmed Schedule เปลี่ยน Mobile Application ต้องยกเลิก Notification ที่ไม่สอดคล้องกับ Schedule ปัจจุบัน และสร้าง Notification ตามเวลาที่ถูกต้อง

### FR-NOTI-08 — Custom Override Conflict

หาก Rescheduling ทำให้ Custom Notification Time ไม่ถูกต้อง ระบบต้องแจ้ง User และต้องไม่แก้ค่าดังกล่าวอย่างเงียบ ๆ

### FR-NOTI-09 — Local Notification

MVP ใช้ Local System Notification เป็นหลัก และไม่ต้องพึ่ง Remote Push Notification

### FR-NOTI-10 — Notification as Derived State

Notification เป็น Derived State จาก Confirmed Schedule ไม่ใช่ Source of Truth ของ Schedule

### FR-NOTI-11 — Notification Failure

หาก Notification ไม่สามารถสร้างหรืออัปเดตได้ ระบบต้องไม่ Rollback Confirmed Schedule โดยอัตโนมัติ

---

# 2.3.18 User Settings

### FR-SET-01 — Time Window Settings

ผู้ใช้ต้องสามารถจัดการ User-defined Semantic Time Windows ได้

### FR-SET-02 — Notification Settings

ผู้ใช้ต้องสามารถกำหนด Notification Defaults ได้

### FR-SET-03 — User-specific Settings

Settings ต้องถูกแยกตาม User และต้องไม่ส่งผลต่อ User อื่น

### FR-SET-04 — Default Fallback

การไม่กำหนด User Override ต้องทำให้ระบบย้อนกลับไปใช้ System Default ตาม Policy

---

# 2.3.19 Planning Request Lifecycle

Planning Request ต้องรองรับ Lifecycle ดังนี้:

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

### FR-REQ-01

ระบบต้องสามารถติดตามสถานะของ Planning Request ได้

### FR-REQ-02

Planning Request ที่ต้องการข้อมูลเพิ่มต้องเปลี่ยนเป็น `NEEDS_CLARIFICATION`

### FR-REQ-03

คำตอบ Clarification ต้องสามารถทำให้ Request กลับไปยัง Processing ได้

### FR-REQ-04

คำขอที่ประมวลผลสำเร็จต้องจบด้วย `COMPLETED`

### FR-REQ-05

ความผิดพลาดที่ไม่สามารถประมวลผลต่อได้ต้องจบด้วย `FAILED` พร้อม Error Information ที่เหมาะสม

---

# 2.4 Domain and Business Rules

ส่วนนี้เป็นกฎที่ **ทุก Module ต้องปฏิบัติตามร่วมกัน** ไม่ใช่เฉพาะ Backend หรือ Planning Engine

## BR-01 — User Final Decision

User ต้องเป็นผู้ตัดสินใจขั้นสุดท้ายก่อน Confirmed Schedule เปลี่ยน

## BR-02 — AI Does Not Schedule

AI/NLP สามารถเข้าใจและแปลงข้อมูล แต่ไม่สามารถเป็นผู้กำหนด Schedule โดยตรง

## BR-03 — Planner Does Not Interpret Natural Language

Planning Engine ต้องรับ Planning Representation ที่ผ่าน Validation/Normalization แล้ว

## BR-04 — Proposed ≠ Confirmed

Proposal และ Confirmed Schedule เป็น State ที่แตกต่างกัน

## BR-05 — Confirmation Creates New Version

Confirmed Schedule ที่เปลี่ยนต้องผ่าน Explicit Confirmation และสร้าง Schedule Version ใหม่

## BR-06 — Notification From Confirmed Schedule

เฉพาะ Confirmed Schedule เท่านั้นที่มีสิทธิ์สร้าง Notification

## BR-07 — Hard Constraints Cannot Be Silently Relaxed

ระบบต้องไม่ลดความเข้มงวดของ Hard Constraint เพื่อให้ได้ Feasible Plan โดยไม่แจ้ง User

## BR-08 — Unknown ≠ Ambiguous

ค่าที่ไม่มีข้อมูลไม่ควรถูกตีความเท่ากับข้อมูลที่มีหลายความหมาย

## BR-09 — Unsupported ≠ Missing

ความสามารถที่ระบบไม่รองรับต้องไม่ถูกตีความว่าเป็นเพียงข้อมูลที่ขาดหาย

## BR-10 — No Invented Planning-critical Data

Planning-critical Information ที่ไม่มีหลักฐานรองรับต้องไม่ถูกสร้างขึ้นเอง

## BR-11 — Container and Child

Container สามารถ overlap กับ Child ที่เป็นสมาชิกได้ตาม Membership Semantics

## BR-12 — Activity Overlap

Activity ที่ใช้ Execution Context เดียวกันไม่สามารถ overlap กันใน MVP

## BR-13 — Unavailability Conflict

Activity ที่ overlap กับ Unavailability ถือเป็น Hard Conflict

## BR-14 — Adjacent Intervals

ช่วงเวลาที่ต่อกันพอดี เช่น:

```text
09:00–10:00
10:00–11:00
```

ไม่ถือว่า Overlap

ระบบใช้ Semantics แบบ Half-Open Interval:

```text
[start, end)
```

## BR-15 — Calendar Data Range ≠ Planning Horizon

Calendar สามารถเก็บและแสดงข้อมูลระยะยาวได้ โดยไม่จำเป็นต้องนำข้อมูลทั้งหมดเข้าสู่ CP-SAT ในทุก Operation

## BR-16 — Replanning Horizon Is Context-dependent

Replanning Horizon สามารถแตกต่างจาก Normal Planning Horizon ได้ตามบริบทของการเปลี่ยนแปลง

## BR-17 — Historical Schedule Is Immutable

Historical Schedule Version ไม่สามารถถูกแก้ไขย้อนหลัง

## BR-18 — Stale Proposal Cannot Override Current Schedule

Proposal ที่อ้างอิง Schedule Version เก่าต้องไม่สามารถเขียนทับ Current Schedule ได้

## BR-19 — No Dummy Candidates

Candidate ต้องมีความแตกต่างและคุณค่าที่มีความหมายต่อการตัดสินใจของ User

## BR-20 — No Autonomous Confirmed Schedule Modification

Backend หรือ AI Process ไม่สามารถเปลี่ยน Confirmed Schedule เองจากผลการประมวลผลภายใน

---

# 2.5 Non-Functional Requirements

## 2.5.1 Security Requirements

### NFR-SEC-01

Password ต้องถูกจัดเก็บด้วย Password Hashing Algorithm ที่เหมาะสม โดย MVP ใช้ Argon2id

### NFR-SEC-02

Access Token ต้องมีอายุจำกัดตาม Authentication Policy

### NFR-SEC-03

Refresh Session ต้องรองรับ Absolute Session Lifetime

### NFR-SEC-04

Email Verification Token ต้องเป็น One-Time Token และมีอายุจำกัด

### NFR-SEC-05

Password Reset Token ต้องเป็น One-Time Token และมีอายุจำกัด

### NFR-SEC-06

การเปลี่ยน Password ต้องสามารถเพิกถอน Existing Refresh Sessions ตาม Policy

### NFR-SEC-07

Logout ต้องยกเลิก Session/Device State ที่เกี่ยวข้องตาม Policy

### NFR-SEC-08

ระบบต้องตรวจสอบ Authorization ฝั่ง Server ทุกครั้งที่เข้าถึง User-owned Resource

### NFR-SEC-09

AI Provider Key และ Database Credentials ต้องอยู่ฝั่ง Backend และต้องไม่ฝังใน Mobile Application

### NFR-SEC-10

Secret และ Credential ต้องไม่ถูก Commit ลง Source Repository

### NFR-SEC-11

Protected Network Communication ใน Demo/Production ต้องใช้ HTTPS

### NFR-SEC-12

ระบบต้องมี Rate Limiting สำหรับ Authentication และ Operations ที่มีความเสี่ยงต่อ Abuse เช่น Planning/AI-related Requests

### NFR-SEC-13

ระบบต้องไม่บันทึก Sensitive Information ลง Log โดยไม่จำเป็น

---

# 2.5.2 Reliability and Consistency

### NFR-REL-01

Confirmed Schedule ต้องเปลี่ยนผ่าน Explicit User Confirmation เท่านั้น

### NFR-REL-02

Schedule Version ที่ถูกสร้างแล้วต้องไม่ถูกแก้ไข

### NFR-REL-03

Stale Proposal ต้องถูกปฏิเสธก่อนทำให้ Current Schedule เปลี่ยน

### NFR-REL-04

Side-effecting Operations ที่มีความเสี่ยงต่อการทำซ้ำต้องรองรับ Idempotency ตาม API Policy

### NFR-REL-05

Database Transaction ต้องสามารถ Rollback ได้เมื่อการเขียนข้อมูลที่เกี่ยวข้องล้มเหลว

### NFR-REL-06

การล้มเหลวของ Notification ต้องไม่ทำให้ Schedule สูญเสียความถูกต้อง

### NFR-REL-07

ระบบต้องไม่สร้าง State ที่ขัดแย้งระหว่าง Proposal, Schedule Version และ Current Schedule

---

# 2.5.3 Performance

ตัวเลขจริงจะไม่ถูกกำหนดโดยการคาดเดา แต่จะกำหนดจาก Performance Benchmark

### NFR-PERF-01

Planning Operation ต้องมี Solver Time Limit

### NFR-PERF-02

Planning Operation ต้องมี Maximum Planning Horizon

### NFR-PERF-03

Planning Operation ต้องมี Maximum Number of Planning Objects

### NFR-PERF-04

AI Request ต้องมี Maximum Input Size ที่เหมาะสม

### NFR-PERF-05

API ที่คืนข้อมูลจำนวนมากต้องรองรับ Pagination

### NFR-PERF-06

ระบบต้องสามารถวัด Planning Runtime และ Resource Usage ได้

### NFR-PERF-07

ระบบต้องใช้ Performance Benchmark เพื่อกำหนด Operational Limit ที่เหมาะสม

### NFR-PERF-08

ระบบต้องไม่ตัด Activity หรือ Constraint ออกจาก Planning Model โดยไม่แจ้ง User เพียงเพื่อให้อยู่ภายใต้ Performance Limit

---

# 2.5.4 Maintainability

### NFR-MNT-01

ระบบต้องแยก AI/NLP และ Planning Engine เป็น Module ที่มี Boundary ชัดเจน

### NFR-MNT-02

AI Provider ต้องสามารถเปลี่ยน Provider ผ่าน Provider Adapter โดยไม่จำเป็นต้องเปลี่ยน Business Logic หลัก

### NFR-MNT-03

Database Schema ต้องบริหารด้วย Migration Tool

### NFR-MNT-04

API Contract ต้องสามารถตรวจสอบได้จาก Schema ที่กำหนด

### NFR-MNT-05

Domain Rules ที่สำคัญต้องไม่กระจายอยู่เฉพาะใน UI

---

# 2.5.5 Usability

### NFR-USE-01

ผู้ใช้ต้องสามารถเข้าใจสถานะของกระบวนการ Planning ได้ เช่น Processing, Clarification, Proposal และ Confirmed

### NFR-USE-02

ระบบต้องแยก Proposal ออกจาก Confirmed Schedule อย่างชัดเจน

### NFR-USE-03

Conflict จาก Manual Edit ต้องถูกแสดงในลักษณะที่ผู้ใช้สามารถระบุสิ่งที่ต้องแก้ไขได้

### NFR-USE-04

ระบบไม่ควรบังคับให้ User ตอบ Clarification ที่ไม่มีความจำเป็นต่อการดำเนินการปัจจุบัน

### NFR-USE-05

User ต้องสามารถยกเลิกหรือปฏิเสธ Proposal ได้

---

# 2.5.6 Testability

### NFR-TEST-01

AI/NLP Component ต้องสามารถทดสอบแยกจาก Planning Engine

### NFR-TEST-02

Planning Engine ต้องสามารถทดสอบด้วย Structured Planning Inputs โดยไม่ต้องเรียก AI

### NFR-TEST-03

API ต้องสามารถทดสอบในระดับ Unit และ Integration

### NFR-TEST-04

Critical Domain Rules ต้องมี Automated Tests

### NFR-TEST-05

Core End-to-End Flow ต้องสามารถทดสอบตั้งแต่ Natural Language Input จนถึง Confirmed Schedule

---

# 2.6 MVP Scope Constraints

ข้อกำหนดต่อไปนี้อยู่ภายนอก MVP และไม่ควรถูกนำเข้ามาโดยปริยายระหว่าง Implementation

| Capability                    | MVP |
| ----------------------------- | --- |
| Natural Language Text Input   | ✅   |
| AI/NLP Extraction             | ✅   |
| Clarification                 | ✅   |
| Constraint-Based Planning     | ✅   |
| CP-SAT                        | ✅   |
| Preferences                   | ✅   |
| Candidate Plans               | ✅   |
| Human-in-the-Loop             | ✅   |
| Adaptive Replanning           | ✅   |
| Manual Draft Edit             | ✅   |
| Internal Calendar             | ✅   |
| Local Notifications           | ✅   |
| Availability / Unavailability | ✅   |
| Semantic Time Windows         | ✅   |
| Voice / Speech-to-Text        | ❌   |
| Apple Calendar Sync           | ❌   |
| Google Calendar Sync          | ❌   |
| Device Calendar Sync          | ❌   |
| Remote Push Notification      | ❌   |
| Concurrent Multitasking       | ❌   |
| Activity Splitting            | ❌   |
| Complex Recurrence            | ❌   |
| Traffic / Route Optimization  | ❌   |
| Reinforcement Learning        | ❌   |
| Autonomous Life Management    | ❌   |
| Full Behavioral Learning      | ❌   |
| Social Login                  | ❌   |
| MFA                           | ❌   |
| Microservices                 | ❌   |

---

# 2.7 System Limits

ระบบกำหนดให้มี Operational Limits แต่ค่าจริงจะต้องมาจากการทดลอง

```text
MAX_PLANNING_HORIZON
MAX_PLANNING_OBJECTS
MAX_SOLVER_TIME
MAX_AI_INPUT_SIZE
API PAGE SIZE
RATE LIMIT
```

หลักการคือ:

1. Limit ต้องวัดได้
2. Limit ต้องไม่ทำให้ Hard Constraint ถูกละเลย
3. Limit ต้องไม่ทำให้ข้อมูลถูกตัดทิ้งโดยไม่มีการแจ้ง User
4. Limit ควรสอดคล้องกับ Performance Benchmark

---

# 2.8 Key User Flows

## Flow A — Initial AI Planning

```text
User
 ↓
Enter Natural Language
 ↓
Create Planning Request
 ↓
AI/NLP
 ↓
Validation / Normalization
 ↓
Planning Representation
 ↓
Planning Engine
 ↓
Candidate Plan(s)
 ↓
Proposal
 ↓
User Review
 ↓
Confirm
 ↓
New Schedule Version
 ↓
Local Notification
```

---

## Flow B — Clarification

```text
Natural Language
 ↓
AI/NLP
 ↓
Ambiguity / Missing Critical Information
 ↓
NEEDS_CLARIFICATION
 ↓
User Response
 ↓
Original Planning Context + Response
 ↓
Processing
 ↓
Planning
 ↓
Proposal
```

---

## Flow C — No Feasible Plan

```text
Planning Request
 ↓
Planning Engine
 ↓
Hard Constraints Conflict
 ↓
No Feasible Solution
 ↓
NO_FEASIBLE_PLAN
```

ระบบต้องไม่สร้าง Schedule ที่ผิด Hard Constraint เพียงเพื่อคืนผลลัพธ์ให้ User

---

## Flow D — Replanning

```text
Current Confirmed Schedule
 ↓
New Activity / Changed Activity / New Constraint / Feedback
 ↓
Impact Detection
 ↓
Affected Context
 ↓
Affected Replanning Horizon
 ↓
Rebuild Planning Model
 ↓
Solve
 ↓
Proposal
 ↓
User Review
 ↓
Confirm
 ↓
New Schedule Version
 ↓
Notification Update
```

---

## Flow E — Manual Edit

```text
Confirmed Schedule
 ↓
Manual Edit
 ↓
Draft
 ↓
Validation
 ├── Conflict
 │     ↓
 │  Fix Draft
 │
 └── Valid
       ↓
    Confirm
       ↓
New Schedule Version
```

---

# 2.9 Acceptance Criteria

## AC-01 — Natural Language to Schedule

เมื่อผู้ใช้ส่ง Input ที่มีข้อมูลเพียงพอ ระบบต้องสามารถ:

1. รับ Input
2. Extract Structured Planning Information
3. Validate ข้อมูล
4. สร้าง Planning Model
5. Solve
6. แสดง Proposal
7. รอ User Confirmation

โดยไม่เปลี่ยน Confirmed Schedule ก่อน User Confirm

---

## AC-02 — Ambiguous Time

เมื่อ Input มีเวลาที่กำกวม เช่น:

> “พรุ่งนี้ 6 โมงไปวิ่ง”

และระบบไม่มี Context ที่เพียงพอในการระบุว่าเป็น 06:00 หรือ 18:00 ระบบต้องเข้าสู่ Clarification Flow แทนการเดาเวลาเอง

---

## AC-03 — Date-Only Activity

เมื่อผู้ใช้ระบุเพียงวันที่ เช่น:

> “พรุ่งนี้ซื้อของขวัญให้แฟน”

ระบบสามารถสร้าง Date-Only Activity โดยไม่จำเป็นต้องถามเวลาในทันที หากการดำเนินการปัจจุบันไม่ต้องใช้เวลาที่แน่นอน

---

## AC-04 — Hard Conflict

เมื่อ Activity สองรายการมี Execution Context เดียวกันและมีช่วงเวลาทับกัน ระบบต้องไม่ยอมรับ Schedule ดังกล่าวเป็น Feasible Schedule

---

## AC-05 — Unavailability

เมื่อ Activity overlap กับ Unavailability ระบบต้องถือว่าเป็น Hard Conflict และไม่อนุญาตให้ Confirm Schedule ที่ละเมิดเงื่อนไข

---

## AC-06 — Fixed Time

เมื่อผู้ใช้กำหนด Activity แบบ Fixed Time ระบบต้องไม่เลื่อนเวลานั้นเพียงเพื่อสร้าง Candidate เพิ่ม

หากไม่มี Alternative ที่มีความหมาย ต้องสามารถคืน Candidate เพียง 1 ชุดได้

---

## AC-07 — Replanning

เมื่อ Activity ที่อยู่ใน Current Schedule ถูกเปลี่ยนเวลา ระบบต้องตรวจสอบผลกระทบและสามารถสร้าง Proposal ใหม่โดยไม่เปลี่ยน Current Confirmed Schedule จนกว่าผู้ใช้จะ Confirm

---

## AC-08 — Manual Conflict

เมื่อผู้ใช้แก้ไข Draft แล้วทำให้เกิด Hard Conflict:

```text
Conflict = TRUE
Confirm = Disabled
```

ผู้ใช้ต้องแก้ Conflict ก่อน Confirm

---

## AC-09 — Stale Proposal

เมื่อ Proposal ถูกสร้างจาก Schedule Version V1 และ Current Schedule เปลี่ยนเป็น V2 Proposal ของ V1 ต้องไม่สามารถ Confirm เพื่อเขียนทับ V2 ได้

---

## AC-10 — Notification Update

เมื่อ Confirmed Schedule เปลี่ยนจาก:

```text
09:00 Activity
```

เป็น:

```text
12:00 Activity
```

ระบบ Mobile ต้องยกเลิก Notification ที่สัมพันธ์กับเวลาเดิม และสร้าง Notification ใหม่ตาม Effective Schedule

---

# 2.10 Requirement Priorities

เพื่อใช้บริหาร MVP Requirements ถูกแบ่งเป็น:

### Must Have

ฟังก์ชันที่จำเป็นต่อ Core Contribution ของโครงการ เช่น:

* Natural Language Input
* AI/NLP Extraction
* Validation
* Clarification
* Constraint-Based Planning
* Preferences
* Proposal
* Human-in-the-Loop
* Replanning
* Schedule Versioning
* Internal Calendar
* Local Notification

### Supporting

ฟังก์ชันที่จำเป็นต่อการใช้งานระบบให้สมบูรณ์ เช่น:

* Authentication
* Availability / Unavailability
* Time Window Settings
* Notification Settings
* Manual Activity Management
* Manual Schedule Editing

### Future

ความสามารถที่ไม่ได้อยู่ใน MVP และต้องไม่ถูกนำเข้ามาเป็น Requirement แฝง เช่น:

* Voice Input
* External Calendar Integration
* Advanced Behavioral Adaptation
* Autonomous Planning
* Complex Route Optimization
* Concurrent Multitasking
* Remote Push Notification

---

# 2.11 Requirement Traceability

Requirements หลักของ LONGTUA เชื่อมโยงกับ Research Questions ดังนี้:

| Research Question                                                    | Requirements             |
| -------------------------------------------------------------------- | ------------------------ |
| RQ1 — Natural Language → Structured Planning Information             | FR-PLN, FR-AMB, FR-VAL   |
| RQ2 — Constraints / Preferences → Feasible and User-aligned Schedule | FR-RULE, FR-IP, FR-AV    |
| RQ3 — Adapt / Re-plan when circumstances change                      | FR-REP, FR-SCH           |
| RQ4 — User Feedback improves alignment                               | FR-HITL, FR-PROP, FR-REP |

และเชื่อมต่อไปยัง Evaluation:

| Evaluation            | Requirements              |
| --------------------- | ------------------------- |
| E1 NLP                | FR-PLN, FR-AMB, FR-VAL    |
| E2 Initial Planning   | FR-RULE, FR-IP            |
| E3 Replanning         | FR-REP                    |
| E4 Candidates         | FR-IP, FR-PROP            |
| E5 Human-in-the-Loop  | FR-HITL, FR-EDIT, FR-PROP |
| E6 End-to-End         | Core Requirements ทั้งหมด |
| Performance Benchmark | NFR-PERF                  |

---

# 2.12 Requirement Freeze Rules

เมื่อ Requirement นี้ถูกนำไปใช้เป็น Baseline แล้ว การเปลี่ยนแปลงต้องไม่เกิดโดยการแก้ Code เพียงอย่างเดียว

หากต้องการเปลี่ยน Behavior หลัก ต้องตรวจสอบผลกระทบต่อ:

```text
Requirements
 ↓
Architecture
 ↓
Domain Model
 ↓
Database
 ↓
API
 ↓
AI/NLP
 ↓
Planning
 ↓
Replanning
 ↓
UI
 ↓
Evaluation
```

โดยเฉพาะหลักการต่อไปนี้ถือเป็น **Core Invariants** และไม่ควรเปลี่ยนโดยไม่มีการทบทวน Design ทั้งระบบ:

> User เป็น Final Decision Maker
> AI Understands, Planner Schedules
> Proposed Schedule ≠ Confirmed Schedule
> Only Explicit Confirmation changes Confirmed Schedule
> Only Confirmed Schedule generates Notification
> Hard Constraints are never silently relaxed
> Historical Schedule Versions are immutable
> Stale Proposals cannot override Current Schedule
