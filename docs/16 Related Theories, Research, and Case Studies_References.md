# 16. Related Theories, Research, and Case Studies / References

## 16.1 Purpose

เอกสารนี้รวบรวมทฤษฎี แนวคิด งานวิจัยที่เกี่ยวข้อง และกรณีศึกษาของระบบที่มีคุณลักษณะใกล้เคียงกับ LONGTUA เพื่อใช้เป็นพื้นฐานทางวิชาการสำหรับการออกแบบและประเมินระบบ

เนื้อหาแบ่งเป็น 3 ส่วนหลัก:

1. **ทฤษฎีและแนวคิดที่เกี่ยวข้อง**
2. **งานวิจัยที่เกี่ยวข้อง**
3. **กรณีศึกษาและระบบที่มีอยู่จริง**

วัตถุประสงค์สำคัญไม่ใช่เพียงการแสดงว่ามีงานวิจัยเกี่ยวข้องกับแต่ละ component แต่ต้องแสดงความสัมพันธ์ระหว่าง:

```text
Research / Theory
        ↓
Design Principle
        ↓
LONGTUA Design
        ↓
Evaluation
```

ดังนั้นแต่ละงานวิจัยจะถูกพิจารณาในมุม:

- งานศึกษาปัญหาอะไร
- เสนอแนวทางอะไร
- ผลการศึกษาสนับสนุนอะไร
- เกี่ยวข้องกับ LONGTUA อย่างไร
- LONGTUA นำมาใช้ส่วนใด
- ส่วนใดยังคงเป็นข้อแตกต่างของ LONGTUA

---

# 16.2 Reference Selection Criteria

การคัดเลือกแหล่งอ้างอิงสำหรับโครงงานใช้หลักดังนี้:

### 16.2.1 Publication Year

งานวิจัยหลักที่ใช้เป็น project citation ต้องอยู่ในช่วง:

```text
2020 – ปัจจุบัน
```

เพื่อให้สอดคล้องกับ research scope ที่กำหนดไว้

### 16.2.2 Relevance

เลือกงานที่เกี่ยวข้องโดยตรงกับ:

- Natural Language Understanding
- Event Extraction
- Temporal Understanding
- Information Extraction
- Structured LLM Output
- Constraint Programming
- Scheduling
- Preference-aware Planning
- Re-planning / Rescheduling
- Human-in-the-loop
- Clarification
- Interactive Decision Support
- Calendar / Scheduling Systems
- Evaluation

### 16.2.3 Source Quality

ลำดับความสำคัญของแหล่ง:

1. Peer-reviewed conference/journal
2. Official publisher / digital library
3. Official research organization
4. Official technical documentation
5. Product documentation สำหรับกรณีศึกษา

ไม่ใช้ blog หรือโพสต์ทั่วไปเป็นหลักฐานสำหรับ research claim สำคัญ

---

# 16.3 Theoretical Foundation

## 16.3.1 Natural Language Processing

Natural Language Processing (NLP) คือสาขาที่ศึกษาวิธีทำให้คอมพิวเตอร์สามารถประมวลผลและตีความภาษามนุษย์

สำหรับ LONGTUA จุดสำคัญไม่ได้อยู่ที่การสร้าง chatbot แต่เป็นการเปลี่ยนข้อความธรรมชาติให้เป็น **structured planning information**

แนวคิด:

```text
Natural Language
      ↓
Semantic Understanding
      ↓
Structured Representation
```

ตัวอย่าง:

> “พรุ่งนี้ตอนเย็นไปวิ่งหนึ่งชั่วโมง”

สามารถเปลี่ยนเป็นแนวคิดเชิงโครงสร้าง:

```text
Activity
type = TASK
title = วิ่ง

date = tomorrow
time = semantic: EVENING
duration = 60 minutes
```

ดังนั้น NLP เป็น **understanding layer** ไม่ใช่ optimization layer

---

# 16.4 Information Extraction

Information Extraction (IE) มีเป้าหมายในการแปลงข้อมูลจากข้อความที่ไม่มีโครงสร้างเป็นข้อมูลที่มีโครงสร้าง

แนวคิดพื้นฐาน:

```text
Unstructured Text
       ↓
Entities / Events / Relations / Attributes
       ↓
Structured Data
```

งานวิจัยด้าน Event Extraction แสดงให้เห็นว่า event information สามารถถูกมองเป็น structured representation แทนที่จะเป็นเพียง classification ของ token แต่ละตัว

Liu et al. (2020) เสนอการมอง Event Extraction เป็น Machine Reading Comprehension และแสดงว่าการ formulate งานในลักษณะนี้ช่วยให้สามารถดึง event arguments จากข้อความได้ โดยเฉพาะในสถานการณ์ที่มีข้อมูลฝึกน้อย

แนวคิดนี้สอดคล้องกับ LONGTUA ที่ต้องดึงข้อมูลเชิงโครงสร้างจากข้อความ เช่น:

- Activity
- Date
- Time
- Duration
- Constraint
- Preference
- Relation

### การประยุกต์ใช้ใน LONGTUA

LONGTUA จึงออกแบบ AI/NLP เป็น:

```text
Text
 ↓
Event / Activity Detection
 ↓
Attribute Extraction
 ↓
Temporal Understanding
 ↓
Relation Extraction
 ↓
Structured Output
```

---

# 16.5 Event Extraction

Event Extraction มุ่งระบุว่า:

1. เกิดเหตุการณ์อะไร
2. เหตุการณ์มีองค์ประกอบอะไร
3. entity หรือ attribute ใดเกี่ยวข้องกับเหตุการณ์นั้น

Text2Event ของ Lu et al. (2021) เสนอแนวทาง sequence-to-structure generation สำหรับการ extract event structure จาก text โดยตรง และชี้ให้เห็นปัญหาความซับซ้อนของ event structure และ semantic gap ระหว่างข้อความกับ event representation

แนวคิดนี้มีความเกี่ยวข้องโดยตรงกับ LONGTUA เพราะระบบไม่ได้ต้องการเพียงรู้ว่า user “พูดถึงการวิ่ง” แต่ต้องรู้ด้วยว่า:

```text
Activity = วิ่ง
Date = พรุ่งนี้
Time = ช่วงเย็น
Duration = 1 ชั่วโมง
```

ดังนั้น **event extraction เป็นพื้นฐานของการสร้าง Planning Representation**

---

# 16.6 Structured Information Extraction with Language Models

เมื่อใช้ LLM ใน IE ปัญหาหนึ่งคือ output ที่ได้อาจมีรูปแบบไม่สม่ำเสมอ

งานของ Li, Ramprasad และ Zhang (2024) ชี้ว่าการให้ LLM สร้าง output ใน structured format โดยตรงอาจไม่สม่ำเสมอ และเสนอการแยกขั้นตอนการสร้างเนื้อหาออกจากการจัดรูปแบบโครงสร้าง เพื่อเพิ่มความน่าเชื่อถือของ structured generation

Wu et al. (2024) ศึกษาการ extract structured entities ด้วย language models และเสนอกรอบ structured entity extraction พร้อมวิธีประเมินที่ละเอียดขึ้นสำหรับข้อมูลเชิงโครงสร้าง

ChatUIE ของ Xu et al. (2024) ศึกษา unified information extraction ผ่าน conversational/LLM-based paradigm ซึ่งสะท้อนแนวทางการใช้ LLM ในงาน IE ที่ต้องรองรับ schema หลากหลาย

### Implication for LONGTUA

ผลจากงานเหล่านี้สนับสนุน design:

```text
LLM
 ↓
Structured Output
 ↓
Schema Validation
 ↓
Domain Validation
 ↓
Normalization
 ↓
Planning Representation
```

ไม่ควรให้ LLM output ถูกนำไปสร้าง schedule โดยตรง

---

# 16.7 Temporal Information Extraction

Temporal understanding เป็นองค์ประกอบสำคัญของ LONGTUA เพราะกิจกรรมที่เหมือนกันอาจให้ผลการวางแผนต่างกันอย่างสิ้นเชิงเมื่อเวลาแตกต่างกัน

