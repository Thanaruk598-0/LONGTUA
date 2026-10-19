# 15. Limitations & Future Work

## 15.1 Purpose

เอกสารนี้กำหนดข้อจำกัดของ LONGTUA ในขอบเขต MVP และแนวทางการต่อยอดในอนาคต โดยมีเป้าหมายเพื่อ:

1. ระบุสิ่งที่ระบบ MVP ยังไม่รองรับอย่างชัดเจน
2. แยกข้อจำกัดที่เกิดจากขอบเขตโครงงานออกจากข้อจำกัดเชิงเทคนิค
3. ป้องกันการตีความเกินจริงเกี่ยวกับความสามารถของระบบ
4. ใช้เป็นพื้นฐานสำหรับอภิปรายผลการทดลอง
5. กำหนดแนวทางการพัฒนาระบบในอนาคตโดยไม่ทำให้ MVP ขยายเกินขอบเขต

หลักสำคัญคือ **Future Work ไม่ใช่รายการ feature ที่ต้องทำให้เสร็จใน MVP** แต่เป็นแนวทางที่สามารถต่อยอดจาก architecture และผลการประเมินของระบบได้

---

# 15.2 Scope Boundary of MVP

LONGTUA MVP มุ่งเน้นการทำงานตาม pipeline:

```text id="7lq5gz"
Natural Language
      ↓
AI / NLP Understanding
      ↓
Validation / Normalization
      ↓
Constraint-based Planning
      ↓
Proposal
      ↓
Human Review
      ↓
Confirmed Schedule
      ↓
Re-planning
      ↓
Notification
```

MVP ไม่ได้มีเป้าหมายที่จะเป็น autonomous personal assistant ที่สามารถควบคุมหรือปรับตารางชีวิตของผู้ใช้ทั้งหมดโดยไม่ต้องมีการยืนยัน

---

# 15.3 General Limitations

## 15.3.1 Limited Planning Domain

ระบบรองรับกิจกรรมและข้อจำกัดตาม domain model ที่กำหนดไว้สำหรับ MVP

ประเภท Activity หลัก:

* TASK
* EVENT
* APPOINTMENT
* MEETING
* TRAVEL
* OTHER

รูปแบบการใช้งานที่มี business logic ซับซ้อนกว่านี้อาจยังไม่ครอบคลุม

ตัวอย่าง:

* multi-user scheduling
* resource allocation หลายประเภท
* shared room/resource constraints
* complex organizational scheduling

สิ่งเหล่านี้อยู่นอกขอบเขตของ MVP

---

# 15.4 Natural Language Understanding Limitations

AI/NLP เป็น probabilistic component ดังนั้นอาจเกิดข้อผิดพลาดใน:

* การตีความ Activity
* Temporal Expression
* Duration
* Relation
* Ambiguity
* Context-dependent meaning
* User wording ที่ซับซ้อนหรือคลุมเครือ

ระบบจึงต้องมี Validation / Normalization หลัง AI และไม่ควรนำ AI output ไปใช้เป็น scheduling decision โดยตรง

แนวคิดสำคัญ:

```text id="0ap8w2"
AI Output
≠
Trusted Planning Data
```

---

# 15.5 Temporal Language Limitation

ภาษาธรรมชาติที่เกี่ยวข้องกับเวลาอาจมีความหลากหลายสูง เช่น:

> “ช่วงบ่าย”

> “ประมาณสองโมง”

> “เย็น ๆ”

> “อีกสองวัน”

> “ก่อนประชุม”

ความหมายบางประเภทขึ้นกับ context และ user preference

MVP จึงกำหนด semantic time windows และ normalization policy เพื่อให้ระบบสามารถแปลงข้อมูลเหล่านี้เข้าสู่ planning representation ที่ deterministic มากขึ้น

อย่างไรก็ตาม ระบบอาจยังมีข้อผิดพลาดในกรณีที่ภาษา:

