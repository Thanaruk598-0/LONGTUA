# 12. UI / UX Behavior Specification

## 12.1 Purpose

เอกสารนี้กำหนดพฤติกรรมของระบบและโครงสร้างการใช้งานในส่วน Mobile Application ของ LONGTUA โดยมีเป้าหมายเพื่อให้:

1. ผู้ใช้สามารถสร้างและจัดการกิจกรรมได้โดยไม่จำเป็นต้องกรอกข้อมูลแบบตายตัวทุกครั้ง
2. ผู้ใช้สามารถวางแผนด้วย Natural Language
3. ผู้ใช้สามารถตรวจสอบและตัดสินใจเลือกแผนที่ระบบเสนอ
4. ผู้ใช้สามารถแก้ไขแผนและสั่ง Re-planning ได้เมื่อสถานการณ์เปลี่ยน
5. ผู้ใช้สามารถเห็นตารางปัจจุบันและกิจกรรมที่เกี่ยวข้องได้อย่างชัดเจน
6. ผู้ใช้สามารถจัดการ Availability, Notification และ Time Window Settings
7. UI สามารถสะท้อนสถานะของระบบ เช่น กำลังประมวลผล, ต้องการข้อมูลเพิ่ม, มีข้อขัดแย้ง หรือรอการยืนยัน

เอกสารนี้กำหนด **behavioral specification** ไม่ใช่ visual design specification โดยรายละเอียดด้านสี, typography, iconography, spacing, component styling และ visual identity จะกำหนดใน Figma

---

# 12.2 UI/UX Design Principles

UI ของ LONGTUA ต้องยึดหลักดังต่อไปนี้

### 12.2.1 User remains the final decision-maker

ระบบสามารถเสนอแผนหรือการเปลี่ยนแปลงตาราง แต่จะต้องไม่ถือว่าข้อเสนอเป็นตารางที่ได้รับการยืนยันแล้ว

```text
Proposed
   ↓
User Review
   ↓
Confirm
   ↓
Confirmed Schedule
```

หากผู้ใช้ไม่ยืนยัน ระบบจะไม่เปลี่ยน Confirmed Schedule

---

### 12.2.2 Input should be lightweight

ผู้ใช้ควรสามารถเริ่มต้นจากข้อความธรรมชาติ เช่น

> “พรุ่งนี้บ่ายไปซื้อของขวัญให้แฟน”

โดยไม่จำเป็นต้องกรอกทุก field ผ่าน form ตั้งแต่ต้น

หากข้อมูลไม่เพียงพอ ระบบจะถามเฉพาะข้อมูลที่จำเป็นต่อการตีความหรือการวางแผน

---

### 12.2.3 Show system state clearly

ผู้ใช้ต้องสามารถแยกได้อย่างชัดเจนว่า:

* กิจกรรมที่บันทึกไว้
* กิจกรรมที่อยู่ใน Draft
* Proposal
* Confirmed Schedule
* Conflict
* Clarification
* Replanning
* Notification

ไม่ควรใช้ UI ที่ทำให้ผู้ใช้เข้าใจว่า Proposal ได้ถูกนำไปใช้แล้วทั้งที่ยังไม่ได้ Confirm

---

### 12.2.4 Preserve user control during changes

เมื่อมีการเปลี่ยนแปลง:

```text
Current Schedule
      ↓
Re-planning
      ↓
New Proposal
      ↓
User Review
      ↓
Confirm
```

Current Schedule ต้องยังคงเดิมจนกว่าผู้ใช้จะยืนยัน Proposal ใหม่

---

### 12.2.5 Minimize unnecessary clarification

ระบบไม่ควรถามทุกครั้งที่ข้อมูลไม่ครบ

ตัวอย่าง:

> “พรุ่งนี้ไปซื้อของขวัญให้แฟน”

สามารถบันทึก Activity แบบ date-only ได้โดยไม่จำเป็นต้องถามเวลาและ duration ทันที

แต่:

> “พรุ่งนี้ 6 โมงไปวิ่ง”

หากไม่สามารถระบุได้ว่าเป็น 06:00 หรือ 18:00 และความแตกต่างมีผลต่อการวางแผน ระบบควรขอ clarification

---

# 12.3 Application Information Architecture

โครงสร้างหลักของ Mobile Application:

```text
LONGTUA
│
├── Calendar / Planner
│   ├── Year View
│   ├── Month View
│   ├── Day View
│   └── Activity Detail
│
├── Planning
│   ├── Natural Language Input
│   ├── Processing
│   ├── Clarification
│   ├── Proposal
│   ├── Feedback
│   └── Re-planning
│
├── Activity
│   ├── Create
│   ├── Detail
│   ├── Edit
│   └── Cancel / Delete
│
├── Availability
│   ├── List
│   ├── Create
│   └── Edit
│
└── Settings
    ├── Account
    ├── Time Windows
    └── Notifications
```

ในระดับ Navigation หลัก MVP สามารถจัดเป็น:

```text
Calendar / Planner
        │
        ├── Add Activity / Plan
        │
        └── Settings
```

