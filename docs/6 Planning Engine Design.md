# 6. Planning Engine Design

## 6.1 Purpose

เอกสารฉบับนี้กำหนดการออกแบบ Planning Engine ของ LONGTUA — Personal Adaptive Planner ตั้งแต่การรับ Planning Representation การสร้าง Constraint Programming Model ด้วย Google OR-Tools CP-SAT การกำหนดตัวแปรตัดสินใจ การกำหนด Hard Constraints และ Preferences การสร้าง Candidate Plans การจัดการ Initial Planning และ Replanning ตลอดจนการจัดการผลลัพธ์และข้อผิดพลาดของ Solver

Planning Engine เป็น **Scheduling / Optimization Layer** ของระบบ

หน้าที่หลักคือ:

> **นำข้อมูลที่ผ่านการทำความเข้าใจและตรวจสอบแล้วมาคำนวณว่า Activity ควรถูกจัดวางลงในช่วงเวลาใดภายใต้ข้อจำกัดและความต้องการที่กำหนด**

Planning Engine ไม่รับผิดชอบ:

* Natural Language Understanding
* Prompt Processing
* Intent Extraction
* Ambiguity Detection
* Clarification Question Generation
* User Confirmation
* Notification Generation

---

# 6.2 Planning Engine Role

ตำแหน่งของ Planning Engine ในระบบ:

```text
Natural Language
      ↓
AI / NLP
      ↓
Structured Planning Information
      ↓
Validation / Normalization
      ↓
Planning Representation
      ↓
┌─────────────────────────────┐
│       Planning Engine       │
│                             │
│  Model Construction         │
│  Constraints                │
│  Preferences                │
│  Optimization               │
│  Candidate Generation       │
└──────────────┬──────────────┘
               ↓
          Candidate(s)
               ↓
            Proposal
```

หลักการสำคัญ:

> AI เป็นผู้ตีความข้อมูล
> Planning Engine เป็นผู้คำนวณ Schedule
> User เป็นผู้ตัดสินใจผลลัพธ์

---

# 6.3 Planning Technology

LONGTUA ใช้:

> **Google OR-Tools CP-SAT**

เป็น Planning / Optimization Engine หลัก

CP-SAT ถูกออกแบบสำหรับปัญหา Integer Programming / Constraint Programming และใช้ตัวแปรและข้อจำกัดที่อยู่ในรูป Integer โดยตรง จึงสอดคล้องกับการแทนเวลาเป็นจำนวนเต็มนาทีภายใน Planning Horizon ของ LONGTUA

OR-Tools ยังมีรูปแบบ Modeling สำหรับ Scheduling ที่ใช้ Start Time, End Time และ Interval Variables รวมถึง Constraints เช่น Precedence และ No-Overlap ซึ่งเป็นแนวคิดที่ตรงกับ Scheduling Model ของ LONGTUA

การเลือก CP-SAT เป็นการเลือก Technology สำหรับ MVP ไม่ได้หมายความว่าเป็น Algorithm ที่ดีที่สุดสำหรับ Personal Planning ทุกกรณี

---

# 6.4 Planning Engine Inputs

Planning Engine ไม่รับ Natural Language โดยตรง

Input หลักคือ:

```text
Planning Representation
```

ประกอบด้วยข้อมูลที่ผ่าน:

```text
AI / NLP
      ↓
Schema Validation
      ↓
Domain Validation
      ↓
Normalization
      ↓
Planning Representation
```

ข้อมูลที่ Planning Engine สามารถใช้ได้ เช่น:

* Planning Objects
* Activity Information
* Start / End Constraints
* Duration
* Deadline
* Time Windows
* Availability
* Unavailability
* Precedence
* Container Membership
* Hard Constraints
* Preferences
* Existing Schedule
* Planning Horizon
* Replanning Context
* Stability Reference
* Optional / Required Status

---

# 6.5 Planning Readiness

ก่อนสร้าง CP-SAT Model ระบบต้องตรวจว่า Planning Representation พร้อมสำหรับการคำนวณหรือไม่

```text
Planning Representation
        ↓
Planning Readiness Check
        ↓
     Ready?
    /      \
  Yes       No
   ↓         ↓
 Build      Clarify /
 Model      Store / Fail
```

ข้อมูลที่ยังเป็น Unknown ไม่ได้หมายความว่าจะเข้าสู่ Planner ได้เสมอ

ตัวอย่าง:

> “พรุ่งนี้อยากทำรายงาน”

หาก Operation ต้องสร้าง Schedule ทันที แต่ Duration เป็นข้อมูลที่จำเป็นและไม่มี Policy ที่ใช้แทนได้ ระบบอาจยังไม่ Planning Ready

แต่หาก User เพียงต้องการเก็บ Activity ไว้ก่อน ระบบสามารถเก็บเป็น Date-Only Activity โดยไม่เรียก Planning Engine

ดังนั้น:

```text
Stored Activity
≠
Schedulable Activity
```

---

# 6.6 Schedulable Activity

Activity ที่เข้าสู่ CP-SAT ต้องมีข้อมูลเพียงพอสำหรับการกำหนด Placement ใน Schedule ตาม Policy ของ Operation นั้น

อย่างน้อยต้องสามารถกำหนด:

```text
Start Time
End Time
Duration
```

ในกรณีที่ Start Time ยัง Flexible ระบบสามารถให้ Solver เป็นผู้เลือก Start Time ได้

ตัวอย่าง:

```text
Duration = 120 min
Window = AFTERNOON
```

ไม่จำเป็นต้องรู้ Start Time ล่วงหน้า

Planner จะเป็นผู้หา:

```text
s_i
```

ที่เหมาะสมภายในขอบเขตที่อนุญาต

---

# 6.7 Planning Horizon

Planning Horizon คือช่วงเวลาที่ CP-SAT ใช้ในการคำนวณหนึ่ง Operation

กำหนดเป็น:

```text
H = [H_start, H_end)
```

ภายใน Model ใช้ Integer Minutes โดยกำหนดจุดเริ่มต้นของ Horizon เป็น `0`

ตัวอย่าง:

```text
Planning Horizon:
2026-10-04 00:00
        ถึง
2026-10-06 00:00
```

สามารถแปลงเป็น:

```text
0 → 2880 minutes
```

ไม่ใช้ Fixed 15-Minute Slot เป็นพื้นฐานของ Model

---

# 6.8 Calendar Range vs Planning Horizon

สองแนวคิดนี้ต้องแยกจากกันอย่างเด็ดขาด

```text
Calendar Data Range
= ขอบเขตการเก็บ/ดู/แก้ไขข้อมูล

Planning Horizon
= ขอบเขตการคำนวณของ CP-SAT
```

ดังนั้น Activity ในเดือนถัดไปยังสามารถมีอยู่ใน Database และ Calendar ได้ แม้ไม่ได้ถูกส่งเข้า Solver ใน Planning Operation ปัจจุบัน

เมื่อ Activity ระยะไกลได้รับผลกระทบจากการเปลี่ยนแปลง ระบบสามารถกำหนด Affected Replanning Horizon ใหม่ตามบริบท

---

# 6.9 Internal Time Representation

เวลาภายใน CP-SAT ใช้:

> **Integer Minutes Relative to Planning Horizon**

เช่น:

```text
Horizon Start = 08:00

08:00 → 0
08:30 → 30
09:00 → 60
```

ข้อดี:

* CP-SAT ทำงานกับ Integer ได้โดยตรง
* หลีกเลี่ยง Floating Point
* รองรับเวลาแบบละเอียดถึงระดับนาที
* ไม่บังคับ Slot Size ตายตัว
* แปลงกลับเป็น DateTime ได้ง่าย

CP-SAT ต้องสร้าง Model บนค่า Integer ตามรูปแบบของ Solver อย่างเป็นทางการ

---

# 6.10 Planning Variables

สำหรับ Activity ที่ต้อง Schedule:

```text
s_i = Start Time
e_i = End Time
d_i = Duration
```

มีความสัมพันธ์:

```text
e_i = s_i + d_i
```

โดย `d_i` เป็นค่าคงที่หรือค่าที่กำหนดตาม Planning Representation

การ Modeling ในรูป Start / End / Interval เป็นรูปแบบมาตรฐานที่ OR-Tools ใช้กับ Scheduling Problems

---

# 6.11 Interval Representation

สำหรับ Activity ที่มี Duration แน่นอน สามารถสร้าง:

```text
Interval_i = [s_i, e_i)
```

โดย:

```text
e_i = s_i + d_i
```

การใช้ Half-Open Interval สอดคล้องกับ Domain Rule ของ LONGTUA:

```text
[start, end)
```

ดังนั้น:

```text
09:00–10:00
10:00–11:00
```

ไม่ถือว่า Overlap

---

# 6.12 Decision Variable Domain

Start Time ของ Activity ต้องอยู่ภายใน Planning Horizon:

```text
H_start ≤ s_i
```

และ:

```text
e_i ≤ H_end
```

หรือใน Relative Integer Representation:

```text
0 ≤ s_i
e_i ≤ H
```

โดย `H` คือความยาวของ Planning Horizon

---

# 6.13 Fixed Time Constraint

หาก User ระบุเวลาตายตัว:

```text
Start = 14:00
End = 16:00
```

Planner ต้องกำหนด:

```text
s_i = 14:00
e_i = 16:00
```

Fixed Time เป็น Hard Constraint

ไม่ควรเลื่อนเพื่อสร้าง Candidate เพิ่ม

หาก Fixed Time ขัดกับ Hard Constraints อื่นและไม่มีทางแก้ไข:

```text
NO_FEASIBLE_PLAN
```

OR-Tools Scheduling Examples ใช้ Constraint ที่กำหนด Start/End และ Duration ให้สัมพันธ์กันในลักษณะเดียวกัน

---

# 6.14 Earliest Start

หาก Activity ต้องไม่เริ่มก่อนเวลาที่กำหนด:

```text
s_i ≥ earliest_start_i
```

ตัวอย่าง:

> “หลัง 13:00 ค่อยทำงานนี้”

จะกลายเป็น:

```text
s_i ≥ 13:00
```

---

# 6.15 Latest Start

หาก Domain หรือ Constraint กำหนด Latest Start:

```text
s_i ≤ latest_start_i
```

ค่า Latest Start สามารถเกิดจาก Deadline และ Duration ได้ เช่น:

```text
latest_start = deadline - duration
```

โดย Planner สามารถคำนวณ Domain นี้จากข้อมูลที่ผ่าน Normalization แล้ว

---

# 6.16 Deadline Constraint

หาก Activity มี Deadline:

```text
e_i ≤ deadline_i
```

Deadline หมายถึงเวลาสุดท้ายที่ Activity ต้องเสร็จ

ไม่ใช่ Start Time

ตัวอย่าง:

```text
Duration = 120
Deadline = 18:00
```

ต้องมี:

```text
e_i ≤ 18:00
```

---

# 6.17 Semantic Time Window

Semantic Window เช่น:

```text
MORNING
AFTERNOON
EVENING
```

ไม่ควรถูกส่งให้ CP-SAT เป็นคำภาษาไทยหรือ String

ต้องผ่าน:

```text
Semantic Window
      ↓
Time Window Policy
      ↓
Concrete Interval(s)
      ↓
Planning Constraint
```

ตัวอย่าง:

```text
AFTERNOON
→ 13:00–16:00
```

หาก User Override:

```text
AFTERNOON
→ 12:00–17:00
```

Planner ใช้ Concrete Range ที่ผ่าน Normalization แล้ว

---

# 6.18 Time Window Constraint

หาก Activity ต้องอยู่ภายในช่วง:

```text
W = [w_start, w_end)
```

โดย Activity ไม่สามารถแบ่งออกเป็นหลายช่วงใน MVP:

```text
s_i ≥ w_start
e_i ≤ w_end
```

ดังนั้น Activity ต้องอยู่ภายใน Window เดียวอย่างสมบูรณ์

ตัวอย่าง:

```text
Window = 13:00–16:00
Duration = 2h
```

Valid:

```text
13:00–15:00
14:00–16:00
```

Invalid:

```text
15:00–17:00
```

---

# 6.19 Cross-Midnight Time Window

Time Window ที่คร่อมเที่ยงคืน เช่น:

```text
19:00–06:00
```

ต้องถูก Normalize ให้เป็น Concrete Date-Scoped Intervals ก่อนเข้าสู่ Planning Model

ตัวอย่าง:

```text
2026-10-04 19:00
→
2026-10-05 06:00
```

Planner ไม่ควรต้องตีความความหมายของคำว่า “กลางคืน” เอง

---

# 6.20 Availability Constraint

Availability กำหนดช่วงที่ Activity สามารถถูกวางได้

สมมติ Available Interval:

```text
A = [a_start, a_end)
```

Activity ต้อง satisfy:

```text
s_i ≥ a_start
e_i ≤ a_end
```

หากมีหลาย Availability Windows ระบบสามารถเลือก Window ที่เหมาะสมได้ แต่ Activity หนึ่งรายการไม่สามารถถูกแบ่งข้าม Window ใน MVP

---

# 6.21 Multiple Availability Windows

ตัวอย่าง:

```text
Availability:
09:00–12:00
13:00–17:00
```

Activity 2 ชั่วโมงสามารถอยู่ใน:

```text
09:00–11:00
10:00–12:00
13:00–15:00
15:00–17:00
```

แต่ไม่สามารถ:

```text
11:00–14:00
```

เพราะมีช่วง Unavailable 12:00–13:00 คั่นกลาง

หลักนี้เกิดจากการที่ Activity ต้องเป็น Continuous Interval ใน MVP

---

# 6.22 Unavailability Constraint

สำหรับ Unavailable Interval:

```text
U = [u_start, u_end)
```

Activity ต้องไม่ overlap:

```text
e_i ≤ u_start
OR
u_end ≤ s_i
```

ดังนั้น:

```text
Activity overlaps Unavailability
→ Hard Conflict
```

---

# 6.23 No-Overlap Constraint

สำหรับ Activity สองรายการที่ใช้ Execution Context เดียวกัน:

```text
i
j
```

ต้องมีอย่างใดอย่างหนึ่ง:

```text
e_i ≤ s_j
```

หรือ:

```text
e_j ≤ s_i
```

จึงจะไม่เกิด Overlap

Constraint ลักษณะนี้เป็นรูปแบบพื้นฐานของ Scheduling / No-Overlap Modeling ใน OR-Tools

---

# 6.24 Execution Context

MVP ถือว่า User มี Execution Capacity หลักหนึ่งชุดสำหรับ Activity ที่ต้องใช้เวลาของผู้ใช้

ดังนั้น Activity ทั่วไปจะไม่สามารถทำพร้อมกันได้