ตัวอย่าง:

> “ไปวิ่งตอนเช้า”

> “ไปวิ่งตอนเย็น”

จึงต้องแยก temporal information ออกจาก event/activity information

---

# 16.8 Event Time Extraction

Wen et al. (2021) เสนอ Event Time Extraction and Propagation via Graph Attention Networks โดยศึกษาการ grounding events ลงบน timeline และชี้ว่าข้อมูลเวลาของ event หลายกรณีไม่ได้ถูกระบุโดยตรงใน local context ของ event นั้น

แนวคิดดังกล่าวสะท้อนปัญหาใน LONGTUA เช่น:

```text
“ประชุมตอนบ่าย”
```

ไม่ได้ให้ exact time แต่ให้ semantic temporal information

ดังนั้น LONGTUA จึงแยก:

```text
EXACT_TIME
SEMANTIC_WINDOW
APPROXIMATE_TIME
UNKNOWN
AMBIGUOUS
```

แทนการบังคับให้ทุกข้อความกลายเป็น exact time

---

# 16.9 Relative Event Time

Wen and Ji (2021) ศึกษาการใช้ Relative Event Time เพื่อเพิ่มประสิทธิภาพการสกัด temporal relation ระหว่าง events และชี้ให้เห็นว่าข้อมูล event-time แบบ explicit มีอยู่ค่อนข้างจำกัด จึงต้องอาศัยความสัมพันธ์เชิงเวลาเพิ่มเติมในการ reasoning

แนวคิดนี้สนับสนุนการใช้ temporal relation เช่น:

```text
A BEFORE B
A AFTER B
```

ใน LONGTUA

ตัวอย่าง:

> “กินข้าวก่อนประชุม”

สามารถสร้าง relation:

```text
Meal BEFORE Meeting
```

แต่การตีความ relation ไม่ควรเป็นหน้าที่ของ Planning Engine

---

# 16.10 Temporal Relation Extraction

Temporal Relation Extraction มีเป้าหมายในการระบุความสัมพันธ์ด้านเวลาระหว่าง events เช่น:

- BEFORE
- AFTER
- SIMULTANEOUS / OVERLAP

งานของ Wu et al. และงานร่วมสมัยด้าน temporal relation แสดงให้เห็นว่า syntax, context และ relation ระหว่าง events มีความสำคัญต่อ temporal reasoning

งาน Extracting Temporal Event Relation with Syntax-guided Graph Transformer ของปี 2022 เสนอการใช้ syntactic dependency และ temporal cues เพื่อช่วยจำแนก temporal relations โดยเฉพาะเมื่อ events อยู่ห่างกันในข้อความ

นอกจากนี้ More than Classification: A Unified Framework for Event Temporal Relation Extraction (2023) แสดงให้เห็นว่า temporal relation extraction ไม่ควรถูกมองเพียงเป็น simple one-label classification problem เท่านั้น

---

# 16.11 Temporal Reasoning as a Separate Layer

จากงานด้าน temporal extraction สามารถสรุป design principle สำหรับ LONGTUA ได้ว่า:

```text
AI / NLP
    ↓
Extract Temporal Information
    ↓
Temporal Relations
    ↓
Validation / Normalization
    ↓
Planner
```

AI มีหน้าที่ระบุ:

> “A ก่อน B”

แต่ Planner มีหน้าที่ตัดสินว่า:

> “ดังนั้น A และ B ควรถูกจัดเวลาอย่างไรภายใต้ constraints ทั้งหมด”

นี่เป็นการแยก:

```text
Semantic Interpretation
≠
Scheduling Optimization
```

อย่างชัดเจน

---

# 16.12 Fine-Grained Event Semantics

Wang et al. (2024) ศึกษา Event Semantic Classification in Context และแบ่ง event semantics ออกเป็นหลายมิติ เช่น modality, affirmation, specificity, telicity, durativity และ kinesis

งานวิจัยพบว่าการเข้าใจ event semantics ในรายละเอียดสามารถช่วยงาน downstream อย่าง event extraction และ temporal relation extraction ได้

แนวคิดนี้มีความสำคัญกับ LONGTUA โดยเฉพาะการแยก:

```text
ACTIVITY
CONTAINER
AVAILABILITY
UNAVAILABILITY
```

เพราะข้อความที่ดูคล้ายกันอาจมี semantics แตกต่างกัน

ตัวอย่าง:

> “ทำงานวันจันทร์ถึงศุกร์ 8 โมงถึง 5 โมง”

อาจหมายถึง:

```text
AVAILABILITY
```

ขณะที่:

> “มีสัมมนาวันจันทร์ 8 โมงถึง 5 โมง”

อาจเป็น:

```text
CONTAINER / EVENT
```

ดังนั้น Object Type ไม่ควรถูกกำหนดจาก keyword อย่างเดียว

---

# 16.13 Event Relations and Dependencies

งาน EDeR: Towards Understanding Dependency Relations Between Events (2023) เสนอการศึกษาความสัมพันธ์ dependency ระหว่าง events และชี้ว่า event relations มีมากกว่าความสัมพันธ์เชิง temporal หรือ causal ที่ใช้กันโดยทั่วไป

แนวคิดนี้สนับสนุนการมี relation layer ใน LONGTUA:

```text
Temporal Relation
+
Structural Relation
+
Planning Constraint
```

แต่แต่ละประเภทต้องถูกเก็บใน model คนละ semantics

---

# 16.14 Event Timeline Datasets

TIMELINE ของ Alsayyahi และ Batista-Navarro (2023) เป็น corpus สำหรับการ annotate temporal relations อย่างละเอียด โดยมีเป้าหมายเพื่อสนับสนุนการ ordering ของ events และการประเมิน temporal relation extraction

แนวคิดจากงานนี้มีประโยชน์ต่อ LONGTUA ในด้าน:

- test dataset design
- temporal relation evaluation
- ordering evaluation
- annotation strategy

กล่าวคือ dataset สำหรับ E1 ไม่ควรมีเพียงคำสั่ง “เวลาเท่าไร” แต่ควรรวม relation ระหว่าง events ด้วย

---

# 16.15 Constraint Programming

Constraint Programming (CP) เป็นแนวทางในการค้นหา solution จาก domain ที่มีตัวเลือกจำนวนมาก โดยกำหนด constraints เพื่อจำกัด solution space

Google อธิบายว่า CP เหมาะกับปัญหาที่มีความเป็นไปได้จำนวนมากและต้องค้นหา solution ที่สอดคล้องกับ constraints จำนวนมาก รวมถึง scheduling problems

แนวคิดพื้นฐาน:

```text
Decision Variables
+
Constraints
+
Objective
=
Optimization Problem
```

LONGTUA ใช้ framework นี้เพื่อเปลี่ยน:

```text
Planning Representation
```

ไปเป็น:

```text
Feasible Schedule
```

---

# 16.16 Hard Constraints

Hard Constraint คือเงื่อนไขที่ต้องเป็นจริง

ตัวอย่าง:

```text
Activity must end before deadline
Activity must not overlap unavailable time
Fixed activity must remain at fixed time
```

เชิงแนวคิด:

```text
Hard Constraint violation
→
Invalid Solution
```

นี่เป็นสิ่งสำคัญต่อ LONGTUA เพราะระบบต้องไม่เสนอแผนที่ละเมิดเงื่อนไขสำคัญเพียงเพื่อให้ดู “เหมาะสม”

---

# 16.17 Preferences / Soft Objectives

Preferences เป็นเงื่อนไขที่ต้องการให้ระบบพยายามตอบสนอง แต่ไม่จำเป็นต้องบังคับว่าทำไม่ได้แล้ว solution ต้อง invalid เสมอ

ตัวอย่าง:

```text
Prefer morning
Prefer fewer changes
Prefer earlier completion
```

จึงเกิดความแตกต่าง:

```text
Hard Constraint
→ Must satisfy

Preference
→ Prefer to satisfy
```