โดยหน้า Calendar/Planner เป็นจุดศูนย์กลางของการใช้งาน

---

# 12.4 Global UI States

หน้าจอที่เรียก backend ต้องรองรับ state พื้นฐานอย่างน้อยดังนี้

### Loading

ใช้ระหว่างรอข้อมูลจาก backend

ตัวอย่าง:

* loading calendar
* loading activity detail
* processing planning request
* loading proposal

UI ต้องไม่ตีความ Loading เป็น Empty State

---

### Empty

ใช้เมื่อไม่มีข้อมูลที่ตรงกับบริบท

ตัวอย่าง:

* ไม่มี Activity วันนี้
* ไม่มี Availability Rule
* ยังไม่มี Proposal

Empty State ควรมี action ที่สัมพันธ์กับบริบท เช่น:

```text
ยังไม่มีแผนสำหรับวันนี้

[ + เพิ่มกิจกรรม ]   [ วางแผนด้วย AI ]
```

---

### Error

ใช้เมื่อ request ไม่สำเร็จหรือระบบไม่สามารถดำเนินการได้

ควรแสดง:

* สิ่งที่เกิดขึ้น
* ผลกระทบ
* action ที่ผู้ใช้ทำได้

เช่น:

```text
ไม่สามารถโหลดตารางได้

[ ลองใหม่ ]
```

---

### Conflict

ใช้เมื่อข้อมูลหรือ Draft มีข้อขัดแย้งกับ Hard Constraint

เช่น:

```text
กิจกรรมนี้ชนกับ
Meeting 14:00–15:00

[ แก้ไขเวลา ]
```

---

### Success

ใช้หลัง operation สำเร็จ เช่น:

* Activity created
* Proposal confirmed
* Activity cancelled
* Settings updated

ข้อความควรกระชับและไม่ขัดจังหวะการใช้งานเกินจำเป็น

---

# 12.5 Calendar / Planner

Calendar เป็นหน้าหลักสำหรับตรวจสอบตารางปัจจุบัน

ระบบรองรับ:

```text
Year
 ↓
Month
 ↓
Day
 ↓
Timeline
```

ผู้ใช้สามารถเปลี่ยนระดับการแสดงผลได้โดยไม่เปลี่ยนข้อมูลของ Schedule

---

# 12.6 Year View

## Purpose

ใช้สำหรับดูภาพรวมของปีและค้นหาวันที่มีแผน

## Required Behavior

แสดง:

* เดือนทั้ง 12 เดือน
* วันที่
* indicator ของวันที่มี Activity
* indicator ที่สามารถบอกได้ว่าวันนั้นมีข้อมูลหรือกำหนดการ

การแตะวันที่ต้องนำผู้ใช้เข้าสู่ Month หรือ Day context ที่สัมพันธ์กับวันที่เลือก

Year View ไม่จำเป็นต้องแสดงรายละเอียด Activity ทั้งหมด

---

# 12.7 Month View

## Purpose

ใช้สำหรับดูภาพรวมกิจกรรมในระดับเดือน

## Required Behavior

แสดง:

* calendar grid
* วันที่
* indicator สำหรับวันที่มี Activity
* indicator สำหรับวันที่มี All Day / date-only Activity
* current date
* selected date

การแตะวันที่จะเปิด Day View ของวันนั้น

Month View ไม่จำเป็นต้องแสดงรายละเอียดทั้งหมดของ Activity หากข้อมูลหนาแน่นเกินไป

---

# 12.8 Day View

Day View เป็น view หลักสำหรับดูการจัดเวลา

โครงสร้าง:

```text
Date
Today / Navigation
-------------------------
All Day / Unscheduled
-------------------------
Timeline
00:00
01:00
02:00
...
23:00
```

## Timed Activities

Activity ที่มีเวลาเริ่มต้นและสิ้นสุดจะแสดงตามตำแหน่งเวลาใน Timeline

ตัวอย่าง:

```text
09:00 ┌──────────────────┐
      │ อ่านหนังสือ       │
11:00 └──────────────────┘
```

---

## Date-only Activities

Activity ที่มีเพียงวันที่แต่ไม่มีเวลา ต้องแสดงในส่วน:

```text
All Day / Unscheduled
```

ไม่ควรแสดง Activity ใน Timeline เวลา 06:00 เพียงเพราะ notification default ถูกกำหนดเป็น 06:00

เหตุผลคือ:

```text
Notification Time ≠ Activity Start Time
```

---

## Today Shortcut

ผู้ใช้ต้องสามารถกลับไปยังวันที่ปัจจุบันได้อย่างรวดเร็วจาก Calendar

---

# 12.9 Activity Display States

Activity ต้องมี state ที่ UI สามารถแสดงความแตกต่างได้ เช่น:

### Scheduled

Activity มี placement ใน Confirmed Schedule

### Unscheduled

Activity มีอยู่ในระบบแต่ยังไม่มีเวลาที่จัดลง Schedule เช่น date-only Activity

### Cancelled

Activity ถูกยกเลิกและไม่ควรแสดงเป็นกิจกรรมที่ต้องทำใน Schedule ปัจจุบัน

### Draft

