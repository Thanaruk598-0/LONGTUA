# 7. Replanning Design

## 7.1 Purpose

เอกสารฉบับนี้กำหนดการออกแบบกระบวนการ Adaptive Replanning ของ LONGTUA — Personal Adaptive Planner ซึ่งเป็นกระบวนการที่ระบบใช้ในการสร้าง Proposal ใหม่เมื่อข้อมูล ความต้องการ ข้อจำกัด หรือสถานการณ์ของผู้ใช้เปลี่ยนแปลงหลังจากมี Schedule อยู่แล้ว

Replanning แตกต่างจาก Initial Planning ตรงที่ระบบมี **Existing Confirmed Schedule** เป็นบริบทอ้างอิง และต้องพิจารณาว่าส่วนใดของ Schedule ได้รับผลกระทบ ส่วนใดควรถูกคงไว้ และส่วนใดสามารถปรับเปลี่ยนได้

หลักการสำคัญคือ:

> **เมื่อสถานการณ์เปลี่ยน ระบบไม่ควรจัดตารางทั้งหมดใหม่โดยไม่จำเป็น แต่ต้องวิเคราะห์ผลกระทบก่อน จากนั้นจึงสร้างแผนใหม่ภายในขอบเขตที่เกี่ยวข้อง และให้ผู้ใช้ตรวจสอบ Proposal ก่อนเปลี่ยน Confirmed Schedule**

Replanning ใน MVP ใช้ **Full Model Rebuild + Re-solve** ภายใน Affected Replanning Horizon

---

# 7.2 Role of Replanning

ตำแหน่งของ Replanning ในระบบ:

```text
Existing Confirmed Schedule
            +
New Information / Change
            ↓
     Impact Detection
            ↓
     Affected Context
            ↓
   Replanning Horizon
            ↓
     Planning Model
            ↓
        CP-SAT
            ↓
     New Candidate(s)
            ↓
         Proposal
            ↓
      User Review
            ↓
         Confirm
            ↓
 New Confirmed Schedule Version
```

ดังนั้น Replanning ไม่ได้แก้ Schedule โดยตรง แต่เป็นการสร้าง **ข้อเสนอใหม่จากสถานการณ์ล่าสุด**

---

# 7.3 Initial Planning vs Replanning

| Aspect                      | Initial Planning                    | Replanning                    |
| --------------------------- | ----------------------------------- | ----------------------------- |
| Existing Confirmed Schedule | อาจไม่มี                            | มี                            |
| Stability                   | ไม่จำเป็นต้องใช้เป็น Objective หลัก | ใช้                           |
| Trigger                     | New Planning Request                | Change / Feedback / Situation |
| Affected Context            | ไม่ต้องวิเคราะห์จาก Schedule เดิม   | ต้องวิเคราะห์                 |
| Horizon                     | Normal Planning Horizon             | Affected Replanning Horizon   |
| Model                       | Build ใหม่                          | Build ใหม่                    |
| Output                      | Proposal                            | New Proposal                  |
| Confirm                     | User                                | User                          |

ความแตกต่างสำคัญที่สุดคือ:

```text
Initial Planning
= Find a good schedule

Replanning
= Find a new schedule while considering
  what should remain unchanged
```

---

# 7.4 Replanning Triggers

Replanning สามารถเกิดจากการเปลี่ยนแปลงที่มีผลต่อ Schedule เช่น:

### 7.4.1 New Activity

ตัวอย่าง:

> “พรุ่งนี้บ่ายสามมีประชุมเพิ่ม”

Activity ใหม่อาจทำให้ Schedule เดิมมี Conflict และต้องจัดกิจกรรมบางรายการใหม่

---

### 7.4.2 Activity Time Changed

เช่น:

```text
Meeting
จาก 14:00
เป็น 16:00
```

อาจกระทบกิจกรรมอื่นที่อยู่ใกล้เคียง

---

### 7.4.3 Activity Duration Changed

เช่น:

```text
Study
เดิม 1 ชั่วโมง
ใหม่ 2 ชั่วโมง
```

อาจทำให้กิจกรรมถัดไปต้องเลื่อน

---

### 7.4.4 Deadline Changed

เช่น:

```text
Deadline
จาก Friday
เป็น Thursday
```

อาจทำให้ Planner ต้องจัดกิจกรรมก่อนหน้าใหม่

---

### 7.4.5 Availability Changed

เช่น:

```text
จาก:
13:00–17:00 Available

เป็น:
13:00–15:00 Available
```

กิจกรรมบางรายการอาจไม่สามารถอยู่ในตำแหน่งเดิมได้

---

### 7.4.6 Unavailability Added

เช่น:

> “พรุ่งนี้ 14:00–16:00 ไม่ว่าง”

ระบบต้องนำช่วงดังกล่าวเป็น Hard Constraint ในการ Replanning

---

### 7.4.7 Activity Cancelled

เมื่อกิจกรรมถูกยกเลิก:

```text
Cancelled Activity
        ↓
Impact Detection
        ↓
Replanning
```

อาจทำให้เกิดเวลาว่างหรือเปิดโอกาสให้ Activity อื่นกลับไปอยู่ตำแหน่งเดิม/ตำแหน่งที่เหมาะสมกว่า

---

### 7.4.8 User Feedback

ตัวอย่าง:

> “ขออ่านหนังสือตอนเย็นแทน และอยากให้กระทบกิจกรรมอื่นน้อยที่สุด”

สามารถนำไปสู่ Replanning ได้โดยการแปลง Feedback เป็น Structured Requirement / Preference

---

# 7.5 Non-Replanning Changes

ไม่ใช่การแก้ Activity ทุกประเภทต้อง Replan

ตัวอย่าง:

```text
เปลี่ยน Title
เปลี่ยน Description
เปลี่ยนข้อมูลแสดงผลที่ไม่กระทบ Planning
```

โดยทั่วไปไม่จำเป็นต้อง Replan หากไม่มีข้อมูล Planning ที่เปลี่ยน

ดังนั้นระบบต้องมี:

