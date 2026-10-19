# 17. Cross-Document Consistency Review & Design Lock

## 17.1 Purpose

เอกสารนี้ใช้ตรวจสอบความสอดคล้องของเอกสาร System Design ทั้ง 16 ฉบับของ LONGTUA และกำหนด semantic decisions ที่ต้องใช้เป็น Source of Truth ร่วมกันก่อนเริ่ม Figma, Task Breakdown และ Coding

เอกสารที่ตรวจ:

```text
01 Project Overview
02 Requirements Specification
03 System Architecture
04 Domain & Planning Model
05 AI / NLP Design
06 Planning Engine Design
07 Replanning Design
08 Schedule & Notification Design
09 Database Design
10 API Design
11 Security Design
12 UI / UX Behavior Specification
13 Testing & Evaluation Design
14 Development & Implementation Specification
15 Limitations & Future Work
16 Related Theories, Research, and References
```

เป้าหมายของการตรวจไม่ใช่การเพิ่ม feature แต่เป็นการตอบคำถาม:

> **เอกสารทุกฉบับกำลังพูดถึงระบบเดียวกัน และเมื่อ implement จริงจะเกิด behavior เดียวกันหรือไม่**

---

# 17.2 Consistency Status

ภาพรวม:

```text id="w9j2r4"
Architecture          ✅ Consistent
Domain Model          ✅ Consistent
AI / NLP Boundary     ✅ Consistent
Planning Boundary     ✅ Consistent
Schedule Model        ✅ Consistent
Notification Model    ✅ Consistent
Database Structure    ✅ Mostly Consistent
API Behavior          ⚠ Needs semantic lock
UI Behavior           ⚠ Needs semantic lock
Testing               ✅ Consistent
Future Work           ✅ Consistent
References            ⚠ Minor metadata correction
```

ดังนั้นยังไม่ควรบอกว่า “ทุกอย่าง 100% locked” จนกว่าประเด็นต่อไปนี้จะถูกกำหนดเป็นมาตรฐานกลาง

---

# 17.3 Master Terminology

คำศัพท์ต่อไปนี้ให้ถือเป็น terminology กลางของทั้ง project

| Term               | Official Meaning                                                |
| ------------------ | --------------------------------------------------------------- |
| Planning Object    | Object ที่เกี่ยวข้องกับ planning ได้แก่ Activity หรือ Container |
| Activity           | หน่วยงาน/เหตุการณ์ที่ต้องใช้ execution capacity                 |
| Container          | ช่วงเวลาหรือ commitment ที่สามารถมี child activities            |
| Availability       | ช่วงเวลาที่ planner สามารถวาง activity ได้                      |
| Unavailability     | ช่วงเวลาที่ planner ห้ามวาง activity                            |
| Planning Request   | คำขอให้ระบบตีความและ/หรือวางแผน                                 |
| Proposal           | ผลลัพธ์จาก Planning ที่ยังไม่ใช่ Confirmed Schedule             |
| Candidate          | หนึ่งทางเลือกของ Proposal                                       |
| Draft              | การแก้ไขที่ยังไม่ถูก Confirm                                    |
| Confirmed Schedule | ตารางที่ user ยืนยันแล้วและเป็น source of truth                 |
| Schedule Version   | Immutable snapshot ของ Confirmed Schedule                       |
| Re-planning        | การสร้าง Proposal ใหม่จาก Current Schedule + New Information    |
| Clarification      | คำถามเพิ่มเติมเมื่อข้อมูลไม่เพียงพอหรือกำกวมในจุดที่มีผล        |
| Feedback           | ข้อความ/คำสั่งของ user ที่ใช้ปรับ planning requirement          |

---

# 17.4 State Ownership Principle

หนึ่งในหลักที่ต้องใช้ทั้งระบบ:

```text id="p8p3ay"
AI
    → Understanding

Planner
    → Scheduling

Proposal
    → Candidate Result

Draft
    → Temporary User Modification

Confirmed Schedule
    → Source of Truth
```

ไม่มี module ใดสามารถข้าม boundary เหล่านี้ได้โดยตรง

---

# 17.5 Decision 01 — Planning Request State

### Problem

ในบางเอกสารมีการใช้ state ต่างกัน เช่น:

```text
RECEIVED
PROCESSING
NEEDS_CLARIFICATION
PLANNING
PROPOSED
COMPLETED
FAILED
```