* ซับซ้อนมาก
* มีหลายความหมาย
* มี context ที่ไม่เพียงพอ
* ใช้ภาษาพูดที่ผิดรูปแบบ
* มี temporal relation หลายชั้น

---

# 15.6 Ambiguity and Missing Information Limitation

ไม่ใช่ทุกข้อมูลที่หายไปจะสามารถแก้ได้ด้วยการถามผู้ใช้

ระบบต้องตัดสินว่า:

```text id="d7z4cq"
Missing
→ Ask only when necessary
```

ดังนั้นอาจมีกรณีที่:

* ระบบถามมากเกินไป
* ระบบไม่ถามทั้งที่ควรถาม
* คำถามที่สร้างขึ้นไม่ใช่ข้อมูลที่สำคัญที่สุด
* ผู้ใช้ให้คำตอบที่ยังคงไม่ชัดเจน

ประเด็นนี้เป็นข้อจำกัดสำคัญของ Human-in-the-loop planning และเป็นส่วนหนึ่งที่ควรประเมินแยกจาก extraction accuracy

---

# 15.7 AI Hallucination / Unsupported Information

แม้ระบบจะออกแบบให้ AI ไม่สร้าง planning-critical information โดยไม่มีหลักฐาน แต่ AI provider อาจยังมีความเสี่ยงในการสร้างข้อมูลที่ไม่ได้อยู่ใน input

ระบบจึงพึ่งพาหลายชั้น:

```text id="9ojpxb"
AI
 ↓
Schema Validation
 ↓
Domain Validation
 ↓
Normalization
 ↓
Planner
```

อย่างไรก็ตาม validation ไม่สามารถรับประกันได้ว่าความหมายที่ AI สร้างขึ้นถูกต้องเชิง semantic ในทุกกรณี

จึงต้องมี:

* evaluation dataset
* unsupported information metric
* human review
* failure analysis

---

# 15.8 Planning Engine Limitations

MVP ใช้ Google OR-Tools CP-SAT เป็น Planning Engine

CP-SAT มีความสามารถในการแก้ปัญหา constraint-based scheduling ได้ดีสำหรับขอบเขตที่กำหนด แต่ไม่ได้หมายความว่าจะเป็น algorithm ที่ดีที่สุดสำหรับทุกประเภทของ personal planning

ข้อจำกัดที่อาจเกิดขึ้น:

* solve time เพิ่มขึ้นเมื่อ problem complexity เพิ่ม
* search space ขยายเมื่อมี activity จำนวนมาก
* preference objective ที่ซับซ้อนอาจเพิ่ม optimization cost
* candidate generation หลายแผนอาจเพิ่มเวลาในการประมวลผล
* constraints ที่ซับซ้อนมากอาจทำให้ model ใหญ่ขึ้น

ดังนั้น MVP จะกำหนด practical limits จาก Benchmark แทนการกล่าวอ้างว่าระบบรองรับ workload ได้ไม่จำกัด

---

# 15.9 Planning Quality Limitation

“Feasible” ไม่ได้หมายความว่า “ดีที่สุดสำหรับผู้ใช้” ในทุกกรณี

ระบบ optimize ตาม objective ที่กำหนด:

