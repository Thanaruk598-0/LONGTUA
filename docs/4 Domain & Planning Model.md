# 4. Domain & Planning Model

## 4.1 Purpose

เอกสารฉบับนี้กำหนด Domain Model และแนวคิดเชิง Planning ของ LONGTUA — Personal Adaptive Planner เพื่อกำหนดความหมายของข้อมูลและความสัมพันธ์ที่เกี่ยวข้องกับการวางแผนอย่างเป็นทางการ

เนื้อหาในส่วนนี้เป็นพื้นฐานร่วมสำหรับ:

* AI / NLP
* Validation / Normalization
* Planning Representation
* Planning Engine
* Replanning
* Database Design
* API Design
* UI / UX
* Evaluation

เป้าหมายสำคัญคือทำให้คำศัพท์และ Semantics ของระบบมีความหมายเดียวกันตลอดทั้งระบบ เช่น `Activity`, `Container`, `Availability`, `Unavailability`, `Planning Rule`, `Temporal Relation`, `Candidate`, `Proposal` และ `Schedule Item`

---

# 4.2 Domain Overview

LONGTUA มองการวางแผนเป็นปัญหาของการนำกิจกรรมและเงื่อนไขต่าง ๆ มาพิจารณาร่วมกันเพื่อสร้าง Schedule ที่เป็นไปได้และสอดคล้องกับความต้องการของผู้ใช้

องค์ประกอบหลักของ Domain ได้แก่:

```text
Planning Object
├── Activity
└── Container

Time-related Context
├── Availability
├── Unavailability
└── Time Window

Planning Conditions
├── Hard Constraint
└── Preference

Relations
└── Temporal Relation

Planning Process
├── Planning Request
├── Candidate
└── Proposal

Confirmed State
├── Schedule Version
└── Schedule Item
```

แนวคิดสำคัญคือ:

> **Activity เป็นสิ่งที่ผู้ใช้ต้องทำหรือเข้าร่วม ส่วน Schedule Item เป็นผลจากการนำ Activity ไปวางลงใน Schedule**

ดังนั้นทั้งสองสิ่งไม่ใช่ Entity เดียวกันในเชิง Domain

---

# 4.3 Planning Object

## 4.3.1 Definition

**Planning Object** คือวัตถุที่ระบบนำมาพิจารณาในกระบวนการวางแผน

ใน MVP รองรับ 2 ประเภท:

```text
PLANNING_OBJECT
├── ACTIVITY
└── CONTAINER
```

Planning Object เป็น Abstraction ระดับ Domain เพื่อให้ระบบสามารถจัดการทั้งกิจกรรมที่ต้องทำจริงและกรอบกิจกรรมขนาดใหญ่ในรูปแบบเดียวกัน

---

# 4.4 Activity

## 4.4.1 Definition

**Activity** คือกิจกรรม งาน หรือเหตุการณ์ที่ผู้ใช้ต้องการจัดการ และโดยทั่วไปเป็นสิ่งที่ใช้เวลาหรือเกี่ยวข้องกับการกำหนดเวลา

ตัวอย่าง:

* ทำรายงาน
* อ่านหนังสือ
* ไปวิ่ง
* ไปพบแพทย์
* ประชุม
* เดินทาง
* ดูหนัง

Activity เป็นหน่วยหลักที่ Planning Engine พยายามนำไปวางบน Schedule

---

## 4.4.2 Activity Types

MVP รองรับ Activity Type ดังนี้:

| Activity Type | ความหมาย                           |
| ------------- | ---------------------------------- |
| TASK          | งานที่ผู้ใช้ต้องดำเนินการ          |
| EVENT         | เหตุการณ์หรือกิจกรรมตามบริบททั่วไป |
| APPOINTMENT   | นัดหมายที่มีเวลา/บริบทเฉพาะ        |
| MEETING       | การประชุมหรือการพบปะ               |
| TRAVEL        | การเดินทาง                         |
| OTHER         | กิจกรรมอื่นที่ไม่เข้าประเภทข้างต้น |

Activity Type เป็น **Semantic Classification** และไม่ควรถูกใช้เป็นตัวกำหนด Scheduling Behavior โดยอัตโนมัติทุกกรณี

ตัวอย่างเช่น `MEETING` ไม่ได้หมายความว่าเวลาต้อง Fixed เสมอไป หาก User ไม่ได้กำหนด

---

# 4.5 Container

## 4.5.1 Definition

**Container** คือ Planning Object ที่ทำหน้าที่เป็นกรอบหรือช่วงกิจกรรมขนาดใหญ่ และสามารถมี Child Activities อยู่ภายในได้

ตัวอย่าง:

> “พรุ่งนี้มีสัมมนา 08:00–17:00 และมี Workshop 14:00–16:00”

อาจถูกแทนด้วย:

```text
Container
└── Seminar
    08:00–17:00

Child Activity
└── Workshop
    14:00–16:00
```

Container ใน MVP ถือเป็น **Exclusive Commitment**

