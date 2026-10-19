# 5. AI / NLP Design

## 5.1 Purpose

เอกสารฉบับนี้กำหนดการออกแบบส่วน AI / NLP ของ LONGTUA — Personal Adaptive Planner ตั้งแต่การรับข้อความภาษาธรรมชาติ การทำความเข้าใจข้อมูล การสกัดข้อมูลเชิงโครงสร้าง การทำความเข้าใจเวลาและความสัมพันธ์ระหว่างกิจกรรม การตรวจจับข้อมูลที่กำกวมและข้อมูลที่ขาด การสร้าง Clarification การตีความ Feedback ของผู้ใช้ ตลอดจนการส่งต่อข้อมูลไปยัง Validation / Normalization และ Planning Representation

AI/NLP ใน LONGTUA ถูกออกแบบให้เป็น **Understanding Layer** ไม่ใช่ Scheduling Layer

หลักการสำคัญคือ:

> **AI เข้าใจสิ่งที่ผู้ใช้ต้องการ แต่ Planning Engine เป็นผู้คำนวณว่าจะจัดตารางอย่างไร และ User เป็นผู้ตัดสินใจว่าจะยืนยันผลลัพธ์หรือไม่**

แนวทางนี้สอดคล้องกับงานวิจัยด้าน Event-Centric NLP ซึ่งมองการทำความเข้าใจเหตุการณ์ว่าไม่ได้มีเพียงตัว Event แต่รวมถึงโครงสร้างภายใน Event, Participants, Properties รวมถึงความสัมพันธ์ระหว่าง Events เช่น Membership และ Temporal Relations ด้วย

---

# 5.2 Role of AI / NLP in LONGTUA

AI/NLP รับผิดชอบการเปลี่ยน:

```text
Natural Language
        ↓
Structured Planning Information
```

ไม่ใช่:

```text
Natural Language
        ↓
Final Schedule
```

ดังนั้น Architecture ที่ถูกต้องคือ:

```text
User
 ↓
Natural Language
 ↓
AI / NLP
 ↓
Validation / Normalization
 ↓
Planning Representation
 ↓
Planning Engine
```

และไม่ใช่:

```text
User
 ↓
AI
 ↓
Schedule
```

โดยตรง

---

# 5.3 AI / NLP Responsibilities

AI/NLP มีหน้าที่หลักดังนี้

1. Planning Object Understanding
2. Activity Type Understanding
3. Attribute Extraction
4. Temporal Understanding
5. Temporal Relation Extraction
6. Contextual Reference Resolution
7. Ambiguity Detection
8. Missing Information Detection
9. Clarification Decision
10. Unsupported Request Detection
11. User Feedback Interpretation
12. Structured Output Generation

---

# 5.4 AI / NLP Non-Responsibilities

AI/NLP **ไม่มีหน้าที่** ดังต่อไปนี้:

* จัด Start Time ของ Activity
* เลือกลำดับ Activity ที่ดีที่สุด
* ตรวจ Feasibility ของ Schedule แทน CP-SAT
* แก้ Conflict ด้วยการเลื่อน Activity เอง
* เปลี่ยน Confirmed Schedule
* Confirm Proposal
* สร้าง Notification
* ตัด Hard Constraint เพื่อให้ได้คำตอบ
* ตัด Activity ที่ User ระบุเป็น Required ออกเอง
* เข้าถึง Database โดยตรง
* ตัดสินใจ Autonomous ว่าผู้ใช้ควรใช้ Schedule ใด

กล่าวโดยสรุป:

> **AI สร้างความเข้าใจเชิงโครงสร้าง แต่ไม่สร้าง Commitment ของ Schedule**

---

# 5.5 Input Contract

Input หลักของ AI/NLP คือ:

```text
User Text
```

พร้อม Context ที่เกี่ยวข้องเมื่อจำเป็น

Context อาจประกอบด้วย:

* Reference Time
* Relevant Existing Activities
* Relevant Planning Rules
* Relevant Availability / Unavailability
* Existing Planning Request Context
* Pending Clarification Context
* User Settings ที่จำเป็น เช่น Time Window

ระบบไม่ควรส่งทั้งฐานข้อมูลหรือ Conversation History ทั้งหมดให้ AI โดยอัตโนมัติ

หลักการคือ:

> **Relevant Context Only**

เพื่อให้ Context มีขนาดเหมาะสมและลดข้อมูลที่ไม่เกี่ยวข้อง

---

# 5.6 Example Input

ตัวอย่างข้อความ:

> “พรุ่งนี้ช่วงบ่ายอยากทำรายงานประมาณสองชั่วโมง แต่หกโมงเย็นมีนัดกินข้าว แล้วอยากออกกำลังกายก่อนนอน”

ข้อความนี้มีหลายองค์ประกอบ:

```text
Activity 1
= ทำรายงาน

Date
= Tomorrow

Time Window
= Afternoon

Duration
= Approximately 2 hours

Activity 2
= กินข้าว

Start Time
= 18:00

Activity 3
= ออกกำลังกาย

Temporal Preference / Relation
= Before Sleep
```

AI ไม่ควรตอบกลับเป็น:

> “ผมจัดตารางให้ 14:00–16:00”

แต่ควรตอบกลับเป็น Structured Planning Information ที่ Planner นำไปคำนวณต่อ

---

# 5.7 AI / NLP Processing Pipeline

Pipeline หลัก:

```text
+----------------------+
| Natural Language     |
+----------+-----------+
           |
           v
+----------------------+
| Input Preprocessing  |
+----------+-----------+
           |
           v
+----------------------+
| Event / Activity     |
| Detection            |
+----------+-----------+
           |
           v
+----------------------+
| Planning Object      |
| Classification      |
+----------+-----------+
           |
           v
+----------------------+
| Attribute Extraction |
+----------+-----------+
           |
           v
+----------------------+
| Temporal Understanding|
+----------+-----------+
           |
           v
+----------------------+
| Relation Extraction  |
+----------+-----------+
           |
           v
+----------------------+
| Ambiguity / Missing  |
| Information Analysis |
+----------+-----------+
           |
           v
+----------------------+
| Clarification        |
| Decision             |
+----------+-----------+
           |
           v
+----------------------+
| Structured Output     |
+----------+-----------+
           |
           v
+----------------------+
| Validation /          |
| Normalization         |
+----------------------+
```

