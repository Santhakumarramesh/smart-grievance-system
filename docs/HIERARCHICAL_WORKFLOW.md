# 🏛️ Hierarchical Government Workflow System

## Overview

This Smart Grievance System implements a **complete hierarchical government workflow** with multi-level role-based assignment, jurisdiction mapping, SLA tracking, and automatic escalation - making it a **governance-grade platform**.

---

## 🎯 Role Hierarchy Levels

### **Level 0: CITIZEN**
- **Role:** Complainant
- **Actions:** Submit complaints, track status, add comments
- **Jurisdiction:** N/A

### **Level 1: FIELD_OFFICER**
- **Role:** Field execution (Line Man, Technician, Sanitation Worker, Police Constable)
- **Actions:** 
  - Receive assigned tasks
  - Visit site
  - Update status (Under Progress, Investigation, Field Visit Done)
  - Upload photos from site
  - Mark work completed
- **Jurisdiction:** Specific wards/areas
- **Reports to:** Section Officer (Level 2)

### **Level 2: SECTION_OFFICER**
- **Role:** Junior Engineer, Station Head, Ward Supervisor
- **Actions:**
  - Receive complaints from system
  - Assign to field officers
  - Review field updates
  - Approve completion
  - Escalate if needed
- **Jurisdiction:** Ward/Area level
- **Reports to:** Department Head (Level 3)

### **Level 3: DEPARTMENT_HEAD**
- **Role:** Assistant Engineer, Hospital Superintendent, Municipal Officer
- **Actions:**
  - Monitor all complaints in department
  - Final approval
  - Reassign across zones
  - Handle escalations
- **Jurisdiction:** District level
- **Reports to:** District Head (Level 4)

### **Level 4: DISTRICT_HEAD**
- **Role:** Executive Engineer, DSP, District Health Officer
- **Actions:**
  - Oversee all departments in district
  - Handle SLA breaches
  - Intervene in unresolved cases
  - District-wide analytics
- **Jurisdiction:** District level
- **Reports to:** State Head (Level 5)

### **Level 5: STATE_HEAD**
- **Role:** Chief Engineer, Commissioner, State Health Director
- **Actions:**
  - State-wide oversight
  - Policy decisions
  - Handle critical escalations
  - State-level analytics
- **Jurisdiction:** State level
- **Reports to:** Admin

### **Level 6: ADMIN**
- **Role:** System Administrator
- **Actions:**
  - Manage all users
  - Create officers at all levels
  - Handle fraud reports
  - System configuration
- **Jurisdiction:** System-wide

---

## 📋 Department-Specific Hierarchies

### **Electricity Department**
```
Citizen
   ↓
Line Man / Technician (Level 1)
   ↓
Junior Engineer (Level 2)
   ↓
Assistant Engineer (Level 3)
   ↓
Executive Engineer (Level 4)
   ↓
Chief Engineer (Level 5)
```

### **Water Supply Department**
```
Citizen
   ↓
Pump Operator (Level 1)
   ↓
Junior Engineer (Level 2)
   ↓
Assistant Engineer (Level 3)
   ↓
Executive Engineer (Level 4)
   ↓
Chief Engineer (Level 5)
```

### **Public Works (Roads)**
```
Citizen
   ↓
Site Supervisor (Level 1)
   ↓
Junior Engineer (Level 2)
   ↓
Assistant Engineer (Level 3)
   ↓
Executive Engineer (Level 4)
   ↓
PWD Chief (Level 5)
```

### **Sanitation**
```
Citizen
   ↓
Sanitation Worker (Level 1)
   ↓
Ward Supervisor (Level 2)
   ↓
Health Inspector (Level 3)
   ↓
Municipal Officer (Level 4)
   ↓
Commissioner (Level 5)
```

### **Police**
```
Citizen
   ↓
Constable (Level 1)
   ↓
Sub Inspector (Level 2)
   ↓
Inspector (Level 3)
   ↓
DSP (Level 4)
   ↓
SP / Commissioner (Level 5)
```