กล่าวคือ Container เองใช้เป็นข้อจำกัดด้านเวลาต่อกิจกรรมภายนอก แม้ Child Activity ภายในจะสามารถ overlap กับ Container ได้ตาม Membership Semantics

---

# 4.6 Container Membership

Container Membership เป็นความสัมพันธ์เชิงโครงสร้างระหว่าง Container และ Child Activity

```text
Container
    │
    ├── Child Activity A
    ├── Child Activity B
    └── Child Activity C
```

Membership บอกว่า Activity ใดอยู่ภายใน Container

ดังนั้น:

```text
CONTAINS
```

และ

```text
WITHIN
```

ถือเป็น **Structural Membership Semantics**

ไม่จำเป็นต้องเก็บเป็น Generic Temporal Relation หากความสัมพันธ์นั้นถูกแทนด้วย Container Membership โดยตรง

---

# 4.7 Activity vs Container

ความแตกต่างหลัก:

| Aspect                       | Activity | Container             |
| ---------------------------- | -------- | --------------------- |
| เป็นสิ่งที่ User ทำ/เข้าร่วม | ✅        | อาจเป็นกรอบของกิจกรรม |
| ใช้เป็นหน่วย Scheduling      | ✅        | ✅                     |
| มี Child Activities          | ❌        | ✅                     |
| เป็น Exclusive Commitment    | ตามบริบท | ✅ ใน MVP              |
| ใช้ Membership               | ❌        | ✅                     |

ข้อสำคัญ:

> `Activity Type` และ `Planning Object Type` เป็นคนละแนวคิด

เช่น:

```text
“ทำงานจันทร์–ศุกร์ 08:00–17:00”
```

อาจหมายถึง `AVAILABILITY`

ขณะที่:

```text
“ทำรายงาน 08:00–17:00”
```

หมายถึง `ACTIVITY`

ดังนั้นระบบไม่ควรใช้ Keyword เพียงอย่างเดียวในการจำแนกความหมาย

---

# 4.8 Availability

## 4.8.1 Definition

**Availability** คือช่วงเวลาที่ Planner สามารถนำ Activity ไปจัดวางได้

Availability ไม่ใช่ Activity และไม่ใช้ Execution Capacity ของผู้ใช้

ตัวอย่าง:

> จันทร์–ศุกร์ 08:00–17:00 ว่างสำหรับทำงาน

สามารถแทนเป็น:

```text
AVAILABLE
MON–FRI
08:00–17:00
```

---

## 4.8.2 Availability Types

Availability รองรับ:

### One-Time

เช่น:

> พรุ่งนี้ 10:00–12:00 ว่าง

### Recurring

เช่น:

> จันทร์–ศุกร์ 08:00–17:00

---

# 4.9 Unavailability

## 4.9.1 Definition

**Unavailability** คือช่วงเวลาที่ User ไม่สามารถรับ Activity เพิ่มได้

ตัวอย่าง:

> ทุกวันจันทร์ 18:00–20:00 ไม่ว่าง

หรือ:

> พรุ่งนี้ 13:00–15:00 ไม่ว่าง

Unavailability เป็น Hard Constraint ต่อการ Scheduling

ดังนั้น:

```text
Activity overlaps Unavailability
        ↓
Hard Conflict
```

---

# 4.10 Availability vs Activity

สองสิ่งนี้ต้องไม่ถูกตีความเหมือนกัน

```text
Availability
= “สามารถจัดกิจกรรมได้ที่นี่”

Activity
= “ต้องการจัดกิจกรรมตรงนี้”
```

ดังนั้น:

```text
Availability: 08:00–17:00
Activity:     10:00–12:00
```

ไม่ถือว่า Conflict

แต่:

```text
Unavailability: 08:00–17:00
Activity:       10:00–12:00
```

ถือว่า Conflict

---

# 4.11 Time Representation

ระบบต้องสามารถแยกประเภทของข้อมูลด้านเวลาออกจากกัน เพื่อไม่ให้ข้อมูลที่มีความหมายต่างกันถูกตีความเหมือนกัน

Time Information ที่รองรับใน MVP:

```text
Exact Time
Time Range
Date
Duration
Deadline
Semantic Time Window
Relative Time
Approximate Time
Approximate Duration
Unknown Time
```

---

# 4.12 Exact Time

Exact Time คือเวลาที่ User ระบุอย่างชัดเจน

ตัวอย่าง:

> “บ่ายสองโมง”

ตีความเป็น:

```text
14:00
```

เมื่อ Exact Time ถูกระบุชัดเจน ระบบต้องรักษาค่านั้นไว้

---

# 4.13 Time Range

Time Range คือช่วงเวลาที่มี Start และ End

ตัวอย่าง:

> 14:00–16:00

แทนด้วย:

```text
[start = 14:00,
 end   = 16:00]
```

Time Range สามารถใช้เป็น:

* Fixed Schedule
* Availability
* Unavailability
* Container Window
* Candidate Placement Boundary