---

# 5.8 Input Preprocessing

Preprocessing มีหน้าที่เตรียม Input ให้ AI สามารถตีความได้อย่างสม่ำเสมอ

ขั้นตอนอาจรวมถึง:

* ตรวจสอบข้อความว่าง
* ตรวจสอบ Input Size
* Normalize Basic Text Representation
* เก็บ Reference Time
* ระบุ Language / Locale Context หากจำเป็น
* เตรียม Relevant Context

Preprocessing ไม่ควรทำการตีความ Domain ที่ควรเป็นหน้าที่ของ AI/NLP หรือ Validation

---

# 5.9 Activity / Event Detection

AI ต้องระบุว่าข้อความกล่าวถึงกิจกรรมหรือเหตุการณ์ใด

ตัวอย่าง:

> “พรุ่งนี้ไปประชุมตอนสิบโมง แล้วตอนบ่ายอยากอ่านหนังสือ”

อาจได้:

```text
Event 1 = ประชุม
Event 2 = อ่านหนังสือ
```

งาน Event-Centric NLP ให้ความสำคัญกับการตรวจจับ Event และโครงสร้าง/ความสัมพันธ์ของ Event เป็นองค์ประกอบสำคัญของ Natural Language Understanding

---

# 5.10 Planning Object Classification

หลังจากระบุ Event/Activity แล้ว AI ต้องพิจารณาว่าสิ่งนั้นเป็น Planning Object ประเภทใด

MVP รองรับ:

```text
ACTIVITY
CONTAINER
```

การตัดสินใจต้องใช้บริบท ไม่ใช่ Keyword เพียงอย่างเดียว

### Example 1

> “ทำงานจันทร์ถึงศุกร์ 8 โมงถึง 5 โมง”

อาจหมายถึง:

```text
AVAILABILITY
```

ไม่ใช่ Activity

### Example 2

> “มีสัมมนา 8 โมงถึง 5 โมง และมี Workshop ตอนบ่าย”

อาจหมายถึง:

```text
Container = สัมมนา
Child Activity = Workshop
```

### Example 3

> “ทำรายงานตั้งแต่ 8 โมงถึง 5 โมง”

อาจหมายถึง:

```text
Activity
```

การจำแนก Event และ Membership/Relations จากบริบทเป็นประเด็นที่งาน Event-Centric NLP ให้ความสำคัญ และงานด้าน Event-Event Relation ยังแสดงให้เห็นว่าความสัมพันธ์ด้านเวลาและ Membership สามารถต้องพิจารณาร่วมกันได้

---

# 5.11 Activity Type Classification

เมื่อ object ถูกจำแนกเป็น Activity ระบบสามารถระบุ Activity Type:

```text
TASK
EVENT
APPOINTMENT
MEETING
TRAVEL
OTHER
```

Activity Type ใช้เป็น Semantic Information

ไม่ควรใช้เพียงเพื่ออนุมาน Scheduling Behavior โดยอัตโนมัติ

ตัวอย่าง:

> “ประชุมพรุ่งนี้ช่วงบ่าย”

ไม่ได้หมายความว่าเวลาต้อง Fixed Time เสมอไป

AI สามารถระบุ:

```text
activity_type = MEETING
time_type = SEMANTIC_WINDOW
window = AFTERNOON
```

จากนั้น Planning Engine เป็นผู้ตัดสินว่าจะวางเมื่อใด

---

# 5.12 Attribute Extraction

AI ต้องสามารถสกัด Attribute ที่เกี่ยวข้องกับ Planning เช่น:

```text
Title
Description
Activity Type
Date
Start Time
End Time
Duration
Deadline
Priority
Requirement Strength
Time Window
Notification Preference
Temporal Relation
Container Membership
```

อย่างไรก็ตาม Attribute บางประเภทอาจถูกสร้างภายหลังจาก Validation / Normalization ไม่จำเป็นต้องให้ AI คืนเป็น Final Value ทั้งหมด

---

# 5.13 Requirement Strength

ข้อความของ User สามารถมีระดับความหนักเบาของความต้องการต่างกัน

ตัวอย่าง:

> “ต้องไปหาหมอตอน 10 โมง”

มีลักษณะเป็น Explicit Requirement

ขณะที่:

> “อยากออกกำลังกายตอนเย็น”

มีลักษณะเป็น Preference

AI ควรแยก Semantic Intention เหล่านี้ออกจากกันเพื่อให้ Validation / Planning Layer นำไปจัดประเภทเป็น:

```text
HARD / EXPLICIT REQUIREMENT
หรือ
PREFERENCE
```

โดยการตัดสิน Domain Policy สุดท้ายควรอยู่ใน Application/Domain Layer ไม่ควรปล่อยให้ Prompt เป็นผู้กำหนดเพียงอย่างเดียว

---

# 5.14 Temporal Understanding

Temporal Understanding เป็นส่วนสำคัญของระบบ เนื่องจาก Planning ต้องใช้เวลาที่ถูกต้อง

AI ต้องสามารถจัดประเภทข้อมูลเวลาเป็น:

```text
EXACT_TIME
TIME_RANGE
DATE
DURATION
DEADLINE
SEMANTIC_WINDOW
RELATIVE_TIME
APPROXIMATE_TIME
APPROXIMATE_DURATION
UNKNOWN
```

งานด้าน Temporal Relation Extraction ถือว่า Temporal Relations ระหว่าง Events เป็นส่วนสำคัญของ Natural Language Understanding และมีงานร่วมสมัยที่พัฒนาโครงสร้างการให้เหตุผลเกี่ยวกับความสัมพันธ์เหล่านี้โดยเฉพาะ

---

# 5.15 Exact Time

ตัวอย่าง:

> “บ่ายสองโมง”

AI ควรระบุ:

```text
time_type = EXACT_TIME
time = 14:00
```

หากบริบทภาษาไม่ได้ทำให้เกิด Ambiguity