ขณะที่บางส่วนใช้คำว่า:

```text
PROPOSED
```

เป็นผลลัพธ์ และบางที่มี semantics คล้าย lifecycle อื่น

### Final Decision

Planning Request lifecycle ให้ใช้:

```text id="18m4qz"
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

`PROPOSED` หมายถึง request ประมวลผลจนสร้าง Proposal สำเร็จ

`COMPLETED` ไม่จำเป็นสำหรับ MVP เพราะ Proposal และ Confirmed Schedule เป็นคนละ lifecycle

การ Confirm Proposal ไม่ได้ทำให้ Planning Request กลายเป็น Schedule โดยตรง

ดังนั้น:

```text
Planning Request
≠
Proposal
≠
Schedule Version
```

---

# 17.6 Decision 02 — Proposal State

Proposal lifecycle เป็น:

```text id="r50k0x"
PENDING
   ├── CONFIRMED
   ├── REJECTED
   └── INVALIDATED
```

### Meaning

#### PENDING

Proposal ยังสามารถ review ได้

#### CONFIRMED

User confirm สำเร็จและ Proposal ถูกนำไปสร้าง Schedule Version

#### REJECTED

User ปฏิเสธ Proposal

#### INVALIDATED

Proposal ไม่สามารถใช้ได้อีก เช่น Current Schedule Version เปลี่ยนไปแล้ว

ไม่มี:

```text
EXPIRED
```

---

# 17.7 Decision 03 — Meaning of parent_request_id

`parent_request_id` ต้องไม่ถูกตีความเป็น “ทุก request ที่ต่อเนื่องกัน”

ให้ใช้สำหรับ request lineage ที่เป็นผลมาจาก request ก่อนหน้า เช่น:

```text id="8r5fyi"
Original Planning Request
        ↓
Feedback / Re-planning Request
        ↓
New Planning Request
```

สำหรับ clarification:

```text id="4d4z0g"
Original Request
        ↓
NEEDS_CLARIFICATION
        ↓
Clarification Response
        ↓
Continue same logical Planning Request
```

ดังนั้น clarification response ไม่จำเป็นต้องสร้าง request ใหม่ทุกครั้ง

`parent_request_id` จึงใช้เมื่อเกิด request ใหม่จริงที่ต้องการเก็บ lineage

---

# 17.8 Decision 04 — Planning-affecting Activity Changes

นี่เป็นหนึ่งในประเด็นสำคัญที่สุด

### Problem

ถ้า Activity ที่อยู่ใน Current Schedule ถูกแก้:

```text
19:00 → 21:00
```

แต่ Activity record ถูก update ทันที ขณะที่ user ยังไม่ได้ Confirm Re-planning Proposal จะทำให้:

```text
Activity Data
≠
Confirmed Schedule
```

และอาจทำให้ Current Schedule ดูไม่สอดคล้องกับ constraint ใหม่

### Final Decision

แยกการแก้ Activity เป็น 2 ประเภท

#### A. Non-planning Change

ตัวอย่าง:

* Title
* Description
* metadata ที่ไม่กระทบ scheduling

สามารถ update ได้โดยตรง

#### B. Planning-affecting Change

ตัวอย่าง:

* Date
* Start Time
* End Time
* Duration
* Deadline
* Fixed Time
* Planning-related constraints

ต้องเข้าสู่ planning flow:

```text id="1ayb26"
Current Activity
      ↓
Change Request
      ↓
Planning
      ↓
Proposal
      ↓
User Review
      ↓
Confirm
      ↓
Apply Activity Change
+
Create New Schedule Version
```

ดังนั้น **Activity change และ Schedule change ต้อง commit ร่วมกันตอน Confirm**

ก่อน Confirm:

```text
Current Activity = unchanged
Current Schedule = unchanged
```

นี่เป็นการรักษา consistency ระหว่าง Activity State และ Schedule State

---

# 17.9 Decision 05 — Planning-affecting Availability Changes

ใช้หลักเดียวกับ Activity

หาก Availability / Unavailability change ไม่มีผลต่อ Current Schedule:

```text
Save Rule
```

สามารถดำเนินการได้โดยตรง

แต่ถ้า change กระทบ Current Schedule เช่น:

```text
เพิ่ม Unavailable
13:00–16:00