```text id="rd4wz0"
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

ดังนั้นคุณภาพของแผนขึ้นอยู่กับ:

* ความถูกต้องของ input
* completeness ของ constraints/preferences
* correctness ของ AI extraction
* model design
* objective weighting
* available planning horizon

แผนที่ระบบสร้างจึงควรตีความว่าเป็น **system-generated proposal ภายใต้ model ที่กำหนด** ไม่ใช่คำตอบที่เป็นสากลหรือเหมาะที่สุดในทุกสถานการณ์

---

# 15.10 Re-planning Limitations

MVP ใช้ full model rebuild + re-solve ภายใน bounded affected planning horizon

แนวทางนี้มีข้อดีด้าน simplicity และ correctness แต่มีข้อจำกัด:

* การ solve ใหม่อาจใช้เวลาเพิ่มเมื่อ schedule ซับซ้อน
* การเปลี่ยนแปลงหนึ่งรายการอาจส่งผลต่อหลายกิจกรรม
* Stability objective ช่วยลดการเปลี่ยนแปลง แต่ไม่สามารถรับประกันว่าจะไม่มีการย้ายกิจกรรมที่ไม่เกี่ยวข้อง
* หากไม่มี feasible solution ระบบอาจต้องให้ผู้ใช้แก้ constraint หรือ input

MVP จึงไม่ได้รับประกันว่าทุกการเปลี่ยนแปลงจะสามารถ re-plan ได้สำเร็จ

---

# 15.11 Schedule Stability Limitation

ระบบใช้:

```text id="p6ac3x"
D = Σ |newStart(i) - oldStart(i)|
```

เพื่อวัดและช่วยควบคุมการเปลี่ยนแปลงของ schedule

แต่ metric นี้ไม่ได้สะท้อนความ “น่ารำคาญ” ของการเปลี่ยนตารางในทุกมิติ

ตัวอย่าง:

* ขยับกิจกรรมสำคัญ 30 นาที
* ขยับกิจกรรมที่ไม่สำคัญหลายกิจกรรมครั้งละ 10 นาที

ค่า D อาจใกล้เคียงกัน แต่ประสบการณ์ผู้ใช้อาจแตกต่างกันมาก

ดังนั้น future work สามารถพัฒนา stability metric ที่พิจารณา:

* activity importance
* user commitment
* disruption
* จำนวนกิจกรรมที่เปลี่ยน
* proximity to execution time

ได้ในอนาคต

---

# 15.12 Candidate Plan Limitations

MVP รองรับ Proposal จำนวน 1–3 candidates

ข้อจำกัดนี้ช่วยควบคุม complexity และ interaction cost

อย่างไรก็ตาม จำนวน candidate ที่เหมาะสมอาจขึ้นกับ:

* problem complexity
* number of feasible solutions
* meaningful differences
* user preference

การเพิ่ม candidate ไม่ได้หมายความว่าคุณภาพของ user experience จะดีขึ้นเสมอไป

Future work สามารถศึกษา:

* adaptive candidate count
* diversity-aware candidate generation
* personalized candidate ranking

---

# 15.13 Human-in-the-loop Limitations

LONGTUA ให้ user เป็น final decision-maker

ข้อดีคือช่วยลดความเสี่ยงจากการเปลี่ยน schedule โดยอัตโนมัติ แต่มี trade-off:

```text id="zntt7g"
More User Control
        ↓
More Interaction
```

หาก Proposal มีความซับซ้อนมาก ผู้ใช้อาจต้องใช้เวลาในการตรวจสอบหรือให้ feedback

ดังนั้น usability ของ HITL จะขึ้นอยู่กับ:

* clarity ของ Proposal
* จำนวนตัวเลือก
* quality ของ explanation
* interaction effort
* user's familiarity with planning

ประเด็นนี้เป็นเหตุผลที่ต้องประเมิน E5 แยกจาก technical performance

---

# 15.14 Notification Limitations

MVP ใช้ Local Notification บน mobile device

ดังนั้น notification มีข้อจำกัด เช่น:

* ขึ้นอยู่กับ device / operating system
* ขึ้นอยู่กับ permission
* local notification เป็น device-specific
* reinstall หรือเปลี่ยน device ต้อง rebuild notification state
* backend ไม่สามารถรับประกัน delivery แบบ remote push

Notification จึงถือเป็น derived state จาก Confirmed Schedule ไม่ใช่ source of truth

---

# 15.15 Calendar Integration Limitation

MVP ใช้ Calendar ภายในระบบเท่านั้น

ยังไม่มี:

* Apple Calendar integration
* Google Calendar integration
* Device Calendar integration
* external calendar synchronization

ดังนั้นข้อมูล Schedule ของ LONGTUA ไม่ได้ถูก synchronize ไปยัง calendar application ภายนอก

---

# 15.16 Voice Input Limitation

แม้แนวคิด user experience ของระบบจะได้รับแรงบันดาลใจจากการพูดแล้วได้ตาราง แต่ **Voice / Speech-to-Text ไม่ได้เป็นส่วนหนึ่งของ MVP**

Input flow คือ:

```text id="7a8xur"
System / Device Input
      ↓