ตัวอย่าง:

```text
Study
14:00–15:00

Meeting
14:30–15:30
```

เกิด:

```text
Conflict
```

ข้อยกเว้นสำคัญคือ Container Membership

---

# 6.25 Container / Child Constraint

สมมติ:

```text
Container C
Child Activity A
```

ต้องมี:

```text
s_C ≤ s_A
e_A ≤ e_C
```

จึงทำให้ Child อยู่ภายใน Container

Child สามารถ overlap Container ได้:

```text
Container
08:00–17:00

Child
14:00–16:00
```

และไม่ถือเป็น Conflict

---

# 6.26 Container Exclusivity

Container ใน MVP เป็น Exclusive Commitment

ดังนั้น Activity ที่ไม่ใช่ Child:

```text
Unrelated Activity
```

ไม่สามารถ overlap Container ได้

ตัวอย่าง:

```text
Container
08:00–17:00

Unrelated Activity
15:00–16:00
```

ถือว่า Conflict

จึงได้:

```text
Container ↔ Child
    Allowed

Container ↔ Unrelated Activity
    Conflict
```

---

# 6.27 Container and No-Overlap

การสร้าง No-Overlap Constraint ต้องพิจารณา Membership ก่อน

ไม่ควรทำ:

```text
NoOverlap(all intervals)
```

แบบไม่ดูความสัมพันธ์

เพราะจะทำให้:

```text
Container 08:00–17:00
Child     14:00–16:00
```

ถูกมองว่า Conflict อย่างผิดความหมาย

ดังนั้น Constraint Construction ต้องเข้าใจ Domain Semantics ก่อนสร้าง CP-SAT Model

---

# 6.28 Precedence Constraint

สำหรับ:

```text
A BEFORE B
```

ใช้:

```text
e_A ≤ s_B
```

สำหรับ:

```text
A AFTER B
```

สามารถ Normalize เป็น:

```text
B BEFORE A
```

ดังนั้นภายใน Planning Model สามารถใช้ Canonical Relation `BEFORE` เป็นหลักได้

Precedence Constraint เป็นหนึ่งใน Constraint พื้นฐานของ Scheduling Problems ที่ OR-Tools ใช้ในตัวอย่าง Job Shop Scheduling

---

# 6.29 OVERLAP Relation

`OVERLAP` เป็น Semantic Temporal Relation

แต่:

```text
Temporal OVERLAP
≠
Scheduling Permission
```

ใน MVP:

```text
Activity A OVERLAP Activity B
```

ไม่ได้ทำให้ Planner อนุญาตให้ A และ B ทำพร้อมกัน

หาก Input ต้องการ Concurrent Execution จริง ๆ ระบบต้องถือว่าอยู่นอก Capability ของ MVP และต้องไม่สร้าง overlapping schedule แบบเงียบ ๆ

---

# 6.30 Conflict Semantics in Planner

Planner ต้องใช้ Domain Context ก่อนตัดสิน Conflict

### Activity ↔ Activity

Same Execution Context + overlap:

```text
Conflict
```

### Activity ↔ Unavailability

Overlap:

```text
Conflict
```

### Activity ↔ Availability

Overlap:

```text
Allowed
```

### Container ↔ Child

Overlap:

```text
Allowed
```

### Container ↔ Unrelated Activity

Overlap:

```text
Conflict
```

---

# 6.31 Duration Constraint

Duration เป็นส่วนหนึ่งของ Interval Model:

```text
e_i = s_i + d_i
```

โดย:

```text
d_i > 0
```

ถ้า Duration เป็น Approximate Value:

```text
d_i = nominal_duration
qualifier = APPROXIMATE
```

MVP ใช้ Nominal Duration ในการคำนวณ แต่ต้องไม่เปลี่ยนข้อมูลต้นทางให้ดูเหมือนเป็น Exact Duration

---

# 6.32 Activity That Cannot Be Scheduled

กรณีต่อไปนี้อาจทำให้ Activity ยังไม่สามารถเข้าสู่ Solver:

```text
Duration = Unknown
Required Time = Unknown
Planning Operation ต้องใช้ข้อมูลดังกล่าว
```

ระบบต้อง:

```text
Clarify
```

แทน:

```text
Guess Duration
```

อย่างไรก็ตาม Date-Only Activity สามารถถูกเก็บไว้ในระบบโดยยังไม่ถูก Schedule ได้ เมื่อ Operation ปัจจุบันไม่จำเป็นต้องนำ Activity นั้นเข้าสู่ Planner

---

# 6.33 Required vs Optional Activities

Planning Model ต้องสามารถแยก Activity เป็น:

```text
REQUIRED
OPTIONAL
```

### Required

ต้องอยู่ใน Schedule ที่ Feasible

### Optional

สามารถถูกละไว้ได้หากไม่สามารถจัดได้โดยไม่เสีย Hard Constraints และไม่ขัดกับการวางแผนของ Required Activities

Optional Activities จะอยู่ในลำดับต่ำสุดของ Objective Hierarchy

---

# 6.34 Required Activity Rule

หาก Required Activity ไม่สามารถถูก Schedule ได้:

```text
NO_FEASIBLE_PLAN
```

ไม่ใช่:

```text
Remove Activity
```

เพื่อให้ Solver ได้คำตอบ

---

# 6.35 Optional Activity Rule

Optional Activity อาจถูก:

```text
Scheduled
```

หรือ:

```text
Not Scheduled
```

ตาม Objective

แต่การไม่ Schedule ต้องสามารถอธิบายได้ตาม Planning Result

ไม่ควรตัด Optional Activity แบบเงียบ ๆ

---

# 6.36 Hard Constraints

Hard Constraints เป็น Constraints ที่ต้องเป็นจริงในทุก Feasible Solution

LONGTUA รองรับอย่างน้อย:

```text
1. Planning Horizon
2. Duration
3. Fixed Time
4. Earliest Start
5. Latest Start
6. Time Window
7. Deadline
8. Availability
9. Unavailability
10. No-Overlap
11. Precedence
12. Container Containment
13. Required Activity Presence
```

หาก Constraint ใดถูกละเมิด:

```text
Solution = Not Feasible
```

---

# 6.37 Hard Constraint Integrity

Planning Engine ห้ามทำสิ่งต่อไปนี้เพื่อสร้าง Solution:

```text
Relax Fixed Time
Ignore Deadline
Ignore Unavailability
Allow Required Activities to overlap
Move activity outside Time Window
Remove Required Activity
```

โดยไม่ได้รับอนุญาตจาก User/Policy อย่างชัดเจน

หลักการคือ:

> **No Silent Relaxation**

---

# 6.38 Preferences

Preferences เป็น Soft Objectives

ตัวอย่าง:

> “อยากอ่านหนังสือตอนเย็น”

หรือ:

> “ถ้าเป็นไปได้อยากจัดงานสำคัญก่อน”

Preference จะไม่ทำให้ Schedule เป็น Invalid หากไม่สามารถทำตามได้

ตัวอย่าง:

```text
Preference:
Study → EVENING
```

ถ้าช่วง Evening เต็ม:

```text
Schedule ยัง Feasible
Preference Satisfaction ลดลง
```

---

# 6.39 Preference Representation

Preference เชิงนามธรรมควรถูกแปลงเป็นตัวแปรหรือค่า Satisfaction ที่ Planner ประเมินได้

แนวคิด:

```text
Preference P_j
       ↓
Satisfaction Variable q_j
       ↓
0 = Not Satisfied
1 = Satisfied
```