งานด้าน scheduling และ interactive decision support แสดงให้เห็นว่าการจัดตารางในโลกจริงมักเกี่ยวข้องกับหลาย objective และ trade-off ไม่ใช่เพียง feasibility อย่างเดียว

---

# 16.18 Scheduling as Optimization

งานด้าน scheduling มักพิจารณา:

- activities
- time
- constraints
- resources
- objectives

งานทบทวนด้าน scheduling ระบุว่าปัญหาจัดตารางมีความซับซ้อนเพิ่มขึ้นเมื่อจำนวน activity, constraints และ objective เพิ่มขึ้น และแนวทางที่ใช้มีทั้ง constraint programming, optimization, metaheuristics และ machine learning

สำหรับ LONGTUA จึงเลือก CP-SAT เป็น technology choice ของ MVP ไม่ใช่การกล่าวว่า CP-SAT เป็นวิธีที่ดีที่สุดสำหรับ personal planning ทุกประเภท

---

# 16.19 CP-SAT

CP-SAT เป็น solver ใน OR-Tools ที่รวมแนวคิดด้าน constraint programming และ SAT-based solving

Google ระบุว่า CP-SAT ทำงานบน integer formulation และ solver สามารถคืนสถานะ เช่น:

```text
OPTIMAL
FEASIBLE
INFEASIBLE
MODEL_INVALID
UNKNOWN
```

ซึ่งเหมาะกับ architecture ของ LONGTUA ที่ต้องแยก “หา solution ได้” กับ “หาไม่ได้” อย่างชัดเจน

การออกแบบ LONGTUA จึงใช้:

```text
Integer Minutes
+
Interval Variables
+
Hard Constraints
+
Preference Objective
```

โดยไม่กำหนด fixed 15-minute slots เป็น assumption พื้นฐานของ model

---

# 16.20 Preference-aware Scheduling

งานวิจัยด้าน scheduling preference แสดงให้เห็นว่า “เวลาที่เหมาะสม” ของผู้ใช้ไม่ได้มีลักษณะเดียวทั้งหมด

Rhythm of Work (2024) ใช้ interviews, survey และข้อมูล calendar ขนาดใหญ่เพื่อศึกษาพฤติกรรมการจัดตาราง และพบ preference ที่มีทั้งแบบ cyclical เช่นความเหมาะสมของวัน/ช่วงเวลา และแบบ relational เช่นการกระจาย meetings ออกจากกัน นอกจากนี้ยังพบความแตกต่างระหว่าง preference และพฤติกรรมจริงของผู้ใช้

แนวคิดนี้สนับสนุนการที่ LONGTUA:

- แยก preference ออกจาก hard constraint
- ไม่ assume ว่าผู้ใช้ทุกคนมี preference เดียวกัน
- เปิดให้มี user-defined Time Windows
- ประเมิน preference satisfaction แยกจาก feasibility

---

# 16.21 Interactive Preference Elicitation

“I Want It That Way”: Enabling Interactive Decision Support Using Large Language Models and Constraint Programming (Lawless et al., 2024) เป็นงานที่เกี่ยวข้องกับ LONGTUA โดยตรงมาก

งานนี้ผสาน:

```text
LLM
+
Constraint Programming
+
User Interaction
```

เพื่อสนับสนุน interactive decision support ในบริบท meeting scheduling และศึกษาทั้งการ elicitation ของ preferences, system performance และ user interaction

ประเด็นสำคัญของงานคือ preference บางอย่างอาจไม่ได้มีอยู่ครบตั้งแต่ต้น แต่เกิดขึ้นหรือถูกทำให้ชัดเจนระหว่าง interaction

### ความสัมพันธ์กับ LONGTUA

LONGTUA ใช้แนวคิด:

```text
AI Proposal
    ↓
User Review
    ↓
Feedback
    ↓
Re-planning
```

แทนการพยายามกำหนด preference ทุกอย่างก่อนเริ่ม planning

อย่างไรก็ตาม LONGTUA ยังรักษาหลัก:

```text
User confirms before schedule changes
```

---

# 16.22 Human-in-the-loop Planning

Human-in-the-loop (HITL) คือแนวทางที่มนุษย์ไม่ได้ถูกลดบทบาทเหลือเพียงผู้รับ output แต่มีส่วนร่วมใน decision process

Expectation-Aware Planning ของ Sreedharan et al. (2020) ศึกษาการวางแผนในสถานการณ์ที่ expectation ของมนุษย์อาจแตกต่างจาก model ของ system และเน้นการสร้าง plans ที่สามารถอธิบายและทำงานร่วมกับมนุษย์ได้

RADAR-X (Valmeekam et al., 2021) แสดงแนวทาง interactive decision support ที่ user สามารถโต้ตอบกับ proposed plans และให้ข้อมูลหรือทางเลือกเพิ่มเติมเพื่อให้ระบบปรับข้อเสนอ

### Application to LONGTUA

หลักการเหล่านี้สนับสนุน:

```text
AI generates proposal
        ↓
Human evaluates
        ↓
Human can reject / edit / feedback
        ↓
System revises
```

ไม่ใช่:

```text
AI
 ↓
Autonomous confirmation
```

---

# 16.23 Clarification

Clarification คือการที่ระบบขอข้อมูลเพิ่มจากผู้ใช้เมื่อข้อมูลเดิมไม่เพียงพอต่อการทำงานอย่างถูกต้อง

ปัญหาหลักมี 2 ส่วน:

```text
Should the system ask?
```

และ:

```text
What should it ask?
```

งาน Where to Go for the Holidays (2022) แสดงให้เห็นว่าผู้ใช้อาจรู้เป้าหมายของตนเอง แต่ยังไม่ได้กำหนดรายละเอียดที่เพียงพอสำหรับระบบ และศึกษาการสนทนาเพื่อช่วยทำให้ user goal ชัดเจนขึ้น

Conversational Search with Mixed-Initiative (2022) ก็ศึกษา scenario ที่ user query มีความคลุมเครือหรือไม่ครบถ้วน และระบบต้องเลือก clarification ที่เหมาะสมจาก context

งาน Clarifying the Path to User Satisfaction (2024) พบว่าคำถาม clarification ที่มีความเฉพาะเจาะจงมีประโยชน์มากกว่าคำถามกว้าง ๆ และ query ที่สั้นหรือกำกวมได้รับประโยชน์จาก clarification มากกว่า

---

# 16.24 Clarification Policy in LONGTUA

จากแนวคิดเหล่านี้ LONGTUA จึงไม่ใช้:

```text
Missing field
→
Always ask
```

แต่ใช้:

```text
Missing / Ambiguous
        ↓
Does it affect interpretation?
        ↓
Does it affect planning?
        ↓
Yes → Ask
No  → Continue
```

ตัวอย่าง:

### Case A

> “พรุ่งนี้ซื้อของขวัญ”

ยังสามารถเก็บเป็น date-only Activity ได้

### Case B

> “พรุ่งนี้ 6 โมงไปวิ่ง”

หาก context ไม่สามารถบอกได้ว่าเป็น 06:00 หรือ 18:00 และมีผลต่อ planning:

```text
→ Clarification
```

นี่เป็น core behavior ของ LONGTUA

---

# 16.25 Re-planning / Reactive Scheduling

Planning ในโลกจริงไม่ได้จบเมื่อสร้าง schedule ครั้งแรก เพราะข้อมูลสามารถเปลี่ยนได้

เช่น:

```text
Meeting moved
Duration changed
New activity
Unavailable period added
Activity cancelled
User changes preference
```

จึงเกิดปัญหา:

```text
Original Schedule
      ↓
New Information
      ↓
Re-planning
```

งานวิจัยด้าน rescheduling ชี้ว่า schedule ที่มีอยู่สามารถต้องถูกปรับเมื่อเกิด disturbance หรือข้อมูลใหม่ และความท้าทายสำคัญคือการหาสมดุลระหว่างการตอบสนองต่อการเปลี่ยนแปลงกับความต่อเนื่องของ schedule เดิม

---

# 16.26 Stability during Re-planning

การสร้าง schedule ใหม่ทั้งหมดโดยไม่สนใจ schedule เดิมอาจทำให้เกิดการเปลี่ยนแปลงมากเกินไป