Exact Time ต้องถูกเก็บเป็นข้อมูลที่มีความชัดเจน และไม่ควรถูกแปลงเป็น Time Window โดยไม่จำเป็น

---

# 5.16 Ambiguous Time

ตัวอย่าง:

> “พรุ่งนี้ 6 โมงไปวิ่ง”

อาจหมายถึง:

```text
06:00
หรือ
18:00
```

หากระบบไม่มี Context ที่สามารถระบุได้อย่างน่าเชื่อถือ:

```text
ambiguity = TRUE
```

และต้องเข้าสู่ Clarification Policy

ระบบต้องไม่เลือก 06:00 หรือ 18:00 เพียงเพราะเป็นค่าที่โมเดลคิดว่าน่าจะถูก

---

# 5.17 Semantic Time Window

ตัวอย่าง:

> “ช่วงบ่าย”

AI:

```text
time_type = SEMANTIC_WINDOW
window = AFTERNOON
```

จากนั้น:

```text
AFTERNOON
    ↓
Validation / Normalization
    ↓
User Override ?
   ├── Yes → User-defined Range
   └── No  → System Default
```

AI ไม่จำเป็นต้องรู้ Final Concrete Range หากข้อมูลนั้นถูกกำหนดโดย Policy ของระบบ

---

# 5.18 Approximate Time

ตัวอย่าง:

> “ประมาณบ่ายสอง”

AI:

```text
time_type = APPROXIMATE_TIME
nominal_time = 14:00
qualifier = APPROXIMATE
```

ระบบต้องรักษา Qualifier ไว้

ไม่ควรแปลงเป็น:

```text
EXACT_TIME = 14:00
```

โดยทำให้ข้อมูลว่าเป็น “ประมาณ” หายไป

---

# 5.19 Approximate Duration

ตัวอย่าง:

> “ใช้เวลาประมาณสองชั่วโมง”

AI:

```text
duration = 120 min
qualifier = APPROXIMATE
```

MVP สามารถใช้ 120 นาทีเป็น Nominal Planning Value แต่ต้องคง Qualifier ไว้ใน Structured Information

---

# 5.20 Date and Relative Time

ตัวอย่าง:

> “พรุ่งนี้”

AI ควรสร้าง Semantic Representation ที่อ้างอิง:

```text
referenceTime
```

เช่น:

```text
referenceTime.date = 2026-10-03
input = “พรุ่งนี้”
resolvedDate = 2026-10-04
```

ตัวอย่างเป็นเพียงการอธิบาย Concept การคำนวณ ไม่ใช่การกำหนดวันที่ตายตัวใน Schema

`currentDate` ไม่จำเป็นต้องเป็น Field แยกใน Planning Representation หากสามารถ Derive จาก `referenceTime`

---

# 5.21 Time Range

ตัวอย่าง:

> “บ่ายโมงถึงบ่ายสี่โมง”

AI:

```text
time_type = TIME_RANGE
start = 13:00
end = 16:00
```

หากใช้เป็น Fixed Time:

```text
Start = 13:00
End = 16:00
```

Planner ต้องถือเป็น Hard Timing Requirement ตาม Domain Policy

---

# 5.22 Duration Without Start Time

ตัวอย่าง:

> “พรุ่งนี้อยากทำรายงานสองชั่วโมง”

AI:

```text
date = tomorrow
duration = 120 min
start_time = UNKNOWN
```

กรณีนี้ยังไม่จำเป็นต้อง Clarify หาก Planner สามารถหาช่วงเวลาที่เหมาะสมได้

นี่เป็นเหตุผลที่:

> Missing Information ≠ Automatic Clarification

---

# 5.23 Deadline Understanding

ตัวอย่าง:

> “ต้องส่งรายงานภายในวันศุกร์”

AI ควรแยก:

```text
deadline = Friday
```

ไม่ใช่:

```text
start_time = Friday
```

และ Planner ต้องตีความเป็น:

```text
Activity End ≤ Deadline
```

เมื่อสามารถระบุ Deadline ได้อย่างชัดเจน

---

# 5.24 Temporal Relation Extraction

AI ต้องสามารถตรวจจับ Relation ที่ MVP รองรับ:

```text
BEFORE
AFTER
OVERLAP
```

ตัวอย่าง:

> “อ่านหนังสือก่อนออกไปกินข้าว”

ได้:

```text
Study BEFORE Dinner
```

งานวิจัยด้าน Temporal Relation Extraction สนับสนุนความสำคัญของการแยกความสัมพันธ์เชิงเวลา เช่น Before, After และ Simultaneous ระหว่าง Events และงานปี 2022 ยังแสดงให้เห็นว่าความสัมพันธ์ที่อยู่ห่างกันในข้อความและมีบริบทคั่นกลางเป็นความท้าทายสำคัญของงานนี้

---

# 5.25 Structural Relation: Container Membership

Container Membership เป็น Structural Relation ไม่ใช่ Generic Temporal Relation

ตัวอย่าง:

> “มีสัมมนา 8–17 และ Workshop 14–16 อยู่ในงานสัมมนา”

ควรแทน:

```text
Container
  └── Child Activity
```

มากกว่าการสร้าง:

```text
Container CONTAINS Child
```

เป็น Temporal Relation แบบเดียวกับ BEFORE/AFTER/OVERLAP

ดังนั้น:

```text
container_membership
```

เป็น Structural Domain Concept

ส่วน:

```text
temporal_relation
```

ใช้สำหรับ Temporal Semantics

แนวคิดการพิจารณา Event Hierarchy และ Membership ร่วมกับ Temporal Structure มีปรากฏในงาน Event-Event Relation ระยะหลังด้วย

---

# 5.26 OVERLAP Semantics

หาก User ระบุ:

> “ประชุมชนกับคลาส”

AI อาจตรวจพบ:

```text
OVERLAP
```

แต่ AI ไม่ควรสรุปว่า:

> “ดังนั้นทำสองอย่างพร้อมกันได้”

การอนุญาตหรือไม่อนุญาตให้ Schedule ซ้อนกันเป็นหน้าที่ของ Planning Engine

ดังนั้น:

```text
AI:
Temporal Meaning = OVERLAP

Planner:
Scheduling Feasibility = Conflict / Allowed
```

ตาม Execution Context

---

# 5.27 Context Resolution

ข้อความอาจมี Reference ที่ไม่สมบูรณ์

เช่น:

> “ย้ายอันนี้ไปตอนเย็น”

คำว่า “อันนี้” ต้องอ้างอิง Relevant Context

AI อาจได้รับ:

```text
Current Proposal
Relevant Activities
Recent User Interaction
```

แล้วสามารถระบุ:

```text
target_activity = Activity X
requested_window = EVENING
```

แต่ไม่ควรเข้าถึงทั้ง Database เพื่อค้นหาว่า “อันนี้” คืออะไร

---

# 5.28 Context Scope

Context ที่ส่งให้ AI ควรแบ่งเป็น:

### Required Context

ข้อมูลที่จำเป็นต่อ Interpretation เช่น:

* Reference Time
* Pending Clarification
* Target Activity
* Current Proposal ที่กำลัง Review

### Relevant Context

ข้อมูลที่ช่วย Resolve Meaning เช่น:

* Existing Activities ใกล้เคียง
* Related Temporal Relations
* Relevant User Settings

### Irrelevant Context

ไม่ควรถูกส่งโดยไม่จำเป็น เช่น:

* Activity ที่อยู่ไกลจากเหตุการณ์และไม่เกี่ยวข้อง
* User Data ที่ไม่มีส่วนต่อคำขอ
* Conversation History ทั้งหมด
* Database ทั้งหมด

---

# 5.29 Ambiguity Detection

AI ต้องประเมินว่า Input มีความกำกวมหรือไม่

ตัวอย่าง:

```text
“6 โมง”
```

อาจเป็น:

```text
06:00
18:00
```

แต่:

```text
“18:00”
```

ไม่มี Ambiguity ในกรณีปกติ

Ambiguity Detection เป็น Task ที่มีงานวิจัยเฉพาะด้าน และงานล่าสุดบางงานแยกกระบวนการออกเป็น Ambiguity Detection → Clarification Question Generation → Interpretation/Answering ซึ่งเป็นแนวทางที่สอดคล้องกับการออกแบบ LONGTUA

---

# 5.30 Missing Information Detection

ระบบต้องสามารถระบุได้ว่า Information ใดหายไป

ตัวอย่าง:

> “พรุ่งนี้ประชุมกับอาจารย์”

อาจรู้:

```text
Activity = Meeting
Date = Tomorrow
```

แต่ยังไม่รู้:

```text
Start Time
Duration
```

อย่างไรก็ตาม:

```text
Missing
≠
Must Clarify
```

ต้องดูว่าข้อมูลที่หายมีผลต่อ Operation ปัจจุบันหรือไม่

---

# 5.31 Clarification Decision

ระบบใช้หลัก:

> **Ask only when uncertainty affects interpretation or planning feasibility**

ตัวอย่างที่ควรถาม:

> “พรุ่งนี้ 6 โมงไปวิ่ง”

เพราะ 06:00 และ 18:00 อาจนำไปสู่ Schedule ที่แตกต่างกันอย่างมีนัยสำคัญ

ตัวอย่างที่ยังไม่จำเป็นต้องถาม:

> “พรุ่งนี้ซื้อของขวัญให้แฟน”

เพราะสามารถสร้าง Date-Only Activity ได้ก่อน

แนวคิดของการใช้ Clarification เพื่อเพิ่มความชัดเจนของ User Intent มีงานวิจัยรองรับ โดยงานปี 2021 ศึกษาการถาม Clarifying Question เมื่อ Query ยังไม่เฉพาะเจาะจงพอ และงานปี 2023 แยกชัดเจนระหว่าง Ambiguity Detection และ Clarification Generation

---

# 5.32 Clarification Decision Model

Conceptual Decision:

```text
Input
 ↓
Is information missing?
 ├── No
 │    ↓
 │  Continue
 │
 └── Yes
      ↓
Does missing/ambiguous info affect
interpretation or planning?
      ├── No → Continue with Unknown
      └── Yes
             ↓
         Clarification
```

---

# 5.33 Clarification Types

Clarification ใน MVP ควรถามแบบเฉพาะจุด

### Time Clarification

> “6 โมง หมายถึง 06:00 หรือ 18:00 ครับ?”

### Duration Clarification

เมื่อ Duration เป็นสิ่งจำเป็นต่อการ Scheduling แต่ไม่สามารถใช้ Policy หรือ Context ช่วยได้

### Activity Reference Clarification

เมื่อ User ระบุ:

> “เลื่อนไปเย็น”

แต่มี Activity ที่อาจเป็น Target ได้หลายรายการ

### Requirement Clarification

เมื่อไม่สามารถตัดสินได้ว่า User ต้องการบังคับ Constraint หรือเพียงแค่ Preference และความแตกต่างนั้นมีผลต่อผลลัพธ์

---

# 5.34 Clarification Quality

Clarification ควร:

* Specific
* Easy to Answer
* Resolve One Important Uncertainty
* Avoid Asking Unnecessary Questions
* Preserve Original Context

แนวคิดของ Clarification ในงาน Conversational AI ให้ความสำคัญกับการทำให้คำถามช่วยแยก Interpretation ที่เป็นไปได้ออกจากกันแทนที่จะถามข้อมูลแบบกว้าง ๆ

---

# 5.35 Clarification State

ในระดับ Application:

```text
Planning Request
      ↓
NEEDS_CLARIFICATION
      ↓
User Response
      ↓
Parent Request Context
      ↓
PROCESSING
```

Clarification ไม่ถูกออกแบบเป็น Independent Database Entity ใน MVP

ดังนั้นข้อมูลที่ต้องใช้ต่อจะสัมพันธ์กับ:

```text
planning_request
parent_request_id
```

---

# 5.36 Structured Output

AI ต้องส่งข้อมูลออกใน Schema ที่กำหนดไว้

Conceptual Structure:

```json
{
  "objects": [
    {
      "object_type": "ACTIVITY",
      "activity_type": "TASK",
      "title": "ทำรายงาน",
      "date": {
        "type": "RELATIVE_DATE",
        "value": "TOMORROW"
      },
      "time": {
        "type": "SEMANTIC_WINDOW",
        "value": "AFTERNOON"
      },
      "duration": {
        "value_minutes": 120,
        "qualifier": "APPROXIMATE"
      }
    }
  ],
  "relations": [],
  "clarification": null
}
```

โครงสร้างนี้เป็น **Conceptual Contract** และจะถูกทำให้ละเอียดต่อใน API / AI Contract Specification โดยไม่ควรนำ JSON ตัวอย่างนี้ไปถือเป็น Final API Schema โดยตรง

---

# 5.37 Why Structured Output

Structured Output ช่วยให้ AI Output มี Boundary ที่ชัดเจนก่อนเข้าสู่ Validation และ Planning

งานปี 2024 เช่น ChatUIE สำรวจการใช้ LLM สำหรับ Unified Information Extraction และระบุความท้าทายของการดึง Structured Information ภายใต้ Schema รวมถึงเสนอการใช้ Generation Constraints เพื่อช่วยลดการสร้าง Element ที่ไม่ได้อยู่ใน Input

อีกงานในปี 2024 ศึกษาปัญหาความไม่สม่ำเสมอของ LLM ในการสร้าง Structured Text และเสนอการแยกการสร้างเนื้อหาออกจากการจัดให้อยู่ในโครงสร้างเป้าหมาย

ดังนั้น LONGTUA จึงไม่ควรเชื่อ AI Output เพียงเพราะ Output อยู่ในรูป JSON แต่ต้องมี Validation Layer ต่อจากนั้น

---

# 5.38 Schema Validation

Flow:

```text
AI Output
    ↓
JSON / Schema Validation
    ↓
Valid?
 ├── No → AI Output Error
 └── Yes
       ↓
Domain Validation
```

Schema Validation ตรวจ:

* Required Fields
* Data Types
* Enum Values
* Object Structure
* Nesting
* Nullability
* Identifier References

---

# 5.39 Domain Validation

หลังผ่าน Schema แล้วต้องตรวจ Domain Rules

ตัวอย่าง:

```text
start = 15:00
end = 14:00
```

Schema อาจถูกต้องในรูปแบบข้อมูล แต่ Domain ไม่ถูกต้อง

ดังนั้น:

```text
Schema Valid
≠
Domain Valid
```

---

# 5.40 Unsupported Information

AI ต้องสามารถแยกคำขอที่อยู่นอก MVP ออกจาก Missing Information

ตัวอย่าง:

> “จัดเส้นทางโดยเลือกเส้นทางที่รถติดน้อยที่สุดแบบ Real-time”

ระบบอาจระบุ:

```text
unsupported_capability = ROUTE_OPTIMIZATION_REALTIME_TRAFFIC
```

ไม่ควรพยายามสร้างข้อมูลทางจราจรขึ้นมาเอง

---

# 5.41 Hallucination / Unsupported Inference Control

LONGTUA ต้องถือว่าข้อมูลต่อไปนี้เป็น Planning-Critical:

* Date
* Exact Time
* Time Range
* Duration
* Deadline
* Fixed Time
* Required Relation
* Critical Constraint

AI ห้ามสร้างค่าเหล่านี้ขึ้นมาโดยไม่มี Evidence

ตัวอย่าง:

User:

> “พรุ่งนี้อยากอ่านหนังสือ”

AI ไม่ควรคืน:

```text
start = 14:00
duration = 2 hours
```

เว้นแต่ระบบมีข้อมูลจาก Context/Policy ที่อนุญาตอย่างชัดเจน

---

# 5.42 Evidence Principle

ข้อมูลแต่ละ Field ควรสามารถอธิบายได้ว่ามาจาก:

```text
User Input
หรือ
Relevant Context
หรือ
Explicit System Policy
```

ไม่ใช่:

```text
Model Guess
```

ตัวอย่าง:

```text
“ช่วงบ่าย”
→ User Input

“พรุ่งนี้”
→ User Input + Reference Time

06:00 Notification
→ System Policy

14:00 Activity Start
→ Planning Engine
```

จุดสุดท้ายสำคัญมาก:

> **Activity Start Time ที่ Planner เลือก ไม่ควรย้อนกลับไปถูกมองว่าเป็นสิ่งที่ AI Extract มาจาก User**

---

# 5.43 AI Output Confidence

MVP สามารถเก็บ Internal Confidence/Reason Information เพื่อใช้ในการ Debug และ Evaluation ได้ตามความเหมาะสม แต่ Confidence Score ไม่ควรเป็นตัวแทนของ Domain Validation

กล่าวคือ:

```text
confidence = high
```

ไม่ได้แปลว่า:

```text
domain_valid = true
```

Validation ต้องตรวจด้วย Rule จริง

---

# 5.44 Feedback Understanding

User สามารถให้ Feedback เช่น:

> “อันนี้อยากเลื่อนไปช่วงเย็น”

AI มีหน้าที่:

```text
Feedback Text
 ↓
Target Activity
 ↓
Requested Change
 ↓
New Requirement / Preference
```

ตัวอย่าง:

```text
target = Study
requested_window = EVENING
```

จากนั้น:

```text
Validation
 ↓
Planning Representation
 ↓
Replanning
```

AI ไม่ควรตอบด้วยการเลือกเวลาใหม่เอง

---

# 5.45 Negative Feedback

ผู้ใช้สามารถบอกว่า:

> “ตารางนี้ไม่โอเค”

เพียงอย่างเดียวอาจไม่เพียงพอสำหรับ Replanning ที่มีความหมาย

ระบบอาจต้อง Clarify เช่น:

> “ต้องการปรับช่วงเวลา หรือมีข้อจำกัดอะไรเพิ่มเติมไหม?”

แต่ถ้า User ให้ข้อมูล:

> “ไม่อยากให้วิ่งตอนกลางคืน ขอเป็นช่วงเย็นแทน”

สามารถแปลงเป็น Preference / Requirement ได้ทันที

---

# 5.46 AI and Replanning Boundary