Text
      ↓
LONGTUA
```

แทนที่จะเป็น:

```text id="qj4wjx"
Voice
 ↓
STT
 ↓
LONGTUA
```

ผู้ใช้สามารถใช้ระบบ Speech-to-Text ของ device เพื่อสร้าง text แล้วส่งให้ LONGTUA ได้ แต่ STT engine ไม่ใช่ component ภายในระบบ MVP

---

# 15.17 Recurrence Limitation

MVP รองรับ recurring Availability Rules แต่ไม่ได้มุ่งรองรับ recurring Activity ที่ซับซ้อนเต็มรูปแบบ

กรณีที่อยู่นอก MVP เช่น:

* recurrence exception ซับซ้อน
* irregular recurrence
* recurrence rule แบบเต็มมาตรฐาน
* recurring activity ที่มี dependency ซับซ้อน

สามารถพัฒนาในอนาคตได้

---

# 15.18 Concurrent Multitasking Limitation

MVP ถือว่า Activity ที่ใช้ execution context เดียวกันไม่สามารถ overlap ได้

ดังนั้นระบบยังไม่รองรับการ model งานหลายอย่างพร้อมกันอย่างแท้จริง เช่น:

> “ฟัง lecture ไปพร้อมกับตอบ email”

หากนำ concurrent scheduling เข้ามา จะต้องมีการเปลี่ยน Domain Model และ Planning Model ในอนาคต

---

# 15.19 Route and Travel Optimization Limitation

แม้ Activity Type จะรองรับ `TRAVEL` แต่ MVP ไม่ได้มุ่งทำ:

* real-time traffic
* route optimization
* multi-stop routing
* transportation mode optimization
* dynamic travel time prediction

Travel ใน MVP สามารถใช้เป็น scheduled activity ได้ แต่ไม่ได้หมายความว่าระบบเป็น route planning system

---

# 15.20 Behavioral Adaptation Limitation

คำว่า “Adaptive” ใน MVP เน้น:

```text id="zbyb3r"
Change in Information
        ↓
Re-planning
```

และ:

```text id="q9v2z3"
User Feedback
        ↓
Planning Modification
        ↓
Re-planning
```

MVP ยังไม่ทำ:

* Reinforcement Learning
* long-term user behavior modeling
* automatic preference learning
* predictive behavior modeling
* autonomous lifestyle optimization

ดังนั้น adaptive behavior ใน MVP ไม่ควรถูกกล่าวอ้างว่าเป็น machine-learning personalization เต็มรูปแบบ

---

# 15.21 Autonomous Planning Limitation

ระบบไม่ทำ autonomous schedule modification

หลักการ:

```text id="w3j4b0"
AI Suggests
      ↓
User Reviews
      ↓
User Confirms
```

ไม่ใช่:

```text id="r3g9qk"
AI
 ↓