และมี Activity
14:00–15:00
```

ต้องเข้า:

```text id="3j5qvp"
Change
 ↓
Conflict / Replanning
 ↓
Proposal
 ↓
User Review
 ↓
Confirm
```

ก่อน Confirm:

```text
Confirmed Schedule
= unchanged
```

เมื่อ Confirm สำเร็จ:

```text
Availability Rule
+
Schedule Version
```

ต้องถูก commit ใน operation เดียวกันตาม transaction boundary ที่เหมาะสม

---

# 17.10 Decision 06 — Availability Semantics

กำหนด behavior กลาง:

### No Availability Rules

หมายถึง:

> ไม่มี explicit availability restriction

planner สามารถพิจารณาเวลาภายใน planning horizon ได้ โดยยังต้องเคารพ Unavailability และ constraints อื่น

### Availability Exists

Activity ต้องถูกจัดให้อยู่ภายใน Available window ที่เกี่ยวข้อง

### Unavailability Precedence

หาก Available และ Unavailable overlap:

```text
AVAILABLE
+
UNAVAILABLE
```

ให้:

```text
UNAVAILABLE wins
```

ตัวอย่าง:

```text
Available
08:00–17:00

Unavailable
13:00–14:00
```

ผลที่ planner ใช้:

```text
Allowed:
08:00–13:00
14:00–17:00
```

---

# 17.11 Decision 07 — Activity Status vs Schedule Status

ไม่ควรเก็บ:

```text
SCHEDULED
UNSCHEDULED
```

เป็น Activity lifecycle state หากสามารถ derive จาก Schedule ได้

### Activity Lifecycle

ใช้แนวคิด:

```text
ACTIVE
CANCELLED
```

และ:

```text
deleted_at
```

ใช้เป็น soft-delete mechanism

### Schedule State

การที่ Activity มี placement หรือไม่ให้ดูจาก:

```text
Schedule Items
```

ดังนั้น:

```text
Activity Status
≠
Scheduling Status
```

ตัวอย่าง:

```text
ACTIVE Activity
+
No Schedule Item
=
Unscheduled
```

---

# 17.12 Decision 08 — Date-only Activity

Date-only Activity ยังคง valid

ตัวอย่าง:

> “พรุ่งนี้ซื้อของขวัญ”

ข้อมูล:

```text id="6n6e2r"
Date = known
Time = UNKNOWN
Duration = UNKNOWN
```

ไม่ต้องถามทันทีถ้ายังไม่จำเป็นต่อ operation

UI:

```text
All Day / Unscheduled
```

และ:

```text
Notification
06:00
```

เป็นคนละ semantic

ห้ามเปลี่ยน 06:00 ให้กลายเป็น Activity Start Time

---

# 17.13 Decision 09 — Time Window Semantics

Semantic windows กลาง:

```text id="dlqp7q"
LATE_NIGHT     [00:00,06:00)
MORNING        [06:00,09:00)
LATE_MORNING   [09:00,12:00)
NOON           [12:00,13:00)
AFTERNOON      [13:00,16:00)
EVENING        [16:00,19:00)
NIGHT          [19:00,24:00)
```

มีคุณสมบัติ:

```text
No Gap
No Overlap
Full 24-hour Coverage
```

User-defined settings มี precedence เหนือ defaults

ถ้า user override เฉพาะบางช่วง ระบบใช้ default ในส่วนที่ไม่ได้ override ตาม policy ที่กำหนดไว้

---

# 17.14 Decision 10 — Manual Schedule Edit

Manual Edit ใช้:

```text id="7ed1hj"
Confirmed Schedule
       ↓
Local Draft
       ↓
Validate
       ↓
Confirm
       ↓
New Schedule Version
```

Draft:

* ไม่ใช่ database Schedule Version
* ไม่สร้าง notification
* แก้ได้
* conflict ได้ชั่วคราว

เมื่อ conflict:

```text
Confirm = Disabled
```

Current Schedule ไม่เปลี่ยน

---

# 17.15 Decision 11 — Manual Confirm Stale Protection

Manual Edit ก็ต้องมี concurrency protection เช่นเดียวกับ Proposal

เพราะ:

```text
User opens Schedule Version 5
      ↓
Another operation creates Version 6
      ↓
