# 11. Security Design

## 11.1 Purpose

เอกสารฉบับนี้กำหนดแนวทางด้าน Security ของ LONGTUA — Personal Adaptive Planner เพื่อปกป้อง:

* User Account
* Authentication Credentials
* Access Tokens
* User-owned Planning Data
* Schedule Data
* AI-related Data
* Database
* API
* Notification-related Information
* Historical Schedule
* System Secrets

เอกสารนี้เป็น Security Baseline สำหรับ:

* Mobile Application
* Backend API
* Authentication
* Database
* AI/NLP
* Planning Engine
* Schedule Management
* Deployment
* Logging
* Testing

เป้าหมายหลักคือ:

> **ผู้ใช้ต้องสามารถเข้าถึงและแก้ไขเฉพาะข้อมูลที่ตนเองมีสิทธิ์ ระบบต้องไม่เปิดเผย Secret และ AI ต้องได้รับเฉพาะข้อมูลที่จำเป็นต่อการประมวลผล**

---

# 11.2 Security Objectives

LONGTUA ให้ความสำคัญกับหลักการต่อไปนี้

### SO-01 — Confidentiality

ป้องกันไม่ให้ User หรือ Component ที่ไม่มีสิทธิ์เข้าถึงข้อมูลของผู้อื่น

### SO-02 — Integrity

ป้องกันการเปลี่ยนแปลง Schedule และข้อมูลสำคัญโดยไม่ได้รับอนุญาต

### SO-03 — Authentication

ตรวจสอบว่าผู้ใช้เป็นเจ้าของ Account จริงก่อนเข้าถึง Protected Resources

### SO-04 — Authorization

ตรวจสอบสิทธิ์ของ User ต่อ Resource ทุกครั้ง

### SO-05 — Credential Protection

Password, Token และ Secret ต้องไม่ถูกเก็บหรือส่งโดยไม่ปลอดภัย

### SO-06 — AI Isolation

AI Provider ต้องไม่เข้าถึง Database หรือ Secret โดยตรง

### SO-07 — Schedule Integrity

Confirmed Schedule ต้องไม่ถูกเปลี่ยนโดย AI หรือ Backend Process โดยไม่มี Explicit User Confirmation

### SO-08 — Privacy-Aware Context

AI ต้องได้รับเฉพาะ Relevant Context ที่จำเป็น

### SO-09 — Error Safety

Error Response ต้องไม่เปิดเผย Internal Secret หรือ Sensitive Information

### SO-10 — Auditability

Critical State Transition ต้องสามารถ Trace ได้อย่างเหมาะสมผ่าน Request ID, Schedule Version และ Planning Request

---

# 11.3 Security Architecture

Security ของ LONGTUA ใช้หลายชั้น:

```text
+------------------------+
| Mobile Application     |
| Secure Token Storage   |
+-----------+------------+
            |
          HTTPS
            |
            v
+------------------------+
| API / Authentication   |
+-----------+------------+
            |
            v
+------------------------+
| Authorization          |
| Ownership Check        |
+-----------+------------+
            |
            v
+------------------------+
| Input / Domain         |
| Validation             |
+-----------+------------+
            |
       +----+----+
       |         |
       v         v
     AI/NLP   Application
       |         |
       |         v
       |    Planning Core
       |         |
       +----+----+
            |
            v
+------------------------+
| Persistence Layer      |
+-----------+------------+
            |
            v
+------------------------+
| PostgreSQL             |
+------------------------+
```

Security ไม่ได้พึ่ง Authentication เพียงอย่างเดียว แต่ต้องตรวจสอบ Authorization, Input Validation และ Domain Rules ต่อเนื่องกัน

---

# 11.4 Security Boundaries

LONGTUA มี Security Boundary หลักดังนี้:

```text
User
  ↓
Mobile
  ↓
HTTPS
  ↓
Backend API
  ↓
Application
  ↓
AI / Planner / Database
```

แต่ละ Boundary มีความรับผิดชอบต่างกัน

### Mobile Boundary

ป้องกัน Credential และ Client State

### API Boundary

Authentication, Authorization และ Input Validation

### Application Boundary

Business Rule Enforcement

### AI Boundary

Controlled Data Access และ Output Validation

### Database Boundary

Persistence Integrity และ Ownership-related Data Structure

---

# 11.5 Threat Model Scope

MVP พิจารณาภัยคุกคามหลัก:

```text
T1 Unauthorized Account Access
T2 Token Theft / Misuse
T3 Broken Object-Level Authorization
T4 Malicious / Invalid API Input
T5 Prompt Injection / AI Manipulation
T6 AI Hallucination / Unsupported Inference
T7 Secret Leakage
T8 SQL / Injection-style Input Abuse
T9 Excessive API Requests
T10 Schedule Tampering
T11 Stale Proposal Override
T12 Information Leakage Through Errors
T13 Sensitive Data Leakage Through Logs
T14 Cross-user Data Access
T15 Notification-related State Inconsistency
```

Threat ที่อยู่นอก MVP เช่น Advanced Device Compromise หรือ Enterprise-grade Security Monitoring ไม่ถือเป็น Core Scope แต่ต้องไม่ทำให้ระบบออกแบบผิดหลักพื้นฐาน

---

# 11.6 Authentication Model

LONGTUA ใช้:

> **Email + Password**

ใน MVP

ไม่รองรับ:

* Google Login
* Apple Login
* Facebook Login
* MFA
* Social Account Linking

ใน MVP

---

# 11.7 Password Security

Password ต้อง:

* ไม่เก็บเป็น Plain Text
* ไม่เก็บใน Client-side Persistent Storage
* ไม่ปรากฏใน Log
* ไม่ปรากฏใน Error Response
* ไม่ถูกส่งไปยัง AI Provider

Password Hashing ใช้:

> **Argon2id**

Database เก็บเฉพาะ:

```text id="rtth4m"
password_hash
```

ไม่เก็บ Password เดิม

---

# 11.8 Password Hash Boundary

Flow:

```text
User Password
      ↓
Backend Authentication
      ↓
Argon2id
      ↓
password_hash
      ↓
PostgreSQL
```

ไม่ควร:

```text id="jqprtu"
Mobile
 ↓
Hash
 ↓
Backend
```

เป็นกลไกหลักแทน Server-side Password Verification

Client ต้องใช้ HTTPS เพื่อส่ง Credential อย่างปลอดภัย

---

# 11.9 Password Policy

ระบบต้องมี Password Policy ที่กำหนด:

* Minimum Length
* Allowed Character Rules
* Validation Rules

แต่ค่าตัวเลขที่แน่นอนยังเป็น:

> **Implementation / Security Policy Parameter**

และไม่ควรกำหนดแบบ Arbitrary ใน Design หากไม่ได้มีเหตุผลรองรับ

---

# 11.10 Login Flow