Automatically Change Schedule
```

การนำ autonomous agent behavior มาใช้ในอนาคตต้องมีการศึกษาเพิ่มเติมด้าน:

* trust
* safety
* authorization
* explainability
* rollback
* user control

---

# 15.22 Multi-user / Collaborative Limitation

MVP เป็น personal planner

ยังไม่รองรับ:

* shared calendar
* group planning
* family schedule
* team scheduling
* collaborative editing
* multi-user constraints

การเพิ่มฟังก์ชันเหล่านี้จะทำให้ planning model เปลี่ยนจาก single-user scheduling ไปสู่ distributed / multi-agent scheduling มากขึ้น

---

# 15.23 System Scalability Limitation

Architecture เป็น Modular Monolith เพื่อให้เหมาะกับ scope ของ MVP

ยังไม่ได้ออกแบบเพื่อรองรับ:

* massive concurrent users
* geographically distributed deployment
* multi-region database
* independently scaling AI/planner services
* distributed job queues

หากระบบเติบโตจริง สามารถวิเคราะห์ bottleneck จาก benchmark และ production workload ก่อนตัดสินใจแยก module ออกเป็น services

---

# 15.24 AI Provider Dependency

แม้ระบบมี provider abstraction แต่ quality และ latency อาจแตกต่างกันตาม AI provider/model

การเปลี่ยน:

```text id="cvn7x7"
Gemini
→
Claude
```

อาจทำให้:

* extraction quality เปลี่ยน
* clarification behavior เปลี่ยน
* output stability เปลี่ยน
* cost เปลี่ยน
* latency เปลี่ยน

ดังนั้น AI model/provider configuration ต้องถูกบันทึกในการ evaluation เพื่อให้สามารถตีความผลได้ถูกต้อง

---

# 15.25 Evaluation Limitations

ผล evaluation ของระบบอาจได้รับผลกระทบจาก:

* ขนาด dataset
* รูปแบบของ test cases
* ความหลากหลายของผู้ใช้
* synthetic data
* จำนวนผู้เข้าร่วม user evaluation
* scenario ที่ใช้
* AI model version
* system configuration

ดังนั้นผลการทดลองควรถูกนำเสนอภายใต้ experimental setup ที่ระบุไว้อย่างชัดเจน และไม่ควรสรุปเกิน population หรือ context ที่ทดสอบ

---

# 15.26 Research Contribution Boundary

LONGTUA ไม่ได้อ้างว่า:

> “เป็นระบบแรกที่ใช้ AI ทำ personal planning”

และไม่ได้อ้างว่า:

> “ค้นพบ scheduling algorithm ใหม่”

Contribution ของโครงงานมุ่งเน้นที่:

```text id="d4jzqk"
Integration
+
System Design
+
Human-in-the-loop Interaction
+
Adaptive Re-planning
+
Empirical Evaluation
```

ภายใต้บริบทของ personal planning จาก Natural Language และ Constraint-based Scheduling

ดังนั้นคุณค่าของโครงงานควรถูกอภิปรายผ่าน:

* system integration
* design decisions
* measured performance
* planning quality
* adaptation behavior
* user alignment

ไม่ใช่ claim ว่า algorithm ทุกส่วนเป็นนวัตกรรมใหม่

---

# 15.27 Future Work Overview

Future Work สามารถแบ่งเป็น 6 กลุ่มหลัก:

```text id="m3c8j4"
1. Richer Natural Language
2. Advanced Planning
3. Deeper Adaptation
4. External Integration
5. Advanced Collaboration
6. Scalability / Productionization
```

---

# 15.28 Future Work — Richer Natural Language

สามารถพัฒนา:

* Voice input
* multilingual planning
* richer temporal language
* context-aware references
* conversational planning
* multi-turn clarification
* better semantic relation understanding

ตัวอย่าง:

```text id="a6y5t1"
User:
"พรุ่งนี้อยากออกกำลังกายตอนเช้า
แต่ถ้าฝนตกให้ย้ายไปช่วงเย็น"
```

อนาคตสามารถรองรับ conditional planning ได้ละเอียดขึ้น

---

# 15.29 Future Work — Advanced Planning

สามารถต่อยอด:

* richer resource constraints
* multi-resource scheduling
* activity splitting
* concurrent tasks
* complex recurrence
* travel optimization
* multi-objective optimization
* alternative optimization algorithms

CP-SAT ยังคงเป็น baseline ที่สามารถใช้เปรียบเทียบกับ planner อื่นได้

---

# 15.30 Future Work — Advanced Re-planning

สามารถพัฒนา:

* incremental solving
* partial re-optimization
* stronger stability objectives
* disruption-aware optimization
* event-driven replanning
* predictive replanning

โดยวัดเทียบกับ MVP full-rebuild approach

ตัวอย่างการศึกษา:

```text id="odfkr0"
Full Rebuild + Re-solve
vs
Incremental / Local Re-optimization
```

เพื่อศึกษาความแตกต่างด้าน:

* runtime
* quality
* stability
* implementation complexity

---

# 15.31 Future Work — Personalized Adaptation

อนาคตสามารถเรียนรู้ preference จาก behavior ได้ เช่น:

```text id="n8u3ru"
User repeatedly moves Study
from evening → morning
```

ระบบอาจ infer ว่าผู้ใช้มี preference ต่อช่วงเช้า

แต่การทำดังกล่าวควรผ่านการศึกษาเพิ่มเติมเรื่อง:

* preference learning
* confidence
* privacy
* explainability
* user consent
* correction mechanism

และไม่ควรเปลี่ยน user preference โดยไม่มีวิธีตรวจสอบหรือแก้ไข

---

# 15.32 Future Work — Smarter Candidate Generation

Candidate generation ในอนาคตสามารถเป็น:

```text id="5qj9v4"
Best Overall
Earliest Completion
Most Stable
Preference-focused
```

โดยให้ผู้ใช้เลือก strategy ที่เหมาะกับสถานการณ์

อย่างไรก็ตามแต่ละ candidate ต้องยังผ่าน Hard Constraint validation

---

# 15.33 Future Work — External Calendar Integration

สามารถต่อยอด:

```text id="m8s4i6"
LONGTUA
 ↔
