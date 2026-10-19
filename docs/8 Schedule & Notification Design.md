# 8. Schedule & Notification Design

## 8.1 Purpose

เอกสารฉบับนี้กำหนดการออกแบบ Schedule และ Notification ของ LONGTUA — Personal Adaptive Planner ตั้งแต่ความหมายของ Confirmed Schedule, Schedule Version และ Schedule Item กระบวนการสร้าง Draft การ Validate และ Confirm ไปจนถึง Policy สำหรับ Local Notification การสร้าง ยกเลิก และปรับปรุง Notification เมื่อ Schedule เปลี่ยนแปลง

เอกสารนี้ทำหน้าที่เป็น Source of Truth สำหรับ:

* Schedule Management
* Proposal Confirmation
* Manual Schedule Editing
* Schedule Versioning
* Calendar Presentation
* Notification Management
* Mobile Local Notification
* Database Design
* API Design
* UI/UX Behavior

หลักการสำคัญของส่วนนี้คือ:

> **Confirmed Schedule เป็น Source of Truth และ Notification เป็น Derived State ที่สร้างขึ้นจาก Confirmed Schedule เท่านั้น**

---

# 8.2 Core Concepts

ระบบแยกองค์ประกอบต่อไปนี้ออกจากกันอย่างชัดเจน:

```text
Activity
= สิ่งที่ผู้ใช้ต้องทำ/เข้าร่วม

Schedule Item
= ตำแหน่งของ Activity ที่ถูกวางลงใน Schedule

Proposal
= แผนที่ระบบเสนอให้ User พิจารณา

Draft Schedule
= ตารางชั่วคราวระหว่างการแก้ไข

Confirmed Schedule
= ตารางที่ User ยืนยันแล้ว

Schedule Version
= Snapshot ของ Confirmed Schedule ณ เวลาหนึ่ง

Notification
= การแจ้งเตือนที่สร้างจาก Confirmed Schedule
```

ความสัมพันธ์:

```text
Activity
    ↓
Schedule Placement
    ↓
Schedule Item
    ↓
Schedule Version
    ↓
Confirmed Schedule
    ↓
Notification
```

---

# 8.3 Schedule as Source of Truth

LONGTUA กำหนดให้:

> **Confirmed Schedule เป็น Source of Truth ของตารางที่ระบบถือว่ายืนยันแล้ว**

ดังนั้นหากข้อมูล Notification ไม่ตรงกับ Schedule:

```text
Schedule = ถูกต้อง
Notification = ต้องปรับให้สอดคล้อง
```

ไม่ใช่:

```text
Notification = Source
Schedule = ปรับตาม Notification
```

ตัวอย่าง:

```text
Activity Start = 12:00
Notification = 11:00
```

หาก Notification ไม่ทำงาน:

```text
Confirmed Schedule
ยังคงเป็น 12:00
```

ระบบไม่ Rollback Schedule เพียงเพราะ Notification Failure

---

# 8.4 Activity vs Schedule Item

Activity และ Schedule Item เป็นคนละ Domain Concept

## Activity

แสดงว่า:

> ผู้ใช้ต้องทำอะไร

## Schedule Item

แสดงว่า:

> Activity นั้นถูกวางไว้เมื่อใดใน Confirmed Schedule

ตัวอย่าง:

```text
Activity
Title = อ่านหนังสือ
Duration = 120 min

Schedule Item
Start = 14:00
End = 16:00
```

Activity เดียวสามารถมี Placement แตกต่างกันใน Schedule Version ต่างกันได้

ตัวอย่าง:

```text
Version 1
Study = 14:00–16:00

Version 2
Study = 16:00–18:00
```

ทั้งสองยังอ้างอิง Activity เดียวกัน

---

# 8.5 Confirmed Schedule

Confirmed Schedule คือ Schedule ที่ User ยอมรับและระบบบันทึกเป็น Current Schedule แล้ว

Confirmed Schedule ต้องมีเงื่อนไข:

1. ผ่าน Validation
2. ไม่มี Hard Constraint Conflict
3. ผ่าน Explicit User Confirmation
4. ถูกสร้างเป็น Schedule Version ใหม่

Proposal ที่ยังไม่ได้ Confirm **ไม่ใช่ Confirmed Schedule**

---

# 8.6 Proposed Schedule

Proposal เป็นผลลัพธ์ที่อยู่ระหว่างการพิจารณา

```text
Planning Engine
      ↓
Candidate(s)
      ↓
Proposal
      ↓
User Review
```

Proposal:

* ยังไม่เปลี่ยน Current Schedule
* ยังไม่สร้าง Confirmed Notification
* สามารถถูก Reject ได้
* สามารถถูก Invalidated ได้
* สามารถถูก Confirm ได้เมื่อยังไม่ Stale

---

# 8.7 Proposal vs Confirmed Schedule

| State              | ใช้เป็น Current Schedule | สร้าง Notification | User ต้อง Confirm |
| ------------------ | -----------------------: | -----------------: | ----------------: |
| Proposal           |                        ❌ |                  ❌ |                 ✅ |
| Confirmed Schedule |                        ✅ |                  ✅ |      เกิดขึ้นแล้ว |
| Draft              |                        ❌ |                  ❌ |     ✅ ก่อน Commit |

ดังนั้น:

```text
Proposal
≠
Confirmed Schedule
```

เป็น Invariant ของระบบ

---

# 8.8 Schedule Version

Schedule Version คือ Immutable Snapshot ของ Confirmed Schedule

ตัวอย่าง:

```text
Version 1
   ↓
Version 2
   ↓
Version 3
```

แต่ละ Version ประกอบด้วย:

```text
Schedule Version
├── version number
├── creation information
├── source / confirmation context
└── Schedule Items
```