```text id="nmfssq"
User
 ↓
Email + Password
 ↓
HTTPS
 ↓
Backend
 ↓
Find User
 ↓
Verify Password Hash
 ↓
Account Status Check
 ↓
Create Authentication Session
 ↓
Issue Access Token
 ↓
Authenticated Client
```

หาก Credential ไม่ถูกต้อง:

```text id="7k60if"
Authentication Failure
```

ระบบไม่ควรเปิดเผยว่าข้อมูลใดเป็นส่วนที่ผิด เช่น:

> “Email นี้มีอยู่แต่ Password ผิด”

โดยไม่จำเป็น

---

# 11.11 Account Status

Account สามารถมีสถานะ เช่น:

```text id="nzpvgh"
ACTIVE
LOCKED
```

### ACTIVE

สามารถ Authenticate ได้ตาม Policy

### LOCKED

ไม่สามารถ Login/Refresh ตาม Policy

รายละเอียดว่า Account จะเข้าสู่ `LOCKED` ด้วยเงื่อนไขใดต้องกำหนดใน Authentication Policy / Implementation โดยไม่ควรทำเป็น Permanent Lock เพียงจากการ Login ผิดไม่กี่ครั้งโดยไม่มีนโยบายรองรับ

---

# 11.12 Email Verification

Email Verification Token:

* One-Time
* มี Expiration
* เก็บแบบ Hash
* ใช้ซ้ำไม่ได้

Expiration:

> **24 ชั่วโมง**

จาก Authentication Policy ของ MVP

Flow:

```text id="tl6gq4"
Register
 ↓
Create Verification Token
 ↓
Send Verification Message
 ↓
User Opens Link / Submits Token
 ↓
Verify Token
 ↓
Mark Email Verified
```

---

# 11.13 Password Reset

Password Reset Token:

* One-Time
* มี Expiration
* เก็บแบบ Hash
* ใช้ซ้ำไม่ได้

Expiration:

> **30 นาที**

Flow:

```text id="9y2kuv"
Forgot Password
 ↓
Create Reset Token
 ↓
User submits Token
 ↓
Validate
 ↓
Set New Password
 ↓
Revoke Existing Refresh Sessions
```

---

# 11.14 Access Token

Access Token ใช้:

> JWT

Lifetime:

> **15 นาที**

Client ต้องส่ง:

```http id="v4l5ep"
Authorization: Bearer <access_token>
```

Access Token ต้อง:

* มี Expiration
* ไม่ใส่ Sensitive Data โดยไม่จำเป็น
* ตรวจ Signature ฝั่ง Server
* ตรวจ Expiration
* ตรวจ Relevant Claims ตาม Policy

---

# 11.15 JWT Content

JWT ควรเก็บเฉพาะ Claims ที่จำเป็น เช่น:

```text id="l4d8f7"
subject / user identifier
issued-at
expiration
session context ตามความจำเป็น
```

ไม่ควรใส่:

* Password
* Password Hash
* AI API Key
* Database Credential
* Sensitive Planning Data จำนวนมาก

---

# 11.16 Refresh Session

Refresh Session เป็น Backend-managed authentication state

Database:

```text id="th2s8q"
auth_sessions
```

Session ต้องสามารถ:

* Expire
* Revoke
* ตรวจ User
* ตรวจ Lifetime

---

# 11.17 Remember Me Policy

```text id="am9wz9"
Remember Me OFF
→ 7 days

Remember Me ON
→ 30 days
```

เป็น Refresh Session Lifetime

ทั้งสองกรณีต้องอยู่ภายใต้ Absolute Session Lifetime

---

# 11.18 Session Revocation

Refresh Session ต้องสามารถถูก Revoke เมื่อ:

* User Logout
* Session หมดอายุ
* Security Event
* Password Change
* Administrative / System Policy

หลังถูก Revoke:

```text id="mjrs3b"
Refresh
→ Unauthorized
```

---

# 11.19 Password Change Effect

เมื่อ User เปลี่ยน Password สำเร็จ:

```text id="4z2lpo"
Existing Refresh Sessions
        ↓
Revoke
```

จุดประสงค์คือป้องกัน Session เดิมที่อาจถูกเข้าถึงโดยบุคคลอื่น

User ต้อง Authenticate ใหม่ตาม Policy

---

# 11.20 Logout

Logout ต้อง:

```text id="x3ug5o"
Client
→ delete local authentication state

Backend
→ revoke refresh session
```

หากมี Device Session State ที่เกี่ยวข้องต้องถูก Clear / Revoke ตาม Policy

Access Token ซึ่งเป็น Short-lived ไม่จำเป็นต้องถูกเก็บใน Database เพื่อ Revoke ราย Token หากระบบพึ่ง Expiration และ Refresh Session Revocation ตาม Design

---

# 11.21 Secure Token Storage

Mobile ต้องใช้:

> `expo-secure-store`

สำหรับ Token ที่ต้อง Persist บนอุปกรณ์

ไม่ควรเก็บ Authentication Tokens ใน:

* Plain Text File
* General-purpose Async Storage
* Application source code
* Hard-coded Configuration

---

# 11.22 Token Transmission

Token ต้องส่งผ่าน:

> HTTPS

ไม่ควรส่ง Credential หรือ Token ผ่าน:

* HTTP Plain Text
* URL Query Parameter
* Log
* Analytics Payload

---

# 11.23 Token Leakage Prevention

ห้าม Log:

```text id="s4f7ih"
Access Token
Refresh Token
Verification Token
Password Reset Token
Password
API Key
Database Password
JWT Signing Secret
```

รวมถึงไม่ควรใส่ลง Exception Stack Trace ที่ Client เห็น

---

# 11.24 Authorization Model

LONGTUA ใช้:

> **Ownership-based Authorization**

หมายถึง User สามารถเข้าถึงเฉพาะ Resource ที่ตนเป็นเจ้าของ

ตัวอย่าง:

```text id="rfim6h"
User A
→ Activity A
✓

User A
→ Activity B owned by User B
✗
```

---

# 11.25 Server-side Authorization

Authorization ต้องตรวจฝั่ง Server ทุกครั้ง

ไม่เชื่อ:

```json id="1tq29z"
{
  "userId": "..."
}
```

จาก Client ว่าเป็น Owner

Authenticated User Identity ต้องมาจาก:

```text id="l6d8d7"
Authentication Context
```

---

# 11.26 Broken Object-Level Authorization Protection

ทุก Resource ที่มี `{id}` ต้องตรวจ:

```text id="r5mw4p"
Resource.id
+
Authenticated User
```

ก่อนอ่าน/แก้ไข/ลบ/Confirm

เช่น:

```text id="e4twis"
/api/proposals/{id}/confirm
```

ต้องตรวจว่า Proposal เป็นของ User จริง

---

# 11.27 Cross-user Access Prevention

ต้องทดสอบอย่างน้อย:

```text id="fi8hhw"
User A → GET User B Activity
User A → PATCH User B Activity
User A → GET User B Proposal
User A → Confirm User B Proposal
User A → GET User B Schedule
User A → Modify User B Availability
```