ดังนั้น LONGTUA ใช้:

```text
Stability Objective
```

ใน Re-planning

Operational measure:

```text
D = Σ |s_new(i) - s_old(i)|
```

โดยมีเป้าหมายเพื่อลด unnecessary changes

แต่ stability ไม่สามารถ override:

```text
Hard Constraint
หรือ
New Explicit User Requirement
```

---

# 16.27 Re-planning as a Multi-objective Problem

งานด้าน multi-objective rescheduling ชี้ว่าการปรับ schedule มักต้องพิจารณา objective หลายตัวพร้อมกัน เช่น efficiency, quality, disturbance และ human factors

ดังนั้น LONGTUA ใช้ลำดับ:

```text
1. Hard Feasibility
2. Explicit User Requirements
3. Preferences
4. Stability
5. Optional Activities
```

เพื่อป้องกันการตีความว่า “รักษาตารางเดิมไว้” สำคัญกว่าความต้องการใหม่ของผู้ใช้

---

# 16.28 Planning Window / Bounded Re-planning

งานด้าน rescheduling ระบุว่าขนาดของ problem และ horizon มีผลต่อความซับซ้อนและ computational cost ของ scheduling

LONGTUA จึงไม่ได้ re-plan timeline แบบไม่มีขอบเขต แต่ใช้:

```text
Affected Context
+
Bounded Planning Horizon
```

เพื่อควบคุม problem size

วิธีนี้ช่วยให้ MVP สามารถใช้ full model rebuild + re-solve ได้โดยยังคงมี practical boundary ที่สามารถ benchmark ได้

---

# 16.29 Structured Event-to-Plan Pipeline

จากงานวิจัยทั้งหมดข้างต้น สามารถสรุป theoretical pipeline ที่ LONGTUA ใช้ได้เป็น:

```text
Natural Language
        ↓
Event / Activity Extraction
        ↓
Temporal Understanding
        ↓
Relation Extraction
        ↓
Ambiguity / Missing Information
        ↓
Structured Output
        ↓
Validation / Normalization
        ↓
Planning Representation
        ↓
Constraint-based Planning
        ↓
Proposal
        ↓
Human Review
        ↓
Confirmed Schedule
```

จุดสำคัญคือการไม่รวมทุกอย่างไว้ใน LLM ตัวเดียว

---

# 16.30 Related Research Summary

ตารางต่อไปนี้สรุปงานวิจัยหลักที่มีความสัมพันธ์กับ LONGTUA

| งานวิจัย                                          |   ปี | ประเด็นหลัก                  | สิ่งที่ LONGTUA นำมาใช้               |
| ------------------------------------------------- | ---: | ---------------------------- | ------------------------------------- |
| Event Extraction as Machine Reading Comprehension | 2020 | Event Extraction             | Structured event understanding        |
| Expectation-Aware Planning                        | 2020 | Human-aware planning         | Human expectation / HITL              |
| Text2Event                                        | 2021 | Event-to-structure           | Structured activity extraction        |
| Event Time Extraction and Propagation             | 2021 | Event time                   | Temporal grounding                    |
| Relative Event Time                               | 2021 | Temporal relation            | Relative time reasoning               |
| RADAR-X                                           | 2021 | Interactive planning         | Proposal + interaction                |
| Extracting Temporal Event Relation with SGT       | 2022 | Temporal relations           | Relation extraction                   |
| Mixed-Type Dialogs for Clarification              | 2022 | Clarification                | Ask user when needed                  |
| Conversational Search with Mixed-Initiative       | 2022 | Clarification                | Context-aware clarification           |
| LEAF                                              | 2023 | Event temporal relations     | Rich temporal reasoning               |
| TIMELINE                                          | 2023 | Temporal dataset             | Evaluation dataset concepts           |
| EDeR                                              | 2023 | Event dependency             | Event relation modeling               |
| Code4Struct                                       | 2023 | Structured LLM output        | Structured representation             |
| Event Semantic Classification in Context          | 2024 | Fine-grained event semantics | Object / event interpretation         |
| Chaining Event Spans                              | 2024 | Temporal grounding           | Temporal relation understanding       |
| ChatUIE                                           | 2024 | LLM Information Extraction   | Unified structured extraction         |
| Learning to Extract Structured Entities           | 2024 | Structured entity extraction | Schema-based extraction               |
| Clarifying the Path to User Satisfaction          | 2024 | Clarification                | Specific targeted questions           |
| I Want It That Way                                | 2024 | LLM + CP + interaction       | Interactive preference-aware planning |
| Rhythm of Work                                    | 2024 | Scheduling preferences       | User preference modeling              |

---

# 16.31 Research Gap Positioning

จากการทบทวนงานที่เกี่ยวข้อง ไม่ควรกล่าวว่า:

> “ไม่มีงานวิจัยใดทำ intelligent scheduling มาก่อน”

เพราะมีงานเกี่ยวกับ event extraction, scheduling, interactive decision support, preference modeling และ rescheduling อยู่แล้ว

Research gap ของ LONGTUA จึงควรวางเป็น **integration and context gap**

กล่าวคือ:

```text
Existing Research
├── NLP / Event Extraction
├── Temporal Understanding
├── Constraint Scheduling
├── Preference-aware Planning
├── Re-planning
└── Human-in-the-loop
```

แต่ LONGTUA มุ่งรวมองค์ประกอบเหล่านี้ไว้ใน workflow เดียวสำหรับ personal planning:

```text
Natural Language
        ↓
Structured Planning Information
        ↓
Constraint-based Planning
        ↓
Interactive Proposal
        ↓
User Feedback
        ↓
Adaptive Re-planning
```

ดังนั้น contribution ไม่ใช่การเสนอ scheduling algorithm ใหม่ทั้งหมด แต่เป็น:

```text
Integration
+
System Architecture
+
Human-in-the-loop Workflow
+
Adaptive Re-planning
+
Empirical Evaluation
```

---

# 16.32 Research Positioning against “I Want It That Way”

งาน “I Want It That Way” เป็นหนึ่งในงานที่ใกล้ LONGTUA มากที่สุด เพราะรวม LLM และ Constraint Programming เข้าด้วยกัน และใช้ interaction เพื่อ elicitation preferences

อย่างไรก็ตาม LONGTUA มีจุดเน้นที่ต่างกัน:

| Dimension         | I Want It That Way                       | LONGTUA                               |
| ----------------- | ---------------------------------------- | ------------------------------------- |
| Primary context   | Meeting scheduling                       | General personal planning             |
| NLP input         | User interaction / preference expression | Natural-language planning input       |
| Planning          | Constraint Programming                   | CP-SAT                                |
| Preferences       | Interactive elicitation                  | Explicit preferences + feedback       |
| Clarification     | Interaction-driven                       | Ambiguity / necessity-driven          |
| Re-planning       | Interactive revision                     | Change-triggered adaptive re-planning |
| Schedule state    | Decision support                         | Proposal / Draft / Confirmed Version  |
| User confirmation | Interactive                              | Required before schedule change       |
| Notification      | Not core focus                           | Local notification synchronization    |
| Calendar          | Scheduling context                       | Internal personal planner             |

ดังนั้นงานดังกล่าวเป็นทั้ง **related work และ conceptual support** สำหรับ architecture ของ LONGTUA แต่ไม่ได้หมายความว่า LONGTUA เป็นการทำซ้ำงานนั้น

---

# 16.33 Case Study 1 — Apple Calendar

Apple Calendar เป็นตัวอย่างของ traditional calendar-centered interaction

บน iPhone ผู้ใช้สามารถสร้าง event โดยกำหนด title, location, start/end time, invitees และรายละเอียดอื่น ๆ และสามารถกำหนด alert ก่อน event ได้ นอกจากนี้ Calendar รองรับการแก้ start/end time โดยตรงจาก calendar view

Apple ยังมี default alert settings และ event-level alert customization รวมถึง time-zone handling ใน Calendar

### จุดเด่น