> **Planning Impact Classification**

ก่อนเรียก Replanning

---

# 7.6 Change Classification

การเปลี่ยนแปลงสามารถแบ่งเป็น:

```text
Change
├── Non-Planning Change
├── Local Change
├── Schedule-Affecting Change
└── Replanning-required Change
```

### Non-Planning Change

ไม่ต้อง Replan

### Local Change

กระทบเพียงข้อมูลเฉพาะรายการ แต่ไม่กระทบ Current Schedule

### Schedule-Affecting Change

มีโอกาสกระทบ Current Schedule และต้องวิเคราะห์

### Replanning-required Change

ตรวจพบว่าการเปลี่ยนแปลงทำให้ Current Schedule ใช้งานไม่ได้หรือมี Requirement ใหม่ที่ต้องคำนวณ Schedule ใหม่

---

# 7.7 Impact Detection

Impact Detection เป็นขั้นตอนก่อน Replanning

```text
Change
  ↓
Identify Changed Object
  ↓
Identify Changed Property
  ↓
Check Planning Relevance
  ↓
Check Current Schedule Impact
  ↓
Determine Affected Context
```

ตัวอย่าง:

```text
Change:
Meeting 14:00 → 16:00
```

ระบบต้องตรวจ:

```text
Meeting itself
Activities around 14:00–16:00
Temporal Relations
Availability
Unavailability
Deadline
Container Membership
```

---

# 7.8 Planning Impact Categories

การเปลี่ยนแปลงที่ใช้พิจารณาผลกระทบ ได้แก่:

```text
Time
Duration
Date
Deadline
Fixed Time
Availability
Unavailability
Temporal Relation
Container Membership
Required / Optional
Planning Requirement
Preference
Cancellation
Restoration
```

การเปลี่ยนแปลงเฉพาะ `Title` หรือ `Description` ไม่ควรถูกถือเป็น Planning Change โดยอัตโนมัติ

---

# 7.9 Affected Context

เมื่อเกิด Change ระบบต้องระบุ:

> **Affected Context**

ซึ่งหมายถึง Planning Objects และ Rules ที่อาจได้รับผลกระทบจากการเปลี่ยนแปลง

ตัวอย่าง:

```text
Changed Activity A
      ↓
Temporal Relation
      ↓
Activity B
      ↓
Availability
      ↓
Activity C
```

Context สามารถขยายตาม Dependency ที่เกี่ยวข้อง

---

# 7.10 Affected Context Categories

Affected Context อาจประกอบด้วย:

### Directly Affected

Object ที่ถูกเปลี่ยนโดยตรง

### Constraint-related

Object ที่แชร์ Constraint หรือ Availability ที่ได้รับผลกระทบ

### Temporal-related

Object ที่มี Temporal Relation กับ Changed Object

### Schedule-related

Schedule Item ที่อยู่ใกล้หรืออาจเกิด Conflict

### Container-related

Child / Parent ของ Container ที่ได้รับผลกระทบ

### Requirement-related

Activity ที่เกี่ยวข้องกับ New Requirement / Preference

---

# 7.11 Example — Direct Impact

Existing:

```text
Study
14:00–16:00

Dinner
18:00–20:00
```

Change:

```text
Study
14:00–17:00
```

Affected Context:

```text
Study
+
Dinner
+
Any activity between 16:00–18:00
```

ไม่จำเป็นต้องดึง Activity ในเดือนอื่นเข้ามาใน Model

---

# 7.12 Example — Indirect Impact

Existing:

```text
A → BEFORE → B
B → BEFORE → C
```

ถ้า A ใช้เวลานานขึ้น:

```text
A duration ↑
```

อาจกระทบ:

```text
B
C
```

แม้ B/C จะไม่ได้ถูกแก้โดยตรง

ดังนั้น Impact Detection ต้องพิจารณา Dependency Graph ไม่ใช่ดูเฉพาะ Object ที่ได้รับการแก้ไข

---

# 7.13 Affected Replanning Horizon

หลังระบุ Affected Context แล้ว ระบบต้องสร้าง:

> **Affected Replanning Horizon**

ซึ่งเป็นช่วงเวลาที่ต้องนำไปคำนวณใหม่

```text
Changed Context
      ↓
Temporal / Schedule Impact
      ↓
Affected Period
      ↓
Replanning Horizon
```

Replanning Horizon อาจเล็กกว่า Normal Planning Horizon

---

# 7.14 Replanning Horizon Example

สมมติ:

```text
Today = 7 January
Changed Activity = 15 February
```

Normal Planning Horizon:

```text
7–20 January
```

ไม่เพียงพอสำหรับ Change นี้

ระบบสามารถวิเคราะห์:

```text
Affected Activities
12–18 February
```

แล้วสร้าง:

```text
Replanning Horizon
12–18 February
```

ดังนั้น Calendar ยังเก็บข้อมูล February ได้ แม้ Normal Planning Operation ปัจจุบันจะทำงานใน January

---

# 7.15 Horizon Selection Principle

Affected Replanning Horizon ต้อง:

1. ครอบคลุม Changed Activity
2. ครอบคลุม Activities ที่ได้รับผลกระทบ
3. ครอบคลุม Constraints/Relations ที่จำเป็น
4. ไม่กว้างเกินความจำเป็นจนทำให้ Solver ทำงานโดยไม่จำเป็น
5. ไม่แคบจนทำให้ Conflict ที่เกิดจริงหลุดออกจาก Model

หลักคือ:

> **Small enough to compute, large enough to preserve correctness**

---

# 7.16 Past Schedule

กิจกรรมที่อยู่ในอดีต:

```text
Past
```

ไม่ควรถูกเลื่อนกลับมาจัดใหม่

ดังนั้นโดยทั่วไป:

```text
Past Schedule
= Frozen
```

และไม่ควรถูกนำมาเป็น Movable Activity ใน Replanning

---

# 7.17 Unaffected Schedule

Activity ที่อยู่ในอนาคตและไม่มีผลกระทบสามารถ:

```text
Freeze
```

ไว้ที่ตำแหน่งเดิม