Replanning Flow:

```text
User Change / Feedback
       ↓
AI / NLP
       ↓
Structured Change
       ↓
Validation
       ↓
Planning Representation
       ↓
Planning Engine
```

AI ไม่ควร:

```text
Old Schedule
 ↓
AI
 ↓
New Schedule
```

โดยตรง

---

# 5.47 AI and Existing Schedule

เมื่อ User ขอแก้ตาราง เช่น:

> “พรุ่งนี้ประชุมเลื่อนจากบ่ายสองเป็นสี่โมง”

AI อาจ Extract:

```text
Target Activity = Meeting
New Start Time = 16:00
```

แต่ AI ไม่ควรตัดสินใจ:

```text
Study → move to 18:00
Dinner → move to 20:00
```

สิ่งเหล่านี้เป็นผลจาก Planning Core

---

# 5.48 Multi-Turn Context

MVP รองรับ Context ต่อเนื่องที่จำเป็นต่อ Clarification และ Feedback

ตัวอย่าง:

````text
User:
“พรุ่งนี้ 6 โมงไปวิ่ง”

System:
“หมายถึง 06:00 หรือ 18:00?”

User:
“เย็น”

AI ต้องสามารถตีความ “เย็น” โดยอ้างอิง Pending Clarification Context ว่ากำลังตอบคำถามเรื่องเวลา

ผล:

```text
time = 18:00
````

ไม่ควรตีความ “เย็น” เป็น Activity ใหม่

---

# 5.49 Clarification Context Lifecycle

```text
Request A
   ↓
Needs Clarification
   ↓
Pending Context
   ↓
User Response
   ↓
Merge Original Request + Response
   ↓
Continue Processing
```

ดังนั้น Clarification Response ไม่ใช่ Request ใหม่ที่ไม่มีความสัมพันธ์กับ Request เดิม

---

# 5.50 AI Failure Handling

AI Provider อาจ:

* Timeout
* Return Invalid Structure
* Return Unsupported Output
* Return Empty Output
* Fail to Resolve Ambiguity
* Return Missing Required Fields

ในทุกกรณี:

```text
AI Failure
    ↓
Do Not Plan
    ↓
Return Controlled Error / Clarification
```

AI Failure ต้องไม่ทำให้ระบบสร้าง Schedule แบบเดาสุ่มเพื่อให้กระบวนการเดินต่อ

---

# 5.51 Provider Adapter

AI Architecture:

```text
Application
      ↓
AI Service Interface
      ↓
Provider Adapter
   ├── Gemini
   └── Claude
```

Primary Provider:

> Google Gemini

Alternative:

> Claude

Provider-specific Prompt, SDK และ API Detail ต้องอยู่ใน Adapter/AI Integration Layer และไม่รั่วเข้า Domain/Planning Layer

---

# 5.52 Prompt Responsibility

Prompt มีหน้าที่กำหนด:

* Role
* Output Schema
* Domain Definitions
* Allowed Values
* Interpretation Rules
* Clarification Policy
* No-Invention Rule
* Relevant Context

Prompt ไม่ควร:

* คำนวณ CP-SAT
* กำหนด Final Schedule
* เปลี่ยน Confirmed Schedule
* เลือก Candidate ที่ดีที่สุดแทน User

---

# 5.53 AI Instruction Hierarchy

AI ควรยึดลำดับ:

```text
1. System Safety / Contract
        ↓
2. Domain Schema
        ↓
3. User Input
        ↓
4. Relevant Context
        ↓
5. Interpretation
```

AI ไม่ควรใช้สิ่งที่ไม่อยู่ใน Input หรือ Context ที่ได้รับมาเป็นข้อเท็จจริง

---

# 5.54 AI Output → Planning Contract

Boundary กลาง:

```text
+---------------------+
| AI / NLP             |
| Understanding        |
+----------+----------+
           |
           | Structured Planning Information
           v
+---------------------+
| Validation           |
| / Normalization      |
+----------+----------+
           |
           | Valid Planning Representation
           v
+---------------------+
| Planning Core        |
| CP-SAT               |
+---------------------+
```

Contract นี้เป็นหนึ่งใน Architecture Boundary ที่สำคัญที่สุดของระบบ

---

# 5.55 Responsibility Matrix

| Task                      | AI/NLP | Validation | Planner |             User |
| ------------------------- | -----: | ---------: | ------: | ---------------: |
| Extract Activity          |      ✅ |            |         |                  |
| Classify Object           |      ✅ | ✅ Validate |         |                  |
| Extract Time              |      ✅ |          ✅ |         |                  |
| Detect Ambiguity          |      ✅ |          ✅ |         |                  |
| Ask Clarification         |      ✅ |            |         |                  |
| Verify Domain             |        |          ✅ |         |                  |
| Resolve Schedule          |        |            |       ✅ |                  |
| Check Feasibility         |        |            |       ✅ |                  |
| Create Candidate          |        |            |       ✅ |                  |
| Review Proposal           |        |            |         |                ✅ |
| Confirm Schedule          |        |            |         |                ✅ |
| Replan                    |        |            |       ✅ | ✅ Trigger/Review |
| Interpret Feedback        |      ✅ |          ✅ |         |                  |
| Change Confirmed Schedule |        |            |         |                ✅ |

หมายเหตุ:

> User เป็นผู้สร้าง Commitment ผ่าน Explicit Confirmation ไม่ใช่ AI

---

# 5.56 Example — Complete AI Flow

Input:

> “พรุ่งนี้ช่วงบ่ายอยากอ่านหนังสือสองชั่วโมง แต่หกโมงมีนัดกินข้าว”

AI Output Conceptually:

```text
Object 1
type = ACTIVITY
activity_type = TASK
title = อ่านหนังสือ
date = TOMORROW
time = AFTERNOON
duration = 120

Object 2
type = ACTIVITY
activity_type = EVENT / APPOINTMENT
title = กินข้าว
date = TOMORROW
start = 18:00
```

จากนั้น Validation ตรวจ:

```text
Schema ✓
Date ✓
Duration ✓
Time ✓
```

แล้ว Planning Representation:

```text
Study
duration = 120
window = AFTERNOON