- calendar-centric
- mature event management
- notification
- manual editing
- integration กับ ecosystem

### ข้อจำกัดเมื่อเทียบกับ LONGTUA

การใช้งานพื้นฐานยังมี model ที่ผู้ใช้ต้องกำหนด event ผ่าน calendar interface โดยตรง แม้ Apple จะมี AI-assisted suggestions ใน ecosystem รุ่นใหม่บางส่วนแล้ว

LONGTUA เน้น:

```text
Natural Language
→
Planning
```

มากกว่า:

```text
Form
→
Calendar Event
```

---

# 16.34 Case Study 2 — Google Calendar

Google Calendar รองรับ:

- event management
- tasks
- reminders / notifications
- working hours
- multiple calendars
- sharing
- appointment scheduling

และ Google ปัจจุบันมีความสามารถ AI ในบาง Workspace scenarios เช่นช่วยหาเวลานัดจาก email context และ Calendar

Google Calendar ยังแยก calendar-level notification settings กับ event-level customization

### ความสัมพันธ์กับ LONGTUA

Google Calendar เป็น baseline ที่ดีสำหรับ:

- Calendar UX
- notifications
- date/time representation
- task/calendar interaction

แต่ LONGTUA ตั้งใจให้ planning workflow เป็นระบบของตัวเอง ไม่พึ่ง external calendar synchronization ใน MVP

---

# 16.35 Case Study 3 — Notion Calendar

Notion Calendar เน้นการรวม:

```text
Calendar
+
Tasks / Databases
+
Scheduling
+
Availability
```

และมี scheduling links ทั้งแบบ one-off และ recurring พร้อมกำหนด availability ได้

Notion Calendar ยังสนับสนุนการเชื่อมข้อมูล database กับ calendar และการรวมหลาย calendar accounts

### ความสัมพันธ์กับ LONGTUA

Notion เป็นตัวอย่างของการลด context switching โดยรวมข้อมูล planning และ calendar เข้าไว้ด้วยกัน

แต่ LONGTUA เน้นเพิ่มเติมที่:

```text
Natural Language
+
Constraint-based scheduling
+
Proposal
+
Re-planning
```

แทนที่จะเน้น integration กับ productivity workspace

---

# 16.36 Case Study 4 — Reclaim

Reclaim เป็นกรณีศึกษาที่ใกล้กับ concept ของ adaptive scheduling มาก

ระบบมี:

- Tasks
- Habits
- Smart Meetings
- Priorities
- Availability
- automatic scheduling
- automatic rescheduling
- scheduling rules

Reclaim ระบุว่าสามารถ auto-schedule และ reschedule events ตาม priorities, deadlines, availability และ scheduling rules ได้

ระบบยังรองรับ priority levels และใช้ priority เพื่อกำหนด trade-off เมื่อ calendar มีข้อจำกัด

### ความเหมือนกับ LONGTUA

```text
Availability
+
Priority
+
Deadline
+
Adaptive scheduling
```

### ความแตกต่างสำคัญ

Reclaim เน้นการ **automatic schedule management**

ขณะที่ LONGTUA ใช้:

```text
System Proposal
      ↓
Human Review
      ↓
Confirmation
```

เพื่อให้ user เป็น final decision-maker

---

# 16.37 Case Study 5 — Motion

Motion เป็นอีกระบบที่แสดงแนวคิด AI scheduling อย่างชัดเจน

ระบบระบุว่าสามารถ:

- prioritize tasks
- schedule based on deadlines
- duration
- priorities
- dependencies
- custom time windows
- automatically re-plan เมื่อ schedule เปลี่ยน

ได้

Motion ยังมี meeting scheduling ที่คำนึงถึง preferred meeting windows และ availability

### ความเหมือนกับ LONGTUA

```text
Task
+
Deadline
+
Duration
+
Priority
+
Availability
+
Replanning
```

### ความแตกต่าง

Motion เน้น automatic execution และ continuous re-optimization

LONGTUA เน้น:

```text
Understand user intent
→
Generate proposal
→
User review
→
Confirm
```

ซึ่งเหมาะกับ research focus ด้าน Human-in-the-loop

---

# 16.38 Case Study 6 — Research Prototype: RADAR-X

RADAR-X เป็นตัวอย่างของ interactive decision support ที่ให้ผู้ใช้โต้ตอบกับ proposed plan และใช้ interaction เพื่อปรับ plan และ elicitation of preferences

แนวคิดนี้ใกล้กับ LONGTUA ในส่วน:

```text
Proposed Plan
+
User Feedback
+
Revised Plan
```

จึงเป็น reference สำคัญสำหรับ:

- proposal UI
- feedback
- explanation
- revised plans

---

# 16.39 Case Study 7 — LLM + Constraint Programming

“I Want It That Way” เป็นกรณีศึกษาที่สำคัญที่สุดด้าน architecture

ระบบรวม:

```text
LLM
+
Constraint Programming
+
Preference Elicitation
+
Interactive Decision Support
```

และใช้ meeting scheduling เป็น experimental domain

งานนี้ช่วยสนับสนุนแนวคิดของ LONGTUA ว่า LLM และ optimizer ไม่จำเป็นต้องเป็น component เดียวกัน แต่สามารถมีบทบาทต่างกัน:

```text
LLM
→
Understand User

Constraint Programming
→
Compute Feasible / Preferred Plan
```

ซึ่งตรงกับ architecture principle ของ LONGTUA

---

# 16.40 Comparative Case Study

| System             |   Natural Language | Constraint Planning | Auto Re-plan | User Proposal/Review |  Internal Calendar | Notifications |
| ------------------ | -----------------: | ------------------: | -----------: | -------------------: | -----------------: | ------------: |
| Apple Calendar     | Partial / assisted |             Limited |      Limited |                    ✕ |                  ✓ |             ✓ |
| Google Calendar    | Partial / assisted |             Limited |      Limited |                    ✕ |                  ✓ |             ✓ |
| Notion Calendar    |            Limited |             Limited |      Limited |                    ✕ |                  ✓ |             ✓ |
| Reclaim            |                  ✓ |                   ✓ |            ✓ |              Limited |   ✓ / integrations |             ✓ |
| Motion             |                  ✓ |                   ✓ |            ✓ |              Limited |   ✓ / integrations |             ✓ |
| RADAR-X            |                  ✓ |                   ✓ |  Interactive |                    ✓ | Research prototype |      Not core |
| I Want It That Way |                  ✓ |                   ✓ |  Interactive |                    ✓ | Research prototype |      Not core |
| **LONGTUA**        |              **✓** |               **✓** |        **✓** |       **✓ Required** |              **✓** |   **✓ Local** |

ตารางนี้ไม่ได้มีวัตถุประสงค์เพื่อประกาศว่า LONGTUA “เหนือกว่า” ทุกระบบ แต่เพื่อแสดง **positioning ของระบบแต่ละประเภท**

---

# 16.41 Research-to-Design Traceability

| Research / Theory            | LONGTUA Design                        |
| ---------------------------- | ------------------------------------- |
| Event Extraction             | AI Activity/Event Detection           |
| Structured IE                | Planning Schema                       |
| Temporal Extraction          | Time / Duration / Temporal Relation   |
| Event Semantics              | Activity vs Container vs Availability |
| Constraint Programming       | CP-SAT Planning                       |
| Preference-aware Scheduling  | Preference Objective                  |
| Reactive Scheduling          | Re-planning                           |
| Schedule Stability           | Stability Objective                   |
| Human-in-the-loop            | Proposal + Confirmation               |
| Clarification Research       | Targeted Clarification                |
| Interactive Decision Support | Feedback + Revised Proposal           |
| Calendar Systems             | Calendar View / Notification          |
| Structured Evaluation        | E1–E6                                 |

---

# 16.42 Research Support for LONGTUA Architecture

งานวิจัยที่ทบทวนสนับสนุน architecture separation ดังนี้:

```text
              USER
                ↓
        Natural Language
                ↓
             AI/NLP
                ↓
     Structured Representation
                ↓
       Validation / Normalization
                ↓
       Constraint Planning
                ↓
            Proposal
                ↓
          Human Review
          /     |     \
      Confirm Reject Feedback
          ↓            ↓
      Schedule     Re-planning
          ↓
     Notification
```