หรือสามารถใช้ Score ที่ละเอียดขึ้นเมื่อมีเหตุผลทาง Domain รองรับ

---

# 6.40 Objective Hierarchy

Planning Engine ใช้ Hierarchical Objective:

```text
Level 1
Hard Feasibility
        ↓
Level 2
Explicit User Requirements
        ↓
Level 3
Preferences
        ↓
Level 4
Stability
        ↓
Level 5
Optional Activities
```

โดย Hard Constraint เป็นเงื่อนไขความเป็นไปได้ ไม่ใช่ Soft Score

ดังนั้น:

```text
Feasible + Good Preferences
```

ดีกว่า:

```text
Infeasible + Perfect Preferences
```

เพราะ Solution หลังไม่ใช่ Feasible Schedule

---

# 6.41 Explicit Requirement vs Preference

Requirement ที่ผู้ใช้แสดงอย่างชัดเจนแต่มีลักษณะบังคับ เช่น:

> “ต้องประชุมตอน 10 โมง”

ควรถูกแทนเป็น Hard Constraint

ส่วนข้อความเชิงความต้องการ เช่น:

> “อยากอ่านหนังสือตอนเย็น”

สามารถถูกแทนเป็น Preference

ดังนั้น NLP/Validation ต้องช่วยระบุ Requirement Strength ก่อนเข้าสู่ Planning Representation

---

# 6.42 Lexicographic Objective

เพื่อให้ Objective Hierarchy ไม่ขึ้นอยู่กับ Weight ที่ตั้งแบบ Arbitrary ระบบควรใช้แนวคิด **Lexicographic Optimization**

เชิงแนวคิด:

```text
Optimize Level 1
        ↓
Fix / Preserve best Level 1 result
        ↓
Optimize Level 2
        ↓
Fix / Preserve best Level 2 result
        ↓
Optimize Level 3
        ↓
...
```

หรือใช้ Dominance Weights ที่คำนวณอย่างปลอดภัยจาก Upper Bounds

วิธี Implementation ที่แน่นอนสามารถตัดสินใจภายหลัง แต่ต้องรักษาลำดับความสำคัญเดิม

---

# 6.43 Initial Planning Objective

Initial Planning ไม่มี Existing Confirmed Schedule ที่ต้องรักษา

ดังนั้น:

```text
Stability
```

ไม่จำเป็นต้องมีผลในการ Optimize

หลักคือ:

```text
Feasibility
→ User Requirements
→ Preferences
→ Optional Activities
```

---

# 6.44 Replanning Objective

Replanning มี Existing Confirmed Schedule

ดังนั้น:

```text
Feasibility
→ New Explicit Requirements
→ Preferences
→ Stability
→ Optional Activities
```

Stability ถูกนำเข้าหลัง Requirement และ Preference เพื่อไม่ให้ระบบพยายามรักษาตารางเก่าจนขัดกับความต้องการใหม่ของ User

---

# 6.45 Stability Objective

ใน Replanning ใช้ Existing Schedule เป็น Reference

สำหรับ Activity `i`:

```text
old_start_i = Start Time เดิม
new_start_i = Start Time ใหม่
```

Operational Stability Measure:

```text
D = Σ |new_start_i - old_start_i|
```

เป้าหมายของ Stability:

```text
Minimize D
```

ในขอบเขตของ Activities ที่สามารถเปลี่ยนเวลาได้

---

# 6.46 Stability Does Not Override Requirements

ตัวอย่าง:

```text
Existing:
Study 14:00–16:00
Dinner 18:00–20:00
```

User เปลี่ยน Requirement:

```text
Study ต้องเป็น 10:00
```

แม้จะทำให้:

```text
|10:00 - 14:00| = 240 min
```

แต่ Requirement ใหม่มี Priority สูงกว่า Stability

ดังนั้น Planner ต้องยอมเปลี่ยนเวลาของ Study

หลัก:

```text
Requirement > Stability
```

---

# 6.47 Affected Activities in Replanning

ไม่ใช่ทุก Activity ใน Calendar ต้องถูก Optimize ใหม่

ก่อนสร้าง Model:

```text
Changed Object
      ↓
Impact Detection
      ↓
Related Activities
      ↓
Affected Schedule
```

ระบบระบุ:

```text
Frozen Activities
Movable Activities
New Activities
Removed / Cancelled Activities
```

---

# 6.48 Frozen Activities

Activity ที่อยู่นอก Affected Context หรืออยู่ใน Past สามารถถูก Freeze

เช่น:

```text
Past Activity
→ fixed at existing placement
```

หรือไม่ต้องเข้าสู่ Model หากพ้น Planning Horizon

Unaffected future activities อาจถูกนำเข้าเป็น Fixed Placement เพื่อรักษา Schedule เดิมตาม Replanning Policy

---

# 6.49 Movable Activities

Activity ที่ได้รับผลกระทบและสามารถเลื่อนได้จะมี Decision Variables ใหม่:

```text
s_new_i
e_new_i
```

และ Stability Reference:

```text
s_old_i
```

---

# 6.50 New Activities

Activity ที่เกิดขึ้นจาก User Input ใหม่จะถูกเพิ่มเข้ามาใน Planning Model

ตัวอย่าง:

```text
Existing Schedule
+
New Meeting
```

Planner ต้องจัด Meeting ร่วมกับ Existing Context และ Constraints ที่เกี่ยวข้อง

---

# 6.51 Cancelled Activities

หาก Activity ถูก Cancel:

```text
Activity
→ Removed from Active Planning Set
```

และหากการยกเลิกส่งผลต่อ Current Schedule:

```text
Impact Detection
→ Replanning
```

แต่ไม่จำเป็นต้องลบ Historical Schedule Version

---

# 6.52 Replanning Horizon

Replanning Horizon ถูกกำหนดจาก Affected Context

ตัวอย่าง:

```text
Changed Activity:
15 Feb

Related Activities:
12–18 Feb
```

จึงสามารถกำหนด:

```text
Affected Replanning Horizon:
12–18 Feb
```

โดยไม่จำเป็นต้อง Re-plan ทั้ง Calendar

---

# 6.53 Replanning Model Construction

MVP ใช้:

> **Full Model Rebuild + Re-solve**

ภายใน Affected Replanning Horizon

หมายถึง:

```text
Existing State
+
New State
+
Constraints
+
Preferences
+
Stability Reference
        ↓
Build New CP-SAT Model
        ↓
Solve
```

ไม่ใช้การแก้เฉพาะ Constraint บางตัวบน Solver State เดิมเป็นกลไกหลักของ MVP

ข้อดีคือ:

* Logic เข้าใจง่าย
* ลด State Complexity
* ทดสอบง่าย
* ลดโอกาสเกิด Model State ค้างจากการ Solve ก่อนหน้า

---

# 6.54 Existing Schedule as Reference

Existing Schedule ไม่ได้ถูกส่งให้ Solver ในรูป:

> “ทำตามตารางเก่าทั้งหมด”

แต่ถูกใช้เป็น:

1. Fixed constraints สำหรับสิ่งที่ต้อง Freeze
2. Stability reference สำหรับสิ่งที่เลื่อนได้
3. Context สำหรับ Impact Analysis

ดังนั้น Existing Schedule สามารถถูกเปลี่ยนได้เมื่อ Requirements ใหม่ต้องการ

---

# 6.55 Planning Model for Initial Planning

Conceptually:

```text
M_initial =
    Objects
  + Hard Constraints
  + Preferences
  + Planning Horizon
```

แล้ว:

```text
Solve(M_initial)
```

ผล:

```text
OPTIMAL
หรือ
FEASIBLE
หรือ
INFEASIBLE
หรือ
UNKNOWN
หรือ
MODEL_INVALID
```

---

# 6.56 Planning Model for Replanning

Conceptually:

```text
M_replan =
    Existing Relevant Schedule
  + New / Changed Objects
  + Hard Constraints
  + New Requirements
  + Preferences
  + Replanning Horizon
  + Stability Reference
```

แล้ว:

```text
Solve(M_replan)
```

---

# 6.57 Feasibility

Schedule ถือว่า Feasible เมื่อ:

```text
All Hard Constraints are satisfied
```

ดังนั้น:

```text
Hard Constraint Violation Count = 0
```

เป็นเงื่อนไขพื้นฐาน

Preference Satisfaction ไม่ได้เป็นตัวกำหนด Feasibility

---

# 6.58 Feasible vs Optimal

CP-SAT สามารถคืน:

### OPTIMAL

Solver พบ Feasible Solution ที่ Optimal ตาม Objective ที่กำหนด

### FEASIBLE

Solver พบ Feasible Solution แต่ยังไม่ได้พิสูจน์ว่าเป็น Optimal

ดังนั้น:

```text
FEASIBLE ≠ FAILURE
```

สามารถใช้เป็น Candidate Proposal ได้ หากผลลัพธ์ผ่านระบบตรวจสอบคุณภาพ

OR-Tools ระบุ `OPTIMAL` และ `FEASIBLE` เป็นสถานะที่ต่างกัน โดย `FEASIBLE` หมายถึงพบ Feasible Solution แต่ยังไม่ทราบว่าเป็น Optimal หรือไม่

---

# 6.59 No Feasible Plan

`NO_FEASIBLE_PLAN` สามารถประกาศได้เมื่อ Solver ยืนยันว่า Model:

```text
INFEASIBLE
```

เท่านั้น

ตัวอย่าง:

```text
Activity A
10:00–12:00

Unavailability
09:00–17:00
```

จะทำให้ Model ไม่มี Feasible Solution

---

# 6.60 Solver UNKNOWN

`UNKNOWN` ต้องไม่ถูกตีความว่า:

```text
No Feasible Plan
```

เพราะ `UNKNOWN` อาจเกิดจาก Solver หยุดก่อนที่จะสามารถระบุสถานะได้ เช่น จาก Time Limit หรือข้อจำกัดด้าน Resource

OR-Tools ระบุ `UNKNOWN` แยกจาก `INFEASIBLE` อย่างชัดเจน

ดังนั้น LONGTUA ต้องแยก:

```text
INFEASIBLE
= Proven no solution

UNKNOWN
= Solver result unresolved
```

---

# 6.61 Solver Time Limit

Planning Engine ต้องกำหนด Solver Time Limit

ค่าจริง:

```text
MAX_SOLVER_TIME
```

ยังเป็น TBD และจะได้จาก Performance Benchmark

เมื่อ Time Limit ถูกใช้:

### กรณี Solver พบ Feasible Solution แล้ว

หากผลลัพธ์เป็น:

```text
FEASIBLE
```

สามารถส่ง Candidate ได้ แต่ไม่ควรกล่าวว่าเป็น Optimal

### กรณีไม่ได้ Feasible Solution และสถานะเป็น UNKNOWN

ระบบไม่ควรสร้าง Proposal จากข้อมูลที่ยังไม่มี Feasible Solution

---

# 6.62 Model Invalid

หาก CP-SAT Model ไม่ถูกต้องในระดับ Model Construction:

```text
MODEL_INVALID
```

ต้องถือเป็นระบบ/Implementation Error ไม่ใช่ No Feasible Plan

OR-Tools มีสถานะ `MODEL_INVALID` สำหรับ Model ที่ไม่ผ่าน Validation ของ Solver โดยตรง

---

# 6.63 Solver Status Mapping

| CP-SAT Status | Meaning                         | LONGTUA Interpretation        |
| ------------- | ------------------------------- | ----------------------------- |
| OPTIMAL       | Feasible + optimal              | สำเร็จ                        |
| FEASIBLE      | Feasible but not proven optimal | สำเร็จแบบ Feasible            |
| INFEASIBLE    | Proven no solution              | NO_FEASIBLE_PLAN              |
| UNKNOWN       | Result unresolved               | Planning Unresolved / Failure |
| MODEL_INVALID | Model invalid                   | Internal Planning Error       |

---

# 6.64 Planning Error Categories

Planning Engine ต้องสามารถแยก Error อย่างน้อย:

```text
PLANNING_NOT_READY
PLANNING_HORIZON_EXCEEDED
PLANNING_OBJECT_LIMIT_EXCEEDED
NO_FEASIBLE_PLAN
SOLVER_TIMEOUT / UNKNOWN
MODEL_INVALID
PLANNING_INTERNAL_ERROR
```

รายละเอียด API Error Code จะถูกกำหนดใน API Specification

---

# 6.65 No Silent Truncation

หากจำนวน Activity เกิน:

```text
MAX_PLANNING_OBJECTS
```

ระบบต้องไม่:

```text
Drop Activities
```

เพื่อให้ Model เล็กลงโดยไม่แจ้ง User

ต้อง:

```text
Reject / Limit Exceeded
```

หรือใช้ Flow ที่แจ้ง User และให้ User ปรับ Request

---

# 6.66 No Silent Horizon Truncation

หาก Activity หรือ Constraint ต้องการช่วงเวลาที่เกิน:

```text
MAX_PLANNING_HORIZON
```

ระบบต้องไม่ตัดช่วงเวลาออกเอง

ต้อง:

```text
Horizon Exceeded
```

และไม่ควรสร้าง Schedule ที่ทำให้ User เข้าใจว่าระบบพิจารณาข้อมูลครบทั้งที่ไม่ได้พิจารณา

---

# 6.67 No Partial Planning

สำหรับ Planning Operation ที่ User คาดหวังว่า Required Activities ทั้งหมดต้องถูก Schedule:

```text
All Required Activities
       ↓
Must be scheduled
```

หาก Required Activity หนึ่งรายการไม่สามารถ Schedule ได้:

```text
No Feasible Complete Plan
```

ไม่สร้าง Partial Plan แทนโดยตัด Required Activity ออก

Optional Activities เป็นข้อยกเว้น เพราะสามารถถูกไม่เลือกตาม Policy

---

# 6.68 Candidate Generation

Candidate คือหนึ่ง Feasible Schedule Alternative

Candidate Generation ทำหลังจาก Planning Model สามารถสร้าง Feasible Solution ได้

```text
Planning Model
      ↓
Solve
      ↓
Candidate A
      ↓
Search for meaningful alternative
      ↓
Candidate B
      ↓
Search again
      ↓
Candidate C
```

Candidate ไม่ใช่ Algorithm และไม่ใช่ Planning Mode

---

# 6.69 Candidate Count

ระบบรองรับ:

```text
1 ≤ Candidate Count ≤ 3
```

แต่จำนวนจริงสามารถเป็น:

```text
1
2
หรือ
3
```

ตามผลการวางแผน

---

# 6.70 First Candidate

Candidate แรกควรเป็น Solution ที่ดีที่สุดตาม Objective Hierarchy

โดยทั่วไป:

```text
Candidate A
= Best feasible solution found
```

หาก Solver ให้ `FEASIBLE` แต่ยังไม่พิสูจน์ Optimal:

```text
Candidate A
= Best solution found within solver conditions
```

ไม่ควรเรียกว่า “Optimal” หาก Solver ไม่ได้คืน `OPTIMAL`

---

# 6.71 Alternative Candidate

Candidate B/C ต้อง:

1. Feasible
2. มีคุณภาพอยู่ในระดับที่ยอมรับได้
3. แตกต่างจาก Candidate ก่อนหน้าอย่างมีความหมาย

ไม่จำเป็นต้องแตกต่างเพียงเล็กน้อย เช่น:

```text
Study = 14:00
Study = 14:01
```

อาจไม่ถือว่าเป็น Alternative ที่มีประโยชน์ แม้จะเป็น Feasible Solution ต่างกัน

---

# 6.72 Candidate Quality Threshold

ระบบต้องกำหนดเกณฑ์ว่าคุณภาพของ Candidate B/C ต้องไม่ด้อยจาก Candidate A มากเกินไป

แต่:

```text
Candidate Quality Threshold
```

ยังไม่กำหนดตัวเลขตายตัว

ค่าจริงควรเป็น Implementation / Evaluation Parameter ที่ผ่านการ Benchmark และ Experiment

---

# 6.73 Candidate Diversity

Candidate Diversity คือระดับความแตกต่างระหว่าง Schedule Alternatives

สามารถประเมินจาก:

* Start Time ของ Activities
* Ordering
* Time Window Choice
* Placement Pattern
* การเปลี่ยนแปลงของชุดกิจกรรม

ใน MVP ไม่จำเป็นต้องใช้ Metric เดียวตายตัวตั้งแต่ต้น แต่ Metric ที่เลือกต้องสอดคล้องกับ Experiment Design

---

# 6.74 Candidate Generation Method

Candidate Alternatives สามารถสร้างโดยการ Solve ซ้ำพร้อม Constraint ที่ป้องกันไม่ให้ได้ Schedule เดิมทั้งหมด

Conceptually:

```text
Solve → A
Add diversity / exclusion condition
Solve → B
Add condition
Solve → C
```

ไม่จำเป็นต้อง Enumerate ทุก Feasible Solution

เหตุผลคือจำนวน Schedule ที่เป็นไปได้อาจมีจำนวนมาก และ Requirement ของ LONGTUA ต้องการเพียง Alternatives ที่มีประโยชน์ต่อ User ไม่ใช่ทุก Solution ที่เป็นไปได้

---

# 6.75 No Dummy Candidates

หากมีเพียงหนึ่ง Feasible / Meaningful Solution:

```text
Candidate Count = 1
```

ถือว่าเป็นผลลัพธ์ที่ถูกต้อง

ไม่สร้าง Candidate ที่:

```text
แตกต่างน้อยจนไม่มีประโยชน์
```

เพียงเพื่อให้ครบ 2 หรือ 3 ชุด

---

# 6.76 Fixed Schedule Candidate

กรณี:

> “พรุ่งนี้มีออกไปดูหนัง 13:00–16:00”

หากไม่มี Flexibility:

```text
Candidate A = 13:00–16:00
```

ไม่ควรสร้าง:

```text
Candidate B = 14:00–17:00
```

เพราะละเมิด Fixed Time

ดังนั้น Fixed Requirement สามารถทำให้ Candidate Count เหลือ 1 ได้โดยธรรมชาติ

---

# 6.77 Proposal Output

Planning Engine คืนผลลัพธ์ระดับ:

```text
Candidate(s)
```

ไม่ใช่:

```text
Confirmed Schedule
```

Application Layer จึงนำ Candidate(s) ไปสร้าง:

```text
Proposal
```

ก่อนส่งกลับให้ User

---

# 6.78 Planning Engine Boundary

Planning Engine ห้าม:

```text
Create Proposal DB Record Directly
Change Confirmed Schedule
Send Notification
Show UI
Ask User Question
```

สิ่งเหล่านี้เป็น Responsibility ของ Module อื่น

Planning Core ควรทำหน้าที่:

```text
Planning Representation
        ↓
Solve
        ↓
Planning Result
```

---

# 6.79 Planning Result Contract

Planning Result ระดับ Concept:

```text
PlanningResult
├── status
├── candidates[]
├── objective_summary
├── feasibility
├── solver_metrics
├── planning_horizon
└── diagnostics
```

ตัวอย่าง:

```text
status = OPTIMAL

candidates:
  - Candidate A

objective_summary:
  requirement_score
  preference_score
  stability_score

solver_metrics:
  solve_time
  status
```

รายละเอียด Field-level Schema จะถูกกำหนดใน Implementation Contract / API Specification ภายหลัง

---

# 6.80 Solver Metrics

Planning Engine ควรสามารถเก็บ Metrics ที่จำเป็นต่อ Evaluation เช่น:

* Solver Status
* Solve Time
* Objective Value
* Number of Objects
* Planning Horizon
* Candidate Count
* Model Size Information ตามที่เก็บได้
* Memory Usage ในระดับ Benchmark หาก Environment สามารถวัดได้

Metrics เหล่านี้ใช้สำหรับ:

```text
Performance Benchmark
+
Evaluation
+
Debugging
```

ไม่จำเป็นต้องแสดงทั้งหมดให้ User

---

# 6.81 Initial Planning Flow

```text
Planning Request
      ↓
Planning Representation
      ↓
Planning Readiness
      ↓
Select Relevant Objects
      ↓
Determine Planning Horizon
      ↓
Build CP-SAT Model
      ↓
Add Hard Constraints
      ↓
Add Preferences / Objectives
      ↓
Solve
      ↓
Feasible?
 ├── No → NO_FEASIBLE_PLAN
 └── Yes
       ↓
Candidate Generation
       ↓
Planning Result
       ↓
Proposal
```

---

# 6.82 Replanning Flow

```text
Changed Context
      ↓
Impact Detection
      ↓
Affected Objects
      ↓
Affected Horizon
      ↓
Freeze Past / Unaffected
      ↓
Build New Planning Model
      ↓
Add New Requirements
      ↓
Add Existing Constraints
      ↓
Add Preferences
      ↓
Add Stability Objective
      ↓
Solve
      ↓
Candidate Generation
      ↓
New Proposal
```

---

# 6.83 Example — Initial Planning

Input ที่ผ่าน AI/NLP:

```text
Activity A
Title = อ่านหนังสือ
Date = Tomorrow
Window = AFTERNOON
Duration = 120

Activity B
Title = กินข้าว
Date = Tomorrow
Start = 18:00
Duration = 120
Fixed = TRUE
```

Planning Model:

```text
A:
13:00 ≤ s_A
e_A ≤ 16:00
e_A = s_A + 120

B:
s_B = 18:00
e_B = 20:00
```

No-overlap:

```text
e_A ≤ s_B
OR
e_B ≤ s_A
```

Feasible Example:

```text
A = 13:00–15:00
B = 18:00–20:00
```

Candidate:

```text
A
```

หากไม่มี Alternative ที่มีความหมาย ไม่ต้องสร้าง B/C

---

# 6.84 Example — Conflict

Input:

```text
Activity A
10:00–12:00

Unavailability
09:00–17:00
```

Constraint:

```text
e_A ≤ 09:00
OR
17:00 ≤ s_A
```

ไม่สามารถทำได้ร่วมกับ Fixed Time