Activity อยู่ใน local draft หรือ proposal context และยังไม่เป็น Confirmed Schedule

---

# 12.10 Activity Detail

เมื่อผู้ใช้แตะ Activity ต้องสามารถดูข้อมูลที่เกี่ยวข้อง เช่น:

* Title
* Description
* Activity Type
* Date
* Start Time
* End Time
* Duration
* Notification
* Rules / Constraints ที่เกี่ยวข้อง
* Schedule status

ตัวอย่างโครงสร้าง:

```text
Activity Detail

Title
อ่านหนังสือสอบ

Date
12 October 2026

Time
19:00 – 21:00

Duration
2 hours

Notification
18:00

Type
TASK
```

Action ที่เกี่ยวข้อง:

```text
[ Edit ]
[ Cancel ]
[ Delete ]
```

การแก้ไขข้อมูลควรแยกชัดเจนว่าการเปลี่ยนแปลงนั้น:

1. แก้ข้อมูลทั่วไป
2. กระทบการวางแผน
3. ต้องเกิด Re-planning

ตัวอย่าง Title เปลี่ยนอย่างเดียวโดยทั่วไปไม่ควรทำให้เกิด Re-planning

แต่การเปลี่ยน:

* Date
* Duration
* Fixed Time
* Deadline
* Availability ที่เกี่ยวข้อง

อาจ trigger Re-planning

---

# 12.11 Manual Activity Creation

เมื่อผู้ใช้เลือก:

```text
+
 → Manual
```

ระบบเปิด Activity Form

ข้อมูลที่ user สามารถกำหนดได้ เช่น:

* Title
* Description
* Activity Type
* Date
* Start/End Time
* Duration
* Notification
* Constraint / Preference ที่เกี่ยวข้อง

ไม่จำเป็นต้องบังคับให้ข้อมูลทุก field ถูกกรอก หาก Activity สามารถถูกสร้างในสถานะที่ยังไม่ complete ได้ เช่น date-only activity

หลัง Create สำเร็จ:

```text
Create Activity
      ↓
Validation
      ↓
Activity Saved
      ↓
Schedule / Unscheduled State
```

การสร้าง Activity ไม่ได้หมายความว่าระบบต้องสร้าง Schedule ใหม่ทุกครั้ง

---

# 12.12 Natural Language Planning Entry

ผู้ใช้สามารถเริ่ม planning ได้จากปุ่ม:

```text
+ → AI Planning
```

หรือ action ที่อยู่ในหน้า Planner

หน้าหลักควรมี input ที่สื่อว่าผู้ใช้สามารถพิมพ์เป็นภาษาธรรมชาติได้

ตัวอย่าง:

> “พรุ่งนี้ตอนเย็นไปวิ่ง 1 ชั่วโมง”

เมื่อ Submit:

```text
User Input
    ↓
Processing
```

โดย UI ต้องไม่แสดงข้อความว่า Activity ถูกเพิ่มลงตารางแล้ว ก่อน Proposal ได้รับการยืนยัน

---

# 12.13 Planning Processing State

ระหว่าง AI/NLP และ Planning Engine กำลังทำงาน ระบบจะแสดงสถานะ Processing

ตัวอย่าง:

```text
กำลังทำความเข้าใจสิ่งที่คุณต้องการ...
กำลังตรวจสอบข้อจำกัด...
กำลังจัดตาราง...
```

ข้อความเหล่านี้เป็น explanatory state เท่านั้น ไม่ควรเปิดเผย internal prompt หรือ implementation detail

หาก backend ตอบกลับว่าไม่สามารถสร้างแผนได้ ระบบต้องนำไปสู่ error/result state ที่เหมาะสม

---

# 12.14 Clarification State

เมื่อข้อมูลที่ได้มี ambiguity หรือ missing information ที่มีผลต่อการวางแผน ระบบต้องถามผู้ใช้

ตัวอย่าง:

```text
คุณหมายถึง 6 โมงเช้า หรือ 6 โมงเย็น?

( ) 06:00
( ) 18:00
```

หลักการ:

* ถามเฉพาะสิ่งที่จำเป็น
* ไม่ถาม field ที่ไม่เกี่ยวกับ feasibility
* ไม่ถามเพื่อให้ข้อมูลครบทุกช่องโดยไม่จำเป็น
* ผู้ใช้ต้องสามารถตอบได้โดยตรง
* UI ต้องแสดง context ที่เพียงพอให้ผู้ใช้เข้าใจว่าระบบกำลังถามเรื่องอะไร

Flow:

```text
Planning Input
      ↓
AI/NLP
      ↓
Needs Clarification
      ↓
Clarification UI
      ↓
User Response
      ↓
Planning continues
```

---

# 12.15 Clarification Error / Unsupported Information

หากข้อมูลที่ผู้ใช้ระบุไม่สามารถรองรับใน MVP หรือระบบไม่สามารถตีความได้อย่างปลอดภัย ระบบต้องไม่แต่งข้อมูลขึ้นมาเอง

ตัวอย่าง:

```text
ตอนนี้ยังไม่สามารถวางแผนกิจกรรมประเภทนี้ได้

กรุณาระบุข้อมูลเพิ่มเติมหรือแก้ไขข้อความ
```

ห้ามเปลี่ยน Unsupported เป็นค่าที่ระบบเดาเองโดยไม่มีหลักฐานจาก user input

---

# 12.16 Proposal State

หลัง planning สำเร็จ ระบบจะนำผู้ใช้ไปยัง Proposal

Proposal เป็นผลลัพธ์ที่ผู้ใช้ต้องตรวจสอบก่อนยืนยัน

โครงสร้างเชิงพฤติกรรม:

```text
Proposal
 ├── Candidate A
 ├── Candidate B
 └── Candidate C
```

จำนวน Candidate สามารถเป็น:

```text
1
2
3
```

ไม่จำเป็นต้องมี 3 เสมอไป

---

# 12.17 Proposal Candidate Display

Candidate แต่ละตัวควรทำให้ผู้ใช้เปรียบเทียบได้โดยตรง เช่น:

```text
Plan A
09:00–10:00 Study
10:30–11:30 Meeting

Plan B
10:00–11:00 Study
11:30–12:30 Meeting
```

UI ควรแสดงข้อมูลสำคัญ:

* activities
* start/end times
* conflicts
* relevant constraints
* notable trade-offs
* quality/reason information ที่เข้าใจง่าย

ไม่จำเป็นต้องแสดง raw solver objective score ใน MVP

---

# 12.18 Proposal Actions

ผู้ใช้ต้องสามารถ:

```text
[ Confirm ]
[ Reject ]
[ Give Feedback ]
```

และหากระบบรองรับ manual modification ใน proposal context:

```text
[ Edit ]
```

ก่อน Confirm ระบบควรให้ผู้ใช้สามารถตรวจสอบรายละเอียดที่สำคัญได้

---

# 12.19 Confirm Proposal

เมื่อผู้ใช้กด Confirm:

```text
Proposal
   ↓
Backend Validation
   ↓
Current Schedule Version Check
   ↓
Create New Schedule Version
   ↓
Confirmed Schedule
   ↓
Notification Synchronization
```

หาก Proposal เป็น stale proposal เนื่องจาก Current Schedule เปลี่ยนไปแล้ว:

```text
ไม่สามารถยืนยันแผนนี้ได้
ตารางปัจจุบันมีการเปลี่ยนแปลงแล้ว
```

และผู้ใช้ต้องกลับเข้าสู่ Re-planning หรือสร้าง Proposal ใหม่

---

# 12.20 Reject Proposal

เมื่อ Reject:

* Proposal เปลี่ยนเป็น REJECTED
* Confirmed Schedule ไม่เปลี่ยนแปลง
* notification ไม่เปลี่ยน
* user สามารถเริ่ม planning ใหม่หรือใช้ feedback ต่อได้

---

# 12.21 Feedback UI

Feedback ใช้เมื่อผู้ใช้ต้องการให้ระบบปรับ Proposal

ตัวอย่าง:

> “อยากให้ไปวิ่งตอนเช้ามากกว่า”

หรือ:

> “ไม่อยากให้ประชุมติดกับเวลาเรียน”

Flow:

```text
Proposal
   ↓
Feedback
   ↓
AI Interpretation
   ↓
Planning Modification
   ↓
Re-planning
   ↓
New Proposal
```

Feedback ต้องถูกตีความเป็น planning requirement หรือ modification โดย AI/NLP และต้องผ่าน validation ก่อนส่งให้ Planning Engine

---

# 12.22 Re-planning UI

เมื่อมี change ที่กระทบ schedule ระบบควรแสดงให้ผู้ใช้เห็นว่าการเปลี่ยนแปลงเกิดขึ้นจากอะไร

ตัวอย่าง:

```text
ตารางต้องถูกจัดใหม่

สาเหตุ:
Meeting ถูกเลื่อนเป็น 15:00

สิ่งที่จะเปลี่ยน:
• Study → 09:00 → 10:30
• Exercise → 18:00 → 19:00
```

จากนั้น:

```text
[ Review New Plan ]
```

---

# 12.23 Re-planning Comparison

Proposal จาก Re-planning ควรแสดงความแตกต่างจาก Current Schedule

ตัวอย่าง:

```text
Before
14:00–15:00 Meeting

After
15:00–16:00 Meeting

Changed Activities
Study
14:00 → 16:00
```

เป้าหมายคือช่วยให้ผู้ใช้เข้าใจผลกระทบก่อน Confirm

ระบบไม่ควรเปลี่ยน schedule ทันทีเพียงเพราะ Re-planning สำเร็จ

---

# 12.24 Manual Edit

ผู้ใช้สามารถแก้ไข Schedule ได้โดยตรง

Flow:

```text
Confirmed Schedule
       ↓
Manual Edit
       ↓
Draft
       ↓
Validate
       ↓
Confirm
       ↓
New Schedule Version
```

Draft เป็น local UI state ใน MVP

---

# 12.25 Manual Edit Conflict

หากผู้ใช้ลากหรือแก้เวลาแล้วทำให้เกิด Hard Constraint violation:

```text
Meeting
14:00–15:00

Study
14:30–16:00
```

UI ต้องระบุ conflict อย่างชัดเจน

ตัวอย่าง:

```text
มีเวลาซ้อนกับ Meeting 14:00–15:00
```

และ:

```text
[ Confirm ]  ← Disabled
```

จนกว่า conflict จะถูกแก้ไข

การมี conflict ใน Draft ไม่ควรทำให้ Current Confirmed Schedule เปลี่ยน

---

# 12.26 Manual Schedule Validation

ปุ่ม Confirm ใน Manual Edit ต้องทำงานตามลำดับ:

```text
Draft
 ↓
Validate
 ├── Valid → Enable Confirm
 └── Invalid → Show Conflict
```

Validation ต้องครอบคลุม Hard Constraints ที่เกี่ยวข้อง

Preferences ที่ไม่เหมาะสมไม่ควรถูกแสดงเป็น Hard Conflict เว้นแต่ rule นั้นถูกกำหนดเป็น Hard Constraint

---

# 12.27 Availability / Unavailability UI

ผู้ใช้สามารถจัดการช่วงเวลาที่:

* สามารถทำกิจกรรมได้
* ไม่สามารถทำกิจกรรมได้

ตัวอย่าง:

```text
Availability

Mon–Fri
08:00–17:00
Available

Saturday
10:00–12:00
Available
```

และ:

```text
Unavailable

12 October
13:00–15:00
```

UI ต้องสื่อให้ผู้ใช้เข้าใจว่า Availability ไม่ใช่ Activity

---

# 12.28 Availability Creation

ผู้ใช้ต้องสามารถเลือก:

```text
Available
Unavailable
```

และ:

```text
One-time
Recurring
```

ตัวอย่าง recurring:

```text
Mon–Fri
08:00–17:00
```

ตัวอย่าง one-time:

```text
12 Oct 2026
13:00–15:00
Unavailable
```

เมื่อบันทึกสำเร็จ ระบบสามารถ trigger Re-planning เมื่อกฎนั้นมีผลกับ Current Schedule

---

# 12.29 Availability Change and Re-planning

หากผู้ใช้เพิ่ม Unavailability ที่ชนกับกิจกรรมในตารางปัจจุบัน:

```text
Current Schedule
      ↓
New Unavailability
      ↓
Conflict Detection
      ↓
Re-planning Proposal
```

Current Schedule ต้องไม่ถูกแก้ทันที

ผู้ใช้ต้อง Review และ Confirm Proposal ใหม่

---

# 12.30 Settings

Settings แบ่งเป็นอย่างน้อย:

```text
Settings
│
├── Account
├── Time Windows
└── Notifications
```

Account ใช้จัดการข้อมูลและ session ที่เกี่ยวข้องตาม Security Design

Time Windows และ Notifications เป็น application behavior settings

---

# 12.31 Time Window Settings

ผู้ใช้สามารถดูและแก้ไข semantic time windows เช่น:

```text
Morning
06:00–09:00

Late Morning
09:00–12:00

Afternoon
13:00–16:00
```

ระบบต้องแสดงให้ผู้ใช้เข้าใจว่า setting นี้มีผลต่อการตีความ semantic time เช่น:

> “ช่วงบ่าย”

ไม่ใช่การสร้าง Activity

การเปลี่ยน Time Window Settings ไม่ควรเปลี่ยนตารางที่ Confirmed อยู่โดยอัตโนมัติ

ค่า setting จะถูกนำไปใช้ในการวางแผนครั้งต่อไปหรือ operation ที่จำเป็นตาม system policy

---

# 12.32 Notification Settings

ผู้ใช้สามารถกำหนด default notification policy เช่น:

```text
Date-only Activity
06:00

Timed Activity
1 hour before
```

และสามารถกำหนด Activity-level override ได้

Priority:

```text
Activity Override
      ↓
Global Notification Setting
      ↓
System Default
```

UI ต้องแยก:

```text
Activity Start Time
```

ออกจาก

```text
Notification Time
```

อย่างชัดเจน

---

# 12.33 Notification Behavior

เฉพาะ Confirmed Schedule เท่านั้นที่สร้าง notification

```text
Proposal
   X
   ↓
Confirmed Schedule
   ↓
Notification Sync
```

เมื่อเวลา Activity เปลี่ยน:

```text
Old Notification
      ↓
Cancel
      ↓
New Notification
```

ตัวอย่าง:

```text
เดิม
Activity: 09:00
Notification: 08:00

ใหม่
Activity: 12:00
Notification: 11:00
```

หาก notification configuration ไม่สามารถใช้งานได้ตาม policy ระบบต้องแจ้งปัญหาให้ผู้ใช้ทราบ ไม่ควรแก้เวลาอย่างเงียบ ๆ

---

# 12.34 Notification Failure

Notification failure ต้องไม่ทำให้ Confirmed Schedule ถูก rollback

ตัวอย่าง:

```text
Schedule confirmed successfully.

แต่ไม่สามารถตั้งการแจ้งเตือนได้
```