เหตุผลของการแยก layer:

### AI/NLP

เพราะ natural-language understanding และ structured information extraction เป็น problem domain ของ NLP

### Planning Engine

เพราะ scheduling เป็น constraint/optimization problem ที่มี decision variables, constraints และ objectives

### Human Review

เพราะงาน interactive planning และ decision support แสดงประโยชน์จากการให้มนุษย์มีส่วนร่วมในการประเมินและปรับ decision

---

# 16.43 Research Support for Evaluation

การประเมิน LONGTUA จึงไม่ควรวัดเพียง “ระบบเปิดแอปได้หรือไม่”

แต่ควรแบ่งเป็น:

```text
E1 NLP
E2 Planning
E3 Re-planning
E4 Candidate
E5 HITL
E6 End-to-End
```

เพราะความถูกต้องของแต่ละ layer มีความหมายแตกต่างกัน

ตัวอย่าง:

```text
AI extraction ถูกต้อง
≠
Schedule feasible

Schedule feasible
≠
User satisfied

User satisfied
≠
System performant
```

จึงต้องประเมินแยกตาม research question

---

# 16.44 Final Research Position

จาก literature review นี้ LONGTUA สามารถวางตำแหน่งได้ว่า:

> **LONGTUA เป็นระบบ Personal Adaptive Planner ที่บูรณาการ Natural Language Understanding, Structured Planning Representation, Constraint-based Scheduling, Human-in-the-loop Decision Making และ Adaptive Re-planning เข้าเป็น workflow เดียวสำหรับ personal planning**

Research contribution จึงเน้น:

```text
1. Integrated System Design
2. Natural Language → Planning Representation
3. Constraint-based Personal Planning
4. Human-in-the-loop Proposal Workflow
5. Adaptive Re-planning
6. Empirical Evaluation
```

ไม่อ้างว่า:

```text
“เป็นระบบแรก”
“เป็น algorithm ใหม่”
“ดีที่สุด”
“แก้ปัญหา personal planning ได้ทั้งหมด”
```

---

# 16.45 Reference List — Academic Research

## [R01] Liu et al. (2020)

**Liu, J., Chen, Y., Liu, K., Bi, W., & Liu, X. (2020).**
_Event Extraction as Machine Reading Comprehension._
Proceedings of EMNLP 2020, 1641–1651.