ทุกกรณีต้องถูกปฏิเสธตาม Authorization Policy

---

# 11.28 Ownership of Relationships

สำหรับ:

```text id="qv0w3l"
container_memberships
temporal_relations
planning_rules
```

ระบบต้องตรวจว่า Objects ทั้งหมดอยู่ใน Ownership Scope เดียวกัน

ตัวอย่าง:

```text id="x7j519"
Container owned by A
Child owned by B
```

ต้องไม่สามารถสร้าง Relationship ได้

---

# 11.29 API Input Validation

ทุก Request ต้องผ่าน:

```text id="3k9u3q"
Schema Validation
      ↓
Domain Validation
      ↓
Business Rule Validation
```

ก่อน Database Operation

---

# 11.30 Input Validation Goals

ป้องกัน:

* Invalid Type
* Invalid Enum
* Invalid Date
* Invalid Duration
* Invalid UUID
* Unexpected Fields
* Oversized Input
* Invalid JSON
* Invalid State Transition

---

# 11.31 SQL Injection Protection

Database Access ต้องใช้:

* SQLAlchemy Parameter Binding
* ORM / Parameterized Queries
* Controlled Query Construction

ไม่ควรประกอบ SQL ด้วย User Input โดยใช้ String Concatenation

ตัวอย่างที่ไม่ควรทำ:

```text id="8hax7a"
"SELECT * FROM activities WHERE id = '" + user_input + "'"
```

Application ต้องควบคุม Query Structure

---

# 11.32 Mass Assignment Protection

Client ไม่ควรสามารถแก้ Field ใดก็ได้เพียงเพราะส่ง Field นั้นมา

เช่น User ไม่ควรแก้:

```text id="csa5gi"
user_id
status ของ Proposal
is_current ของ Schedule Version
created_at
version_number
```

ผ่าน Generic PATCH

Request DTO ต้องกำหนด Allowed Fields อย่างชัดเจน

---

# 11.33 Privilege Boundary

Mobile Client ไม่มีสิทธิ์กำหนด:

* User Ownership
* Schedule Version Current State
* Proposal Status โดยตรง
* Authorization State
* Database IDs ของ Owner
* AI Provider Configuration
* Solver Configuration

สิ่งเหล่านี้ต้องควบคุมฝั่ง Backend

---

# 11.34 AI Data Security Boundary

AI Provider ต้องได้รับเฉพาะข้อมูลที่จำเป็น

Concept:

```text id="5kz4l4"
Database
   ↓
Relevant Context Selection
   ↓
Data Minimization
   ↓
AI Provider
```

ไม่ใช่:

```text id="2hu4cq"
Database
   ↓
Entire User Data
   ↓
AI
```

---

# 11.35 Data Minimization

Context ที่สามารถส่ง AI ได้แก่:

* Current Planning Request
* Relevant Activities
* Relevant Rules
* Relevant Availability / Unavailability
* Pending Clarification Context
* Current Proposal Context
* Necessary User Settings

ไม่ควรส่งโดยอัตโนมัติ:

* Password
* Authentication Tokens
* Secret
* Database Credential
* Entire User Database Record
* Unrelated Activity History
* Entire Database
* Entire Conversation History

---

# 11.36 AI Provider Credential Isolation

AI API Key ต้องเก็บ:

> Backend Environment Secret

ไม่อยู่ใน:

* React Native Bundle
* Expo Configuration ที่ส่งไป Client
* Git Repository
* Mobile Source Code

Flow:

```text id="r99ckf"
Mobile
 ↓
Backend
 ↓
AI Provider
```

ไม่ใช่:

```text id="n8nyim"
Mobile
 ↓
AI Provider
```

โดยตรง

---

# 11.37 AI Prompt Injection Protection

Natural Language Input ถือเป็น:

> **Untrusted User Data**

ดังนั้นข้อความของ User ไม่ควรถูกถือเป็น System Instruction

AI Layer ต้องออกแบบ Prompt ให้แยก:

```text id="e5g2zq"
System Instructions
+
Domain Rules
+
Schema
+
User Input
+
Relevant Context
```

อย่างชัดเจน

User Input ไม่สามารถเปลี่ยน:

* AI Role
* Output Schema
* Security Rules
* No-Invention Rule
* Tool Permissions

ได้

---

# 11.38 AI Tool Isolation

ใน MVP AI Provider ไม่มีสิทธิ์:

* Query Database
* Execute SQL
* Modify Schedule
* Send Notification
* Modify User Account
* Call Arbitrary Internal API

AI ทำได้เฉพาะ:

> Structured Interpretation

ผ่าน Provider Adapter

---

# 11.39 AI Output Validation

แม้ AI Output มี JSON ถูกต้อง:

```text id="68wev8"
JSON Valid
```

ก็ยังไม่ได้หมายความว่า:

```text id="xhf8c7"
Domain Valid
```

จึงต้อง:

```text id="z68wxc"
AI Output
 ↓
Schema Validation
 ↓
Domain Validation
 ↓
Planning Readiness
```

---

# 11.40 AI Hallucination Protection

Planning-Critical Fields ต้องไม่ถูกสร้างขึ้นโดยไม่มี Evidence

เช่น:

* Date
* Exact Time
* Duration
* Deadline
* Fixed Time
* Required Relation

ที่มาได้เพียง:

```text id="2ye3sl"
User Input
หรือ
Relevant Context
หรือ
Explicit System Policy
```

ไม่ใช่ Model Guess

---

# 11.41 Evidence Boundary

ตัวอย่าง:

```text id="o8xw6n"
User:
“ช่วงบ่าย”
```

Source:

```text id="6c6t6k"
Time Window = User Input
```

จากนั้น:

```text id="etphaf"
AFTERNOON
→ Concrete Time Range
```

มาจาก:

```text id="mtr4j8"
System Default / User Override
```

แต่:

```text id="n2s9oh"
Actual Activity Start = 14:00
```

มาจาก:

```text id="p7b9w0"
Planning Engine
```

ไม่ใช่ AI Extraction

---

# 11.42 AI Output Does Not Commit State

AI Output สามารถนำไป:

```text id="j2ud8g"
Planning Representation
```

แต่ไม่สามารถ:

```text id="vg6z8m"
Create Confirmed Schedule
```

หรือ:

```text id="5y7rj6"
Change Current Schedule
```

ได้โดยตรง

---

# 11.43 Planning Security Boundary

Planning Core รับ Structured Input เท่านั้น

ต้องไม่มีช่องทางให้ User ป้อน:

```text id="f03z89"
Solver Parameter
Constraint Weight
Objective Value
```

โดยตรงจนสามารถ bypass Business Rule

User Request ต้องถูก:

```text id="fnn2t6"
Interpret
Validate
Normalize
```

ก่อนเข้าสู่ Planner

---

# 11.44 Hard Constraint Integrity