Dinner
fixed_start = 18:00
```

Planning Engine จึงเป็นผู้หาเวลาที่เหมาะสม

---

# 5.57 Example — Ambiguity

Input:

> “พรุ่งนี้ 6 โมงไปวิ่ง”

AI:

```text
activity = วิ่ง
date = TOMORROW
time = AMBIGUOUS
possible = 06:00 / 18:00
```

Application:

```text
NEEDS_CLARIFICATION
```

User:

> “หกโมงเย็น”

AI:

```text
resolved_time = 18:00
```

จากนั้น Planner จึงทำงานต่อ

---

# 5.58 Example — Missing Duration

Input:

> “พรุ่งนี้ช่วงบ่ายทำรายงาน”

AI:

```text
activity = ทำรายงาน
date = TOMORROW
window = AFTERNOON
duration = UNKNOWN
```

Policy ตรวจ:

```text
Can current operation proceed?
```

ถ้าไม่จำเป็นต้องมี Duration ในขั้นตอนปัจจุบัน:

```text
Continue
```

ถ้าการสร้าง Schedule จำเป็นต้องใช้ Duration แต่ไม่มี Default/Policy ที่อนุญาต:

```text
Clarification
```

---

# 5.59 Example — Unsupported Request

Input:

> “ช่วยจัดตารางโดยคำนวณเส้นทางตามรถติดสดด้วย”

AI:

```text
unsupported = REALTIME_TRAFFIC_ROUTE_OPTIMIZATION
```

ระบบไม่ควรสร้าง Route หรือ Traffic Estimate เอง

---

# 5.60 Example — Feedback

Existing Proposal:

```text
Study = 14:00–16:00
Dinner = 18:00
```

User:

> “ขออ่านหนังสือช่วงเย็นแทน และไม่อยากให้กระทบเวลานอน”

AI:

```text
target = Study
requested_window = EVENING
preference = preserve_sleep_time
```

Planner:

```text
Existing Schedule
+
New Requirement
+
Preference
+
Constraints
↓
Replanning
```

ผลลัพธ์กลับเป็น New Proposal ไม่ใช่การเปลี่ยน Confirmed Schedule โดยตรง

---

# 5.61 Structured Extraction Contract

AI Output ควรมีองค์ประกอบระดับ Concept ดังนี้:

```text
PlanningExtraction
├── Objects
│   ├── object_type
│   ├── activity_type
│   ├── title
│   ├── description
│   ├── temporal_information
│   ├── duration
│   ├── deadline
│   ├── requirement_strength
│   └── attributes
│
├── Relations
│   ├── temporal_relation
│   └── object_references
│
├── Constraints / Preferences
│
├── Ambiguities
│
├── Missing Information
│
├── Unsupported Requests
│
└── Clarification
```

รายละเอียด Field-Level Schema จะถูกกำหนดใน AI Contract เอกสารถัดไป/ส่วน Implementation Specification โดยต้องไม่ขัดกับ Domain Model นี้

---

# 5.62 Validation Pipeline

AI Output ต้องผ่าน 3 ระดับ:

```text
Level 1
Schema Validation
       ↓
Level 2
Domain Validation
       ↓