User tries to Confirm old Draft
```

จึงต้องส่งหรือผูก:

```text
expected current schedule version
```

ไปกับ Manual Confirm operation

Backend ต้องตรวจ:

```text id="f8t6hm"
Expected Version
=
Current Version?
```

ถ้าไม่:

```text
409 Conflict / Stale State
```

ห้ามสร้าง Version ใหม่จาก Draft ที่ base version เก่า

---

# 17.16 Decision 12 — Proposal source_schedule_version_id

`proposals.source_schedule_version_id` มีความหมายว่า:

> Proposal นี้ถูกสร้างขึ้นโดยอ้างอิง Current Schedule Version ใด

กรณี Initial Planning ที่ยังไม่มี Current Schedule:

```text
source_schedule_version_id = NULL
```

กรณี Re-planning:

```text
source_schedule_version_id = current version
```

Confirm ต้องตรวจอีกครั้งก่อน transaction

---

# 17.17 Decision 13 — Schedule Version

Schedule Version เป็น immutable snapshot

```text id="dbi4c6"
Version N
   ↓
Version N+1
```

Version N:

```text
READ-ONLY
```

และต่อหนึ่ง user:

```text
Current Version = exactly 1
```

หรือ:

```text
No Version
```

หาก user ยังไม่เคยมี Confirmed Schedule

ดังนั้นจึงไม่มี:

```text
current_schedule
```

table

---

# 17.18 Decision 14 — Notification Source

มาตรฐานกลาง:

```text id="qorqqg"
Confirmed Schedule
       ↓
Notification Coordinator
       ↓
Local Notifications
```

ไม่:

```text
Proposal
↓
Notification
```

และไม่:

```text
Activity Form
↓
Notification
```

จนกว่าจะมี Confirmed Schedule ที่เกี่ยวข้อง

---

# 17.19 Decision 15 — Notification Defaults

ลำดับ precedence:

```text id="2sqy0j"
Activity Override
       ↓
Global User Setting
       ↓
System Default
```

System defaults:

```text
Date-only Activity → 06:00
Timed Activity     → 1 hour before start
```

Notification Time:

```text
≤ Activity Start
```

สำหรับ time-specific Activity หาก 1 ชั่วโมงก่อนข้ามวัน สามารถเกิด notification ในวันก่อนหน้าได้ เพราะ notification time เป็น absolute datetime

---

# 17.20 Decision 16 — Notification and Rescheduling

เมื่อ Confirmed Schedule เปลี่ยน:

```text id="29p7xk"
Old Schedule
    ↓
New Confirmed Schedule
    ↓
Cancel Obsolete Local Notification
    ↓
Schedule Effective Notification
```

Notification failure:

```text
Notification failure
≠
Schedule failure
```

Confirmed Schedule ต้องยังคงอยู่

---

# 17.21 Decision 17 — API Versioning

MVP ใช้:

```text
/api/...
```

ไม่ใช้:

```text
/api/v1/...
```

การเปลี่ยน internal implementation เช่น:

```text
CP-SAT Algorithm
Prompt
AI Provider
Database optimization
```

ไม่จำเป็นต้องสร้าง API v2 หาก API contract ไม่เปลี่ยน

ใช้ v2 เมื่อเกิด:

```text
Breaking API Contract Change
```

เท่านั้น

---

# 17.22 Decision 18 — API Responsibility

ห้ามสร้าง public endpoint เช่น:

```text
/api/ai/extract
/api/cp-sat/solve
```

สำหรับ client โดยตรงใน MVP

Client เรียก business-oriented endpoint:

```text
/api/planning/requests
```

แล้ว backend orchestrates:

```text
AI
→
Validation
→
Planning
→
Proposal
```

เหตุผลคือ API contract ควร expose **business capability** ไม่ใช่ internal implementation

---

# 17.23 Decision 19 — AI / Planner Boundary

AI:

```text
Understand
Extract
Interpret
Clarify
```

Planner:

```text
Schedule
Optimize
Check Feasibility
Re-plan
```

ดังนั้น:

```text
AI cannot choose final schedule
Planner cannot interpret raw natural language
```

---

# 17.24 Decision 20 — Human-in-the-loop Boundary

การเปลี่ยน Confirmed Schedule ต้องเกิดจาก explicit user action

ตัวอย่าง:

```text id="9pnfgu"
Proposal
 ↓
User Review
 ↓