ตามบริบท

---

# 4.14 Duration

Duration คือระยะเวลาที่ใช้ดำเนิน Activity

ตัวอย่าง:

> อ่านหนังสือ 2 ชั่วโมง

หมายถึง:

```text
duration = 120 minutes
```

สำหรับ Activity ที่ยังไม่มี Duration ระบบต้องไม่เติมค่าขึ้นมาเองโดยไม่มี Policy รองรับ

---

# 4.15 Approximate Time / Duration

ระบบรองรับค่าประมาณ เช่น:

> “ประมาณบ่ายสอง”

หรือ:

> “น่าจะใช้เวลาประมาณหนึ่งชั่วโมง”

ข้อมูลต้องเก็บทั้ง:

```text
Value
+
Qualifier = APPROXIMATE
```

MVP สามารถใช้ค่าดังกล่าวเป็น Nominal Planning Value ในการคำนวณ แต่ต้องรักษาข้อมูลว่าเป็น Approximate เพื่อไม่ให้ตีความว่าเป็นค่าที่ User ระบุอย่างแน่นอน

---

# 4.16 Deadline

Deadline คือเวลาสุดท้ายที่ Activity ต้องเสร็จ

ตัวอย่าง:

> “ต้องส่งรายงานภายในวันศุกร์”

สามารถแทนเป็น Constraint ว่า:

```text
End Time ≤ Deadline
```

Deadline ไม่ใช่ Start Time

ดังนั้น:

```text
Deadline = Friday 23:59
```

ไม่ได้หมายความว่า Activity ต้องเริ่มเวลา 23:59

---

# 4.17 Semantic Time Window

Semantic Time Window คือช่วงเวลาที่แทนด้วยคำเชิงความหมาย เช่น:

* เช้า
* สาย
* เที่ยง
* บ่าย
* เย็น
* กลางคืน

ระบบใช้ Canonical Semantic Windows ดังนี้:

| Window       | Default     |
| ------------ | ----------- |
| LATE_NIGHT   | 00:00–06:00 |
| MORNING      | 06:00–09:00 |
| LATE_MORNING | 09:00–12:00 |
| NOON         | 12:00–13:00 |
| AFTERNOON    | 13:00–16:00 |
| EVENING      | 16:00–19:00 |
| NIGHT        | 19:00–24:00 |

ช่วงทั้งหมดครอบคลุม 24 ชั่วโมงโดยไม่มีช่องว่าง และใช้ Half-Open Interval:

```text
[start, end)
```

---

# 4.18 Time Window Override

User สามารถ Override Semantic Window บางประเภทได้

ตัวอย่าง:

```text
MORNING
06:00–12:00

AFTERNOON
12:00–17:00

EVENING
17:00–19:00

NIGHT
19:00–06:00
```

หาก User กำหนด Override:

```text
User Override
     ↓
ใช้ค่าของ User
```

หากไม่ได้กำหนด:

```text
System Default
     ↓
ใช้ค่ามาตรฐาน
```

การ Override เป็น User-level Global Setting

---

# 4.19 Relative Time

Relative Time คือเวลาที่ต้องตีความโดยอ้างอิง Reference Time

ตัวอย่าง:

* วันนี้
* พรุ่งนี้
* อาทิตย์หน้า
* อีกสองวัน
* วันจันทร์หน้า

ระบบต้องมี:

```text
referenceTime
```

ซึ่งประกอบด้วยอย่างน้อย:

* Date
* Time
* Timezone Context

การมี `currentDate` แยกอีกตัวใน Planning Model ไม่จำเป็น หากสามารถ derive จาก `referenceTime` ได้

---

# 4.20 Unknown Information

Unknown หมายถึงระบบหรือ User ยังไม่มีข้อมูลนั้น

ตัวอย่าง:

> “พรุ่งนี้ไปซื้อของขวัญให้แฟน”

ระบบรู้:

```text
Date = Tomorrow
Activity = Buy Gift
```

แต่ยังไม่รู้:

```text
Start Time
Duration
```

การมี Unknown ไม่ได้หมายความว่าระบบต้องถาม User ทันที

ระบบสามารถเก็บ Activity เป็น Date-Only Activity ได้เมื่อข้อมูลที่ขาดยังไม่จำเป็นต่อ Operation ปัจจุบัน

---

# 4.21 Ambiguous Information

Ambiguous หมายถึงข้อมูลมีความเป็นไปได้มากกว่าหนึ่งความหมาย

ตัวอย่าง:

> “พรุ่งนี้ 6 โมงไปวิ่ง”

อาจหมายถึง:

```text
06:00
หรือ
18:00
```

หาก Context ไม่เพียงพอ และความแตกต่างมีผลต่อ Scheduling:

```text
Ambiguous
    ↓
Clarification
```

ระบบไม่ควรเลือกค่าหนึ่งค่าด้วยการเดาโดยไม่มีหลักฐาน

---

# 4.22 Unsupported Information