เพื่อให้ Planner ไม่เลื่อนกิจกรรมเหล่านั้นโดยไม่มีเหตุผล

---

# 7.18 Movable Schedule

Activity ที่อยู่ใน Affected Context และสามารถเลื่อนได้:

```text
Movable
```

สามารถมี `Start Time` ใหม่ได้

Planner ต้องเคารพ:

* Hard Constraints
* Explicit Requirements
* Preferences
* Stability

---

# 7.19 New Activities

Activity ใหม่ที่เกิดจาก Change:

```text
New Activity
```

ต้องถูกเพิ่มเข้า Planning Model ใน Replanning Operation

ตัวอย่าง:

```text
Existing Schedule
+
New Meeting 15:00–16:00
```

Planner ต้องพิจารณา Meeting ร่วมกับ Activities ที่เกี่ยวข้อง

---

# 7.20 Cancelled Activities

เมื่อ Activity ถูกยกเลิก:

```text
Activity
→ CANCELLED
```

Activity ไม่ควรถูก Schedule ใน New Plan

แต่ Historical Schedule Version ที่เคยมี Activity ดังกล่าวต้องไม่ถูกแก้ไข

---

# 7.21 Restored Activities

หากระบบในอนาคตรองรับการ Restore Activity ที่ถูกยกเลิก:

```text
Cancelled
→ Restored
```

ถ้าการ Restore ส่งผลต่อ Current Schedule สามารถ Trigger Replanning ได้

ใน MVP การ Restore ต้องไม่ทำลาย Historical Schedule Version

---

# 7.22 Freeze Strategy

Replanning ใช้แนวคิด:

```text
Frozen
vs
Movable
```

โดย:

### Frozen

* Past Items
* Unaffected Future Items
* Items ที่ User/Policy กำหนดให้คงที่
* Fixed Activities ที่อยู่นอก Change Scope

### Movable

* Affected Flexible Activities
* New Activities
* Activities ที่ Requirement ใหม่อนุญาตให้เลื่อน

---

# 7.23 Freeze Does Not Mean Database Lock

คำว่า Freeze ใน Replanning หมายถึง:

> **ตรึง Placement ใน Planning Model**

ไม่ใช่:

> Lock Database Row อย่างถาวร

ดังนั้น:

```text
Frozen Activity
```

หมายถึง Planner ไม่เปลี่ยนตำแหน่งของมันในการ Solve ครั้งนั้น

---

# 7.24 Replanning Model

สำหรับ Replanning:

```text
M_replan =
Existing Relevant Schedule
+
New / Changed Information
+
Hard Constraints
+
Preferences
+
Replanning Horizon
+
Stability Reference
```

โดย Model ใหม่ถูกสร้างขึ้นตาม Current State

---

# 7.25 Full Model Rebuild

MVP ใช้:

> **Full Model Rebuild + Re-solve**

หมายถึงเมื่อ Replanning เกิดขึ้น ระบบจะสร้าง Planning Model ใหม่อีกครั้งจาก State ปัจจุบัน แทนการแก้ไข Solver State เดิมแบบ Incremental เป็นกลไกหลัก

Flow:

```text
Current State
   ↓
Build Model
   ↓
Add Frozen Items
   ↓
Add Movable Items
   ↓
Add New Items
   ↓
Add Constraints
   ↓
Add Preferences
   ↓
Add Stability Objective
   ↓
Solve
```

---

# 7.26 Why Full Model Rebuild for MVP

การใช้ Full Model Rebuild มีข้อดี:

* ลด State Complexity
* ทำให้ Model Construction เป็น Deterministic Process มากขึ้น
* Debug ง่ายกว่า
* Test ง่ายกว่า
* ลดปัญหา State จาก Previous Solve
* เหมาะกับขนาดระบบที่จำกัดใน MVP

ระบบไม่ได้อ้างว่าการ Rebuild เป็นวิธีที่มีประสิทธิภาพสูงสุดสำหรับทุกขนาดปัญหา

หากในอนาคตระบบมี Scale ใหญ่ขึ้น สามารถพิจารณา Incremental / Advanced Replanning ได้

---

# 7.27 Replanning Constraint Preservation

Replanning ต้องรักษา:

```text
Existing Hard Constraints
+
New Hard Constraints
```

หาก Change เพิ่ม Constraint ใหม่:

```text
Old Constraint
+
New Constraint
```

ทั้งสองต้องถูกพิจารณาร่วมกัน

ห้ามเอา Constraint เก่าออกเพียงเพื่อให้ได้ Feasible Solution โดยไม่มีเหตุผล/Policy รองรับ

---

# 7.28 New Requirement Handling

หาก User ระบุ:

> “ประชุมนี้ต้องเป็น 15:00”

ระบบต้องแปลงเป็น:

```text
New Fixed Time Requirement
```

Planner ต้องให้ความสำคัญกับ Requirement นี้ตาม Objective Hierarchy

ถ้าตารางเดิมไม่สามารถคงไว้ได้:

```text
Requirement
>
Stability
```

---

# 7.29 Preference Handling in Replanning

หาก User ระบุ:

> “อยากอ่านหนังสือตอนเย็น”

ระบบจะถือเป็น Preference ตาม Domain Policy

Planner จะพยายามทำให้ Preference เป็นจริง แต่สามารถเลือกเวลาอื่นได้ถ้าจำเป็นเพื่อรักษา Feasibility

---

# 7.30 Stability Reference

ทุก Movable Activity ที่มี Existing Placement สามารถมี Reference:

```text
old_start_i
```

และ Candidate ใหม่มี:

```text
new_start_i
```

ความแตกต่าง:

```text
|new_start_i - old_start_i|
```

ใช้วัดการเปลี่ยนแปลง

---

# 7.31 Stability Objective

สำหรับ Replanning:

```text
D = Σ |new_start_i - old_start_i|
```

และระบบมีเป้าหมาย:

```text
Minimize D
```

ภายใต้ Constraints และ Requirements ทั้งหมด

---

# 7.32 Why Stability Is Not First Priority