Planning Engine ต้องไม่:

* Relax Hard Constraint แบบเงียบ ๆ
* Remove Required Activity
* Ignore Deadline
* Ignore Unavailability
* Ignore Fixed Time
* Create Invalid Overlap

เพื่อให้ได้ Solution

---

# 11.45 Schedule Integrity

Confirmed Schedule เปลี่ยนได้จาก:

```text id="cr5c3f"
Explicit User Confirmation
```

ผ่าน:

* Proposal Confirmation
* Manual Schedule Confirmation

เท่านั้น

AI Process และ Background Process ไม่สามารถทำ:

```text id="lmxj13"
UPDATE current schedule
```

โดยตรง

---

# 11.46 Schedule Version Integrity

Schedule Version:

* มี Unique Version Number ต่อ User
* Current Version มีได้หนึ่งรายการ
* Historical Version Immutable

Database และ Application ต้องร่วมกันป้องกัน:

```text id="b9f3p9"
Duplicate Current Version
Duplicate Version Number
Historical Mutation
```

---

# 11.47 Stale Proposal Protection

ก่อน Confirm Proposal:

```text id="u57az4"
Proposal.source_schedule_version_id
==
Current Schedule Version ID
```

ถ้าไม่ตรง:

```text id="3uidwa"
STALE_PROPOSAL
```

ระบบต้องไม่สร้าง New Schedule Version

---

# 11.48 Manual Edit Integrity

Manual Edit ต้องเกิดใน Draft

ดังนั้น User สามารถทำ:

```text id="89b8t7"
Draft Conflict
```

ได้ชั่วคราว แต่:

```text id="u2o9vs"
Confirm
= Disabled
```

จนกว่า Conflict หาย

Client ไม่สามารถ bypass Validation ด้วยการส่ง `force=true`

---

# 11.49 API State Transition Security

Client ไม่สามารถเลือก State Transition ที่ไม่ถูกต้อง เช่น:

```text id="nwh5n2"
REJECTED
→ CONFIRMED
```

หรือ:

```text id="fdoxkh"
INVALIDATED
→ CONFIRMED
```

Server ต้องเป็นผู้ควบคุม State Machine

---

# 11.50 Proposal State Security

Allowed:

```text id="d3exi1"
PENDING
 ├── CONFIRMED
 ├── REJECTED
 └── INVALIDATED
```

ไม่อนุญาต Transition ที่ขัดกับ Lifecycle

---

# 11.51 Schedule Version Concurrency

การ Confirm ต้องมี:

```text id="hznp75"
Current Version Check
```

และ Transaction/Lock Strategy ที่เหมาะสม

กรณีสอง Request พร้อมกัน:

```text id="1npxx0"
Confirm A
Confirm B
```

ต้องไม่ทำให้:

```text id="90y1im"
Schedule Version ถูก Commit ซ้ำผิดลำดับ
```

---

# 11.52 Idempotency Security

Idempotency ป้องกัน Duplicate Side Effect เช่น:

```text id="2f8pv7"
Confirm
→ Network Timeout
→ Client Retry
```

Request เดิมที่ใช้ Key เดิม:

```text id="e1j8eh"
→ ไม่สร้าง Version เพิ่ม
```

Key เดิมกับ Payload ต่างกัน:

```text id="y6e6hj"
→ Reject
```

---

# 11.53 Rate Limiting

Rate Limit อย่างน้อยควรครอบคลุม:

```text id="1otudm"
Login
Register
Forgot Password
Planning Request
Clarification
Feedback
Proposal Confirmation
```

เมื่อเกิน Limit:

```text id="o2x2sc"
429 Too Many Requests
```

ค่าจริงเป็น Security/Operational Configuration และต้องปรับตามการทดสอบ

---

# 11.54 Brute-force Protection

Authentication ต้องมีการควบคุมความถี่ของการ Login เพื่อป้องกันการเดา Password

กลไกสามารถประกอบด้วย:

```text id="3ar9sq"
Rate Limiting
+
Authentication Monitoring
+
Temporary Security Response
```

ไม่ควรพึ่ง Account Lock แบบถาวรเป็นวิธีเดียว

---

# 11.55 Abuse Protection for AI / Planning

Planning และ AI Operations มีต้นทุนสูงกว่า CRUD ทั่วไป

จึงควรมี:

```text id="j60g31"
Rate Limit
+
Input Size Limit
+
Planning Object Limit
+
Solver Time Limit
+
AI Context Limit
```

เพื่อป้องกัน Resource Exhaustion

---

# 11.56 Request Size Limits

ระบบต้องกำหนด Maximum Input Size สำหรับ:

* Natural Language Request
* Feedback
* Clarification Response
* API JSON Payload

ค่าจริงเป็น Configuration Parameter

หากเกิน:

```text id="my38kb"
400 / 413
```

ตาม API Contract

---

# 11.57 Planning Resource Limits

Planner ต้องจำกัด:

```text id="xq2r11"
Planning Horizon
Planning Object Count
Solver Time
Candidate Count
```

แต่ห้ามใช้ Limit เพื่อ:

* ตัด Required Activity เงียบ ๆ
* Relax Constraint
* ลดข้อมูลโดยไม่แจ้ง

---

# 11.58 Database Credential Security

PostgreSQL Credential ต้องอยู่ใน Backend Environment Configuration

ไม่อยู่ใน:

* Mobile
* Git
* API Response
* Logs
* AI Prompt

Database Connection ต้องใช้ Least Privilege เท่าที่ Environment รองรับ

---

# 11.59 Environment Secret Management

Secret ได้แก่:

```text id="4dtcyf"
DATABASE_URL / credentials
JWT signing secret
AI Provider Key
Email Service Credentials
Deployment secrets
```

เก็บใน:

> Environment / Secret Management

ไม่ควร Hard-code

Repository ควรมี:

```text id="v7zi75"
.env.example
```

แต่ไม่ควรมี Secret จริง

---

# 11.60 Git Security

ต้องไม่ Commit:

```text id="9gpj5s"
.env
Private Keys
API Keys
Passwords
Tokens
Production Credentials
Database Dumps
```

ควรใช้:

```text id="dbkgx5"
.gitignore
Secret Management
Environment Variables
```

---

# 11.61 Logging Security

Logs ต้องไม่มี:

* Password
* Access Token
* Refresh Token
* Reset Token
* Verification Token
* AI API Key
* Database Credential
* Sensitive User Data ที่ไม่จำเป็น

---

# 11.62 Request ID

ทุก Request ควรมี Trace Identifier เช่น:

```text id="aodgqs"
requestId
```

เพื่อเชื่อม:

```text id="nzv8sn"
API Request
 ↓
Application
 ↓
AI / Planner
 ↓
Database
```

โดย `requestId` ไม่ควรเปิดเผยข้อมูลลับ

---

# 11.63 Error Disclosure

Client ควรได้รับ:

```text id="rrz57e"
Error Code
Safe Message
Relevant Details
Request ID
```