Unsupported หมายถึงความต้องการหรือข้อมูลที่อยู่นอก Capability ที่ MVP รองรับ

ตัวอย่าง:

> User ขอให้ระบบคำนวณ Route โดยพิจารณารถติดแบบ Real-time

หากระบบไม่มีความสามารถดังกล่าว:

```text
Unsupported
≠
Missing
```

ระบบต้องแจ้งว่าไม่รองรับ แทนการประมาณหรือเปลี่ยนความหมายโดยอัตโนมัติ

---

# 4.23 Unknown vs Ambiguous vs Unsupported

| State       | ความหมาย       | การตอบสนอง                    |
| ----------- | -------------- | ----------------------------- |
| Unknown     | ยังไม่มีข้อมูล | อาจรอ/ถามเมื่อจำเป็น          |
| Ambiguous   | มีหลายความหมาย | Clarify เมื่อมีผลต่อ Planning |
| Unsupported | ระบบไม่รองรับ  | แจ้งข้อจำกัด                  |

หลักการนี้สำคัญต่อทั้ง AI/NLP และ UX

---

# 4.24 Planning Rule

Planning Rule คือเงื่อนไขที่ใช้กำหนดว่า Schedule ใดถือว่ายอมรับได้หรือมีคุณภาพตามความต้องการ

แบ่งเป็น 2 กลุ่ม:

```text
Planning Rule
├── HARD
└── PREFERENCE
```

---

# 4.25 Hard Constraint

Hard Constraint คือเงื่อนไขที่ต้องเป็นจริง

หาก violated:

```text
Schedule = INVALID
```

ตัวอย่าง:

* Fixed Time
* Duration
* Deadline
* Unavailability
* Precedence
* Container Containment
* No-Overlap ตาม Execution Context
* Planning Horizon

Hard Constraint ไม่มีสิทธิ์ถูกผ่อนโดยอัตโนมัติเพื่อให้ได้ Schedule

---

# 4.26 Preference

Preference คือความต้องการเชิงคุณภาพที่ User ต้องการ แต่ไม่ได้ทำให้ Schedule ผิดทันทีหากไม่สามารถทำตามได้

ตัวอย่าง:

> “อยากอ่านหนังสือตอนเย็น”

หรือ:

> “อยากให้กิจกรรมสำคัญทำก่อน”

Preference ถูกใช้ใน Objective/Scoring

แต่:

```text
Preference
    ↓
ห้าม override
Hard Constraint
```

---

# 4.27 Requirement vs Preference

ต้องแยก Explicit Requirement ออกจาก Preference

ตัวอย่าง:

> “พรุ่งนี้ต้องไปหาหมอตอน 10 โมง”

มี Fixed Time ที่มีน้ำหนักสูง

ขณะที่:

> “ถ้าเป็นไปได้อยากออกกำลังกายตอนเย็น”

เป็น Preference

ลำดับการพิจารณา:

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

---

# 4.28 Temporal Relation

Temporal Relation คือความสัมพันธ์ระหว่าง Planning Objects ในเชิงเวลา

MVP รองรับ:

```text
BEFORE
AFTER
OVERLAP
```

ตัวอย่าง:

```text
Activity A BEFORE Activity B
```

หมายถึง:

```text
End(A) ≤ Start(B)
```

ในกรณีที่ใช้เป็น Precedence Constraint

---

# 4.29 BEFORE

`A BEFORE B`

หมายความว่า A ต้องเสร็จก่อนที่ B จะเริ่ม

```text
A: 09:00–10:00
B: 10:00–11:00
```

เป็นไปได้

Adjacent Intervals ที่แตะกันพอดีไม่ถือว่า Conflict

---

# 4.30 AFTER

`A AFTER B`

เป็นความสัมพันธ์กลับด้านของ BEFORE:

```text
Start(A) ≥ End(B)
```

สามารถ Normalize ภายในระบบให้ใช้ Representation ที่สม่ำเสมอได้

---

# 4.31 OVERLAP

`OVERLAP` เป็น Semantic Temporal Relation ที่บอกว่าช่วงเวลาของ Object สองรายการมีการทับซ้อนกัน

แต่:

> **Temporal `OVERLAP` ≠ Permission to Schedule Concurrently**

ตัวอย่าง:

```text
A overlaps B
```

อาจถูกเก็บเพื่ออธิบายข้อมูลที่ User ระบุ แต่ถ้า A และ B ใช้ Execution Context เดียวกัน Planner ยังต้องถือว่าเป็น Conflict ภายใต้ No-Overlap Rule

Concurrent / Multitasking ไม่อยู่ใน MVP

---

# 4.32 Container Temporal Semantics

Container กับ Child สามารถ overlap ได้ตามธรรมชาติของ Membership

ตัวอย่าง:

```text
Container:
08:00–17:00

Child:
14:00–16:00
```

ไม่ถือว่า Conflict เพราะ Child เป็นสมาชิกของ Container

แต่:

```text
Unrelated Activity:
15:00–16:00
```

ถือว่า Conflict หาก Container เป็น Exclusive Commitment

ดังนั้น Conflict ต้องพิจารณาทั้ง:

* Temporal Relation
* Object Type
* Membership
* Execution Context

---

# 4.33 Conflict Model

Conflict ไม่ได้หมายถึงเพียง “เวลาเหลื่อมกัน”

ระบบต้องประเมินตามบริบท

## Activity ↔ Activity

ถ้าใช้ Execution Context เดียวกันและช่วงเวลาซ้อนกัน:

```text
Conflict
```

## Activity ↔ Container

ถ้า Activity เป็น Child:

```text
Allowed
```

ถ้าไม่เกี่ยวข้องกัน และ Container เป็น Exclusive Commitment:

```text
Conflict
```

## Activity ↔ Availability

```text
Allowed
```

เพราะ Availability เปิดช่วงเวลาที่ Planner สามารถใช้ได้

## Activity ↔ Unavailability

```text
Conflict
```

เพราะ Unavailability เป็น Hard Constraint

---

# 4.34 Interval Semantics

ระบบใช้ Half-Open Interval:

```text
[start, end)
```

ดังนั้น:

```text
09:00–10:00
10:00–11:00
```

ไม่ถือว่า Overlap

หลักการนี้ช่วยให้การคำนวณขอบเขตเวลาและ Constraint มีความสม่ำเสมอ

---

# 4.35 Planning Horizon

Planning Horizon คือขอบเขตเวลาที่ Planning Engine ใช้สำหรับการคำนวณครั้งหนึ่ง

เช่น:

```text
Planning Horizon
01 Jan – 14 Jan
```

หมายถึง CP-SAT พิจารณา Schedule ภายในช่วงดังกล่าว

ไม่ได้หมายความว่า:

* Calendar เก็บข้อมูลได้เพียง 14 วัน
* User แก้ Activity ที่อยู่หลังวันที่ 14 ไม่ได้
* Database ลบข้อมูลที่อยู่นอก Horizon

ดังนั้น:

```text
Calendar Data Range
≠
Planning Horizon
```

---

# 4.36 Replanning Horizon

Replanning Horizon คือช่วงเวลาที่ได้รับผลกระทบจากการเปลี่ยนแปลง และจะถูกนำกลับเข้าสู่การวางแผนใหม่

Replanning Horizon ไม่จำเป็นต้องเท่ากับ Normal Planning Horizon

ตัวอย่าง:

```text
Today = 07 Jan

Affected Activity = 15 Feb

Affected Context = 12–18 Feb
```

ระบบสามารถ Re-plan เฉพาะช่วงที่เกี่ยวข้องได้ แม้ Normal Planning Operation จะใช้ช่วงที่สั้นกว่า

---

# 4.37 Planning State

ในระดับ Concept ระบบสามารถอธิบาย Planning State ได้เป็น:

```text
S = (O, C, P, R, U, S_current, M)
```

โดย:

| Symbol      | Meaning                                |
| ----------- | -------------------------------------- |
| `O`         | Planning Objects                       |
| `C`         | Hard Constraints                       |
| `P`         | Preferences                            |
| `R`         | Relations                              |
| `U`         | Availability / Unavailability Context  |
| `S_current` | Existing Confirmed Schedule            |
| `M`         | Additional Planning Metadata / Context |

สำหรับ Initial Planning อาจไม่มี `S_current` ที่มีความหมายต่อ Stability

สำหรับ Replanning ต้องนำ Existing Schedule มาเป็นส่วนหนึ่งของ Planning Context

---

# 4.38 Decision Variables

สำหรับ Activity ที่ต้องถูกจัดเวลา Planning Engine สามารถกำหนด:

```text
s_i = start time
e_i = end time
d_i = duration
```

โดย:

```text
e_i = s_i + d_i
```

เวลาภายใน Planning Model ใช้เป็น Integer Minutes ภายใน Planning Horizon

ระบบไม่กำหนด Fixed 15-minute Slot เป็นข้อจำกัดพื้นฐานของ Model

---

# 4.39 Fixed-Time Activity

หาก Activity มี Fixed Start/End Time:

```text
s_i = fixedStart
e_i = fixedEnd
```

Planner ไม่ควรย้ายเวลาเพื่อสร้าง Candidate ใหม่

หาก Fixed Time ไม่สามารถอยู่ร่วมกับ Constraint อื่นได้:

```text
NO_FEASIBLE_PLAN
```

แทนการผ่อน Fixed Time โดยอัตโนมัติ

---

# 4.40 Activity With Duration but Flexible Start

หาก User ระบุ:

> “พรุ่งนี้อยากอ่านหนังสือ 2 ชั่วโมง ช่วงบ่าย”

ระบบสามารถสร้าง:

```text
duration = 120 min
window = AFTERNOON
```

และให้ Planning Engine หา `s_i` ภายใน Window ที่เหมาะสม

---