Version ที่สร้างแล้วไม่สามารถแก้ไขย้อนหลัง

---

# 8.9 Current Schedule Version

ผู้ใช้แต่ละคนต้องมี Current Schedule Version ได้เพียงหนึ่ง Version

แนวคิด:

```text
V1
V2
V3 ← CURRENT
```

เมื่อ V4 ถูก Confirm:

```text
V1
V2
V3
V4 ← CURRENT
```

V3 ยังคงเป็น Historical Version

---

# 8.10 New Schedule Version

Schedule Version ใหม่เกิดจาก:

### Proposal Confirmation

```text
Proposal
   ↓
User Confirm
   ↓
New Schedule Version
```

### Manual Schedule Confirmation

```text
Draft
   ↓
Validate
   ↓
User Confirm
   ↓
New Schedule Version
```

ไม่มีการสร้าง Current Schedule Version ใหม่จาก AI หรือ Planning Engine โดยตรง

---

# 8.11 Historical Schedule

Historical Schedule Version ใช้สำหรับ:

* Audit
* Debugging
* Stale Proposal Detection
* Evaluation
* Before/After Comparison
* Replanning Stability Analysis

Historical Version ต้อง:

```text
Immutable
```

ไม่ควรแก้ย้อนหลังเพื่อทำให้ State ปัจจุบันตรงกับข้อมูลใหม่

---

# 8.12 Schedule Version Transition

ตัวอย่าง:

```text
Current = V3

User confirms Proposal P
Source Version = V3

        ↓

Create V4
        ↓
V4 = Current
```

และ:

```text
V3 remains immutable
```

---

# 8.13 Schedule Version as Concurrency Boundary

Schedule Version ยังทำหน้าที่เป็น Consistency Reference

Proposal ต้องอ้างอิง:

```text
source_schedule_version_id
```

ก่อน Confirm ระบบต้องตรวจ:

```text
Proposal Source Version
==
Current Schedule Version
```

หากไม่ตรง:

```text
Stale Proposal
```

และไม่สามารถ Confirm เพื่อเขียนทับ Current Schedule ได้

---

# 8.14 Stale Proposal

ตัวอย่าง:

```text
Current Schedule = V3

Proposal A
Source = V3
```

ต่อมา User Confirm Proposal B:

```text
Current Schedule = V4
```

แล้ว User พยายาม Confirm Proposal A:

```text
V3 ≠ V4
```

ระบบต้องปฏิเสธการ Confirm

Proposal A สามารถถูกเปลี่ยนสถานะเป็น:

```text
INVALIDATED
```

ตาม Application Policy

---

# 8.15 Schedule Item

Schedule Item คือ Placement ของ Activity ใน Schedule Version

ข้อมูลเชิงแนวคิด:

```text
Schedule Item
├── schedule_version
├── activity
├── start time
├── end time
└── placement metadata
```

Schedule Item ต้องสอดคล้องกับ Domain Rules เช่น:

```text
end > start
duration > 0
within planning context
```

และห้ามสร้าง Placement ที่ละเมิด Hard Constraint

---

# 8.16 Schedule Item and Activity Lifecycle

Activity สามารถมี Lifecycle ของตนเอง เช่น:

```text
ACTIVE
COMPLETED
CANCELLED
```

ขณะที่ Schedule Item เป็น Snapshot ของ Placement

ดังนั้นการ Cancel Activity ใหม่อาจมีผลต่อ Schedule รุ่นถัดไป แต่ไม่ควรไปแก้ Schedule Item ใน Historical Version เดิม

---

# 8.17 Draft Schedule

Draft คือ Temporary Schedule State ที่เกิดขึ้นระหว่าง Manual Editing

```text
Confirmed Schedule
       ↓
Draft
       ↓
Edit
       ↓
Validate
       ↓
Confirm
```

Draft:

* ไม่ใช่ Current Schedule
* ไม่สร้าง Notification
* สามารถมี Conflict ชั่วคราว
* ต้องผ่าน Validation ก่อน Confirm

---

# 8.18 Why Draft Is Separate

หาก User ลาก Activity จาก:

```text
14:00 → 18:00
```

และช่วง 18:00 มี Activity อื่น:

```text
Draft
= Conflict
```

ระบบไม่ควรแก้ Current Confirmed Schedule ทันที

ดังนั้น:

```text
Current Confirmed Schedule
ยังคงเดิม
```

จนกว่า Draft จะผ่าน Validation และ User Confirm

---

# 8.19 Draft Validation

ก่อน Confirm ต้องตรวจอย่างน้อย:

* Time validity
* Duration
* Fixed Time
* Deadline
* Time Window
* Availability
* Unavailability
* No-Overlap
* Temporal Relations
* Container Containment
* Required Activity Placement

Flow:

```text
Draft
 ↓
Validation
 ├── INVALID / CONFLICT
 └── VALID
```

---

# 8.20 Conflict in Draft

Draft สามารถมี Conflict ระหว่าง Editing

ตัวอย่าง:

```text
A = 09:00–11:00
B = 10:00–12:00
```

ระบบแสดง:

```text
Conflict = TRUE
```

และ:

```text
Confirm = Disabled
```

จนกว่า Conflict จะได้รับการแก้ไข

---

# 8.21 Valid Draft

เมื่อ:

```text
Hard Constraint Violations = 0
```

และข้อมูลอื่นผ่าน Validation:

```text
Draft = Valid
```

จากนั้น User สามารถ Confirm

```text
Draft
 ↓
Confirm
 ↓
New Schedule Version
```

---

# 8.22 Draft Does Not Generate Notification

ไม่ว่าจะ Valid หรือ Invalid:

```text
Draft
→ No Notification
```