ไม่ควรได้รับ:

```text id="6k7fqt"
Python Stack Trace
Database Query
Internal File Path
Environment Variables
AI Prompt
AI Provider Secret
```

---

# 11.64 Error Message Security

ตัวอย่างที่ไม่ควรส่ง:

> `psycopg2.errors.UniqueViolation on /app/src/...`

ควรส่ง:

```text id="yj5upn"
{
  "error": {
    "code": "CONFLICT",
    "message": "The requested resource conflicts with the current state.",
    "requestId": "..."
  }
}
```

รายละเอียด Debug อยู่ใน Server Logs

---

# 11.65 Database Error Handling

Database Error ต้อง:

```text id="ypw6u6"
Log internally
Return safe response
Rollback transaction
```

ไม่ควรให้ SQL Error หลุดไปยัง Client

---

# 11.66 Transaction Security

Critical State Transition เช่น Confirm ต้องใช้ Transaction:

```text id="b3h9kz"
BEGIN
 ↓
Verify Authorization
 ↓
Verify Current Version
 ↓
Validate
 ↓
Create New Version
 ↓
Create Items
 ↓
Update State
 ↓
COMMIT
```

หากเกิด Error:

```text id="r32kyh"
ROLLBACK
```

---

# 11.67 AI Transaction Isolation

ห้ามเปิด Database Transaction ค้างระหว่าง:

```text id="8s9ydk"
AI API Call
```

หรือ:

```text id="qwew5a"
CP-SAT Solve
```

เพราะเป็น Long-running Operations และเพิ่มความเสี่ยงต่อ Resource Exhaustion/Transaction Contention

---

# 11.68 Notification Security

Notification ต้องอิง:

```text id="5wcq8x"
Current Confirmed Schedule
```

ไม่ใช่ Proposal

Mobile ต้องไม่สร้าง Notification จากข้อมูลที่ User B เป็นเจ้าของ

หลัง Login User ใหม่:

```text id="1p5l7g"
Clear User-specific local state
→ Fetch Current Schedule
→ Rebuild local notifications
```

ตาม Mobile Lifecycle

---

# 11.69 Notification Data Minimization

ข้อความ Notification ไม่ควรเปิดเผยข้อมูลละเอียดเกินจำเป็นในกรณีที่ไม่จำเป็น

ตัวอย่าง:

```text id="gx65tg"
“ถึงเวลาประชุม”
```

อาจเหมาะสมกว่า:

```text id="f9q0av"
“ประชุมกับ Dr. [ชื่อเต็ม/ข้อมูลละเอียด] เกี่ยวกับ [ข้อมูลละเอียด]”
```

โดยเฉพาะข้อมูลที่ User อาจไม่ต้องการแสดงบน Lock Screen

รายละเอียด Notification Content Policy เป็น UX/Privacy Configuration ที่สามารถปรับได้ภายหลัง

---

# 11.70 User Data Privacy Boundary

ข้อมูลประเภท:

* Activity
* Schedule
* Planning Request
* Preferences
* Availability
* Feedback

ถือเป็น User-owned Data

การเข้าถึงต้องผ่าน Authorization

ไม่ควรใช้ข้อมูล User หนึ่งคนไปเป็น Context ของ User อื่น

---

# 11.71 AI Context Isolation Between Users

AI Request ของ User A ต้องไม่ใช้:

```text id="u1p1j0"
User B Context
```

โดยเด็ดขาด

Application ต้อง build Context โดยมี:

```text id="wd7a9h"
Authenticated User ID
```

เป็น Boundary แรกก่อนเลือกข้อมูล

---

# 11.72 Data Retention

MVP ไม่กำหนด Automatic Data Purge สำหรับ:

* Schedule History
* Planning Requests
* Proposals

เพื่อไม่ให้ Historical Evaluation/Trace สูญหายโดยไม่จำเป็น

หากอนาคตมี Data Retention Policy ต้องออกแบบ:

```text id="23tsxa"
Retention
→ Archive
→ Delete
```

อย่างชัดเจนและไม่ทำลายข้อกำหนดด้าน History โดยไม่ตั้งใจ

---

# 11.73 Soft Delete Security

`planning_objects.deleted_at` ใช้สำหรับ Soft Delete

หลัง Soft Delete:

```text id="v2rh6f"
User-facing Active Query
→ exclude
```

แต่:

```text id="2l7lv7"
Historical Schedule Version
→ still resolvable
```

ตาม Domain Policy

---

# 11.74 Historical Schedule Security

Historical Schedule Version ต้องไม่ถูกเปลี่ยนด้วย API CRUD ปกติ

ไม่ควรมี Endpoint เช่น:

```text id="56yvf2"
PATCH /api/schedule/versions/{versionId}
```

ใน MVP

Historical State เปลี่ยนได้เฉพาะผ่านการสร้าง Version ใหม่

---

# 11.75 Direct Database Access

ผู้ใช้ไม่สามารถเข้าถึง Database โดยตรง

และ:

```text id="y0h3eh"
Mobile
```

ไม่มี Database Credentials

เช่นเดียวกับ:

```text id="c3rcjw"
AI Provider
```

ไม่มี Database Credentials

---

# 11.76 Internal API Boundary

Internal Module ไม่ควรใช้ Public API เพื่อ Bypass Security Boundary

เช่น:

```text id="b4l7s2"
AI Module
→ direct SQL
```

หรือ:

```text id="pt5l4r"
Planner
→ direct schedule UPDATE
```

ทุก State Transition สำคัญต้องผ่าน Application/Domain Rules

---

# 11.77 API Documentation Security

OpenAPI Documentation เป็น Development/Integration Tool

ใน Demo/Production:

* ไม่ควรเปิดเผย Secret
* ไม่ควรมี Example Password จริง
* ไม่ควรมี Production Token
* ควรพิจารณาการจำกัดการเข้าถึงเอกสารตาม Deployment Policy

---

# 11.78 CORS

Backend ต้องกำหนด Allowed Origins สำหรับ Environment อย่างชัดเจน

ไม่ควรใช้:

```text id="w2cr1b"
Allow-Origin: *
```

เป็น Production Default หากไม่จำเป็น

Development สามารถมี Configuration ที่แตกต่างจาก Production

---

# 11.79 HTTPS Policy

Demo/Production ต้องใช้:

> **HTTPS**

เพื่อป้องกัน Credential และ Token จากการส่งแบบ Plain Text

Development Localhost สามารถใช้ HTTP ตาม Environment ได้หากไม่มี Credential ถูกส่งออกสู่ Network ที่ไม่ปลอดภัย

---

# 11.80 TLS / Certificate Validation

Mobile และ Backend ต้องใช้ Standard TLS Validation

ไม่ควร Disable Certificate Verification เพียงเพื่อแก้ Development Connectivity Problem แล้วนำ Configuration นั้นไป Production

---

# 11.81 Secure Configuration