# 4.41 Date-Only Activity

Activity สามารถมี:

```text
Date = Known
Start Time = Unknown
Duration = Unknown
```

สถานะนี้ยังถือว่าเป็นข้อมูลที่ถูกต้องสำหรับบาง Operation

Date-only Activity ไม่ควรถูกแสดงเหมือนมี Start Time ตาม Notification Default

ตัวอย่าง:

```text
Calendar:
All Day / Unscheduled
```

ไม่ใช่:

```text
06:00 Activity
```

เพียงเพราะ Notification ถูกตั้งไว้ 06:00

---

# 4.42 Notification Time vs Activity Time

Notification Time เป็นข้อมูลด้านการแจ้งเตือน ไม่ใช่ Planning Start Time

ตัวอย่าง:

```text
Activity Start = 09:00
Notification = 08:00
```

ไม่ได้หมายความว่า Activity เริ่ม 08:00

ดังนั้น Domain Model ต้องแยก:

```text
Activity Start Time
≠
Notification Time
```

---

# 4.43 Planning Feasibility

Schedule ถือว่า Feasible เมื่อ:

```text
All Hard Constraints satisfied
```

ดังนั้น:

```text
Hard Constraint Violations = 0
```

จึงเป็นเงื่อนไขพื้นฐานของ Feasible Schedule

Preferences ใช้ประเมินคุณภาพของ Feasible Solutions

---

# 4.44 Feasible vs Preferred

ระบบต้องแยกระหว่าง:

```text
Feasible
```

และ:

```text
Preferred
```

ตัวอย่าง:

Schedule A:

```text
ทุก Hard Constraint ผ่าน
Preference Satisfaction = สูง
```

Schedule B:

```text
ทุก Hard Constraint ผ่าน
Preference Satisfaction = ปานกลาง
```

ทั้งสองอาจ Feasible ได้ แต่ Schedule A มี Objective Quality สูงกว่า

ขณะที่:

Schedule C:

```text
ละเมิด Hard Constraint
```

ต้องถือว่า Invalid แม้ Preference จะถูกตอบสนองครบถ้วนก็ตาม

---

# 4.45 Initial Planning

Initial Planning คือการสร้าง Schedule จากข้อมูลใหม่หรือบริบทปัจจุบัน โดยไม่มี Existing Schedule ที่ต้องรักษาเป็นหลัก

แนวคิด:

```text
Planning Input
+
Constraints
+
Preferences
      ↓
Planning Model
      ↓
CP-SAT
      ↓
Feasible Schedule(s)
```

Stability ไม่จำเป็นต้องเป็น Objective หลักในกรณีนี้

---

# 4.46 Replanning

Replanning คือการสร้าง Schedule ใหม่เมื่อมีข้อมูลหรือสถานการณ์เปลี่ยนจาก Schedule เดิม

Input ประกอบด้วย:

```text
Existing Schedule
+
New Information
+
Existing Constraints
+
New Requirements
+
Preferences
```

ระบบต้องพยายามรักษาส่วนของ Schedule เดิมที่ไม่จำเป็นต้องเปลี่ยน

---

# 4.47 Stability

Stability เป็นแนวคิดในการลดการเปลี่ยนแปลงที่ไม่จำเป็นจาก Existing Schedule

Operational Measure:

```text
D = Σ |s_new(i) - s_old(i)|
```

โดย:

* `s_new(i)` = Start Time ใหม่ของ Activity
* `s_old(i)` = Start Time เดิม

ค่า `D` ต่ำหมายถึงมีการเปลี่ยนแปลงของ Start Time รวมต่ำกว่าในนิยามนี้

อย่างไรก็ตาม Stability เป็น Objective ภายหลัง Explicit User Requirements และ Preferences

---

# 4.48 Affected Context

เมื่อมีการเปลี่ยนแปลง ระบบไม่จำเป็นต้อง Re-plan ทุก Activity ใน Calendar เสมอไป

ระบบพิจารณา:

```text
Changed Object
     ↓
Related Activities
     ↓
Constraints / Relations
     ↓
Affected Schedule
     ↓
Affected Horizon
```

Past และ Unaffected Items ควรถูก Freeze เมื่อไม่จำเป็นต้องเปลี่ยน

---

# 4.49 Optional Activity

Activity บางรายการอาจไม่เป็น Requirement แบบบังคับ และสามารถถูกละไว้เมื่อไม่สามารถจัดได้โดยไม่ทำให้ Hard Constraints เสีย

อย่างไรก็ตาม การตัด Optional Activity ต้องเกิดจาก Planning Policy ที่ชัดเจน ไม่ใช่การตัดข้อมูลเงียบ ๆ

Activity ที่เป็น Explicit User Requirement ไม่ควรถูกตัดเพื่อให้ระบบได้ Feasible Plan

---

# 4.50 Planning Priority Model

สำหรับการตัดสินใจเชิง Planning ระบบใช้ลำดับ:

```text
Level 1
Hard Constraints
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

ความหมาย:

### Level 1 — Feasibility

Schedule ต้องไม่ละเมิด Hard Constraints

### Level 2 — Explicit Requirements

สิ่งที่ User ระบุอย่างชัดเจนควรถูกตอบสนอง

### Level 3 — Preferences

Preference ใช้เลือกระหว่าง Feasible Solutions

### Level 4 — Stability

เมื่อ Replanning ให้ลดการเปลี่ยนแปลงที่ไม่จำเป็น

### Level 5 — Optional Activities

กิจกรรมที่ยืดหยุ่นที่สุดสามารถถูกลดความสำคัญเมื่อจำเป็น

---

# 4.51 Candidate

**Candidate** คือหนึ่งทางเลือกของ Schedule ที่ผ่าน Feasibility Requirements

ตัวอย่าง:

```text
Candidate A
09:00 – 10:00 Study

Candidate B
14:00 – 15:00 Study
```

แต่ Candidate ไม่ได้หมายความว่า:

* Algorithm
* AI Answer
* Planning Strategy
* Proposal

Candidate เป็นเพียง **หนึ่ง Schedule Alternative**

---

# 4.52 Proposal

**Proposal** คือผลลัพธ์ที่นำเสนอให้ User ตรวจสอบ และสามารถประกอบด้วย Candidate หลายชุด

```text
Proposal
├── Candidate A
├── Candidate B
└── Candidate C
```

Proposal อาจมีเพียง:

```text
Candidate A
```

ได้เช่นกัน

ดังนั้น:

```text
1 ≤ Candidate Count ≤ 3
```

---

# 4.53 Candidate Generation Policy

ระบบไม่จำเป็นต้องสร้าง Candidate 3 ชุดทุกครั้ง

Candidate เพิ่มจะถูกสร้างเมื่อ:

1. มี Feasible Alternatives
2. คุณภาพอยู่ในระดับที่ยอมรับได้
3. มีความแตกต่างอย่างมีความหมาย
4. ความแตกต่างช่วยให้ User ตัดสินใจได้

ถ้า Schedule ถูกกำหนดตายตัว:

```text
Candidate Count = 1
```

เป็นผลลัพธ์ที่ถูกต้อง

---

# 4.54 Proposal State vs Schedule State

ต้องแยกสอง State อย่างชัดเจน

```text
Proposal
= Proposed State

Confirmed Schedule
= Committed State
```

ดังนั้น:

```text
AI / Planner
    ↓
Proposal
```

ยังไม่ทำให้:

```text
Confirmed Schedule
```

เปลี่ยน

ต้องมี:

```text
Explicit User Confirmation
```

ก่อนเสมอ

---

# 4.55 Schedule Version

Schedule Version คือ Snapshot ของ Confirmed Schedule ณ จุดเวลาหนึ่ง

ตัวอย่าง:

```text
Version 1
     ↓
Version 2
     ↓
Version 3
```

แต่ละ Version:

* Immutable
* มีหมายเลข Version
* สามารถอ้างอิงย้อนหลังได้
* ใช้เป็น Source Version ของ Proposal

Current Schedule คือ Schedule Version ที่ถูกทำเครื่องหมายเป็น Current

---

# 4.56 Schedule Item

Schedule Item คือรายการที่เป็นผลจากการนำ Activity ไปวางบนช่วงเวลาใน Confirmed Schedule

ตัวอย่าง:

```text
Activity:
“อ่านหนังสือ”

Schedule Item:
14:00–16:00
```

Activity เป็น Domain Object

Schedule Item เป็น Placement ใน Schedule

ดังนั้น Activity เดียวอาจถูกนำไปปรากฏใน Schedule Version ต่างกันในช่วงเวลาต่างกัน

---

# 4.57 Schedule as Source of Truth

Confirmed Schedule เป็น Source of Truth สำหรับเวลาที่ระบบถือว่ายืนยันแล้ว

Notification เป็น Derived State

ดังนั้น:

```text
Confirmed Schedule
        ↓
Notification
```

ไม่ใช่:

```text
Notification
        ↓
Schedule
```

หาก Notification ทำงานผิดพลาด Schedule ยังคงถูกต้อง

---

# 4.58 Domain Lifecycle Summary

## Activity

```text
ACTIVE
   ├── COMPLETED
   └── CANCELLED
```

Soft Delete (`deleted_at`) เป็น Storage Concern และไม่ควรปะปนกับ Business Status

---

## Planning Request

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

---

## Proposal

```text
PENDING
 ├── CONFIRMED
 ├── REJECTED
 └── INVALIDATED
```

---

## Schedule Version

```text
Immutable Version 1
        ↓
Immutable Version 2
        ↓