ผู้ใช้ยังคงมี schedule ที่ยืนยันแล้ว แต่ UI ควรสื่อสถานะ notification ให้เหมาะสม

---

# 12.35 Calendar Navigation

ผู้ใช้ต้องสามารถ:

* ไปวันนี้
* ไปวันก่อนหน้า
* ไปวันถัดไป
* เปลี่ยน Year / Month / Day context
* แตะวันที่เพื่อดูรายละเอียด

Navigation ต้องไม่สร้างหรือแก้ Activity โดยอัตโนมัติ

---

# 12.36 Add Action

ปุ่ม Add ต้องเป็น entry point สำหรับ:

```text
+
├── Manual Activity
└── AI Planning
```

โดยให้ผู้ใช้เลือกวิธีสร้างตามความต้องการ

Manual เหมาะกับกรณีที่ user รู้ข้อมูลอยู่แล้ว

AI Planning เหมาะกับกรณีที่ user ต้องการให้ระบบแปลง natural language เป็น planning information

---

# 12.37 Activity Cancellation

การ Cancel Activity ต้องแยกจาก Delete

```text
Cancel
→ Activity remains as historical record
→ removed from active planning
```

ส่วน Delete ใช้สำหรับการลบ Activity ตาม domain policy

หาก Activity ที่ถูก Cancel อยู่ใน Confirmed Schedule และ cancellation กระทบตาราง ต้องเข้าสู่ Re-planning ตาม Replanning Design

---

# 12.38 Schedule Version Visibility

ผู้ใช้ไม่จำเป็นต้องเห็น internal version number ในทุกกรณี

อย่างไรก็ตาม UI ในจุดที่มีการ Re-planning หรือ Proposal ควรสามารถสื่อได้ว่า:

```text
Current Schedule
```

และ:

```text
Proposed Changes
```

เป็นคนละสถานะกัน

Historical versions เป็น immutable และไม่ควรมี UI ที่ทำให้ user เข้าใจว่าสามารถแก้ไข historical version ได้โดยตรง

---

# 12.39 Stale Proposal UX

กรณี:

```text
Proposal A
   ↓
Current Schedule changes
   ↓
Proposal A becomes stale
```

เมื่อผู้ใช้เปิด Proposal A:

```text
แผนนี้ไม่ตรงกับตารางปัจจุบันแล้ว
จึงไม่สามารถยืนยันได้
```

Action:

```text
[ Create New Plan ]
```

ห้ามให้ผู้ใช้ Confirm stale Proposal

---

# 12.40 No Feasible Plan UX

กรณี Planning Engine หา solution ที่เป็นไปตาม Hard Constraints ไม่ได้ ระบบต้องไม่แสดง schedule ที่ผิด constraint เป็นผลลัพธ์สำเร็จ

ตัวอย่าง:

```text
ยังไม่สามารถจัดตารางตามเงื่อนไขทั้งหมดได้

ปัญหาที่พบ:
• Meeting ถูกกำหนดไว้เวลา 13:00–15:00
• คุณไม่ว่างช่วง 13:00–16:00
```

แนวทาง UX สามารถนำเสนอให้ผู้ใช้:

```text
[ แก้ไขข้อจำกัด ]
[ แก้ไขกิจกรรม ]
[ ลองวางแผนใหม่ ]
```

แต่ต้องไม่ลด Hard Constraint อัตโนมัติเพื่อทำให้เกิด solution

---

# 12.41 Confirmed Schedule Source of Truth

UI ทุกส่วนที่แสดงตารางปัจจุบันต้องอ้างอิง Confirmed Schedule ปัจจุบัน

ไม่ควรให้ Proposal หรือ local Draft ถูกแสดงเป็น schedule จริงหลังจากผู้ใช้เปลี่ยนหน้าจอโดยไม่ได้ Confirm

หลักการ:

```text
Confirmed Schedule
        ↓
Calendar
        ↓
Notifications
```

ส่วน:

```text
Proposal / Draft
```

เป็น temporary planning state

---

# 12.42 User Flow: Initial Planning

```text
Calendar
   ↓
Add
   ↓
AI Planning
   ↓
Natural Language Input
   ↓
Submit
   ↓
Processing
   ↓
Clarification? ── Yes ──> Clarification UI
   │                              ↓
   │                         User Response
   │                              ↓
   └──────────── No ──────────────┘
                   ↓
              Planning
                   ↓
                Proposal
                   ↓
             User Review
              /    |    \
         Confirm Reject Feedback
            ↓        ↓       ↓
       New Version   End   Re-planning
```

---

# 12.43 User Flow: Re-planning

```text
Existing Schedule
       ↓
Change Detected
       ↓
Impact Analysis
       ↓
Re-planning
       ↓
Proposal
       ↓
Show Before / After
       ↓
User Review
       ↓
Confirm
       ↓
New Schedule Version
       ↓
Notification Sync
```

---

# 12.44 User Flow: Manual Edit

```text
Calendar
   ↓
Activity / Schedule
   ↓
Edit
   ↓
Draft
   ↓
Modify
   ↓
Validate
  /    \
Valid  Invalid
 ↓        ↓
Confirm  Conflict
 ↓
New Schedule Version
```