เพราะ Draft ยังไม่ใช่ Confirmed Schedule

---

# 8.23 Manual Confirmation

Manual Confirmation เป็นกระบวนการ:

```text
Draft
 ↓
Validate
 ↓
User Confirm
 ↓
Create Schedule Version
 ↓
Current Schedule Update
 ↓
Notification Synchronization
```

การเขียนข้อมูลที่สำคัญควรเกิดใน Transaction เดียวกันใน Backend ตาม Transaction Policy

---

# 8.24 Calendar Representation

Calendar เป็นการแสดงผลของ Schedule ไม่ใช่ฐานข้อมูลอีกชุดหนึ่ง

```text
Schedule Version
      ↓
Schedule Items
      ↓
Calendar UI
```

Calendar รองรับ:

* Year
* Month
* Day
* Timeline

---

# 8.25 Year View

Year View ใช้สำหรับ:

* Overview
* Navigation
* Identify Days With Activities
* Identify Busy Periods

Year View ไม่ควรแสดงข้อมูลทุก Scheduling Detail ของทั้งปีพร้อมกัน

---

# 8.26 Month View

Month View ใช้สำหรับ:

* ดูภาพรวมรายเดือน
* ดูกิจกรรมตามวันที่
* Navigation ไปยัง Day View
* แสดง Indicators

---

# 8.27 Day View

Day View ใช้:

> Time-based Timeline

เช่น:

```text
08:00
09:00
10:00
11:00
...
```

Schedule Items ที่มีเวลาแสดงตามตำแหน่งจริงใน Timeline

---

# 8.28 Date-Only Activity

Activity ที่มี:

```text
Date = Known
Start Time = Unknown
```

ต้องแสดงใน:

> All Day / Unscheduled

ไม่ใช่:

> Notification Time

---

# 8.29 Notification Time Is Not Activity Time

ตัวอย่าง:

```text
Activity Start = 09:00
Notification = 08:00
```

Calendar:

```text
Activity = 09:00
```

ไม่ใช่:

```text
Activity = 08:00
```

แม้ Notification จะถูกส่งตอน 08:00

หลัก:

```text
Activity Start Time
≠
Notification Time
```

---

# 8.30 Notification Architecture

LONGTUA ใช้ **Local Notification** สำหรับ MVP