สมมติ:

```text
Existing:
Study = 14:00–16:00
```

User บอก:

> “วันนี้อยากย้ายอ่านหนังสือเป็น 18:00”

หาก Stability มี Priority สูงที่สุด ระบบอาจพยายามเก็บ 14:00 ซึ่งขัดกับ Requirement ใหม่

ดังนั้นลำดับที่ถูกต้อง:

```text
Feasibility
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

# 7.33 Minimal Change Principle

Stability ใน LONGTUA ไม่ได้หมายความว่า:

> “ห้ามเปลี่ยนตารางเดิม”

แต่หมายถึง:

> **“เมื่อจำเป็นต้องเปลี่ยน ให้เปลี่ยนเท่าที่จำเป็น”**

ดังนั้น:

```text
No Change Needed
→ Keep

Change Required
→ Minimize Unnecessary Change
```

---

# 7.34 Example — Minimal Replanning

Existing:

```text
A 09:00–10:00
B 10:00–11:00
C 13:00–14:00
D 15:00–16:00
```

New Activity:

```text
X 10:30–11:30
```

ถ้า B สามารถย้ายเป็น:

```text
B 11:30–12:30
```

และ C/D ยังอยู่ตำแหน่งเดิมได้:

```text
A → unchanged
B → moved
C → unchanged
D → unchanged
```

นี่เป็นผลที่สอดคล้องกับ Stability Principle มากกว่าการย้ายทุก Activity ในวันนั้น

---

# 7.35 Example — Stability Must Yield

Existing:

```text
A = 14:00–16:00
```

New Requirement:

```text
A must be 18:00–20:00
```

Planner ต้องเปลี่ยน A แม้ Stability จะเพิ่มขึ้น

เพราะ:

```text
New Explicit Requirement
>
Stability
```

---

# 7.36 User Feedback as Replanning Trigger

Feedback สามารถทำหน้าที่เป็น Change Input

ตัวอย่าง:

> “ตารางนี้แน่นเกินไป ขอให้มีเวลาพักก่อนประชุม”

AI/NLP:

```text
Feedback
↓
Structured Requirement / Preference
```

Planner:

```text
Existing Schedule
+
New Requirement
+
Constraints
+
Preference
+
Stability
```

แล้วสร้าง Proposal ใหม่

---

# 7.37 Feedback Must Not Modify Schedule Directly

แม้ Feedback จะถูกตีความโดย AI:

```text
AI
→ Requested Change
```

ก็ยังไม่สามารถ:

```text
AI
→ Edit Confirmed Schedule
```

โดยตรง

ต้อง:

```text
Feedback
→ Replanning
→ Proposal
→ User Confirm
```

---

# 7.38 Example — Feedback Loop

```text
Initial Proposal
       ↓
User:
“ไม่สะดวกเวลานี้”
       ↓
AI / NLP
       ↓
Requested Window = Evening
       ↓
Replanning
       ↓
New Proposal
       ↓
User:
“อันนี้โอเค”
       ↓
Confirm
       ↓
New Schedule Version
```

---

# 7.39 Replanning Without Explicit Feedback

Replanning ไม่จำเป็นต้องเกิดจากข้อความ Feedback เท่านั้น

สามารถเกิดจาก Direct Activity Update เช่น:

```text
PATCH Activity
```

เช่น:

```text
Meeting
14:00 → 16:00
```

หาก Current Schedule ได้รับผลกระทบ:

```text
Impact Detection
→ Replanning
```

---

# 7.40 Replanning Trigger Matrix

| Change                    | Planning Impact              | Replanning                        |
| ------------------------- | ---------------------------- | --------------------------------- |
| Title                     | โดยทั่วไปไม่มี               | ❌                                 |
| Description               | โดยทั่วไปไม่มี               | ❌                                 |
| Duration                  | อาจกระทบ                     | ✅ เมื่อ Current Schedule ได้รับผล |
| Date                      | อาจกระทบ                     | ✅                                 |
| Fixed Time                | กระทบโดยตรง                  | ✅                                 |
| Deadline                  | อาจกระทบ                     | ✅                                 |
| Availability              | อาจกระทบหลายรายการ           | ✅                                 |
| Unavailability            | อาจกระทบหลายรายการ           | ✅                                 |
| Temporal Relation         | อาจกระทบหลายรายการ           | ✅                                 |
| Container Membership      | อาจกระทบ                     | ✅                                 |
| Cancellation              | อาจเปิดพื้นที่ใหม่           | ✅ เมื่อ Schedule ได้รับผล         |
| Preference                | อาจทำให้ User ต้องการแผนใหม่ | ✅ เมื่อใช้เป็น Planning Change    |
| Notification Setting Only | ไม่กระทบ Schedule            | ❌                                 |
| Notification Override     | ไม่กระทบ Schedule Placement  | ❌                                 |

ตารางนี้เป็น Baseline; Application Layer ต้องพิจารณา Current State ก่อนเรียก Replanning จริง

---

# 7.41 Replanning Workflow

กระบวนการมาตรฐาน:

```text
1. Detect Change
       ↓
2. Classify Change
       ↓
3. Determine Planning Impact
       ↓
4. Identify Affected Context
       ↓
5. Determine Affected Horizon
       ↓
6. Freeze Past / Unaffected Items
       ↓
7. Build New Planning Model
       ↓
8. Add New / Changed Requirements
       ↓
9. Add Existing Constraints
       ↓
10. Add Preferences
       ↓
11. Add Stability Objective
       ↓
12. Solve
       ↓
13. Validate Result
       ↓
14. Generate Candidate(s)
       ↓
15. Create New Proposal
       ↓
16. User Review
       ↓
17. Confirm / Reject / Feedback
```

---

# 7.42 Replanning State Machine

```text
Current Confirmed Schedule
          |
          | Change
          v
   IMPACT ANALYSIS
          |
      +---+---+
      |       |
 No Impact  Impact
      |       |
      |       v
      |   REPLANNING
      |       |
      |       v
      |   PROPOSAL
      |       |
      |   +---+---+
      |   |       |
      | Confirm  Reject
      |   |       |
      |   v       v
      | New      End
      | Version
      |
      v