ผล:

```text
INFEASIBLE
```

LONGTUA:

```text
NO_FEASIBLE_PLAN
```

ไม่ย้าย Activity ไป 17:00 เพราะ Fixed Time เป็น Hard Constraint

---

# 6.85 Example — Flexible Schedule

Input:

```text
Study
Duration = 120
Window = AFTERNOON

Dinner
Fixed = 18:00
```

Possible:

```text
Candidate A
13:00–15:00 Study

Candidate B
14:00–16:00 Study
```

หากทั้งสองมีคุณภาพเพียงพอและแตกต่างกันอย่างมีความหมาย สามารถส่งเป็น:

```text
Proposal
├── Candidate A
└── Candidate B
```

---

# 6.86 Example — Replanning

Existing:

```text
Study
14:00–16:00

Dinner
18:00–20:00
```

New User Input:

> “ประชุมเลื่อนมาเป็น 15:00–16:00”

Planner:

```text
Existing Schedule
+
New Meeting
+
No-Overlap
+
Existing Constraints
+
Stability
```

อาจสร้าง:

```text
New Proposal
Study = moved
Meeting = 15:00–16:00
Dinner = 18:00–20:00
```

แต่:

```text
Current Confirmed Schedule
```

ยังไม่เปลี่ยนจนกว่า User จะ Confirm Proposal

---

# 6.87 Example — Stability

Existing:

```text
A = 09:00–10:00
B = 10:00–11:00
C = 13:00–14:00
```

New activity ต้องเพิ่มเข้ามาเวลา 09:30–10:30

Planner ต้องจัดตารางใหม่

หากมีหลาย Feasible Solutions:

```text
Solution A:
B = 10:30–11:30
C = 13:00–14:00

Solution B:
B = 11:00–12:00
C = 14:00–15:00
```

Stability Objective มีแนวโน้มสนับสนุน Solution A เพราะการเลื่อนโดยรวมต่ำกว่า

แต่หากมี Requirement ใหม่ที่บังคับให้ C ต้องเป็น 14:00:

```text
Requirement
>
Stability
```

Planner ต้องให้ Requirement ใหม่ชนะ

---

# 6.88 Example — No Feasible Plan

```text
A
Fixed 09:00–11:00

B
Fixed 10:00–12:00

Same Execution Context
```

จะมี:

```text
A overlaps B
```

และทั้งสอง Fixed

จึงไม่มีวิธีเลื่อนใด ๆ:

```text
INFEASIBLE
```

ระบบต้องคืน:

```text
NO_FEASIBLE_PLAN
```

ไม่สร้าง Alternative ที่ทำให้ Fixed Time ผิด

---

# 6.89 Example — Solver Timeout

หาก Model มีขนาดใหญ่และ Solver หยุดโดย Time Limit:

กรณี 1:

```text
Status = FEASIBLE
```

ระบบสามารถใช้ Feasible Solution ที่พบเป็น Candidate ได้ โดยระบุว่าไม่ได้รับการพิสูจน์ Optimal

กรณี 2:

```text
Status = UNKNOWN
```

และไม่มี Feasible Solution ที่ใช้ได้:

ระบบต้องไม่ประกาศ:

```text
NO_FEASIBLE_PLAN
```

แต่ต้องรายงานว่า Planning ยังไม่สามารถได้ผลลัพธ์ที่ยืนยันได้

---

# 6.90 Planning Result Quality

ก่อน Candidate ถูกนำไปสร้าง Proposal ต้องตรวจ:

```text
Hard Constraints
      ↓
All satisfied?
      ↓
Yes
      ↓
Candidate Quality
      ↓
Candidate accepted
```

Planning Engine ไม่ควรคืน Candidate ที่ละเมิด Hard Constraint แม้ Objective Score จะสูง

---

# 6.91 Post-Solve Validation

แม้ CP-SAT เป็นผู้รับผิดชอบ Constraint Enforcement แต่ระบบควรมี Independent Result Validation หลัง Solver เพื่อป้องกันข้อผิดพลาดในการ Mapping หรือ Serialization

Flow:

```text
CP-SAT Result
      ↓
Decode Solution
      ↓
Domain Validation
      ↓
Schedule Candidate
```

ตรวจอย่างน้อย:

* Activity Placement
* Start / End
* Duration
* Fixed Time
* Deadline
* Window
* Availability
* Unavailability
* No-Overlap
* Precedence
* Container Containment

หาก Decode/Mapping ทำให้เกิด Domain Error:

```text
Reject Candidate
```

ไม่ส่ง Proposal ต่อ

---

# 6.92 Planner Determinism

Planning Engine ควรพยายามทำให้การทดลองสามารถ Reproduce ได้

ข้อมูลที่ควรควบคุมในการ Evaluation เช่น:

* Solver Version
* Configuration
* Time Limit
* Randomization / Seed เมื่อใช้งาน
* Input Dataset
* Planning Model Version

จุดประสงค์คือให้ผลการทดลองเปรียบเทียบกันได้

---

# 6.93 Performance Limits

Planning Engine มี Limits ได้แก่:

```text
MAX_PLANNING_HORIZON
MAX_PLANNING_OBJECTS
MAX_SOLVER_TIME
MAX_CANDIDATES
```

แต่:

```text
MAX_PLANNING_HORIZON
MAX_PLANNING_OBJECTS
MAX_SOLVER_TIME
```

ยังไม่กำหนดตัวเลขตายตัว

ค่าจริงต้องได้จาก Performance Benchmark

---

# 6.94 Performance Benchmark

Benchmark ต้องทดลองอย่างน้อยตามตัวแปร:

```text
Planning Horizon
×
Number of Activities
×
Constraint Density
×
Candidate Count
```

และวัด:

```text
Solve Time
Memory Usage
Feasibility
Objective Quality
Candidate Generation Time
```

จุดประสงค์คือค้นหา Operational Boundary ของ LONGTUA

ไม่ใช่พิสูจน์ว่า CP-SAT เร็วที่สุดเมื่อเทียบกับทุก Algorithm

---

# 6.95 Planning Evaluation

Planning Engine สามารถประเมินได้ด้วย:

### Feasibility

```text
Feasibility Rate
```

### Constraint Integrity

```text
Hard Constraint Violation Count
```

ควรเป็น:

```text
0
```

สำหรับ Accepted Feasible Schedule

### Deadline

```text
Deadline Satisfaction
```

### Preference

```text
Preference Satisfaction
```

### Runtime

```text
Planning Runtime
```

### Stability

```text
Σ |new_start - old_start|
```

### Candidate

```text
Candidate Count
Candidate Quality
Candidate Diversity
Candidate Generation Runtime
```

---

# 6.96 Research Questions Supported

Planning Engine มีความสัมพันธ์กับ Research Questions ดังนี้:

### RQ2

> Do constraints and preferences help produce feasible and user-aligned schedules?

Planning Engine สามารถประเมิน:

* Feasibility
* Constraint Violation
* Preference Satisfaction
* Deadline Satisfaction

### RQ3

> Can the system adapt/re-plan when new information or situations arise?

Replanning สามารถประเมิน:

* Replanning Success
* Constraint Preservation
* Runtime
* Schedule Changes
* Start-Time Deviation

### RQ4

> Does user feedback during re-planning improve alignment with requirements?

Feedback จาก User จะสร้าง Requirement/Preference ใหม่ แล้วเข้าสู่ Planning Engine เพื่อเปรียบเทียบ:

```text Before Feedback
vs
After Feedback
```

---

# 6.97 Planning Ablation

เพื่อศึกษาผลของส่วนสำคัญของ Planner สามารถออกแบบ Ablation ได้ เช่น:

```text Full Model
vs
Without Preferences
```

หรือสำหรับ Replanning:

```text Replanning + Stability
vs
Replanning without Stability
```

โดย:

* Hard Constraints ต้องคงเดิม
* Dataset และ Input ต้องเหมือนกัน
* เปรียบเทียบ Metric เดียวกัน
* ไม่ควรเปลี่ยนปัจจัยอื่นพร้อมกันโดยไม่ควบคุม

---

# 6.98 Planning Error Analysis

หาก Planning ไม่ได้ผลลัพธ์ตามคาด ควรจำแนกสาเหตุ:

```text P1 Input Not Ready
P2 Incorrect Normalization
P3 Incorrect Constraint Construction
P4 Incorrect Objective Construction
P5 No Feasible Solution
P6 Solver Timeout / UNKNOWN
P7 Candidate Generation Failure
P8 Result Decoding Error
P9 Post-Solve Validation Failure
```

การแยกประเภทช่วยป้องกันการสรุปว่า:

> “CP-SAT ทำงานไม่ดี”

เมื่อจริง ๆ ปัญหาอาจอยู่ที่ AI Output หรือ Model Construction

---

# 6.99 Planner Responsibility Matrix

| Task                      | AI/NLP | Validation | Planner | Application |             User |
| ------------------------- | -----: | ---------: | ------: | ----------: | ---------------: |
| Extract Activity          |      ✅ |            |         |             |                  |
| Normalize Time            |        |          ✅ |         |             |                  |
| Build Planning Model      |        |            |       ✅ |             |                  |
| Check Hard Constraints    |        |            |       ✅ |             |                  |
| Optimize Preferences      |        |            |       ✅ |             |                  |
| Generate Candidate        |        |            |       ✅ |             |                  |
| Create Proposal           |        |            |         |           ✅ |                  |
| Review Proposal           |        |            |         |             |                ✅ |
| Confirm                   |        |            |         |             |                ✅ |
| Replan                    |        |            |         | ✅ / Planner | ✅ Trigger/Review |
| Change Confirmed Schedule |        |            |         |             |                ✅ |

---

# 6.100 Planner Invariants

ต่อไปนี้เป็น Invariants ของ Planning Engine:

```text
PLAN-INV-01
Planner receives structured Planning Representation, not raw Natural Language.

PLAN-INV-02
Every accepted Candidate must satisfy all Hard Constraints.

PLAN-INV-03
Hard Constraints must never be silently relaxed.

PLAN-INV-04
Required Activities must not be removed to force feasibility.

PLAN-INV-05
Planner does not autonomously modify Confirmed Schedule.

PLAN-INV-06
Planner does not generate Notifications.

PLAN-INV-07
Planner does not decide User Confirmation.

PLAN-INV-08
Calendar Data Range is independent from Planning Horizon.

PLAN-INV-09
Replanning uses a context-dependent Affected Horizon.

PLAN-INV-10
Stability cannot override New Explicit Requirements.

PLAN-INV-11
Candidate Count may be 1, 2, or 3.

PLAN-INV-12
Candidate Alternatives must be meaningful, not dummy solutions.

PLAN-INV-13
INFEASIBLE means proven infeasibility; UNKNOWN does not.

PLAN-INV-14
Solver FEASIBLE results must not be presented as OPTIMAL.

PLAN-INV-15
Planning failures must not be silently converted into partial schedules.
```

---

# 6.101 Planning Engine Architecture

สรุปภายใน Module:

```text
                    Planning Representation
                             |
                             v
                  +----------------------+
                  | Planning Readiness   |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | Relevant Object      |
                  | Selection            |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | Horizon Construction |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | CP-SAT Model Builder  |
                  +----------+-----------+
                             |
             +---------------+----------------+
             |               |                |
             v               v                v
        Variables        Hard Rules       Objectives
             |               |                |
             +---------------+----------------+
                             |
                             v
                  +----------------------+
                  | OR-Tools CP-SAT      |
                  +----------+-----------+
                             |
                      Solver Status
                             |
            +----------------+------------------+
            |                |                 |
         OPTIMAL          FEASIBLE         Other
            |                |                 |
            +----------------+-----------------+
                             |
                             v
                  +----------------------+
                  | Candidate Generation |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | Post-Solve           |
                  | Validation           |
                  +----------+-----------+
                             |
                             v
                    Planning Result
```

---

# 6.102 Complete Planning Lifecycle

```text
                    USER INTENT
                         |
                         v
                   AI / NLP
                         |
                         v
            Structured Planning Data
                         |
                         v
              Validation / Normalize
                         |
                         v
               Planning Representation
                         |
                         v
                Planning Readiness
                         |
                 +-------+-------+
                 |               |
               Ready          Not Ready
                 |               |
                 v               v
          Planning Model     Clarification /
                 |             Store / Fail
                 v
            CP-SAT Solve
                 |
          +------+------+------+
          |      |      |      |
       Optimal Feasible Infeasible Unknown
          |      |      |      |
          +------+      |      |
                 |      |      |
                 v      v      v
             Candidate  No   Unresolved
             Generation Plan   Result
                 |
                 v
          Post-Solve Validation
                 |
                 v
              Proposal
                 |
                 v
            USER REVIEW
                 |
        +--------+--------+
        |        |        |
      Reject   Feedback  Confirm
                  |        |
                  v        v
              Replanning  New Schedule
                  |
                  v
              New Proposal
```

---

# 6.103 Design Summary

Planning Engine ของ LONGTUA ใช้ CP-SAT เป็น Computational Core เพื่อจัดกิจกรรมภายใต้ Hard Constraints และ Preferences โดยแยก Feasibility ออกจาก Quality และแยก Initial Planning ออกจาก Replanning

แกนของ Model คือ:

```text
Activity
  ↓
Start / End / Duration
  ↓
Constraints
  ↓
Objectives
  ↓
Feasible Schedule
```

Initial Planning เน้นการสร้าง Schedule ใหม่จาก Requirements และ Preferences

Replanning เพิ่ม Existing Schedule และ Stability Reference เข้ามา

Candidate Generation ทำหลัง Solve และสร้างเฉพาะ Alternatives ที่มี Feasibility, Quality และ Diversity เพียงพอ

ผลลัพธ์ทั้งหมดถูกส่งไปยัง Proposal ก่อน และไม่สามารถเปลี่ยน Confirmed Schedule ได้โดยตรง

---

# 6.104 Core Planning Principle

หลักการของ Planning Engine สามารถสรุปได้ว่า:

> **“จัดกิจกรรมทั้งหมดที่จำเป็นภายใต้ข้อจำกัดที่ต้องเคารพ เลือกแผนที่ตอบสนองความต้องการและ Preference ของผู้ใช้ได้ดีที่สุด และเมื่อเกิดการเปลี่ยนแปลง ให้ปรับเฉพาะส่วนที่ได้รับผลกระทบโดยพยายามรักษาส่วนที่ไม่จำเป็นต้องเปลี่ยน”**

ดังนั้น:

```text
AI / NLP
= Understand

Planning Engine
= Compute

Proposal
= Present

User
= Decide
```

และ Planning Engine จะไม่มีอำนาจเหนือ Confirmed Schedule ของ User