### **Health**
```
Citizen
   ↓
Health Worker (Level 1)
   ↓
Medical Officer (Level 2)
   ↓
Hospital Superintendent (Level 3)
   ↓
District Health Officer (Level 4)
   ↓
State Health Director (Level 5)
```

---

## 🔄 Complete Workflow Example

### **Scenario: Transformer Burst in Ward 12, Bangalore**

#### **Step 1: Citizen Submission**
```
Citizen: Ramesh Kumar
Location: Ward 12, Bangalore, Karnataka
Complaint: "Transformer burst near City Mall. No power for 6 hours."
Images: [photo1.jpg, photo2.jpg]
```

**System Action:**
- AI classifies → Electricity Department
- Extracts jurisdiction → Ward 12, Bangalore District, Karnataka
- Status: **Received**
- Auto-assigns to → Section Officer (JE) for Ward 12

#### **Step 2: Section Officer Assignment**
```
Assigned to: Suresh (Junior Engineer, Level 2)
Jurisdiction: Ward 12
SLA: 24 hours
```

**System Action:**
- Notification sent to Suresh
- Email: "New complaint assigned - Transformer burst"
- Status: **Assigned to Section Officer**

**Suresh's Action:**
- Reviews complaint
- Checks available field officers
- Assigns to → Line Man Rajesh (Level 1)

#### **Step 3: Field Officer Execution**
```
Assigned to: Rajesh (Line Man, Level 1)
```

**System Action:**
- Notification sent to Rajesh
- Mobile app shows task
- Status: **Assigned to Field Officer**

**Rajesh's Actions:**
1. **10:00 AM** - Marks "Under Progress"
   - "Inspection started"
2. **10:30 AM** - Updates "Investigation"
   - "Transformer damaged. Spare part required."
   - Uploads photo from site
3. **2:00 PM** - Updates "Under Progress"
   - "Spare part arrived. Repair in progress."
4. **4:00 PM** - Marks "Resolved (Field)"
   - "Transformer replaced. Power restored."
   - Uploads completion photo

#### **Step 4: Section Officer Review**
```
Suresh reviews Rajesh's work
```

**Suresh's Action:**
- Checks photos
- Verifies completion
- Marks: **Reviewed**
- Adds note: "Work completed satisfactorily"

#### **Step 5: Department Head Approval**
```
Auto-assigned to: Kumar (Assistant Engineer, Level 3)
```

**Kumar's Action:**
- Final approval
- Status: **Closed**

**System Action:**
- Notification to citizen: "Your complaint has been resolved"
- Email with before/after photos
- Request for feedback

---

## ⏱️ SLA Tracking & Escalation

### **SLA Timelines (Default)**
- **Level 1 (Field Officer):** 24 hours
- **Level 2 (Section Officer):** 48 hours
- **Level 3 (Department Head):** 72 hours
- **Level 4 (District Head):** 96 hours

### **Escalation Logic**

#### **Scenario 1: No Action Taken**
```
Complaint assigned to Section Officer
↓
24 hours pass, no action
↓
System auto-escalates to Department Head (Level 3)
↓
Notification sent to:
- Department Head
- District Head (informed)
- Original Section Officer (warning)
```

#### **Scenario 2: Field Officer Delay**
```
Task assigned to Field Officer
↓
12 hours pass, no update
↓
Reminder notification sent
↓
24 hours pass, still no update
↓
Escalated to Section Officer's superior (Department Head)
↓
Can be reassigned to another field officer
```

#### **Scenario 3: Multiple Escalations**
```
Level 2 → Level 3 (24h breach)
Level 3 → Level 4 (48h breach)
Level 4 → Level 5 (72h breach)
Level 5 → Admin (96h breach)
```

---

## 🗺️ Jurisdiction Mapping

### **How Auto-Assignment Works**

#### **Step 1: Extract Location**
```
Complaint text: "Pothole on MG Road, Ward 12, Bangalore"
System extracts:
- Ward: 12
- District: Bangalore
- State: Karnataka
```