Current Schedule
remains unchanged
```

---

# 7.43 Replanning and Proposal

ผลของ Replanning ต้องเป็น:

```text
New Proposal
```

ไม่ใช่:

```text
Direct Schedule Update
```

ดังนั้น User จะสามารถเห็น:

```text
Previous Schedule
vs
Proposed New Schedule
```

ก่อนตัดสินใจ

---

# 7.44 Proposal Change Representation

เพื่อช่วยให้ User เข้าใจ Replanning Proposal ระบบควรสามารถแสดงการเปลี่ยนแปลง เช่น:

```text
Study
14:00–16:00
→
16:00–18:00

Meeting
18:00
→
19:00
```

หรือ:

```text
Unchanged
Moved
Added
Removed
```

โดยเป็น Presentation Layer ที่อ่านข้อมูลจาก Proposal

---

# 7.45 Confirmed Schedule Protection

แม้ New Proposal จะถูกสร้างแล้ว:

```text
Current Confirmed Schedule
```

ยังคงเดิม

จนกว่าจะ:

```text
User Confirm
```

เท่านั้น

---

# 7.46 Schedule Version Transition

เมื่อ User Confirm New Proposal:

```text
Current Version = V3

User Confirms Replan
        ↓
Create V4
        ↓
V4 = Current
```

V3 ยังคงเก็บไว้เป็น Historical Version

---

# 7.47 Stale Proposal in Replanning

กรณีมี Replanning Proposal หลายตัว:

```text
Current = V3

Proposal A
Source = V3

มีการ Confirm Proposal อื่น
→ Current = V4

Try Confirm Proposal A
→ Source V3 ≠ Current V4
```

Proposal A ต้อง:

```text
INVALIDATED
หรือ
Confirmation Rejected
```

ตาม Application Policy

และไม่สามารถ Override V4 ได้

---

# 7.48 Why Versioning Matters for Replanning

Versioning ช่วยให้ระบบ:

* ตรวจ Stale Proposal
* รักษาประวัติ
* Trace การเปลี่ยนแปลง
* เปรียบเทียบ Before/After
* ใช้เป็นข้อมูล Evaluation

ดังนั้น Schedule Version เป็นส่วนสำคัญของ Adaptive Replanning ไม่ใช่เพียง Historical Logging

---

# 7.49 Replanning Failure Cases

Replanning อาจล้มเหลวจาก:

### 1. No Feasible Plan

ข้อจำกัดใหม่ทำให้ไม่มี Schedule ที่เป็นไปได้

### 2. Solver Timeout / UNKNOWN

Solver ไม่สามารถได้ผลลัพธ์ที่ยืนยันได้ภายใน Limit

### 3. Horizon Exceeded

Affected Context ใหญ่เกินขอบเขตที่ระบบกำหนด

### 4. Planning Object Limit

จำนวน Object ที่เกี่ยวข้องเกิน Limit

### 5. Invalid Planning State

ข้อมูล Current Schedule / New Input ไม่สอดคล้องกัน

### 6. AI Interpretation Failure

Feedback หรือ Natural Language Change ไม่สามารถแปลงเป็น Structured Requirement ได้

---

# 7.50 No Feasible Replanning

หาก Replanning ไม่มี Feasible Solution:

```text
Current Confirmed Schedule
        ↓
ยังคงเดิม
```

และ:

```text
New Proposal
        ↓
ไม่ถูกสร้างเป็น Confirmed Schedule
```

ระบบต้องแจ้งว่าไม่สามารถจัดแผนใหม่ตามข้อกำหนดปัจจุบันได้

ห้ามแก้ด้วยการ Relax Hard Constraint อย่างเงียบ ๆ

---

# 7.51 Replanning With Partial Feasibility

MVP ไม่ควรสร้าง Partial Proposal เมื่อ Required Activities บางรายการไม่สามารถ Schedule ได้

ตัวอย่าง:

```text
Required A ✓
Required B ✗
Optional C ✓
```

ต้องไม่คืน:

```text
A + C
```

แล้วบอกว่าเป็น Complete Replanning Result

ต้องรายงานว่า Complete Feasible Plan ไม่สามารถสร้างได้

Optional Activity เป็นข้อยกเว้นตาม Optional Policy

---

# 7.52 Replanning With Solver Timeout

กรณี:

```text
Solver
→ Time Limit
→ FEASIBLE
```

สามารถสร้าง Proposal จาก Feasible Result ได้ แต่ต้องไม่เรียกว่า Optimal

กรณี:

```text
Solver
→ UNKNOWN
→ No usable feasible solution
```

ต้องไม่สร้าง Proposal ที่อ้างว่าเป็น Feasible Schedule

---

# 7.53 Replanning and Notification

Notification ถูกปรับหลัง User Confirm เท่านั้น

Flow:

```text
New Proposal
      ↓
User Confirm
      ↓
New Schedule Version
      ↓
Mobile receives confirmed changes
      ↓
Cancel obsolete local notification
      ↓
Schedule new local notification
```

ก่อน Confirm:

```text
Proposal
→ No Notification Change
```

---

# 7.54 Example — Notification After Replanning

เดิม:

```text
Activity:
09:00

Notification:
08:00
```

Replanning Proposal:

```text
Activity:
12:00