---

# 12.45 User Flow: Date-only Activity

ตัวอย่าง:

> “พรุ่งนี้ไปซื้อของขวัญให้แฟน”

Flow:

```text
Natural Language
      ↓
Activity Created
      ↓
Date = Tomorrow
Time = Unknown
Duration = Unknown
      ↓
Activity saved
      ↓
All Day / Unscheduled
```

ระบบไม่ควรแสดง Activity เวลา 06:00 เพียงเพราะ notification default เป็น 06:00

หากมีการตั้ง notification:

```text
Activity
Date-only

Notification
06:00
```

06:00 มีความหมายเฉพาะกับ notification

---

# 12.46 User Flow: Ambiguous Time

ตัวอย่าง:

> “พรุ่งนี้ 6 โมงไปวิ่ง”

Flow:

```text
Input
 ↓
AI/NLP
 ↓
Ambiguous Time
 ↓
Clarification
 ↓
06:00 or 18:00
 ↓
Planning
 ↓
Proposal
```

หาก context เพียงพอที่จะ resolve ambiguity ได้ ระบบไม่จำเป็นต้องถาม

---

# 12.47 User Flow: Planning Failure

```text
Planning Request
      ↓
Processing
      ↓
Failure
 ├── Clarification Required
 ├── No Feasible Plan
 ├── Unsupported Input
 └── Temporary System Error
```

แต่ละกรณีต้องมี UX ที่แตกต่างกัน

ไม่ควรใช้ข้อความ:

> “Something went wrong”

เพียงอย่างเดียวในทุกสถานการณ์

---

# 12.48 UI Behavior During Network Failure

กรณี backend unavailable:

* ไม่ควรลบข้อมูลที่ผู้ใช้กรอก
* ควรเก็บ draft ที่ยังไม่ได้ submit ใน local state ตามความเหมาะสม
* แจ้งให้ผู้ใช้ทราบว่า operation ยังไม่สำเร็จ
* ไม่แสดง operation เป็นสำเร็จหาก backend ยังไม่ยืนยัน

ตัวอย่าง:

```text
ไม่สามารถเชื่อมต่อกับระบบได้

ข้อมูลของคุณยังไม่ได้ถูกบันทึก

[ ลองอีกครั้ง ]
```

---

# 12.49 UI and Backend Responsibility Boundary

Mobile UI รับผิดชอบ:

* rendering
* navigation
* local draft state
* user interaction
* local notification synchronization
* optimistic interaction เท่าที่ไม่กระทบ consistency

Backend รับผิดชอบ:

* validation
* authentication / authorization
* NLP orchestration
* planning
* proposal generation
* schedule version creation
* conflict validation
* stale proposal checking

AI/NLP รับผิดชอบ:

* intent understanding
* event/activity extraction
* temporal understanding
* clarification decision
* feedback interpretation

Planning Engine รับผิดชอบ:

* feasibility
* hard constraints
* preference-aware optimization
* re-planning
* candidate generation support

UI ไม่ควรฝัง business logic ของ Planning Engine

---

# 12.50 Accessibility and Usability Baseline

MVP ต้องคำนึงถึงอย่างน้อย:

* text สามารถอ่านได้ชัดเจน
* interactive elements มีพื้นที่กดที่เหมาะสม
* สถานะสำคัญไม่สื่อด้วยสีเพียงอย่างเดียว
* error สามารถอ่านและเข้าใจได้
* conflict ต้องมีข้อความบอก ไม่ใช้เพียง visual indication
* การดำเนินการสำคัญ เช่น Confirm / Delete ต้องแยกชัดเจน
* ผู้ใช้ต้องสามารถย้อนกลับจาก flow ที่ไม่ต้องการได้โดยไม่สูญเสียข้อมูลสำคัญโดยไม่ตั้งใจ

---

# 12.51 Figma Scope

Figma ในขั้นตอนถัดไปควรนำ behavioral requirements จากเอกสารนี้ไปสร้าง visual specification

Figma ควรครอบคลุมอย่างน้อย:

1. Authentication
2. Calendar Year
3. Calendar Month
4. Calendar Day
5. Activity Detail
6. Manual Activity Creation
7. AI Planning Input
8. Processing State
9. Clarification State
10. Proposal – Single Candidate
11. Proposal – Multiple Candidates
12. Feedback
13. Re-planning Comparison
14. Manual Edit Draft
15. Manual Edit Conflict
16. Availability
17. Time Window Settings
18. Notification Settings
19. Planning Failure
20. Empty State
21. Network/System Error
22. Stale Proposal
23. Confirmation / Success State

Figma ไม่ควรเพิ่ม behavior ที่ขัดกับเอกสารนี้เพียงเพื่อความสวยงามของ UI

---

# 12.52 UI State Coverage Requirement

ก่อนเริ่ม Implementation ทุก feature ที่มี interaction สำคัญควรมีการระบุ state อย่างน้อย:

```text
Default
Loading
Empty
Success
Error
Conflict
Disabled
Processing
```