[ACL Anthology / Paper](https://aclanthology.org/2020.emnlp-main.128/?utm_source=chatgpt.com)
[PDF](https://aclanthology.org/2020.emnlp-main.128.pdf?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Event Extraction, structured event understanding, AI/NLP layer

---

## [R02] Sreedharan et al. (2020)

**Sreedharan, S., Chakraborti, T., Muise, C., & Kambhampati, S. (2020).**
_Expectation-Aware Planning: A Unifying Framework for Synthesizing and Executing Self-Explaining Plans for Human-Aware Planning._
Proceedings of the AAAI Conference on Artificial Intelligence, 34(03), 2518–2526.

[AAAI Paper](https://ojs.aaai.org/index.php/AAAI/article/view/5634?utm_source=chatgpt.com)
[DOI](https://doi.org/10.1609/aaai.v34i03.5634?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Human-aware planning, human expectations, interactive planning

---

## [R03] Lu et al. (2021)

**Lu, Y., Lin, H., Xu, J., Han, X., Tang, J., Li, A., Sun, L., Liao, M., & Chen, S. (2021).**
_Text2Event: Controllable Sequence-to-Structure Generation for End-to-end Event Extraction._
ACL-IJCNLP 2021, 2795–2806.

[ACL Anthology / Paper](https://aclanthology.org/2021.acl-long.217/?utm_source=chatgpt.com)
[PDF](https://aclanthology.org/2021.acl-long.217.pdf?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Event-to-structure transformation

---

## [R04] Wen et al. (2021)

**Wen, H., Qu, Y., Ji, H., Ning, Q., Han, J., Sil, A., Tong, H., & Roth, D. (2021).**
_Event Time Extraction and Propagation via Graph Attention Networks._
NAACL-HLT 2021, 62–73.

[ACL Anthology / Paper](https://aclanthology.org/2021.naacl-main.6/?utm_source=chatgpt.com)
[PDF](https://aclanthology.org/2021.naacl-main.6.pdf?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Event-time extraction, temporal grounding

---

## [R05] Wen & Ji (2021)

**Wen, H., & Ji, H. (2021).**
_Utilizing Relative Event Time to Enhance Event-Event Temporal Relation Extraction._
EMNLP 2021, 10431–10437.

[ACL Anthology / Paper](https://aclanthology.org/2021.emnlp-main.815/?utm_source=chatgpt.com)
[PDF](https://aclanthology.org/2021.emnlp-main.815.pdf?utm_source=chatgpt.com)
[DOI](https://doi.org/10.18653/v1/2021.emnlp-main.815?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Relative temporal reasoning

---

## [R06] Valmeekam et al. (2021)

**Valmeekam, K., Sreedharan, S., Sengupta, S., & Kambhampati, S. (2021).**
_RADAR-X: An Interactive Interface Pairing Contrastive Explanations with Revised Plan Suggestions._
AAAI 2021.

[AAAI Paper](https://ojs.aaai.org/index.php/AAAI/article/view/18009?utm_source=chatgpt.com)
[DOI](https://doi.org/10.1609/aaai.v35i18.18009?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Interactive planning, revised plan suggestions, user feedback

---

## [R07] Lu et al. / Related temporal relation research (2022)

**Extracting Temporal Event Relation with Syntax-guided Graph Transformer. (2022).**
Findings of NAACL 2022.

[ACL Anthology / Paper](https://aclanthology.org/2022.findings-naacl.29/?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Temporal relation extraction, syntactic context

---

## [R08] Liu et al. (2022)

**Liu, Z., Xu, J., Lei, Z., Wang, H., Niu, Z.-Y., & Wu, H. (2022).**
_Where to Go for the Holidays: Towards Mixed-Type Dialogs for Clarification of User Goals._
ACL 2022, 1024–1034.

[ACL Anthology / Paper](https://aclanthology.org/2022.acl-long.73/?utm_source=chatgpt.com)
[PDF](https://aclanthology.org/2022.acl-long.73.pdf?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Clarification, mixed-initiative dialogue

---

## [R09] Lim et al. (2023)

**Lim, S., Yin, D., & Peng, N. (2023).**
_LEAF: Linguistically Enhanced Event Temporal Relation Framework._

[ACL Anthology / Paper](https://aclanthology.org/2023.pandl-1.2/?utm_source=chatgpt.com)
[PDF](https://aclanthology.org/2023.pandl-1.2.pdf?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Linguistic temporal relations and compositional temporal reasoning

---

## [R10] Alsayyahi & Batista-Navarro (2023)

**Alsayyahi, S., & Batista-Navarro, R. (2023).**
_TIMELINE: Exhaustive Annotation of Temporal Relations Supporting the Automatic Ordering of Events in News Articles._
EMNLP 2023, 16336–16348.

[ACL Anthology / Paper](https://aclanthology.org/2023.emnlp-main.1016/?utm_source=chatgpt.com)
[PDF](https://aclanthology.org/2023.emnlp-main.1016.pdf?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Temporal evaluation and annotation

---

## [R11] Li et al. (2023)

**Li, R., Haslum, P., & Cui, L. (2023).**
_EDeR: Towards Understanding Dependency Relations Between Events._
EMNLP 2023.

[ACL Anthology / Paper](https://aclanthology.org/2023.emnlp-main.926/?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Event dependency relations

---

## [R12] Wang et al. (2023)

**Wang, X., Li, S., & Ji, H. (2023).**
_Code4Struct: Code Generation for Few-Shot Event Structure Prediction._
ACL 2023.

[ACL Anthology / Paper](https://aclanthology.org/2023.acl-long.202/?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Structured representation with LLMs

---

## [R13] Wang et al. (2024)

**Wang, H., Zhang, H., Song, K., Yu, D., & Roth, D. (2024).**
_Event Semantic Classification in Context._
Findings of EACL 2024, 1395–1407.

[ACL Anthology / Paper](https://aclanthology.org/2024.findings-eacl.94/?utm_source=chatgpt.com)
[PDF](https://aclanthology.org/2024.findings-eacl.94.pdf?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Fine-grained event semantics

---

## [R14] Kim et al. (2024)

**Kim, J., Lee, D., Kim, M., & Hwang, S.-W. (2024).**
_Chaining Event Spans for Temporal Relation Grounding._
EACL 2024.

[ACL Anthology / Paper](https://aclanthology.org/2024.eacl-long.101/?utm_source=chatgpt.com)
[PDF](https://aclanthology.org/2024.eacl-long.101.pdf?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Temporal relation grounding

---

## [R15] Xu et al. (2024)

**Xu, J., Sun, M., Zhang, Z., & Zhou, J. (2024).**
_ChatUIE: Exploring Chat-based Unified Information Extraction Using Large Language Models._

[ACL Anthology / Paper](https://aclanthology.org/2024.lrec-main.279/?utm_source=chatgpt.com)
[PDF](https://aclanthology.org/2024.lrec-main.279.pdf?utm_source=chatgpt.com)

**ใช้สนับสนุน:** LLM-based unified information extraction

---

## [R16] Wu et al. (2024)

**Wu, H., Yuan, Y., Mikaelyan, L., Meulemans, A., Liu, X., Hensman, J., & Mitra, B. (2024).**
_Learning to Extract Structured Entities Using Language Models._
EMNLP 2024, 6817–6834.

[ACL Anthology / Paper](https://aclanthology.org/2024.emnlp-main.388/?utm_source=chatgpt.com)
[PDF](https://aclanthology.org/2024.emnlp-main.388.pdf?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Structured entity extraction

---

## [R17] Li et al. (2024)

**Li, Y., Ramprasad, R., & Zhang, C. (2024).**
_A Simple but Effective Approach to Improve Structured Language Model Output for Information Extraction._
Findings of EMNLP 2024.

[ACL Anthology / Paper](https://aclanthology.org/2024.findings-emnlp.295/?utm_source=chatgpt.com)
[PDF](https://aclanthology.org/2024.findings-emnlp.295.pdf?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Structured LLM output and schema reliability

---

## [R18] Rahmani et al. (2024)

**Rahmani, H. A., Wang, X., Aliannejadi, M., Naghiaei, M., & Yilmaz, E. (2024).**
_Clarifying the Path to User Satisfaction: An Investigation into Clarification Usefulness._
Findings of EACL 2024, 1266–1277.

[ACL Anthology / Paper](https://aclanthology.org/2024.findings-eacl.84/?utm_source=chatgpt.com)
[PDF](https://aclanthology.org/2024.findings-eacl.84.pdf?utm_source=chatgpt.com)
[DOI](https://doi.org/10.18653/v1/2024.findings-eacl.84?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Clarification strategy and user satisfaction

---

## [R19] Lawless et al. (2024)

**Lawless, C., Schoeffer, J., Le, L., Rowan, K., Sen, S., St. Hill, C., Suh, J., & Sarrafzadeh, B. (2024).**
_“I Want It That Way”: Enabling Interactive Decision Support Using Large Language Models and Constraint Programming._
ACM Transactions on Interactive Intelligent Systems, 14(3), Article 22.

[Microsoft Research / Publication](https://www.microsoft.com/en-us/research/publication/i-want-it-that-way-enabling-interactive-decision-support-using-large-language-models-and-constraint-programming/?utm_source=chatgpt.com)
[arXiv](https://arxiv.org/abs/2312.06908?utm_source=chatgpt.com)
[DOI](https://doi.org/10.1145/3685053?utm_source=chatgpt.com)

**ใช้สนับสนุน:** LLM + Constraint Programming + interactive preference elicitation

---

## [R20] Sun et al. (2024)

**Sun, L., Mok, L., Sen, S., & Sarrafzadeh, B. (2024).**
_Rhythm of Work: Mixed-methods Characterization of Information Workers Scheduling Preferences and Practices._
Proceedings of the ACM on Human-Computer Interaction, 8(CSCW2), Article 356.

[ACM / Paper](https://doi.org/10.1145/3686895?utm_source=chatgpt.com)
[Microsoft Research](https://www.microsoft.com/en-us/research/publication/rhythm-of-work-mixed-methods-characterization-of-information-workers-scheduling-preferences-and-practices/?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Scheduling preferences, temporal preference patterns, user-centered scheduling

---

## [R21] Zhan et al. (2024)

**Zhan, S., Xie, J., Wong, S. C., Zhu, Y., & Corman, F. (2024).**
_Handling uncertainty in train timetable rescheduling: A review of the literature and future research directions._
Transportation Research Part E, 183, Article 103429.

[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S136655452400019X?utm_source=chatgpt.com)
[DOI](https://doi.org/10.1016/j.tre.2024.103429?utm_source=chatgpt.com)
[TU Delft Research Portal](https://research.tudelft.nl/en/publications/handling-uncertainty-in-train-timetable-rescheduling-a-review-of-/?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Rescheduling under changing conditions and uncertainty

---

## [R22] Nurmi & Kyngäs (2021)

**Nurmi, K., & Kyngäs, N. (2021).**
_A Successful Three-Phase Metaheuristic for the Shift Minimization Personal Task Scheduling Problem._
Advances in Operations Research.

[Wiley / Paper](https://onlinelibrary.wiley.com/doi/10.1155/2021/8876990?utm_source=chatgpt.com)
[DOI](https://doi.org/10.1155/2021/8876990?utm_source=chatgpt.com)

**ใช้สนับสนุน:** Task scheduling, scheduling complexity, optimization evaluation

---

# 16.46 Reference List — Technical Foundations

## [T01] Google OR-Tools

**Google for Developers.**
_Constraint Optimization / CP-SAT Solver._

[Constraint Optimization](https://developers.google.com/optimization/cp?utm_source=chatgpt.com)
[CP-SAT Solver](https://developers.google.com/optimization/cp/cp_solver/?utm_source=chatgpt.com)

**ใช้สนับสนุน:** CP, CP-SAT, scheduling model, solver status

---

# 16.47 Reference List — Case Study Sources

> แหล่งในส่วนนี้ไม่ถูกนับเป็น “academic paper” แต่ใช้เป็น **primary source สำหรับศึกษาระบบที่มีอยู่จริง**

## [C01] Apple Calendar

Apple Support.
_Create and edit events in Calendar on iPhone._

[Apple Support](https://support.apple.com/en-gb/guide/iphone/iph3d110f84/27/ios/27?utm_source=chatgpt.com)

Apple Support.
_Change your Calendar settings on iPhone._

[Apple Support](https://support.apple.com/en-gb/guide/iphone/iphc37be2016/26/ios/26?utm_source=chatgpt.com)

---

## [C02] Google Calendar

Google Workspace.
_Google Calendar — Shareable Online Calendar and Scheduling._

[Google Calendar](https://workspace.google.com/products/calendar/?utm_source=chatgpt.com)

Google Calendar Help.
_Change Google Calendar notifications._

[Google Calendar Help](https://support.google.com/calendar/answer/37242?utm_source=chatgpt.com)

---

## [C03] Notion Calendar

Notion.
_Notion Calendar._

[Notion Calendar](https://www.notion.com/th/product/calendar?utm_source=chatgpt.com)

Notion Help.
_Scheduling & availability in Notion Calendar._

[Notion Help](https://www.notion.com/help/availability-blocking-and-time-zones?utm_source=chatgpt.com)

---

## [C04] Reclaim

Reclaim Help Center.
_How Reclaim manages your schedule automatically._

[Reclaim Documentation](https://help.reclaim.ai/en/articles/6207587-how-reclaim-manages-your-schedule-automatically?utm_source=chatgpt.com)

Reclaim Help Center.
_How Reclaim uses Priorities to intelligently plan your workweek._

[Reclaim Documentation](https://help.reclaim.ai/en/articles/8291694-how-reclaim-uses-priorities-to-intelligently-plan-your-workweek?utm_source=chatgpt.com)

---

## [C05] Motion

Motion.
_AI Calendar._

[Motion AI Calendar](https://www.usemotion.com/features/ai-calendar?utm_source=chatgpt.com)

Motion.
_AI Task Manager._

[Motion AI Task Manager](https://www.usemotion.com/features/ai-task-manager?utm_source=chatgpt.com)

Motion.
_AI Meeting Assistant._

[Motion AI Meeting Assistant](https://www.usemotion.com/features/ai-meeting-assistant?utm_source=chatgpt.com)

---

# 16.48 Citation Usage Map

เพื่อไม่ให้ references กลายเป็นเพียงรายการท้ายเอกสาร แต่เชื่อมกับ design ทั้ง project ให้ใช้ citation ตาม mapping:

| Project Document          | Main References                                                 |
| ------------------------- | --------------------------------------------------------------- |
| Project Overview          | C01–C05, R19–R20                                                |
| Requirements              | R18–R20                                                         |
| System Architecture       | R01, R15–R19, T01                                               |
| Domain & Planning Model   | R03–R05, R13–R15                                                |
| AI / NLP Design           | R01, R03, R12, R15–R17                                          |
| Planning Engine           | T01, R19, R22                                                   |
| Replanning                | R19–R21                                                         |
| Schedule & Notification   | C01, C02, R20                                                   |
| Database Design           | Mainly system design; limited direct research citation required |
| API Design                | Mainly engineering design                                       |
| Security Design           | Mainly security standards / implementation references           |
| UI / UX Behavior          | R06, R18–R20, C01–C05                                           |
| Testing & Evaluation      | R10, R20–R22                                                    |
| Limitations & Future Work | R19–R21                                                         |

---

# 16.49 Recommended Citation Placement

ไม่จำเป็นต้องใส่ citation ทุกประโยค

ควรใส่เมื่อ:

- กล่าวถึงผลจากงานวิจัย
- กล่าวถึงข้อค้นพบของ paper
- กล่าวถึง methodology ของงานอื่น
- อ้างข้อมูลเชิงประจักษ์
- ใช้ผลวิจัยสนับสนุน design decision

ตัวอย่าง:

> LONGTUA ใช้ targeted clarification แทนการถามทุกข้อมูลที่ขาด เนื่องจากงานด้าน clarification พบว่าคำถามที่เฉพาะเจาะจงและตรงกับ ambiguity มีประโยชน์มากกว่า generic clarification

ไม่จำเป็นต้องใส่ citation เมื่ออธิบาย:

> LONGTUA มี endpoint `/api/proposals/{id}/confirm`

เพราะเป็น implementation decision ของ project เอง

---

# 16.50 Important Interpretation Rule

การอ้างอิงงานวิจัยต้องแยก:

```text
Paper says X
```

ออกจาก:

```text
LONGTUA therefore chooses Y
```

ตัวอย่าง:

```text
Research:
Clarification ที่เฉพาะเจาะจงมีประโยชน์กว่า generic clarification

LONGTUA Design:
ถามผู้ใช้ว่า “6 โมงเช้าหรือ 6 โมงเย็น?”
แทนที่จะถามว่า “กรุณาระบุเวลาเพิ่มเติม”
```

อย่างหลังเป็น **project design decision ที่ได้รับแรงสนับสนุนจาก research** ไม่ใช่ claim ว่า paper ออกแบบ LONGTUA

---

# 16.51 Avoided Research Claims

เพื่อรักษาความถูกต้องทางวิชาการ ไม่ควรใช้ถ้อยคำเช่น:

> “จากการวิจัยพบว่า CP-SAT เป็น algorithm ที่ดีที่สุดสำหรับ personal planning”

เพราะหลักฐานที่มีไม่ได้รองรับ claim ดังกล่าว

ควรใช้:

> “LONGTUA เลือก CP-SAT เป็น solver สำหรับ MVP เนื่องจากสามารถ model constraint-based scheduling และ optimization ในรูปแบบที่สอดคล้องกับ planning model ของระบบ”

---

ไม่ควรใช้:

> “LONGTUA เป็นระบบแรกที่รวม LLM กับ scheduling”

เพราะมีงานวิจัยก่อนหน้า เช่น Lawless et al. (2024) ที่รวม LLM กับ Constraint Programming ใน interactive decision support และ meeting scheduling แล้ว

ควรใช้:

> “LONGTUA มุ่งศึกษาการบูรณาการ Natural Language Understanding, constraint-based personal planning, human-in-the-loop และ adaptive re-planning ในบริบทของ personal planning”

---

# 16.52 Overall Literature Structure

ภาพรวมของ literature ที่สนับสนุน LONGTUA:

```text
                NLP
                 │
       ┌─────────┴─────────┐
       ↓                   ↓
Event Extraction      Temporal Understanding
       │                   │
       └─────────┬─────────┘
                 ↓
        Structured Representation
                 ↓
        Constraint Programming
                 ↓
           Scheduling
                 ↓
        Preference Modeling
                 ↓
          Re-planning
                 ↓
      Human-in-the-loop
                 ↓
      Interactive Proposal
                 ↓
        User-aligned Plan
```

---

# 16.53 Final Research Framework for LONGTUA

จาก literature ทั้งหมดสามารถสรุปกรอบแนวคิดของ LONGTUA ได้ดังนี้:

```text
                USER
                  │
                  ▼
        Natural Language Input
                  │
                  ▼
        ┌─────────────────┐
        │   AI / NLP      │
        │                 │
        │ Event Extraction│
        │ Temporal        │
        │ Relations       │
        │ Clarification   │
        └────────┬────────┘
                 │
                 ▼
      Validation / Normalization
                 │
                 ▼
      Planning Representation
                 │
                 ▼
       Constraint-based Planner
                 │
          ┌──────┴──────┐
          ▼             ▼
       Feasible       Preferences
          │             │
          └──────┬──────┘
                 ▼
              Proposal
                 │
                 ▼
           USER REVIEW
        ┌────────┼────────┐
        ▼        ▼        ▼
      Confirm  Reject   Feedback
        │                  │
        ▼                  ▼
  Confirmed Schedule   Re-planning
        │                  │
        ▼                  ▼
 Notification Sync    New Proposal
```

กรอบนี้สะท้อน synthesis จากงานด้าน:

- Event Extraction
- Temporal Reasoning
- Structured IE
- Constraint Programming
- Preference-aware Scheduling
- Reactive Re-planning
- Human-in-the-loop
- Interactive Decision Support
- Clarification

---

# 16.54 Final Reference Principle

References ของ LONGTUA ควรถูกใช้ในลักษณะ:

```text
Research Evidence
       ↓
Design Decision
       ↓
Implementation
       ↓
Evaluation
```

ไม่ใช่:

```text
สร้างระบบเสร็จ
       ↓
ค่อยหา paper มาอ้างย้อนหลัง
```

หลักการนี้สำคัญเพราะ architecture หลักของ LONGTUA เช่น:

- การแยก AI กับ Planner
- การใช้ structured representation
- targeted clarification
- hard constraint vs preference
- human confirmation
- adaptive re-planning
- schedule stability

ควรสามารถอธิบายย้อนกลับได้ว่าเกิดจาก **problem requirement + theoretical reasoning + research evidence** อย่างไร

---

# 16.55 Final Reference Inventory

Academic references หลักของ project set นี้มี:

```text
R01–R22 = 22 academic / research references
T01     = 1 technical foundation
C01–C05 = 5 current system case-study sources
```

รวม:

```text
22 Academic References
+
1 Technical Reference
+
5 Case Study Sources
```

โดย academic references ที่ใช้เป็น project citations อยู่ในช่วง **2020–ปัจจุบัน** และแหล่งอ้างอิงแต่ละรายการมี link ไปยัง paper, publisher, DOI หรือ official research page ตามที่หาได้