Notification:
11:00
```

ก่อน User Confirm:

```text
Current Notification
= 08:00
```

ยังคงเดิม

หลัง Confirm:

```text
Cancel 08:00
Schedule 11:00
```

---

# 7.55 Custom Notification Conflict

ถ้า Activity มี Custom Notification:

```text
Notification = 11:30
Activity Start = 12:00
```

และ Replanning เปลี่ยน Activity เป็น:

```text
Start = 11:00
```

จะได้:

```text
Notification 11:30
>
Activity Start 11:00
```

ซึ่งผิด Notification Policy

ระบบต้องไม่แก้เป็น 10:00 เองโดยเงียบ ๆ

ต้อง:

```text
แจ้ง User
+
Require Correction
```

ตาม Notification Policy

---

# 7.56 Replanning and Manual Edit

Manual Edit ก็สามารถทำให้เกิด Planning Impact ได้

ตัวอย่าง:

```text
User manually moves Study
14:00 → 18:00
```

มีสองกรณี:

### Draft Only

ยังไม่ Confirm:

```text
Draft
→ Validate
```

ยังไม่เรียกว่า Current Schedule Change

### Confirmed Manual Edit

เมื่อ Confirm:

```text
New Schedule Version
```

หาก Product Policy กำหนดให้การเปลี่ยนดังกล่าวเป็น Trigger ของ Subsequent Replanning ต่อ Activity อื่น ระบบสามารถเข้าสู่ Impact Analysis ได้ แต่ไม่ควร Replan เพิ่มโดยไม่จำเป็น

---

# 7.57 Manual Edit vs Adaptive Replanning

ต้องแยก:

```text
Manual Edit
= User explicitly changes placement

Replanning
= System computes a new placement from changed context
```

Manual Edit ไม่ได้หมายความว่า User มอบหมายให้ AI/Replanner เปลี่ยนทั้งตาราง

ดังนั้น:

```text
Manual Edit
→ Draft
→ Validate
→ Confirm
```

ยังคงเป็น Human-Controlled Flow

---

# 7.58 Replanning Horizon and Stability Scope

Stability Metric ควรคำนวณใน Scope ที่เกี่ยวข้องกับ Replanning

ไม่ควรรวม Activities ทั้ง Calendar หากไม่ได้อยู่ใน Replanning Context

ดังนั้น:

```text
D =
Σ |new_start_i - old_start_i|
```

สำหรับ Activities ที่อยู่ใน Stability Scope ที่กำหนด

---

# 7.59 Stability and Frozen Items

Frozen Item ไม่จำเป็นต้องมีค่า Stability Objective เพราะ:

```text
new_start_i = old_start_i
```

ดังนั้น:

```text
|new_start_i - old_start_i| = 0
```

โดยธรรมชาติ

---

# 7.60 Change Propagation

การเปลี่ยนแปลงอาจ propagate ผ่าน:

```text
Activity
  ↓
Temporal Relation
  ↓
Related Activity
  ↓
Container
  ↓
Availability
  ↓
Deadline
```

แต่ไม่ควรขยาย Context อย่างไม่มีขอบเขต

ระบบต้องมีวิธีหยุดที่:

```text
Affected Context Boundary
```

เพื่อควบคุม Complexity

---

# 7.61 Bounded Replanning

Replanning ต้องอยู่ภายใน:

```text
MAX_REPLANNING_HORIZON
```

หรือ Operational Limit ที่กำหนดจาก Benchmark

หาก Affected Context ใหญ่เกิน Limit:

```text
REPLANNING_HORIZON_EXCEEDED
```

ระบบไม่ควร:

* ตัด Activity
* Relax Constraint
* เปลี่ยน Scope เงียบ ๆ

เพื่อให้ Solver ทำงานต่อ

---

# 7.62 Replanning Complexity Control

ตัวแปรที่มีผลต่อ Replanning ได้แก่:

```text
Affected Horizon
×
Affected Activity Count
×
Constraint Density
×
Candidate Count
```

ดังนั้น Performance Benchmark ควรประเมิน Replanning แยกจาก Initial Planning

เพราะแม้จำนวน Activity ทั้งหมดใน Calendar จะเท่ากัน แต่ Affected Context สามารถมีขนาดต่างกันมาก

---

# 7.63 Replanning Evaluation

Replanning ควรประเมินอย่างน้อย:

### Replanning Success

สามารถสร้าง Feasible New Schedule ได้หรือไม่

### Constraint Preservation

Hard Constraint ยังคงถูกต้องหรือไม่

### Requirement Satisfaction

Requirement ใหม่ถูกตอบสนองหรือไม่

### Preference Satisfaction

Preference ยังคงได้รับการตอบสนองในระดับใด

### Runtime

ใช้เวลา Replanning เท่าใด

### Changed Activities

มี Activity กี่รายการที่ถูกเปลี่ยน

### Start-Time Deviation

```text
D = Σ |new_start - old_start|
```

### Stability

วัดการรักษาส่วนที่ไม่จำเป็นต้องเปลี่ยน

---

# 7.64 Replanning Evaluation Metrics

ตัวอย่าง Metrics:

| Metric                       | ความหมาย                                       |
| ---------------------------- | ---------------------------------------------- |
| Replanning Success Rate      | สัดส่วนกรณีที่สร้าง Feasible Re-plan ได้       |
| Hard Constraint Violation    | จำนวน Hard Constraint ที่ผิด                   |
| Requirement Satisfaction     | ระดับที่ Requirement ใหม่ถูกตอบสนอง            |
| Preference Satisfaction      | ระดับ Preference                               |
| Runtime                      | เวลาในการ Replan                               |
| Changed Activity Count       | จำนวน Activity ที่เปลี่ยน                      |
| Start-Time Deviation         | ผลรวมการเปลี่ยน Start Time                     |
| Unaffected Preservation Rate | สัดส่วนกิจกรรมที่ไม่เกี่ยวข้องและไม่ถูกเปลี่ยน |

---

# 7.65 Unaffected Preservation

Metric นี้สำคัญกับ Adaptive Planning

แนวคิด:

```text
Unaffected Activities
        ↓
How many remained unchanged?
```

ตัวอย่าง:

```text
Unaffected = 10
Unchanged = 9