Expo รองรับการสร้าง Scheduled / Local Notifications ผ่าน `expo-notifications` โดย `scheduleNotificationAsync()` คืน Notification Identifier ซึ่งสามารถนำไปใช้ยกเลิก Notification รายการนั้นผ่าน `cancelScheduledNotificationAsync()` ได้ ([Expo Notifications Documentation](https://docs.expo.dev/versions/v56.0.0/sdk/notifications/))

Architecture:

```text
Confirmed Schedule
       ↓
Notification Policy
       ↓
Effective Notification Time
       ↓
Mobile
       ↓
expo-notifications
       ↓
Local Notification
```

---

# 8.31 Local vs Remote Notification

MVP ใช้:

> Local Notification

ไม่ใช้:

> Remote Push Notification

Local Notification ถูกสร้างโดย Application บนอุปกรณ์ ส่วน Push Notification มาจาก Remote Server ซึ่ง Expo แยกสองแนวทางนี้อย่างชัดเจนใน Documentation ([Expo Notifications Documentation](https://docs.expo.dev/push-notifications/what-you-need-to-know/))

ดังนั้น Backend ไม่ต้องทำ Push Notification Delivery ใน MVP

---

# 8.32 Notification Source of Truth

Notification ต้องมี Source:

```text
Confirmed Schedule
```

เท่านั้น

Flow:

```text
Proposal
   X
   ↓
Notification

Confirmed Schedule
   ✓
   ↓
Notification
```

---

# 8.33 Effective Notification Policy

เวลาที่ใช้แจ้งเตือนจริงเรียกว่า:

> **Effective Notification Time**

มาจาก:

```text
Activity-specific Override
        ↓
ถ้ามี → ใช้ Override

ถ้าไม่มี
        ↓
System Notification Default
```

ดังนั้น:

```text
Effective Notification
=
Activity Override
หรือ
System Default
```

---

# 8.34 Time-Specific Activity Notification

สำหรับ Activity ที่มี Start Time:

> System Default = แจ้งเตือนก่อนเริ่มกิจกรรมตามเวลาที่กำหนด

ค่า MVP เบื้องต้น:

```text
60 minutes before
```

เช่น:

```text
Activity Start = 09:00
Notification = 08:00
```

ค่าดังกล่าวเป็น **Configurable System Default** ไม่ใช่ค่าที่ผู้ใช้ถูกบังคับให้ใช้ตลอดไป

---

# 8.35 Date-Only Activity Notification

สำหรับ Activity ที่มีวันที่แต่ยังไม่มี Start Time:

> System Default Notification Time = 06:00 ของวันนั้น

ตัวอย่าง:

```text
Date = 10 October
Start = Unknown
Notification = 10 October 06:00
```

สำคัญ:

```text
06:00
= Notification Time

ไม่ใช่
Activity Start Time
```

Activity ยังคงเป็น Date-Only / Unscheduled ใน Calendar

---

# 8.36 User Notification Default

User สามารถแก้ System Default ได้

ตัวอย่าง:

```text
Date-only default
06:00 → 08:00
```

หรือ:

```text
Time-specific default
60 min → 30 min
```

การเปลี่ยน System Default มีผลกับ Activity ที่:

```text
ไม่มี Activity-level Override
```

เท่านั้น

---

# 8.37 Activity Notification Override

Activity บางรายการสามารถกำหนด Notification Override ของตนเอง

ตัวอย่าง:

```text
System Default = 60 min before

Activity A
Override = 120 min before
```

Effective:

```text
Activity A
= 120 min before
```

ไม่ใช้ 60 นาที

---

# 8.38 Notification Priority

Priority:

```text
Activity Override
       ↓
System Default
```

ไม่มีการ Override:

```text
Use System Default
```

มี Override:

```text
Use Activity Override
```

---

# 8.39 Notification Time Constraint

ต้องมี:

```text
Notification Time ≤ Activity Start Time
```

เสมอ สำหรับ Activity ที่มี Start Time

ตัวอย่าง Valid:

```text
Activity = 12:00
Notification = 11:30
```

ตัวอย่าง Invalid:

```text
Activity = 12:00
Notification = 12:30
```

---

# 8.40 Invalid Custom Notification

หาก User กำหนด:

```text
Activity Start = 12:00
Custom Notification = 12:30
```

ระบบต้องไม่ยอมรับค่าอย่างเงียบ ๆ

ต้อง:

```text
Validation Error
```

และให้ User แก้ไข

---

# 8.41 Notification and Replanning

เมื่อ Replanning สร้าง Proposal ใหม่:

```text
Proposal
→ No Notification Change
```

หลัง User Confirm:

```text
New Schedule Version
→ Synchronize Notifications
```

ดังนั้น:

```text
Replanning
≠
Notification Update
```

จนกว่าจะมี Confirmation

---

# 8.42 Notification Synchronization

หลัง Confirmed Schedule เปลี่ยน:

```text
New Confirmed Schedule
       ↓
Compare With Current Local Notifications
       ↓
Cancel obsolete notifications
       ↓
Create / Reschedule effective notifications
```

ตัวอย่าง:

```text
Old:
Activity = 09:00
Notification = 08:00

New:
Activity = 12:00
Notification = 11:00
```

Mobile:

```text
Cancel 08:00 notification
Schedule 11:00 notification
```

Expo รองรับทั้งการ Schedule Notification และยกเลิก Notification เฉพาะรายการด้วย Identifier ที่ได้จากการ Schedule ([Expo Notifications Documentation](https://docs.expo.dev/versions/v56.0.0/sdk/notifications/))

---

# 8.43 Notification Synchronization Scope

Mobile ไม่จำเป็นต้องยกเลิก Notification ทั้งหมดทุกครั้งที่ Schedule เปลี่ยน

ควรปรับเฉพาะ Notification ที่ได้รับผลกระทบ เช่น:

* Activity moved
* Activity cancelled
* Notification Override changed
* System Default changedสำหรับ Activity ที่ไม่มี Override
* Activity date changed
* Activity time changed

---

# 8.44 Local Notification Identifier

`expo-notifications` คืน Identifier สำหรับ Notification ที่ Schedule แล้ว และ Identifier นี้สามารถใช้ยกเลิก Notification รายการนั้นได้ ([Expo Notifications Documentation](https://docs.expo.dev/versions/v56.0.0/sdk/notifications/))

LONGTUA จึงกำหนดให้:

```text
Local Notification Identifier
= Device-side State
```

ไม่ใช่ Backend Business Entity

---

# 8.45 Why Notification Instance Is Not a Database Table

Notification Identifier ผูกกับ Notification ที่ Schedule บนอุปกรณ์

ดังนั้น MVP ไม่จำเป็นต้องสร้าง:

```text
notification_instances
```

ใน PostgreSQL

Backend เก็บ:

```text
Schedule
+
Notification Policy
+
Override
```

Mobile จัดการ:

```text
Local Notification Identifier
```

---

# 8.46 Notification Mapping

Mobile สามารถรักษา Local Mapping เชิงแนวคิด:

```text
Schedule Item ID
        ↓
Local Notification ID
```

เช่น:

```text
Schedule Item A
→ notification-id-123

Schedule Item B
→ notification-id-456
```

หาก Schedule Item A เปลี่ยน:

```text
Schedule Item A
→ cancel notification-id-123
→ create new notification-id
```

---

# 8.47 Notification on Activity Cancellation

เมื่อ Activity ที่มี Notification ถูก Cancel และการ Cancel ได้รับการ Confirm:

```text
Confirmed Schedule
       ↓
Activity removed from Current Schedule
       ↓
Cancel corresponding local notification
```

Historical Schedule Version ยังคงเก็บ Activity Placement เดิมตาม Version ที่สร้างไว้ก่อนหน้านั้น

---

# 8.48 Notification on Activity Rescheduling

เมื่อ Activity ถูกเลื่อน:

```text
Old Schedule
09:00

New Confirmed Schedule
12:00
```

Notification ต้องปรับตาม:

```text
Old Notification
08:00
```

ถูกยกเลิก และสร้าง Effective Notification ใหม่ เช่น:

```text
11:00
```

---

# 8.49 Notification on System Default Change

สมมติ:

```text
System Default = 60 min
```

User เปลี่ยนเป็น:

```text
30 min
```

Activity ที่ไม่มี Custom Override:

```text
09:00
→ Notification 08:30
```

ต้องถูกปรับ

แต่:

```text
Activity Override = 120 min
```

ไม่ควรเปลี่ยน เพราะ Activity Override มี Priority สูงกว่า

---

# 8.50 Notification on Override Change

หาก Activity มี:

```text
Override = 120 min
```

แล้ว User เปลี่ยนเป็น:

```text
Override = 30 min
```

หลัง Confirmation ของ Setting/Activity:

```text
Old Notification
→ Cancel

New Notification
→ Schedule
```

---

# 8.51 Notification Permission

การสร้าง Local Notification ขึ้นอยู่กับการอนุญาตและพฤติกรรมของระบบปฏิบัติการด้วย ดังนั้นการที่ Schedule ถูก Confirm ไม่ได้หมายความว่า Notification จะถูกแสดงต่อ User เสมอ

สถาปัตยกรรมจึงแยก:

```text
Schedule State
```

ออกจาก:

```text
Notification Delivery State
```

หลักคือ:

> **Schedule Correctness ไม่ขึ้นกับ Notification Delivery Success**

---

# 8.52 Notification Failure

ตัวอย่าง Failure:

* Permission denied
* Schedule Notification API Error
* Invalid Trigger
* Local Notification Not Scheduled
* Notification Cancel Failure
* Device-specific limitation

เมื่อเกิด Failure:

```text
Confirmed Schedule
= ไม่เปลี่ยน
```

ระบบสามารถ:

* แจ้ง User
* Log Error
* Retry Synchronization ตามความเหมาะสม

แต่ไม่ Rollback Schedule

---

# 8.53 Notification Synchronization Failure

ตัวอย่าง:

```text
Schedule Confirmed
        ↓
Notification Update
        ↓
Error
```

ผล:

```text
Schedule = New Version
Notification = Out of Sync
```

สถานะดังกล่าวต้องถูกมองเป็น:

> Derived-State Synchronization Problem

ไม่ใช่ Schedule Transaction Failure

---

# 8.54 Schedule Confirmation Transaction

การ Confirm ควรมี Transaction Boundary:

```text
BEGIN TRANSACTION
        ↓
Validate Confirmation
        ↓
Verify Source Schedule Version
        ↓
Create New Schedule Version
        ↓
Create Schedule Items
        ↓
Update Proposal / Confirmation State
        ↓
COMMIT
```

หลัง Commit แล้วจึงให้ Mobile Synchronize Notification

ไม่ควรเปิด Database Transaction ค้างไว้ระหว่างการ Schedule Local Notification

---

# 8.55 Why Notification Is Outside Schedule Transaction

Local Notification ทำงานบน Device

Database Transaction ทำงานบน Backend

ดังนั้น:

```text
Backend Transaction
≠
Mobile Notification Operation
```

หาก Mobile Notification ล้มเหลวหลัง Commit:

```text
Schedule Version
ยังคงถูกต้อง
```

จึงต้องไม่ Rollback Backend Schedule เพื่อให้ตรงกับ Mobile Notification

---

# 8.56 Calendar and Confirmed Schedule

Calendar ควรอ่านข้อมูลจาก:

```text
Current Schedule Version
```

ไม่ใช่จาก:

```text
Proposal
```

ดังนั้น Proposal ที่กำลังรอ User Review ไม่ควรทำให้ Calendar Current View เปลี่ยนถาวร

---

# 8.57 Proposal Preview

เมื่อ User เปิด Proposal:

```text
Current Schedule
+
Proposed Changes
```

สามารถแสดง:

```text
Added
Moved
Removed
Unchanged
```

แต่เป็น Preview

Current Schedule ยังคงเป็น Version เดิม

---

# 8.58 Proposal Confirmation Effect

เมื่อ User Confirm:

```text
Proposal
       ↓
New Schedule Version
       ↓
Current Schedule changes
       ↓
Calendar reflects new Version
       ↓
Notification synchronization
```

นี่คือจุดเดียวที่ Proposed Schedule กลายเป็น Confirmed Schedule

---

# 8.59 Reject Effect

เมื่อ User Reject:

```text
Proposal
→ REJECTED
```

ผล:

```text
Current Schedule
= unchanged

Current Notifications
= unchanged
```

---

# 8.60 Invalidated Effect

เมื่อ Proposal ถูก Invalidated:

```text
Proposal
→ INVALIDATED
```

ไม่สามารถ Confirm ได้

Current Schedule ไม่เปลี่ยน

Notifications ไม่เปลี่ยน

---

# 8.61 Manual Edit Effect

เมื่อ User Manual Edit:

```text
Current Schedule
→ Draft
```

ระหว่าง Draft:

```text
Calendar current confirmed state
= unchanged
```

หาก User Confirm:

```text
New Schedule Version
```

หาก User Discard:

```text
Current Schedule
= unchanged
```

---

# 8.62 Replanning Effect

เมื่อ Replanning เกิดขึ้น:

```text
Current Schedule
→ Used as Reference
```

ไม่ได้ถูกเขียนทับทันที

ผล:

```text
New Proposal
```

เท่านั้น

---

# 8.63 Replanning Failure Effect

ถ้า Replanning:

```text
NO_FEASIBLE_PLAN
```

หรือ:

```text
UNKNOWN
```

และไม่มี Valid Feasible Candidate:

```text
Current Schedule
= unchanged
```

Notification:

```text
unchanged
```

---

# 8.64 No Feasible Schedule and Current State

สำคัญมาก:

> การที่ “แผนใหม่จัดไม่ได้” ไม่ได้หมายความว่า “ตารางปัจจุบันถูกลบ”

ตัวอย่าง:

```text
Current Schedule = V5

New Requirement
→ No Feasible Replan
```

ผล:

```text
Current Schedule = V5
```

ยังคงอยู่

User สามารถกลับไปแก้ Requirement หรือ Constraint แล้วลองใหม่

---

# 8.65 Schedule State Machine

```text
                CONFIRMED
                    |
              Manual Edit
                    v
                  DRAFT
                 /     \
          Conflict     Valid
             |            |
             |          Confirm
             |            |
             |            v
             |      NEW VERSION
             |            |
             +------------+
```

Proposal Flow:

```text
PLANNING
   ↓
PROPOSAL
   |
   +── REJECTED
   |
   +── INVALIDATED
   |
   +── CONFIRMED
           ↓
       NEW VERSION
```

---

# 8.66 Combined State Model

```text
                    Planning
                       |
                       v
                    Proposal
                   /   |   \
                  /    |    \
            Reject  Feedback  Confirm
              |        |        |
              v        v        v
             End    Replanning  New Version
                         |          |
                         v          v
                      Proposal   Current
                                  Schedule
                                      |
                                      v
                                  Notification
```

---

# 8.67 Schedule Change Categories

Schedule Change สามารถจำแนกเป็น:

```text
ADDED
MOVED
RESIZED
REMOVED
UNCHANGED
```

### ADDED

Activity ใหม่ถูกเพิ่ม

### MOVED

Start/End เปลี่ยน

### RESIZED

Duration เปลี่ยน

### REMOVED

Activity ถูกนำออกจาก Current Schedule

### UNCHANGED

Placement ยังคงเดิม

---

# 8.68 Change Representation

ตัวอย่าง:

```text
Study
14:00–16:00
→
16:00–18:00
```

แสดง:

```text
MOVED
```

ถ้า:

```text
Study
14:00–16:00
```

ยังอยู่:

```text
UNCHANGED
```

หาก Activity ใหม่:

```text
Meeting
18:00–19:00
```

แสดง:

```text
ADDED
```

---

# 8.69 Before / After Comparison

สำหรับ Replanning Proposal:

```text
Before
+
After
```

สามารถใช้เพื่อ:

* User Review
* Explainability
* Evaluation
* Stability Analysis

โดยไม่ต้องแสดงรายละเอียด CP-SAT ภายในแก่ User

---

# 8.70 Explainable Schedule Changes

User ควรสามารถเข้าใจได้อย่างน้อยว่า:

```text
อะไรเปลี่ยน
เมื่อใดเปลี่ยน
และผลกระทบคืออะไร
```

ตัวอย่าง:

> “ประชุมถูกเลื่อนเป็น 16:00 ทำให้เวลาทำรายงานถูกย้ายไป 14:00”

ไม่จำเป็นต้องแสดง Constraint Solver ทั้งหมด

---

# 8.71 Schedule Stability Presentation

ใน Proposal สามารถแสดง:

```text
3 activities unchanged
1 activity moved
1 activity added
```

แทนการแสดงเพียงว่าตารางใหม่ต่างจากเดิม

ข้อมูลดังกล่าวสอดคล้องกับ Stability Evaluation

---

# 8.72 Notification Presentation

Notification เป็น Presentation/Device Concern

User อาจเห็น:

```text
08:00
เตรียมตัวประชุม
```

แต่ Calendar ต้องแสดง:

```text
09:00–10:00
ประชุม
```

อีกครั้ง:

```text
Notification Time
≠
Schedule Time
```

---

# 8.73 Schedule and Notification Data Separation

Backend:

```text
Schedule
Schedule Version
Schedule Item
Notification Policy
Notification Override
```

Mobile:

```text
Local Notification Identifier
Scheduled Notification
Notification Permission / Device State
```

ไม่ควรทำให้ Notification Instance บน Mobile กลายเป็น Source of Truth ของ Backend

---

# 8.74 Notification Synchronization on App State

เมื่อ Mobile เปิด Application หรือกลับเข้าสู่ Active State สามารถตรวจสอบความสอดคล้องระหว่าง:

```text
Current Backend Schedule
vs
Local Notification State
```

ตามความเหมาะสม

หากพบความแตกต่าง:

```text
Synchronize
```

การทำ Synchronization เป็น Device-side Reliability Mechanism และไม่เปลี่ยน Backend Schedule

---

# 8.75 App Reinstallation Consideration

Local Notification State เป็น Device-side State และอาจไม่ตรงกับ Backend หลังการติดตั้ง/ลบ Application

ดังนั้น Mobile ควรสามารถ:

```text
Fetch Current Confirmed Schedule
      ↓
Rebuild Local Notification State
```

ตาม Effective Notification Policy เมื่อจำเป็น

Backend ยังคงเป็น Source of Truth ของ Schedule

---

# 8.76 Notification Scheduling Scope

MVP ไม่จำเป็นต้อง Schedule Notification สำหรับ Activity ที่:

* อยู่ใน Proposal
* อยู่ใน Draft
* ถูก Rejected
* ถูก Invalidated
* ถูก Cancelled
* อยู่ใน Historical Version แต่ไม่อยู่ใน Current Version

เฉพาะ:

```text
Current Confirmed Schedule
```

ที่มี Effective Notification เท่านั้น

---

# 8.77 Notification Policy and Optional Activity

หาก Optional Activity ไม่ถูกนำไปอยู่ใน Current Confirmed Schedule:

```text
No Schedule Item
→ No Notification
```

หาก Optional Activity ถูก Schedule และ Confirmed:

```text
Schedule Item exists
→ Notification may be created
```

ตาม Notification Policy

---

# 8.78 Notification and Date-Only Activity

Date-only Activity:

```text
Date known
Start unknown
```

สามารถมี Notification:

```text
Notification = 06:00 default
```

แต่ยังคง:

```text
Activity Start = Unknown
```

และ:

```text
Calendar = All Day / Unscheduled
```

---

# 8.79 Notification and Approximate Time

หาก Activity มี Approximate Time:

```text
“ประมาณบ่ายสอง”
```

ระบบต้องรักษาว่าเวลานั้นเป็น Approximate ใน Domain Model

การตั้ง Notification ต้องไม่เปลี่ยน Semantic Information จาก Approximate เป็น Exact โดยอัตโนมัติ

Effective Notification Policy ต้องพิจารณาว่ามี Concrete Start Time ที่ใช้ Schedule Notification ได้หรือไม่

หากไม่มีเวลาที่สามารถใช้ได้อย่างถูกต้อง ระบบไม่ควรสร้าง Trigger แบบเดาสุ่ม

---

# 8.80 Notification Policy for Changed Time

หาก Activity ถูกเลื่อนจาก:

```text
09:00
→
12:00
```

และใช้ System Default:

```text
60 minutes before
```

Effective Notification:

```text
08:00
→
11:00
```

ต้อง:

```text
Cancel old
+
Schedule new
```

หลัง Confirm เท่านั้น

---

# 8.81 Notification Policy for Changed Date

หาก Activity เปลี่ยนจาก:

```text
10 October 09:00
```

เป็น:

```text
11 October 09:00
```

ระบบต้อง:

```text
Cancel old notification
Schedule new notification
```

หลัง Confirmed Schedule เปลี่ยน

---

# 8.82 Notification Policy for Cancelled Activity

หาก Activity ถูก Cancel และ Confirmation เสร็จสมบูรณ์:

```text
Current Schedule
→ Activity removed
```

จากนั้น:

```text
Cancel corresponding local notification
```

---

# 8.83 User Control and Notification

User มีอำนาจในการตัดสินใจ Schedule

แต่ Notification เป็นผลจาก Schedule

ดังนั้น:

```text
User confirms schedule
        ↓
System derives notification
```

ไม่ใช่:

```text
Notification system decides schedule
```

---

# 8.84 Schedule Consistency Rules

Schedule ต้องปฏิบัติตาม:

```text
SC-01
Only explicit confirmation can create a new Current Schedule Version.

SC-02
Historical Schedule Versions are immutable.

SC-03
Current Schedule is derived from the latest current Version.

SC-04
Proposal is never Current Schedule before confirmation.

SC-05
Draft is never Current Schedule before confirmation.

SC-06
A stale Proposal cannot override the Current Version.

SC-07
Every Current Schedule Item must satisfy Domain Constraints.

SC-08
Date-only Activity does not gain a Start Time from Notification Policy.

SC-09
Notification Time is separate from Activity Time.

SC-10
Notification is derived from Confirmed Schedule.

SC-11
Notification failure does not invalidate Schedule.

SC-12
Rejected / Invalidated Proposals cannot create Notifications.

SC-13
Historical Versions do not create current-device Notifications.

SC-14
Manual Draft conflicts block confirmation.

SC-15
Adjacent intervals are allowed when end equals next start.
```

---

# 8.85 Notification Consistency Rules

```text
NC-01
Only Current Confirmed Schedule produces active local notifications.

NC-02
Activity Override takes precedence over System Default.

NC-03
System Default changes affect activities without Overrides.

NC-04
Notification Time must not be after Activity Start Time when Start Time is known.

NC-05
Invalid notification configuration must be rejected, not silently corrected.

NC-06
Schedule changes require obsolete notifications to be synchronized.

NC-07
Notification identifiers are device-side state in MVP.

NC-08
Backend does not persist notification instances in MVP.

NC-09
Notification delivery failure does not rollback Schedule.

NC-10
Local notification state may be rebuilt from Current Schedule when needed.
```

---

# 8.86 Schedule Management Architecture

```text
                    CURRENT STATE
                         |
                         v
                 +---------------+
                 | Schedule View |
                 +-------+-------+
                         |
           +-------------+-------------+
           |                           |
           v                           v
       Manual Edit                 Replanning
           |                           |
           v                           v
         Draft                      Proposal
           |                           |
           v                           |
       Validate                         |
           |                           |
           +-------------+-------------+
                         |
                         v
                  User Confirmation
                         |
                         v
                Schedule Version N+1
                         |
                         v
                   Current Schedule
                         |
                         v
              Notification Derivation
                         |
                         v
                Local Notification
```

---

# 8.87 Complete Confirmation Flow

## Proposal Confirmation

```text
Proposal
 ↓
Check Proposal Status
 ↓
Check Source Schedule Version
 ↓
Validate Candidate
 ↓
BEGIN TRANSACTION
 ↓
Create New Schedule Version
 ↓
Create Schedule Items
 ↓
Mark Proposal CONFIRMED
 ↓
Update Current Version
 ↓
COMMIT
 ↓
Mobile Synchronization
 ↓
Notification Update
```

## Manual Confirmation

```text
Draft
 ↓
Validate
 ↓
Conflict?
 ├── Yes → Block
 └── No
       ↓
User Confirm
       ↓
BEGIN TRANSACTION
       ↓
Create New Schedule Version
       ↓
Create Schedule Items
       ↓
COMMIT
       ↓
Mobile Notification Synchronization
```

---

# 8.88 Current Schedule Recovery

หาก Mobile State หาย เช่น:

* Application reinstall
* Local State corruption
* Notification data mismatch

ระบบสามารถ:

```text
Fetch Current Confirmed Schedule
        ↓
Reconstruct Calendar State
        ↓
Rebuild Local Notifications
```

โดย:

```text
Backend Schedule
= Source of Truth
```

---

# 8.89 Schedule and Offline Behavior

MVP ไม่กำหนดให้ Mobile สามารถตัดสินใจ Schedule ใหม่แบบ Offline

หากต้องสร้าง/แก้ Confirmed Schedule:

```text
Mobile
→ Backend
```

และผ่าน Confirmation Flow ของระบบ

Local Notification สามารถทำงานบน Device ตาม Schedule ที่ได้รับการ Confirmed แล้ว

---

# 8.90 Evaluation Mapping

Schedule & Notification Design รองรับการประเมิน:

### E3 Replanning

* Changed Activity Count
* Start-Time Deviation
* Unaffected Preservation
* Constraint Preservation

### E4 Candidate

* Candidate Feasibility
* Candidate Quality
* Candidate Diversity

### E5 Human-in-the-Loop

* User Acceptance
* User Correction
* Confirmation Effort
* Interaction Effort

### E6 End-to-End

```text
Natural Language
→ Proposal
→ Confirmation
→ Schedule
→ Notification
```

สามารถทดสอบเป็น End-to-End Flow ได้

---

# 8.91 Error Taxonomy

Schedule / Notification Errors แบ่งเป็น:

```text
S1 Invalid Schedule Placement
S2 Draft Conflict
S3 Stale Proposal
S4 Version Transition Failure
S5 Schedule Persistence Failure
S6 Notification Permission Failure
S7 Notification Scheduling Failure
S8 Notification Cancellation Failure
S9 Notification Synchronization Failure
S10 Incorrect Date-only Handling
S11 Incorrect Override Priority
S12 Invalid Notification Time
S13 Historical Version Mutation
S14 Current Version Inconsistency
```

การจำแนก Error ช่วยแยก:

```text
Schedule Error
vs
Notification Error
```

ออกจากกัน

---

# 8.92 Design Rationale

## Rationale 1 — Schedule as Source of Truth

ช่วยให้ Schedule และ Notification ไม่กลายเป็นสองแหล่งความจริงที่ขัดกัน

## Rationale 2 — Immutable Schedule Versions

ช่วยรักษา Historical State และรองรับ Stale Proposal Detection

## Rationale 3 — Draft Before Manual Confirmation

ป้องกันการแก้ Confirmed Schedule ระหว่างที่ User ยังอยู่ระหว่างการทดลองแก้ไข

## Rationale 4 — Proposal Before Confirmation

รักษา Human-in-the-Loop และให้ User ตรวจผลก่อน Commit

## Rationale 5 — Notification as Derived State

ลดความซับซ้อนของ Backend และทำให้ Device-specific Notification State ไม่ปะปนกับ Scheduling State

## Rationale 6 — Local Notification for MVP

ลด Infrastructure Complexity เนื่องจากระบบไม่จำเป็นต้องมี Remote Push Delivery ใน Core Contribution

## Rationale 7 — Device-side Notification Identifier

Notification Identifier ที่ได้รับจาก Expo เป็นข้อมูลที่เกี่ยวข้องกับการจัดการ Scheduled Notification บนอุปกรณ์ จึงไม่จำเป็นต้องทำเป็น Persistent Business Entity ของ Backend ([Expo Notifications Documentation](https://docs.expo.dev/versions/v56.0.0/sdk/notifications/))

---

# 8.93 Schedule & Notification Invariants

แกนสำคัญของระบบ:

```text
Schedule INV-01
Confirmed Schedule is the source of truth.

Schedule INV-02
Proposal is not Confirmed Schedule.

Schedule INV-03
Draft is not Confirmed Schedule.

Schedule INV-04
Only Explicit User Confirmation creates a new current version.

Schedule INV-05
Historical Versions are immutable.

Schedule INV-06
Stale Proposal cannot override Current Schedule.

Schedule INV-07
Draft Conflict blocks Confirmation.

Schedule INV-08
Replanning failure leaves Current Schedule unchanged.

Notification INV-01
Only Current Confirmed Schedule creates active notifications.

Notification INV-02
Notification is derived state.

Notification INV-03
Notification time is not Activity start time.

Notification INV-04
Activity Override takes precedence over System Default.

Notification INV-05
Notification failure does not rollback Schedule.

Notification INV-06
Notification state remains device-side in MVP.

Notification INV-07
Notification changes are applied only after Schedule Confirmation.

Notification INV-08
Date-only Notification Time does not become Activity Start Time.
```

---

# 8.94 Complete Schedule Lifecycle

```text
                    ACTIVITY
                        |
                        v
                Planning / Manual
                        |
                        v
                 Candidate / Draft
                        |
                        v
                    Validation
                        |
                        v
                  USER CONFIRM
                        |
                        v
                SCHEDULE VERSION
                        |
                        v
             CURRENT CONFIRMED SCHEDULE
                        |
             +----------+----------+
             |                     |
             v                     v
         Calendar               Notification
             |                     |
             |                Local Device State
             |                     |
             +----------+----------+
                        |
                        v
                    Change
                        |
                +-------+-------+
                |               |
          Manual Edit       Replanning
                |               |
                v               v
              Draft          Proposal
                |               |
                +-------+-------+
                        |
                        v
                 USER CONFIRM
                        |
                        v
               NEW SCHEDULE VERSION
```

---

# 8.95 Summary

Schedule System ของ LONGTUA มีหลักการสำคัญ 4 ประการ:

### 1. Schedule Is the Truth

Confirmed Schedule เป็น Source of Truth

### 2. Version Is Immutable

ทุกการเปลี่ยนที่ Confirmed ต้องสร้าง Version ใหม่ และ Version เดิมไม่ถูกแก้

### 3. User Controls Commitment

Proposal และ Draft ยังไม่เปลี่ยน Current Schedule จนกว่า User จะ Confirm

### 4. Notification Is Derived

Notification สร้างจาก Current Confirmed Schedule และถูก Synchronize เมื่อ Schedule เปลี่ยน

ดังนั้นกระบวนการทั้งหมดของ LONGTUA สามารถสรุปได้ว่า:

```text
Plan
 ↓
Propose
 ↓
Review
 ↓
Confirm
 ↓
Version
 ↓
Schedule
 ↓
Notify
```

และเมื่อสถานการณ์เปลี่ยน:

```text
Change
 ↓
Replan / Edit
 ↓
New Proposal / Draft
 ↓
Review
 ↓
Confirm
 ↓
New Version
 ↓
Resynchronize Notifications
```

หลักการนี้ทำให้ LONGTUA สามารถรักษา **Human-in-the-Loop, Schedule Consistency, Historical State, Replanning และ Device Notification** ให้แยกจากกันอย่างชัดเจน