Environment-specific Configuration:

```text id="1a62fr"
Development
Testing
Demo / Production
```

ต้องแยกกัน

Production ต้องไม่ใช้:

* Development Database
* Development Secret
* Test AI Key
* Debug mode
* Verbose Sensitive Logging

---

# 11.82 Debug Mode

Production:

```text id="se9xe1"
DEBUG = FALSE
```

ไม่ควรเปิด Debug Endpoint หรือ Detailed Error Page ที่เปิดเผย Internal State

---

# 11.83 Security Monitoring

MVP สามารถเก็บ Security-relevant Operational Events เช่น:

```text id="xj5d20"
Login Failure
Logout
Password Reset
Session Revocation
Authorization Failure
Rate Limit
Critical Confirmation Failure
```

โดยไม่เก็บ Credential หรือ Sensitive Content

---

# 11.84 Suspicious Activity

ระบบสามารถตรวจ Pattern เช่น:

* Login Failed หลายครั้ง
* Planning Request จำนวนมากผิดปกติ
* Repeated Proposal Confirmation Failures
* Repeated Authorization Failure
* Excessive API Usage

และใช้:

```text id="mm2qv8"
Rate Limiting
Temporary Security Response
Monitoring
```

ตาม Policy

---

# 11.85 Security Incident Response

หากพบ Secret Leakage หรือ Credential Compromise:

```text id="3fz4u0"
Identify
 ↓
Revoke / Rotate
 ↓
Contain
 ↓
Investigate
 ↓
Recover
```

ตัวอย่าง:

> AI API Key รั่วใน Git

ต้อง:

1. Revoke/Rotate Key
2. Remove Secret from Active Environment
3. ตรวจ Repository History ตามความเหมาะสม
4. Deploy Credential ใหม่

---

# 11.86 Secret Rotation

Secrets ที่สำคัญควรสามารถเปลี่ยนได้โดยไม่ต้องแก้ Source Code เช่น:

```text id="jh5z4h"
AI API Key
Database Credential
JWT Signing Secret
```

รายละเอียด Rotation Procedure เป็น Deployment Concern

---

# 11.87 Authentication API Security

Authentication Endpoint ต้องมี:

```text id="fjvfp5"
Rate Limiting
Input Validation
Generic Error Response
Secure Transport
Credential Protection
```

โดยเฉพาะ:

```text id="2d1xqr"
/login
/forgot-password
/reset-password
```

เพื่อลด Abuse

---

# 11.88 Password Reset Enumeration Protection

สำหรับ:

```text id="t0fl4x"
POST /api/auth/forgot-password
```

Response ควรหลีกเลี่ยงการเปิดเผยว่า Email มี Account อยู่จริงหรือไม่

เช่นใช้ Response ที่มีความหมาย Generic

เป้าหมายคือป้องกัน Account Enumeration

---

# 11.89 Email Verification Enumeration

ระบบควรจำกัดข้อมูลที่เปิดเผยจาก Verification Endpoint

Error Message ไม่ควรบอกข้อมูลภายในเกินจำเป็น เช่น Token ถูกสร้างเมื่อใดหรือ User มีสถานะเฉพาะอะไร หากไม่จำเป็น

---

# 11.90 Session Security

Session ต้องมี:

```text id="vm5q9p"
User
Created At
Expiration
Absolute Expiration
Revocation State
```

Refresh Session ที่ถูก Revoke ไม่สามารถ Refresh ต่อได้

---

# 11.91 Access Token vs Refresh Session

ต้องแยก:

```text id="ctv96w"
Access Token
= Short-lived authentication credential

Refresh Session
= Long-lived revocable backend session
```

Access Token ไม่ควรถูกใช้เป็นฐานข้อมูล Session แบบถาวร

---

# 11.92 API Authorization Matrix

| Resource              | Authentication | Ownership | State Validation |
| --------------------- | -------------: | --------: | ---------------: |
| Activities            |              ✅ |         ✅ |                ✅ |
| Availability          |              ✅ |         ✅ |                ✅ |
| Planning Request      |              ✅ |         ✅ |                ✅ |
| Proposal              |              ✅ |         ✅ |                ✅ |
| Schedule              |              ✅ |         ✅ |                ✅ |
| User Settings         |              ✅ |         ✅ |                ✅ |
| Schedule Confirmation |              ✅ |         ✅ |                ✅ |
| Proposal Confirmation |              ✅ |         ✅ |                ✅ |

---

# 11.93 Security for Proposal Confirmation

ก่อน Confirm:

```text id="q5fdzg"
Authentication
+
Ownership
+
Proposal Status
+
Candidate Validity
+
Current Schedule Version
+
Domain Validation
```

ต้องผ่านทั้งหมด

---

# 11.94 Security for Manual Confirmation

ก่อน Confirm Draft:

```text id="0j7gnz"
Authentication
+
Ownership
+
Base Version
+
Draft Validation
+
No Hard Conflict
```

ต้องผ่านทั้งหมด

---

# 11.95 Security for Replanning

Replanning ต้องอยู่ใน User Ownership Scope เดียวกัน

Context:

```text id="9xdyka"
Current Schedule
+
Changed Activity
+
Rules
+
Availability
```

ต้องเป็นของ Authenticated User

ไม่สามารถส่ง Object ID ของ User อื่นเพื่อใช้เป็น Replanning Context

---

# 11.96 Security and Stale State

Security ไม่ได้จำกัดเพียง “ใครเข้าได้”

ต้องป้องกัน:

> **User ที่มีสิทธิ์จริง แต่กำลังใช้ State ที่ล้าสมัย**

เช่น:

```text id="v3rcf7"
User owns Proposal A
✓

Proposal A built from V3
Current = V4
✗ Confirm
```

นี่จึงเป็นทั้ง:

* Consistency Control
* Concurrency Protection
* Integrity Protection

---

# 11.97 Mobile Logout Security

เมื่อ Logout:

```text id="m1jn4w"
Delete access token
Delete refresh/session client state
Clear user-specific local state
```

โดยเฉพาะ:

* Cached User Data
* Drafts
* Notification Mapping
* User-specific Application State

ต้องไม่ถูกนำไปแสดงต่อ User คนใหม่ที่ Login บนอุปกรณ์เดิม

---

# 11.98 User Switching

กรณี:

```text id="q70p6j"
User A Logout
User B Login
```

Mobile ต้อง:

```text id="8e7m0l"
Clear A's user context
↓
Authenticate B
↓
Fetch B's schedule / activities
↓
Rebuild B's local notification state
```

ไม่ใช้ Cache ของ A

---

# 11.99 Local Notification Security

Local Notification Mapping:

```text id="2cne45"
Schedule Item ID
→ Local Notification ID
```

ต้องอยู่ใน User/Device Context เดียวกัน

การ Logout หรือเปลี่ยน User ต้องไม่ทำให้:

```text id="he7xs3"
User B
ได้รับ Notification ของ User A
```

---