Preservation Rate = 90%
```

Metric นี้ช่วยวัดว่า Replanning รักษาส่วนที่ไม่จำเป็นต้องเปลี่ยนได้มากน้อยเพียงใด

---

# 7.66 Replanning Ablation

เพื่อดูผลของ Stability สามารถเปรียบเทียบ:

```text
Full Replanning
= Constraints + Preferences + Stability
```

กับ:

```text
Without Stability
= Constraints + Preferences
```

แล้วเปรียบเทียบ:

* Start-Time Deviation
* Changed Activity Count
* Requirement Satisfaction
* Preference Satisfaction
* Runtime

Hard Constraints และ Dataset ต้องเหมือนกัน

---

# 7.67 Feedback Ablation

สำหรับ RQ4 สามารถทดลอง:

```text
Planning without Feedback
vs
Planning with Feedback
```

หรือ:

```text
Before Feedback
vs
After Feedback
```

แล้ววัด:

* Requirement Satisfaction
* Preference Satisfaction
* User Acceptance
* Interaction Effort

---

# 7.68 Replanning Error Taxonomy

ข้อผิดพลาดด้าน Replanning ควรจำแนกเป็น:

```text
R1 Change Detection Error
R2 Impact Analysis Error
R3 Affected Context Error
R4 Horizon Selection Error
R5 Freeze / Movable Classification Error
R6 Constraint Construction Error
R7 Stability Objective Error
R8 Solver Failure
R9 Candidate Generation Error
R10 Proposal Staleness
R11 Confirmation Error
R12 Notification Synchronization Error
```

การจำแนกนี้ช่วยแยกปัญหาให้ชัดว่า Error เกิดที่ Replanning Layer, Planning Layer หรือ Schedule Management

---

# 7.69 Replanning Example — Full Scenario

สถานะเดิม:

```text
09:00–10:00  Exercise
10:00–12:00  Study
13:00–14:00  Lunch
14:00–16:00  Project
18:00–20:00  Dinner
```

User แจ้ง:

> “ประชุมเพิ่มพรุ่งนี้ 11 โมงถึงเที่ยง”

ระบบทำ:

```text
1. Detect New Activity
2. Determine Planning Impact
3. Identify Study as affected
4. Determine relevant horizon
5. Freeze unrelated items where possible
6. Add Meeting
7. Rebuild Model
8. Solve
9. Evaluate Stability
10. Create Proposal
```

อาจได้:

```text
Candidate A
09:00–10:00 Exercise
10:00–11:00 Study
11:00–12:00 Meeting
13:00–14:00 Lunch
14:00–16:00 Project
18:00–20:00 Dinner
```

หรือ:

```text
Candidate B
09:00–10:00 Exercise
12:00–14:00 Study
11:00–12:00 Meeting
13:00–14:00 Lunch
...
```

แต่ Candidate B จะถูกยอมรับได้ก็ต่อเมื่อผ่าน Hard Constraints และไม่มี Conflict

User จึงเป็นผู้เลือกว่าจะยืนยัน Candidate ใด

---

# 7.70 Replanning Example — No Feasible Solution

Existing:

```text
Meeting
14:00–16:00
```

User เพิ่ม:

```text
Unavailability
13:00–17:00
```

และ Meeting เป็น Fixed Time

ผล:

```text
Meeting conflicts with Unavailability
```

ไม่มีการย้าย:

```text
14:00 → 17:00
```

เพราะ Fixed Time เป็น Requirement

ผลคือ:

```text
NO_FEASIBLE_PLAN
```

Current Confirmed Schedule ยังคงเดิม จนกว่าผู้ใช้จะเปลี่ยน Constraint/Requirement แล้วสร้าง Replanning ใหม่

---

# 7.71 Replanning Example — Long-range Change

Current date:

```text
7 January
```

Activity:

```text
15 February 14:00–16:00
```

User เปลี่ยนเป็น:

```text
16 February 10:00–12:00
```

ระบบไม่จำเป็นต้อง Replan Calendar ทั้งหมด

สามารถ:

```text
Identify affected period
        ↓
12–18 February
        ↓
Replan only affected context
```

Calendar ยังคงรองรับข้อมูลระยะไกล

---

# 7.72 Replanning Example — Feedback

Initial Proposal:

```text
Study = 14:00–16:00
Project = 16:00–18:00
```

User:

> “ไม่อยากทำงานติดกัน ขอมีเวลาพักอย่างน้อยหนึ่งชั่วโมง”

AI/NLP:

```text
Requirement:
rest_gap >= 60 min
```

Replanning:

```text
Existing Schedule
+
rest_gap >= 60
+
Hard Constraints
+
Preferences
+
Stability
```

New Proposal:

```text
Study = 14:00–16:00
Rest  = 16:00–17:00
Project = 17:00–19:00
```

หรือ Candidate ทางเลือกอื่นที่ Feasible

แต่ยังไม่เป็น Confirmed Schedule จนกว่า User จะ Confirm

---

# 7.73 Replanning and Human-in-the-Loop

Replanning ถูกออกแบบเป็น:

```text
System Detects
      ↓
System Computes
      ↓
System Proposes
      ↓
Human Reviews
      ↓
Human Decides
```

ไม่ใช่:

```text
System Detects
      ↓
System Decides
      ↓
System Applies
```

หลักนี้เป็นหนึ่งใน Core Invariants ของ LONGTUA

---

# 7.74 Replanning Invariants

```text
REP-INV-01
Confirmed Schedule is never changed directly by Replanning.

REP-INV-02
Every Replanning result must become a Proposal before confirmation.

REP-INV-03
Past Schedule Items are not moved backward in time.

REP-INV-04
Unaffected Schedule Items should remain unchanged when possible.

REP-INV-05
Hard Constraints are never silently relaxed.

REP-INV-06
New Explicit Requirements take priority over Stability.

REP-INV-07
Stability is evaluated only within the relevant Replanning Scope.

REP-INV-08
Replanning Horizon is context-dependent.

REP-INV-09
Calendar Data Range is independent from Replanning Horizon.

REP-INV-10
MVP uses Full Model Rebuild + Re-solve.

REP-INV-11
A stale Proposal cannot override a newer Schedule Version.

REP-INV-12
A Replanning failure leaves the Current Confirmed Schedule unchanged.

REP-INV-13
Notification changes occur only after New Schedule Confirmation.

REP-INV-14
No Partial Plan is returned when required activities cannot all be scheduled.