Immutable Version 3
```

Current Version เปลี่ยนเมื่อมีการ Confirm Schedule ใหม่

---

# 4.59 Domain Invariants

ต่อไปนี้เป็นกฎระดับ Domain ที่ทุก Layer ต้องเคารพ

### DI-01 — Planning Object Consistency

Object Type ต้องสอดคล้องกับ Activity Type และข้อมูลที่เกี่ยวข้อง

### DI-02 — Activity Time Consistency

หากมี Start Time และ End Time ต้องมีทั้งคู่ และ:

```text
End > Start
```

### DI-03 — Duration Positivity

Duration ที่นำไปใช้กับ Planning ต้องมากกว่า 0

### DI-04 — Date Consistency

End Date ต้องไม่ก่อน Start Date

### DI-05 — Hard Constraint Integrity

Schedule ที่ละเมิด Hard Constraint ถือว่าไม่ Feasible

### DI-06 — No Autonomous Confirmation

AI หรือ Planner ไม่สามารถเปลี่ยน Confirmed Schedule โดยตรง

### DI-07 — Proposal Separation

Proposal ต้องถูกแยกจาก Confirmed Schedule

### DI-08 — Version Immutability

Schedule Version ที่สร้างแล้วแก้ไขไม่ได้

### DI-09 — Stale Proposal Protection

Proposal ต้องอ้างอิง Source Schedule Version ที่สามารถตรวจสอบได้

### DI-10 — Container Membership

Child Activity ที่อยู่ใน Container ต้องปฏิบัติตาม Containment Rule

### DI-11 — Unavailability

Activity ไม่สามารถถูกจัดใน Unavailability

### DI-12 — Adjacent Intervals

ช่วงเวลาที่ต่อกันพอดีไม่ถือว่า Overlap

### DI-13 — No Unsupported Inference

Unknown หรือ Unsupported Information ต้องไม่ถูกเปลี่ยนเป็นข้อมูลที่ระบบเดาขึ้นเอง

### DI-14 — Notification Separation

Notification Time ไม่ใช่ Activity Start Time

### DI-15 — Calendar / Planning Separation

Calendar Data Range ไม่เท่ากับ Planning Horizon

---

# 4.60 Domain Example

ตัวอย่าง Input:

> “พรุ่งนี้ตอนบ่ายอยากทำรายงานสองชั่วโมง แต่หกโมงเย็นมีนัดกินข้าว และคืนนี้อยากนอนก่อนห้าทุ่ม”

ระบบสามารถสร้าง Domain Representation เชิงแนวคิดได้ประมาณ:

```text
Activity A
Title = ทำรายงาน
Date = Tomorrow
Window = AFTERNOON
Duration = 120 min
Requirement = Required

Activity B
Title = กินข้าว
Date = Tomorrow
Start = 18:00
Type = EVENT / APPOINTMENT ตาม Context

Preference C
Title = นอนก่อน 23:00
Type = Preference / Planning Requirement
```

Planning Engine จากนั้นพิจารณา:

```text
Duration
+
Time Window
+
Fixed Time
+
Preference / Requirement
+
Existing Schedule
+
Availability
```

เพื่อหาตารางที่ Feasible และเหมาะสมที่สุดตาม Objective Hierarchy

หากมีหลายทางเลือกที่แตกต่างอย่างมีความหมาย จึงค่อยสร้าง Candidate หลายชุด

---

# 4.61 Domain Model Summary

Domain ของ LONGTUA สามารถสรุปเป็นโครงสร้างดังนี้:

```text
                         PLANNING OBJECT
                         /             \
                        /               \
                   ACTIVITY          CONTAINER
                      |                  |
                      |             MEMBERSHIP
                      |                  |
                      +--------+---------+
                               |
                         PLANNING CONTEXT
                               |
              +----------------+----------------+
              |                |                |
        AVAILABILITY     UNAVAILABILITY      RULES
                                               |
                                      +--------+--------+
                                      |                 |
                                    HARD            PREFERENCE
                                      |
                                 TEMPORAL RELATIONS
                                      |
                           +----------+----------+
                           |          |          |
                         BEFORE     AFTER      OVERLAP
```

จากนั้น Planning Process:

```text
Natural Language
      ↓
Planning Request
      ↓
Planning Objects + Rules + Context
      ↓
Planning Representation
      ↓
Planning Engine
      ↓
Candidate(s)
      ↓
Proposal
      ↓
User Confirmation
      ↓
Schedule Version
      ↓
Schedule Items
```

---

# 4.62 Core Domain Principle

Domain ของ LONGTUA สามารถสรุปเป็นหลักการเดียวได้ว่า:

> **ระบบไม่ได้พยายามเพียงบันทึกกิจกรรม แต่พยายามนำกิจกรรม ความต้องการ ข้อจำกัด ความสัมพันธ์ของเวลา และบริบทของผู้ใช้มาประกอบกันเพื่อสร้าง Schedule ที่เป็นไปได้ และสามารถนำข้อมูลใหม่มาพิจารณาเพื่อสร้างแผนใหม่ได้**

และทุกการเปลี่ยนแปลงจาก Proposed State ไปสู่ Confirmed State ต้องผ่านการตัดสินใจของผู้ใช้