Confirm
```

แม้ AI จะมี confidence สูง ก็ไม่สามารถข้าม Confirm ได้ใน MVP

---

# 17.25 Decision 21 — Candidate Count

Proposal:

```text
1 ≤ Candidate Count ≤ 3
```

แต่ไม่ต้องมีครบ 3

```text
1 = valid
2 = valid
3 = valid
```

candidate ต้องมี:

* feasible
* meaningful difference
* acceptable quality

ห้ามสร้าง dummy candidate เพื่อให้ครบจำนวน

---

# 17.26 Decision 22 — Re-planning Strategy

MVP:

```text id="2lqxhj"
Change Detection
      ↓
Affected Context
      ↓
Bounded Horizon
      ↓
Full Model Rebuild
      ↓
Re-solve
```

ไม่ใช้ incremental solver เป็น requirement ของ MVP

Future Work อาจเปรียบเทียบ:

```text
Full Rebuild
vs
Incremental Re-optimization
```

---

# 17.27 Decision 23 — Re-planning Stability

Stability ใช้:

```text id="8w7i4r"
D = Σ |s_new(i) - s_old(i)|
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

จึงไม่อนุญาตให้ stability รักษา schedule เดิมโดยละเมิด requirement ใหม่

---

# 17.28 Decision 24 — Current Schedule Safety

หลัก invariant:

```text id="iwr3vo"
Failed Re-planning
       ↓
Current Schedule unchanged
```

และ:

```text
Rejected Proposal
       ↓
Current Schedule unchanged
```

และ:

```text
Stale Proposal
       ↓
Current Schedule unchanged
```

นี่ถือเป็น Critical Safety Invariant

---

# 17.29 Decision 25 — Future Work: Speech-to-Text

ปรับ wording จากเดิมให้ชัดเจน:

### MVP

Voice / Speech-to-Text **ไม่ใช่ component ภายใน LONGTUA**

ผู้ใช้สามารถใช้ OS/device STT เพื่อผลิต text แล้วส่งให้ LONGTUA ได้

### Future Work

เพิ่ม:

```text
Integrated Speech-to-Text
```

ภายใน LONGTUA:

```text
Voice
 ↓
LONGTUA STT
 ↓
Text
 ↓
AI/NLP
```

ดังนั้น Future Work หมายถึง **เพิ่ม STT เป็น capability ภายในระบบเอง**

---

# 17.30 Decision 26 — Research Contribution Boundary

ให้ใช้ wording กลาง:

> LONGTUA มุ่งเน้นการบูรณาการ Natural Language Understanding, Constraint-based Personal Planning, Human-in-the-loop Interaction และ Adaptive Re-planning ใน workflow เดียวสำหรับ personal planning

ไม่ใช้ claim:

* first system
* best system
* universally optimal
* novel scheduling algorithm

เว้นแต่มี evidence ใหม่รองรับโดยตรง

---

# 17.31 Reference Consistency Audit

Reference list จากเอกสารฉบับที่ 16 ได้รับการตรวจสอบกับแหล่งต้นฉบับหลักแล้ว

ตัวอย่างที่ตรวจสอบแล้ว:

* *Event Extraction as Machine Reading Comprehension* — EMNLP 2020 โดย Jian Liu, Yubo Chen, Kang Liu, Wei Bi และ Xiaojiang Liu ตรงกับ ACL Anthology ([ACL](https://aclanthology.org/2020.emnlp-main.128/))
* *Text2Event* — ACL-IJCNLP 2021 และ metadata ตรงกับ ACL Anthology ([ACL](https://aclanthology.org/2021.acl-long.217/))
* *Event Time Extraction and Propagation via Graph Attention Networks* — NAACL 2021 metadata และ authors ตรงกับต้นฉบับ ([ACL](https://aclanthology.org/2021.naacl-main.6/))
* *Utilizing Relative Event Time...* — EMNLP 2021 โดย Haoyang Wen และ Heng Ji ตรงกับต้นฉบับ ([ACL](https://aclanthology.org/2021.emnlp-main.815/))
* *Extracting Temporal Event Relation with Syntax-guided Graph Transformer* — ผู้เขียนที่ถูกต้องคือ Shuaicheng Zhang, Qiang Ning และ Lifu Huang ([ACL](https://aclanthology.org/2022.findings-naacl.29/))
* *TIMELINE* — Sarah Alsayyahi และ Riza Batista-Navarro, EMNLP 2023 ([ACL](https://aclanthology.org/2023.emnlp-main.1016/))
* *EDeR* — Ruiqi Li, Patrik Haslum และ Leyang Cui, EMNLP 2023 ([ACL](https://aclanthology.org/2023.emnlp-main.926/))
* *Code4Struct* — Xingyao Wang, Sha Li และ Heng Ji, ACL 2023 ([ACL](https://aclanthology.org/2023.acl-long.202/))
* *Event Semantic Classification in Context* — Haoyu Wang, Hongming Zhang, Kaiqiang Song, Dong Yu และ Dan Roth, EACL 2024 ([ACL](https://aclanthology.org/2024.findings-eacl.94/))
* *Chaining Event Spans for Temporal Relation Grounding* — Jongho Kim, Dohyeon Lee, Minsoo Kim และ Seung-won Hwang, EACL 2024 ([ACL](https://aclanthology.org/2024.eacl-long.101/))
* *ChatUIE* — Jun Xu, Mengshu Sun, Zhiqiang Zhang และ Jun Zhou, LREC-COLING 2024 ([ACL](https://aclanthology.org/2024.lrec-main.279/))
* *Learning to Extract Structured Entities Using Language Models* — Haolun Wu et al., EMNLP 2024 ([ACL](https://aclanthology.org/2024.emnlp-main.388/))
* *A Simple but Effective Approach to Improve Structured Language Model Output for Information Extraction* — Yinghao Li, Rampi Ramprasad และ Chao Zhang, Findings of EMNLP 2024 ([ACL](https://aclanthology.org/2024.findings-emnlp.295/))
* *Clarifying the Path to User Satisfaction* — Hossein A. Rahmani et al., Findings of EACL 2024 ([ACL](https://aclanthology.org/2024.findings-eacl.84/))
* *“I Want It That Way”* — Connor Lawless et al., ACM TiiS, 2024 โดย Microsoft Research ยืนยัน authors และ publication information ([Microsoft Research](https://www.microsoft.com/en-us/research/publication/i-want-it-that-way-enabling-interactive-decision-support-using-large-language-models-and-constraint-programming/))
* *Rhythm of Work* — Lu Sun, Lillio Mok, Shilad Sen และ Bahareh Sarrafzadeh, PACM HCI 2024 ([ACM](https://doi.org/10.1145/3686895))
* *Handling uncertainty in train timetable rescheduling* — Shuguang Zhan et al., Transportation Research Part E, 2024 ([ScienceDirect](https://www.sciencedirect.com/science/article/pii/S136655452400019X))

### Correction

ในเอกสารฉบับที่ 16 รายการงานปี 2022 เรื่อง Syntax-guided Graph Transformer มี wording ที่คลาดเคลื่อนในบรรทัดหนึ่งเกี่ยวกับ attribution ของผู้เขียน

ให้ใช้ metadata ที่ถูกต้องเป็น:

> **Zhang, S., Ning, Q., & Huang, L. (2022). Extracting Temporal Event Relation with Syntax-guided Graph Transformer. Findings of ACL: NAACL 2022, 379–390.**

---

# 17.32 Academic Reference Year Rule

Reference ที่ใช้เป็น academic research citation ของ project ต้อง:

```text
2020 ≤ Publication Year ≤ Current
```

ไม่มีการนำงานก่อน 2020 กลับมาเป็นหลักฐานหลักโดยไม่มีเหตุผลและ approval จาก project scope

Technical documentation และ product documentation ไม่ถูกนับเป็น academic paper

---

# 17.33 Cross-Document Traceability Matrix

| Decision / Concept         | Documents affected         |
| -------------------------- | -------------------------- |
| Planning Request State     | 02, 05, 10, 14             |
| Proposal State             | 02, 07, 08, 09, 10, 12, 14 |
| Activity Change Flow       | 02, 07, 09, 10, 12, 14     |
| Availability Change Flow   | 02, 07, 09, 10, 12, 14     |
| Activity Status            | 04, 09, 10, 12             |
| Schedule Version           | 04, 07, 08, 09, 10, 12, 14 |
| Manual Edit                | 08, 10, 12, 14             |
| Notification               | 08, 09, 10, 12, 14         |
| AI / Planner Boundary      | 03, 05, 06, 10, 14         |
| Candidate Count            | 06, 07, 08, 09, 12, 13, 14 |
| Re-planning                | 06, 07, 08, 10, 12, 13, 14 |
| HITL                       | 01, 05, 07, 12, 13, 15, 16 |
| Speech-to-Text Future Work | 05, 12, 15, 16             |

---

# 17.34 Final Source-of-Truth Hierarchy

เมื่อต้องตัดสินใจกรณีที่เอกสารมีข้อความไม่ตรงกัน ให้ใช้ลำดับ:

```text id="m08x9d"
1. Requirements
2. Domain Rules
3. Architecture Boundaries
4. API / DB Contract
5. UI Behavior
6. Implementation Details
```

โดย:

```text
Implementation
must follow
Contract
```

ไม่ใช่ให้ code เป็นตัวกำหนด behavior ย้อนกลับไป

หากเกิด conflict จริงระหว่าง Requirements และ Design ต้องแก้ design ให้ตรง requirement ก่อน coding

---

# 17.35 Final Locked Invariants

ต่อจากนี้ให้ถือว่าข้อความต่อไปนี้เป็น invariants ของ LONGTUA:

```text id="2o5q8f"
1. User is the final decision-maker.

2. AI/NLP understands; it does not schedule.

3. Planner schedules; it does not interpret raw natural language.

4. Proposal is not Confirmed Schedule.

5. Draft is not Confirmed Schedule.

6. Only Confirmed Schedule is the schedule source of truth.

7. Only Confirmed Schedule generates notifications.

8. Failed, rejected, or stale proposals cannot modify the current schedule.

9. Historical Schedule Versions are immutable.

10. There can be at most one current Schedule Version per user.

11. AI output must pass schema/domain validation.

12. AI must not invent planning-critical information.

13. Clarification occurs only when necessary for interpretation or planning.

14. Hard Constraints cannot be violated by an accepted plan.

15. Preferences cannot override Hard Constraints.

16. Stability cannot override new explicit requirements.

17. Manual Draft conflicts disable confirmation.

18. Planning-affecting changes are committed only with successful confirmation.

19. Date-only notification time is not Activity start time.

20. MVP does not include integrated Speech-to-Text.
```

---

# 17.36 Documents Requiring Minor Revision

จาก audit นี้ เอกสารที่ควรมี revision เล็กน้อยก่อนถือว่า locked:

```text id="k42f6x"
02 Requirements Specification
04 Domain & Planning Model
07 Replanning Design
08 Schedule & Notification Design
09 Database Design
10 API Design
12 UI / UX Behavior Specification
14 Development & Implementation Specification
15 Limitations & Future Work
16 References
```

ไม่จำเป็นต้องเขียนใหม่ทั้งหมด

เป็นการแก้เพื่อให้ wording และ state ตรงกับ decisions ในเอกสารนี้

---

# 17.37 Documents Already Stable

ส่วนที่ไม่พบ conceptual contradiction สำคัญ:

```text id="xw2d9p"
01 Project Overview
03 System Architecture
05 AI / NLP Design
06 Planning Engine Design
11 Security Design
13 Testing & Evaluation Design
```

เอกสารเหล่านี้ใช้เป็นฐานต่อได้ โดยปรับเฉพาะ terminology ที่เกี่ยวข้องกับ decisions ใหม่

---

# 17.38 Final Consistency Status

หลังจากใช้ decisions ในเอกสารนี้เป็นมาตรฐานกลาง:

```text id="k2t8m9"
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
Replanning
      ↓
Schedule
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
      ↓
Limitations / References
```

สามารถถือว่า **conceptual system design is locked**

โดยเหลือเพียงการแก้ wording/contract เล็กน้อยในเอกสารที่ระบุไว้ ไม่ใช่การออกแบบระบบใหม่ทั้งหมด

---

# 17.39 Final Design Lock

เมื่อผ่าน Consistency Review นี้แล้ว LONGTUA สามารถเข้าสู่ขั้นตอนถัดไป:

```text id="h50xg8"
Consistency Review
        ↓
Contract Freeze
        ↓
Figma
        ↓
Development Task Breakdown
        ↓
Implementation
```

หลักการคือ:

> **จากจุดนี้ การเพิ่ม feature หรือเปลี่ยน behavior ไม่ควรเกิดโดยบังเอิญระหว่าง coding แต่ต้องถือว่าเป็น design change และตรวจผลกระทบต่อเอกสาร/contract ที่เกี่ยวข้องก่อน**