Apple Calendar
 ↔
Google Calendar
```

แต่ต้องออกแบบเรื่อง:

* synchronization direction
* conflict resolution
* external event ownership
* privacy
* authorization
* duplicate events
* notification ownership

จึงไม่ควรเพิ่มเพียงการ import/export แบบง่ายโดยไม่ออกแบบ synchronization semantics

---

# 15.34 Future Work — Collaboration

สามารถพัฒนาไปสู่:

* shared planning
* family planning
* group activities
* team meetings
* collaborative scheduling

ซึ่งจะทำให้ model ต้องพิจารณา:

```text id="8x5y1a"
Multiple Users
+
Multiple Availability
+
Shared Constraints
+
Negotiation
```

---

# 15.35 Future Work — Production Scalability

หากระบบถูกนำไปใช้งานจริงในขนาดใหญ่ สามารถประเมิน:

* asynchronous planning jobs
* task queue
* horizontally scalable planner
* separate AI service
* caching
* observability
* multi-region deployment
* stronger disaster recovery

แต่การแยก service ควรเกิดจาก evidence จาก workload จริง ไม่ใช่เพิ่ม architecture complexity ตั้งแต่ MVP

---

# 15.36 Future Work — Explainable Planning

Proposal ในอนาคตสามารถอธิบายเหตุผลของ schedule ได้ละเอียดขึ้น เช่น:

> “กิจกรรมนี้ถูกจัดช่วงเช้าเพราะคุณระบุว่าต้องการทำก่อนประชุม และช่วงบ่ายมีช่วงเวลาที่ไม่ว่าง”

Explainability สามารถช่วยให้ผู้ใช้:

* เข้าใจเหตุผลของแผน
* ตรวจสอบ constraint
* ให้ feedback ได้ง่ายขึ้น
* เพิ่ม trust ต่อระบบ

---

# 15.37 Future Work — Safety and User Control

หากระบบมี autonomous capability มากขึ้น ต้องเพิ่มกลไก:

* explicit consent
* change preview
* undo
* rollback
* audit history
* action limits
* confidence thresholds

เพื่อรักษาหลัก:

```text id="h8z0ph"
Automation
+
User Control
```

---

# 15.38 Future Work — Advanced Evaluation

อนาคตสามารถเพิ่มการทดลอง:

### Longitudinal Study

ติดตาม user behavior เป็นระยะเวลานาน

### Larger User Study

เพิ่มจำนวนและความหลากหลายของผู้ใช้

### Cross-model Evaluation

เปรียบเทียบ Gemini / Claude / model อื่น

### Planner Comparison

เปรียบเทียบ CP-SAT กับ planning approach อื่น

### Personalization Evaluation

วัดว่าการเรียนรู้จาก behavior สามารถเพิ่ม alignment ได้จริงหรือไม่

---

# 15.39 Prioritization of Future Work

Future Work ที่มีความเป็นไปได้สูงและต่อยอดจาก MVP โดยตรง:

### High Priority

* richer clarification
* better temporal understanding
* improved candidate generation
* stronger replanning stability
* personalized preference learning
* improved explainability

### Medium Priority

* external calendar integration
* complex recurrence
* activity splitting
* richer travel constraints
* collaborative planning

### Long-term

* autonomous planning
* advanced behavioral learning
* large-scale distributed architecture
* multi-user optimization

ลำดับนี้ไม่ได้หมายความว่าต้องทำทั้งหมด แต่ใช้เป็น roadmap เชิงแนวคิดตาม dependency และ complexity

---

# 15.40 MVP-to-Future Evolution

วิวัฒนาการของระบบสามารถมองได้ดังนี้:

```text id="c5h50k"
MVP
Natural Language
+
Constraint Scheduling
+
Human Review
+
Reactive Re-planning
        ↓