และ feature ที่เกี่ยวข้องกับ planning ต้องรองรับ:

```text
Clarification
Proposal
Confirmed
Rejected
Invalidated / Stale
```

เพื่อป้องกันกรณีที่ Figma ออกแบบเฉพาะ happy path แต่ implementation ต้องมาคิด behavior เพิ่มเองภายหลัง

---

# 12.53 UI/UX Acceptance Criteria

## Calendar

* ผู้ใช้สามารถดู Year / Month / Day
* ผู้ใช้สามารถกลับไป Today ได้
* Date-only Activity ไม่ถูกแสดงเป็น timed activity
* Activity ที่มีเวลาแสดงใน Timeline ตาม Schedule
* Calendar แสดง Confirmed Schedule ไม่ใช่ Proposal ที่ยังไม่ Confirm

## Activity

* ผู้ใช้สามารถสร้าง Activity แบบ Manual
* ผู้ใช้สามารถแก้ไข Activity
* ผู้ใช้สามารถ Cancel Activity
* ผู้ใช้สามารถ Delete ตาม policy
* ระบบแยก Activity Start Time ออกจาก Notification Time

## Natural Language Planning

* ผู้ใช้สามารถป้อน Natural Language
* ระบบแสดง Processing State
* ระบบแสดง Clarification เมื่อจำเป็น
* ระบบไม่สร้างข้อมูล planning-critical ที่ผู้ใช้ไม่ได้ระบุโดยพลการ
* ระบบนำผลไปสู่ Proposal ก่อน Confirmed Schedule

## Proposal

* Proposal แสดง candidate ที่มีอยู่จริง
* สามารถมี 1–3 candidates
* ผู้ใช้สามารถ Confirm / Reject / Feedback
* Confirm ต้องตรวจสอบ stale state
* Reject ไม่เปลี่ยน Confirmed Schedule

## Re-planning

* Change ที่กระทบ planning สามารถ trigger Re-planning
* ผู้ใช้เห็นผลต่างระหว่างก่อนและหลัง
* Current Schedule ไม่เปลี่ยนจนกว่าจะ Confirm
* Re-planning failure ไม่ทำลาย Current Schedule

## Manual Edit

* User สามารถแก้ schedule ได้
* Draft สามารถมี conflict ได้
* Confirm ต้อง disabled เมื่อมี Hard Constraint violation
* Confirm ที่สำเร็จสร้าง Schedule Version ใหม่

## Availability

* User สามารถกำหนด Available / Unavailable
* รองรับ one-time และ recurring
* Conflict กับ current schedule สามารถนำไปสู่ Re-planning

## Notification

* เฉพาะ Confirmed Schedule ที่สร้าง local notification
* เวลา notification ไม่ถูกใช้เป็น activity start time
* การย้าย Activity สามารถ sync notification ใหม่
* Notification failure ไม่ rollback schedule

---

# 12.54 Design Traceability

UI/UX ต้องสนับสนุน Research Questions และ Evaluation ดังนี้:

| Research Question | UI/UX Support                                                      |
| ----------------- | ------------------------------------------------------------------ |
| RQ1               | Natural Language Input, Clarification, Structured Activity Display |
| RQ2               | Proposal, Constraint/Preference Feedback, Schedule Review          |
| RQ3               | Re-planning UI, Before/After Comparison                            |
| RQ4               | Feedback UI, Human Review, Re-planning Interaction                 |

UI จึงไม่ได้เป็นเพียง presentation layer แต่เป็นส่วนหนึ่งของ Human-in-the-loop interaction ที่ใช้ประเมินระบบ

---

# 12.55 Out of Scope for UI MVP

สิ่งต่อไปนี้ยังไม่อยู่ใน MVP:

* Voice input / Speech-to-Text ภายในแอป
* Apple Calendar integration
* Google Calendar integration
* Device calendar synchronization
* Remote push notification
* Concurrent multitasking visualization
* Complex route map UI
* Automatic autonomous schedule modification
* Social / shared calendar
* Multi-user collaborative planning
* Complex recurring Activity editor
* Activity splitting UI
* Advanced analytics dashboard

---

# 12.56 Final UI/UX Principle

พฤติกรรมของ UI ต้องสะท้อน architecture และ domain model ของ LONGTUA อย่างสอดคล้องกัน:

```text
User Input
    ↓
AI Understanding
    ↓
Planning
    ↓
Proposal
    ↓
User Review
    ↓
Confirmed Schedule
    ↓
Notification
```

และเมื่อมีการเปลี่ยนแปลง:

```text
Current Schedule
      ↓
Change
      ↓
Re-planning
      ↓
New Proposal
      ↓
User Review
      ↓
New Confirmed Version
```

หลักการสำคัญที่สุดคือ:

> **LONGTUA เสนอแผนให้ผู้ใช้ตัดสินใจ ไม่ใช่ตัดสินใจแทนผู้ใช้**

ดังนั้น UI ทุกส่วนที่เกี่ยวข้องกับการวางแผนต้องรักษาเส้นแบ่งระหว่าง **Proposal, Draft และ Confirmed Schedule** อย่างชัดเจน