REP-INV-15
Replanning must not invent missing planning-critical information.
```

---

# 7.75 Replanning Architecture

```text
                  CHANGE
                    |
                    v
          +--------------------+
          | Change Detection   |
          +---------+----------+
                    |
                    v
          +--------------------+
          | Impact Analysis    |
          +---------+----------+
                    |
                    v
          +--------------------+
          | Affected Context   |
          +---------+----------+
                    |
                    v
          +--------------------+
          | Replanning Horizon |
          +---------+----------+
                    |
          +---------+---------+
          |                   |
          v                   v
      Frozen Items       Movable/New Items
          |                   |
          +---------+---------+
                    |
                    v
          +--------------------+
          | Model Reconstruction|
          +---------+----------+
                    |
                    v
          +--------------------+
          | CP-SAT Re-solve    |
          +---------+----------+
                    |
                    v
          +--------------------+
          | Result Validation  |
          +---------+----------+
                    |
                    v
          +--------------------+
          | Candidate Generation|
          +---------+----------+
                    |
                    v
                Proposal
                    |
                    v
              User Review
                    |
             +------+------+
             |             |
           Reject        Confirm
             |             |
             v             v
            End     New Schedule Version
                           |
                           v
                    Notification Update
```

---

# 7.76 Replanning Data Flow

```text
Existing Confirmed Schedule
          +
New Change / Feedback
          |
          v
   Impact Detection
          |
          v
   Affected Objects
          |
          v
Affected Replanning Horizon
          |
          v
+--------------------------+
| New Planning Model       |
|                          |
| Frozen Schedule          |
| Movable Schedule         |
| New Activities           |
| Hard Constraints         |
| Preferences              |
| Stability Reference      |
+------------+-------------+
             |
             v
          CP-SAT
             |
             v
       New Candidate(s)
             |
             v
          Proposal
             |
             v
        User Review
             |
             v
          Confirm?
         /       \
       No         Yes
       |           |
       v           v
 Current       New Version
 remains           |
 unchanged         v
              Notification
```

---

# 7.77 Replanning Contract

Replanning Input ระดับ Concept:

```text
ReplanningRequest
├── current_schedule_version
├── changed_objects
├── new_requirements
├── new_preferences
├── affected_context
├── replanning_horizon
└── stability_reference
```

Replanning Output:

```text
ReplanningResult
├── status
├── candidates[]
├── changed_items[]
├── preserved_items[]
├── objective_summary
├── stability_metrics
├── solver_metrics
└── diagnostics
```

Field-level Contract จะถูกทำให้เป็นทางการใน API / Application Contract ภายหลัง

---

# 7.78 Replanning and Database

Replanning ไม่จำเป็นต้องมี `replanning` table แยกใน MVP

ข้อมูลที่จำเป็นสามารถกระจายตาม Domain Entities ที่มีอยู่:

```text
planning_requests
planning_objects
planning_rules
temporal_relations
proposals
proposal_items
schedule_versions
schedule_items
```

Current Replanning Context เป็น Application/Planning State

ไม่จำเป็นต้อง Persist ทุก Intermediate State

---

# 7.79 Replanning and Schedule History

Historical Schedule Version ต้องไม่ถูกแก้

ตัวอย่าง:

```text
V1
↓
Initial Plan

V2
↓
After Replanning

V3
↓
After User Feedback
```

สามารถตรวจสอบว่า Schedule เปลี่ยนอย่างไรจากแต่ละ Version ได้

---

# 7.80 Replanning and Evaluation Traceability

Replanning Design สนับสนุน:

### RQ3

> Can the system adapt/re-plan when new information or situations arise?

วัด:

```text
Replanning Success
Constraint Preservation
Runtime
Changed Activities
Start-Time Deviation
```

### RQ4

> Does user feedback during re-planning improve alignment with requirements?

วัด:

```text
Before Feedback
vs
After Feedback

Requirement Satisfaction
Preference Satisfaction
User Acceptance
Interaction Effort
```

---

# 7.81 Replanning Performance Benchmark

ควรแยก Benchmark ของ Replanning จาก Initial Planning

ตัวแปร:

```text
Affected Horizon
×
Affected Object Count
×
Constraint Density
×
Candidate Count
```

วัด:

```text
Replanning Runtime
Memory Usage
Feasibility
Objective Quality
Candidate Generation Runtime
```

เพราะ:

```text
Total Calendar Objects
≠
Replanning Problem Size
```

---

# 7.82 Replanning Limitations in MVP

MVP ตั้งใจไม่รองรับ:

* Incremental Solver State
* Advanced Multi-objective Dynamic Optimization
* Reinforcement Learning for Replanning
* Autonomous Schedule Changes
* Real-time Traffic-based Replanning
* Concurrent Multitasking
* Activity Splitting
* Complex Recurrence-driven Replanning

ข้อจำกัดเหล่านี้ช่วยให้ Replanning Model มีขอบเขตที่ชัดและสามารถประเมินได้ภายในเวลาและทรัพยากรของโครงการ

---

# 7.83 Replanning Design Summary

Adaptive Replanning ของ LONGTUA ไม่ได้หมายถึงการ “เลื่อนทุกกิจกรรมใหม่เมื่อมีอะไรเปลี่ยน”

แต่เป็นกระบวนการ:

```text
Change
 ↓
Understand Impact
 ↓
Identify Affected Context
 ↓
Bound the Replanning Horizon
 ↓
Preserve Unaffected Schedule
 ↓
Rebuild Planning Model
 ↓
Solve with New Requirements
 ↓
Consider Stability
 ↓
Generate Proposal
 ↓
User Decides
 ↓
Create New Schedule Version
```

หลักสำคัญที่สุดคือ:

> **เปลี่ยนเท่าที่จำเป็น แต่ไม่รักษาตารางเดิมจนขัดกับความต้องการใหม่ของผู้ใช้**

ดังนั้น Adaptive ของ LONGTUA จึงเกิดจากการรวม:

```text
Change Detection
+
Constraint-based Replanning
+
Stability
+
Human-in-the-Loop
```

เข้าด้วยกัน