Level 3
Planning Readiness
```

### Schema Validation

> “ข้อมูลมีรูปแบบถูกต้องหรือไม่?”

### Domain Validation

> “ข้อมูลมีความหมายที่ถูกต้องตามระบบหรือไม่?”

### Planning Readiness

> “ข้อมูลเพียงพอและปลอดภัยพอที่จะส่งเข้า Planner หรือยัง?”

---

# 5.63 Planning Readiness

ข้อมูลอาจ:

```text
Schema Valid = TRUE
Domain Valid = TRUE
```

แต่ยัง:

```text
Planning Ready = FALSE
```

เช่น:

> Activity ต้องใช้ Duration แต่ Duration ยัง Unknown และ Policy ไม่สามารถกำหนดค่าได้

กรณีนี้ต้อง:

```text
Clarification
```

ไม่ใช่ส่งเข้า CP-SAT พร้อมค่าเดา

---

# 5.64 AI Evaluation Interface

AI/NLP Module ต้องสามารถถูกประเมินแยกจาก Planning Engine

ข้อมูลที่สามารถวัดได้:

### Extraction

* Precision
* Recall
* F1
* Exact Match
* Field-level Accuracy

### Schema

* Schema Validity Rate

### Unsupported Data

* Unsupported Information Rate
* Unsupported Inference Rate

### Clarification

* Ambiguity Detection Accuracy
* Clarification Decision Accuracy
* Clarification Success Rate

### Temporal

* Date Accuracy
* Time Accuracy
* Duration Accuracy
* Temporal Relation Accuracy

การประเมินต้องแยกความผิดพลาดของ AI ออกจากความผิดพลาดของ Planner เพื่อให้สามารถตอบ RQ1 ได้โดยตรง

---

# 5.65 Error Taxonomy

ข้อผิดพลาดด้าน AI/NLP ควรจำแนกอย่างน้อย:

```text
E1 Object Detection Error
E2 Object Type Classification Error
E3 Activity Type Error
E4 Attribute Extraction Error
E5 Temporal Interpretation Error
E6 Temporal Relation Error
E7 Reference Resolution Error
E8 Ambiguity Detection Error
E9 Missing Information Error
E10 Unsupported Request Error
E11 Clarification Decision Error
E12 Structured Output Error
E13 Unsupported Inference / Hallucination
```

Error Taxonomy นี้จะช่วยใน Error Analysis ภายหลัง

---

# 5.66 Research Foundation

การออกแบบ AI/NLP ของ LONGTUA ถูกวางบนแนวคิดจากงานวิจัยช่วงปี 2020–ปัจจุบัน ซึ่งสอดคล้องกับข้อกำหนดของโครงการที่ใช้เฉพาะงานวิจัยในช่วงเวลาดังกล่าว

งานที่เกี่ยวข้องประกอบด้วย:

### Event-Centric NLP

งานด้าน Event-Centric NLP อธิบายการทำความเข้าใจ Event ทั้งในระดับโครงสร้างภายในและความสัมพันธ์กับ Event อื่น เช่น Membership และ Temporal Relations ซึ่งสอดคล้องกับการที่ LONGTUA ไม่มอง Activity เป็นเพียงข้อความชื่อกิจกรรม แต่เป็น Structured Planning Object ที่มี Attributes และ Relations

### Temporal Relation Extraction

งานปี 2020 และ 2022 ศึกษาการสกัด Temporal Relations ระหว่าง Events และความท้าทายของการตีความความสัมพันธ์เมื่อ Events อยู่ห่างกันหรือมีบริบทคั่นกลาง ซึ่งสนับสนุนการแยก Temporal Understanding ออกเป็นส่วนเฉพาะใน LONGTUA

### Structured Information Extraction with LLMs

งานปี 2024 เช่น ChatUIE และ IEPile ศึกษาการใช้ LLM สำหรับ Structured Information Extraction และความสำคัญของ Schema/Generation Constraints ต่อคุณภาพของผลลัพธ์

ขณะเดียวกัน งานปี 2024 ที่ศึกษา Structured Language Model Output ชี้ให้เห็นว่า Structured Generation เป็นปัญหาที่ต้องพิจารณาแยกจากการสร้างเนื้อหา ทำให้การออกแบบของ LONGTUA ที่มี Validation Layer หลัง AI Output มีเหตุผลในเชิงสถาปัตยกรรม

### Clarification

งานวิจัยปี 2021–2023 ศึกษาการใช้ Clarifying Questions เมื่อ Input มีความกำกวมหรือไม่เฉพาะเจาะจงเพียงพอ และมีงานที่แยก Ambiguity Detection กับ Clarification Generation เป็นกระบวนการที่สามารถประเมินแยกกันได้ ซึ่งสอดคล้องกับ Clarification Pipeline ของ LONGTUA

---

# 5.67 Design Rationale

การออกแบบ AI/NLP ของ LONGTUA ใช้หลักการสำคัญดังนี้

### Rationale 1 — Structured Before Scheduling

Natural Language ไม่ควรถูกส่งเข้า Solver โดยตรง เพราะ Planning Engine ต้องการ Domain Representation ที่มี Semantic ชัดเจน

### Rationale 2 — Validation After AI

LLM Output ไม่ถูกถือว่าเป็นความจริงเพียงเพราะมีรูปแบบถูกต้อง จึงต้องผ่าน Schema และ Domain Validation

### Rationale 3 — Clarify Only When Necessary

การถามทุกครั้งที่ข้อมูลไม่ครบจะเพิ่ม Interaction Burden จึงใช้ Policy ที่ถามเฉพาะ Missing/Ambiguous Information ที่มีผลต่อ Interpretation หรือ Planning

### Rationale 4 — No Invention

Planning-Critical Data ต้องมาจาก User Input, Relevant Context หรือ Explicit System Policy

### Rationale 5 — Planner Owns Scheduling

AI ไม่ควรรับผิดชอบ Scheduling เพราะจะทำให้ AI และ Optimization Logic รวมอยู่ใน Component เดียวกันและทำให้การตรวจสอบ Feasibility/Constraint Integrity ทำได้ยากขึ้น

### Rationale 6 — User Controls Commitment

แม้ AI และ Planner จะสามารถสร้าง Proposal ได้ แต่การเปลี่ยนจาก Proposed State เป็น Confirmed State ต้องเกิดจาก Explicit User Confirmation

---

# 5.68 AI / NLP Invariants

ข้อกำหนดที่ถือเป็น Invariant:

```text
AI-INV-01
AI interprets; Planner schedules.

AI-INV-02
AI never autonomously changes Confirmed Schedule.

AI-INV-03
AI never invents Planning-Critical Information.

AI-INV-04
Ambiguous information is clarified when it affects Planning.

AI-INV-05
Missing information does not automatically require Clarification.

AI-INV-06
Unsupported capability is not silently approximated.

AI-INV-07
AI Output must pass Validation before Planning.

AI-INV-08
AI does not access Database directly.

AI-INV-09
AI does not directly create Notifications.

AI-INV-10
AI does not decide Candidate confirmation.
```

---

# 5.69 AI / NLP End-to-End Summary

กระบวนการทั้งหมดสามารถสรุปได้เป็น:

```text
                 USER
                   |
                   v
          Natural Language
                   |
                   v
          +----------------+
          |   AI / NLP     |
          +-------+--------+
                  |
        +---------+----------+
        |         |          |
        v         v          v
     Objects   Temporal   Relations
        |         |          |
        +---------+----------+
                  |
                  v
       Ambiguity / Missing /
          Unsupported
                  |
          +-------+-------+
          |               |
       Clarify         Continue
          |               |
          +-------+-------+
                  |
                  v
         Structured Output
                  |
                  v
       Schema Validation
                  |
                  v
        Domain Validation
                  |
                  v
      Planning Readiness
                  |
                  v
     Planning Representation
                  |
                  v
         PLANNING CORE
```

---

# 5.70 Core Principle

AI / NLP ของ LONGTUA มีหน้าที่ทำให้ระบบเข้าใจว่า:

> **“ผู้ใช้กำลังต้องการอะไร และเงื่อนไขที่ผู้ใช้ระบุหมายถึงอะไร”**

จากนั้น Planning Engine จึงรับผิดชอบคำถามต่อไปว่า:

> **“ภายใต้ข้อมูลเหล่านั้น ระบบสามารถจัดตารางอย่างไรได้บ้าง”**

และสุดท้าย User เป็นผู้ตอบคำถามว่า:

> **“ฉันต้องการยืนยันแผนนี้หรือไม่”**

จึงได้ Architecture ที่แยกความรับผิดชอบเป็น:

```text
AI/NLP
= Understand

Validation
= Verify

Planning Engine
= Compute

Proposal
= Present

User
= Decide
```

หลักการดังกล่าวเป็นแกนสำคัญของ LONGTUA และต้องคงไว้ในทุกส่วนของระบบ ตั้งแต่ Initial Planning, Clarification, Feedback, Replanning จนถึง Confirmed Schedule