# 11.100 Security and Offline State

MVP ไม่อนุญาตให้ Mobile สร้าง Confirmed Schedule แบบ Offline แล้ว Commit ภายหลังโดยข้าม Server Authorization/Validation

Local Offline State จึงเป็น:

```text id="flxdt4"
Cache / UI State
```

ไม่ใช่ Source of Truth

---

# 11.101 Security Test Strategy

Security Tests ต้องครอบคลุม:

### Authentication

* Invalid Password
* Expired Access Token
* Revoked Refresh Session
* Expired Verification Token
* Reused Token
* Expired Reset Token
* Password Change Session Revocation

### Authorization

* Cross-user Activity Access
* Cross-user Proposal Access
* Cross-user Schedule Access
* Cross-user Settings Access
* Cross-user Relationship Creation

### API

* Invalid Input
* Mass Assignment
* State Bypass
* Replay
* Rate Limit

### AI

* Prompt Injection
* Invalid Structured Output
* Unsupported Inference
* Cross-user Context Leakage

### Schedule

* Stale Proposal
* Concurrent Confirmation
* Draft Conflict
* Historical Version Mutation

### Secret

* Secret in Client
* Secret in Git
* Secret in Log
* Secret in API Response

---

# 11.102 Authentication Test Cases

ตัวอย่าง:

```text id="jhj9oe"
TC-AUTH-01
Valid Login
→ Success

TC-AUTH-02
Invalid Password
→ Authentication Failure

TC-AUTH-03
Expired Access Token
→ 401

TC-AUTH-04
Revoked Refresh Session
→ 401

TC-AUTH-05
Password Change
→ Existing Refresh Sessions revoked

TC-AUTH-06
Reuse Password Reset Token
→ Reject

TC-AUTH-07
Reuse Email Verification Token
→ Reject
```

---

# 11.103 Authorization Test Cases

```text id="4hh0zv"
TC-AUTHZ-01
User A accesses User B Activity
→ Reject

TC-AUTHZ-02
User A modifies User B Activity
→ Reject

TC-AUTHZ-03
User A confirms User B Proposal
→ Reject

TC-AUTHZ-04
User A accesses User B Schedule
→ Reject

TC-AUTHZ-05
Client sends fake userId
→ Ignore / Reject
```

---

# 11.104 AI Security Test Cases

```text id="lkuyt6"
TC-AI-01
Prompt Injection
→ Schema / Domain Boundary remains enforced

TC-AI-02
AI invents time
→ Validation rejects unsupported information

TC-AI-03
AI outputs invalid JSON
→ Planning not executed

TC-AI-04
AI includes User B data
→ Context construction prevents cross-user data

TC-AI-05
AI requests secret / DB
→ No direct access exists
```

---

# 11.105 Schedule Integrity Test Cases

```text id="hvq9ul"
TC-SCH-01
Confirm Proposal from current version
→ New Version

TC-SCH-02
Confirm stale Proposal
→ Reject

TC-SCH-03
Confirm same Proposal twice
→ No duplicate Version

TC-SCH-04
Modify Historical Version
→ Reject

TC-SCH-05
Confirm conflicting Draft
→ Reject

TC-SCH-06
AI attempts direct schedule change
→ Impossible by Architecture
```

---

# 11.106 Notification Security Test Cases

```text id="1lmwfk"
TC-NOTI-01
Proposal exists
→ No notification

TC-NOTI-02
Proposal rejected
→ No notification change

TC-NOTI-03
Schedule confirmed
→ Notification synchronized

TC-NOTI-04
User logout
→ User-specific local notifications cleared / synchronized by client policy

TC-NOTI-05
User B login on same device
→ User A notification state not reused
```

---

# 11.107 Security and Error Handling Test Cases

```text id="dtm38h"
TC-ERR-01
Database Failure
→ Safe Error

TC-ERR-02
AI Failure
→ No Invalid Schedule

TC-ERR-03
Unexpected Exception
→ No Stack Trace to Client

TC-ERR-04
Authorization Failure
→ No Sensitive Resource Information

TC-ERR-05
Rate Limit
→ 429
```

---

# 11.108 Security Configuration Matrix

| Configuration     | Development           | Testing         | Demo / Production |
| ----------------- | --------------------- | --------------- | ----------------- |
| HTTPS             | Environment-dependent | Controlled      | ✅ Required        |
| Debug Mode        | Allowed               | Controlled      | ❌                 |
| Verbose Error     | Allowed locally       | Controlled      | ❌                 |
| Real Secrets      | ❌                     | Test Secrets    | Secure Secrets    |
| Production DB     | ❌                     | ❌               | ✅                 |
| AI Production Key | ❌                     | Test/Controlled | Secure            |
| Broad CORS        | Temporary             | Controlled      | ❌                 |
| Sensitive Logging | ❌                     | ❌               | ❌                 |

---

# 11.109 Security Responsibilities

| Component   | Security Responsibility                    |
| ----------- | ------------------------------------------ |
| Mobile      | Secure Token Storage, Local User Isolation |
| API         | Authentication, Input Validation           |
| Application | Authorization, Business Rules              |
| AI Adapter  | Provider Credential Isolation              |
| AI/NLP      | Controlled Interpretation                  |
| Validation  | Output Safety                              |
| Planning    | Constraint Integrity                       |
| Schedule    | Version / Confirmation Integrity           |
| Database    | Referential / Structural Integrity         |
| Deployment  | Secret / Network / Environment Security    |

---

# 11.110 Security Invariants

```text id="xrw7s5"
SEC-INV-01
Passwords are never stored in plaintext.

SEC-INV-02
Passwords are never sent to AI.

SEC-INV-03
AI Provider keys never exist in the Mobile App.

SEC-INV-04
Database credentials never exist in the Mobile App.

SEC-INV-05
Authenticated identity comes from server-managed auth context.

SEC-INV-06
Every User-owned resource requires server-side ownership validation.

SEC-INV-07
Cross-user relationships are prohibited.

SEC-INV-08
Access Tokens are short-lived.

SEC-INV-09
Refresh Sessions are revocable.

SEC-INV-10
Password change revokes existing refresh sessions according to policy.

SEC-INV-11
One-time authentication tokens cannot be reused.

SEC-INV-12
Sensitive credentials are not logged.

SEC-INV-13
AI does not access Database directly.

SEC-INV-14
AI does not modify Confirmed Schedule directly.

SEC-INV-15
AI output must pass Schema and Domain Validation.

SEC-INV-16
Planning cannot silently relax Hard Constraints.

SEC-INV-17
Stale Proposal cannot override Current Schedule.

SEC-INV-18
Historical Schedule Versions are immutable.

SEC-INV-19
Client cannot bypass State Machine by setting protected fields directly.

SEC-INV-20
Critical Side Effects require Idempotency protection where defined.

SEC-INV-21
Notification state cannot override Schedule state.

SEC-INV-22
Logout isolates User-specific local state.

SEC-INV-23
Production errors do not expose internal secrets or implementation details.

SEC-INV-24
Production traffic uses HTTPS.

SEC-INV-25
Unsupported AI inference cannot be promoted to planning data without validation.
```