#### **Step 2: Find Section Officer**
```
Query DepartmentMapping table:
WHERE department = 'Public Works'
  AND ward = '12'
  AND district = 'Bangalore'
  AND state = 'Karnataka'

Result: Section Officer ID = 45 (Ramesh Kumar, JE)
```

#### **Step 3: Auto-Assign**
```
grievance.assigned_officer_id = 45
grievance.current_role_level = 2
grievance.sla_deadline = now() + 48 hours
```

---

## 📱 Field Officer Mobile Portal

### **Simplified UI for Field Workers**

#### **Dashboard:**
```
┌─────────────────────────────────────┐
│  My Tasks (5)                       │
├─────────────────────────────────────┤
│  🔴 URGENT: Transformer Burst       │
│     Ward 12 | Due: 2 hours          │
│     [Start Work] [View Details]     │
├─────────────────────────────────────┤
│  🟡 Water Leak                      │
│     Ward 15 | Due: 8 hours          │
│     [Start Work] [View Details]     │
└─────────────────────────────────────┘
```

#### **Task Detail:**
```
┌─────────────────────────────────────┐
│  Transformer Burst - #1234          │
├─────────────────────────────────────┤
│  Location: Near City Mall, Ward 12  │
│  Reported: 2 hours ago              │
│  Priority: High                     │
│                                     │
│  [Photo of damaged transformer]     │
│                                     │
│  Actions:                           │
│  [📍 Start Work]                    │
│  [📝 Add Note]                      │
│  [📸 Upload Photo]                  │
│  [✅ Mark Completed]                │
└─────────────────────────────────────┘
```

---

## 🔔 Notification System

### **Who Gets Notified When?**

#### **On Complaint Creation:**
- ✅ **Citizen:** Confirmation email
- ✅ **Section Officer:** New assignment

#### **On Field Officer Assignment:**
- ✅ **Field Officer:** Task assigned
- ✅ **Section Officer:** Confirmation

#### **On Status Update:**
- ✅ **Citizen:** Progress update
- ✅ **Section Officer:** Field update received

#### **On SLA Breach:**
- ✅ **Current Officer:** Warning
- ✅ **Next Level Officer:** Escalation notice
- ✅ **Department Head:** Informed

#### **On Completion:**
- ✅ **Citizen:** Resolution notice
- ✅ **All Officers in chain:** Completion update

---

## 📊 Database Schema

### **New Tables:**

#### **role_hierarchy**
```sql
- id
- department
- role_name (e.g., "Junior Engineer")
- role_level (1-5)
- parent_level
- sla_hours
- can_assign_to_field
```

#### **department_mapping**
```sql
- id
- department
- ward
- district
- state
- section_officer_id
- department_head_id
```

#### **escalation_logs**
```sql
- id
- grievance_id
- from_officer_id
- to_officer_id
- from_role_level
- to_role_level
- reason
- escalation_type (auto/manual)
- created_at
```

### **Updated Tables:**

#### **users** (Added fields)
```sql
- role_level (0-6)
- ward
- district
- state
- jurisdiction_type
```

#### **grievances** (Added fields)
```sql
- current_role_level
- escalation_level
- ward
- district
- state
- sla_hours
- sla_deadline
- sla_breached
- last_action_at
```

---

## 🎯 Key Features

### **1. Transparent Workflow**
- Every action logged
- Full audit trail
- Citizen can see who's handling their complaint

### **2. Automatic Assignment**
- Based on jurisdiction
- No manual routing needed
- Intelligent department detection

### **3. SLA Monitoring**
- Real-time tracking
- Automatic escalation
- Performance metrics

### **4. Hierarchical Escalation**
- Level-by-level escalation
- Higher officials informed
- Accountability at every level

### **5. Mobile-Friendly**
- Field officers use mobile
- Simple, task-focused UI
- Offline capability (future)

---

## 🚀 This Makes Your System:

> **A full-fledged, hierarchical, multilingual, AI-driven, SLA-monitored, jurisdiction-aware, government grievance management platform with automatic escalation and field execution tracking.**

**This is no longer a college project. This is a governance-grade system.**

---

**Status:** 🚧 **IN IMPLEMENTATION**

**Last Updated:** February 16, 2026