Future
Context-aware Planning
+
Personalized Preferences
+
Richer Replanning
+
External Integration
        ↓
Long-term
Collaborative / Predictive / Semi-autonomous Planning
```

การต่อยอดแต่ละระดับควรรักษา core principle:

```text id="im2hk3"
User remains in control
```

---

# 15.41 Final Limitation Principle

ข้อจำกัดของ LONGTUA ไม่ได้หมายความว่าระบบล้มเหลว แต่เป็นการกำหนดขอบเขตที่ชัดเจนของ MVP

ระบบตั้งใจเลือก:

```text id="q7tf0x"
Bounded Scope
+
Strong Core Workflow
+
Measurable Evaluation
```

แทนการพยายามรองรับทุกประเภทของ personal planning ตั้งแต่เวอร์ชันแรก

ดังนั้นผล evaluation ควรถูกตีความภายใต้ขอบเขตนี้

---

# 15.42 Final Future Work Principle

Future development ควรเกิดจากหลัก:

```text id="g9w8xv"
Measure
   ↓
Identify Limitation
   ↓
Research Alternative
   ↓
Implement
   ↓
Compare
```

ไม่ใช่:

```text id="w6f2o1"
Add More Features
   ↓
System becomes bigger
```

โดยเฉพาะการเปลี่ยน CP-SAT, AI provider, Re-planning strategy หรือการเพิ่ม autonomous behavior ควรมี benchmark และ empirical evidence รองรับก่อน

---

# 15.43 Final Statement

LONGTUA MVP มุ่งสร้างระบบ Personal Adaptive Planner ที่สามารถ:

```text id="h5x9vz"
Understand
   ↓
Plan
   ↓
Propose
   ↓
Adapt
   ↓
Let User Decide
```

ข้อจำกัดของ MVP เป็นส่วนหนึ่งของการกำหนด research boundary และช่วยให้การประเมินผลมีความชัดเจน

Future Work จึงมุ่งเพิ่มความสามารถในด้าน:

* Natural Language Understanding
* Planning Complexity
* Re-planning
* Personalization
* Explainability
* Integration
* Collaboration
* Scalability

โดยยังคงรักษาหลักการสำคัญว่า **ระบบช่วยผู้ใช้วางแผน ไม่ใช่ตัดสินใจแทนผู้ใช้โดยไม่มีการควบคุม**