---

# 11.111 Security Design Rationale

## Rationale 1 — Argon2id

ใช้ Password Hashing ที่เหมาะสมสำหรับการจัดเก็บ Credential โดยไม่เก็บ Password จริง

## Rationale 2 — Short-lived Access Token

ลดช่วงเวลาที่ Access Token ที่รั่วไหลสามารถใช้งานได้

## Rationale 3 — Revocable Refresh Session

ทำให้ Server สามารถยุติ Session ที่ไม่ควรใช้งานต่อได้

## Rationale 4 — Ownership-based Authorization

ช่วยป้องกันกรณี User มี Token ที่ถูกต้องแต่พยายามเข้าถึง Resource ของ User อื่น

## Rationale 5 — AI Isolation

AI ไม่ควรมีสิทธิ์เข้าถึง Database หรือ Secret เพราะหน้าที่ของ AI คือ Understanding ไม่ใช่ System Control

## Rationale 6 — Validation After AI

LLM Output ไม่ควรถูกถือว่า Trustworthy เพียงเพราะโครงสร้างถูกต้อง

## Rationale 7 — Version-based Schedule Integrity

Schedule Version ทำหน้าที่ทั้ง Historical Record และ Consistency Boundary

## Rationale 8 — No Notification Entity

Device-specific Notification State ไม่ควรถูกยกขึ้นมาเป็น Backend Security/Business Resource ใน MVP

## Rationale 9 — Data Minimization

ลดข้อมูลที่อาจหลุดไปยัง AI Provider และลด Context ที่ไม่จำเป็น

---

# 11.112 Security ↔ Architecture Traceability

```text id="eaq0v4"
Authentication
→ API Boundary

Authorization
→ Application Boundary

AI Isolation
→ AI Provider Adapter

Input Validation
→ Validation Layer

Constraint Integrity
→ Planning Core

Schedule Integrity
→ Schedule Management

Historical Integrity
→ Schedule Version

Secret Protection
→ Deployment Configuration

Notification Isolation
→ Mobile Device State
```

---

# 11.113 Security ↔ Database Traceability

| Security Concern       | Database Support             |
| ---------------------- | ---------------------------- |
| User Identity          | users                        |
| Session Revocation     | auth_sessions                |
| One-time Tokens        | auth_tokens                  |
| Ownership              | user_id FKs                  |
| Activity Integrity     | planning_objects             |
| Relationship Ownership | related user_id / object FKs |
| Planning Trace         | planning_requests            |
| Proposal Integrity     | proposals                    |
| Stale Protection       | source_schedule_version_id   |
| Schedule History       | schedule_versions            |
| Placement Integrity    | schedule_items               |

Database ช่วย enforce Structural Integrity แต่ Application Layer ยังคงเป็นผู้ควบคุม Business Security Rules

---

# 11.114 Security ↔ API Traceability

```text id="fkmexr"
Authentication
→ /api/auth/*

Ownership
→ All protected resources

Stale Protection
→ /api/proposals/{id}/confirm

Draft Validation
→ /api/schedule/validate

Manual Confirmation
→ /api/schedule/manual-confirm

Rate Limiting
→ Auth + Planning + Side Effects

Error Safety
→ Common Error Contract
```

---

# 11.115 Security ↔ AI Traceability

```text id="brfwqg"
User Text
   ↓
Untrusted Input
   ↓
AI Provider
   ↓
Structured Output
   ↓
Schema Validation
   ↓
Domain Validation
   ↓
Planning
```

AI ไม่ได้รับ:

```text id="bg9s8b"
Credentials
Secrets
Database Access
User B Data
Unrelated User History
```

---

# 11.116 Security ↔ Replanning Traceability

Replanning ต้องตรวจ:

```text id="359w2z"
Authenticated User
        ↓
Current Schedule Ownership
        ↓
Changed Activity Ownership
        ↓
Relevant Context Ownership
        ↓
Replanning
        ↓
Proposal
        ↓
Current Version Check
        ↓
User Confirmation
```

ทำให้การ Replanning ไม่กลายเป็นช่องทางในการแก้ Schedule โดยข้าม Authorization

---

# 11.117 Security ↔ Human-in-the-Loop

Human-in-the-Loop มีประโยชน์ด้าน Security/Integrity ด้วย เพราะ:

```text id="xp2q2k"
AI
 ↓
Proposal
 ↓
User Review
 ↓
Explicit Confirmation
```

ช่วยป้องกัน AI จากการสร้าง Autonomous State Change

ดังนั้น:

> **User Confirmation เป็นทั้ง UX Control และ Integrity Boundary**

---

# 11.118 Security ↔ Notification

Notification:

```text id="0e2zca"
Confirmed Schedule
      ↓
Local Notification
```

ดังนั้น:

```text id="9no0k0"
Proposal
→ No notification
```

และ:

```text id="d8byfk"
Rejected Proposal
→ No notification change
```

ช่วยลดความเสี่ยงที่ข้อมูลที่ยังไม่ได้ Confirm จะถูกแสดงบน Device

---

# 11.119 Security Summary

Security Architecture ของ LONGTUA สามารถสรุปได้ดังนี้:

```text id="kqvp25"
                USER
                  |
                  v
          +---------------+
          | Mobile App    |
          | Secure Store  |
          +-------+-------+
                  |
                HTTPS
                  |
                  v
          +---------------+
          | Authentication|
          +-------+-------+
                  |
                  v
          +---------------+
          | Authorization |
          | Ownership     |
          +-------+-------+
                  |
                  v
          +---------------+
          | Validation    |
          +-------+-------+
                  |
          +-------+-------+
          |               |
          v               v
       AI/NLP          Planning
          |               |
          +-------+-------+
                  |
                  v
          +---------------+
          | Application   |
          | Domain Rules  |
          +-------+-------+
                  |
                  v
          +---------------+
          | PostgreSQL    |
          +---------------+
```

หลักสำคัญ:

```text id="ammljz"
Authenticate
     ↓
Authorize
     ↓
Validate
     ↓
Understand
     ↓
Compute
     ↓
Confirm
     ↓
Commit
```

โดยไม่มี Component ใดสามารถข้าม Security Boundary เพื่อเปลี่ยนข้อมูลสำคัญของ User โดยตรง

---

# 11.120 Final Security Principle

Security ของ LONGTUA ไม่ได้หมายถึงเพียงการ Login อย่างปลอดภัย แต่หมายถึงการรักษา **ความลับ + สิทธิ์ + ความถูกต้องของข้อมูล + ความถูกต้องของ State**

จึงใช้หลัก:

> **Authenticate the user, authorize every resource, validate every important input, isolate AI and secrets, and never allow an unconfirmed result to become a committed schedule.**
