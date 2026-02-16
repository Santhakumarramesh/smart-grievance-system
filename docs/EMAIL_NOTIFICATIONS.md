# 📧 Email & In-App Notifications System

## Overview

The Smart Grievance System now has a **complete notification system** that keeps users, officers, and admins informed about grievance updates through both **email** and **in-app notifications**.

---

## 🎯 Notification Types

### 1. **Officer Assignment Notification** (Admin → Officer)
**Trigger:** Admin assigns a grievance to an officer

**Recipients:**
- ✅ **Officer** (Email + In-App)
- ✅ **Citizen** (Email + In-App)

**Officer Email Contains:**
- 🚨 Case assignment alert
- 📋 Grievance ID and department
- 👤 Complainant information (name, phone)
- 📝 Complaint description
- 🔗 Link to officer portal

**Citizen Email Contains:**
- 👮 Officer details (name, designation)
- 📋 Grievance ID
- ✅ Confirmation of assignment
- 🔗 Link to track complaint

---

### 2. **Status Update Notification** (Officer → Citizen)
**Trigger:** Officer updates grievance status

**Recipients:**
- ✅ **Citizen** (Email + In-App)

**Email Contains:**
- 📌 Old status → New status
- 👮 Officer name who updated
- 💬 Update message from officer
- 🏢 Department handling the case
- 🔗 Link to track complaint

**Status Emojis:**
- 📥 Received
- 📋 Assigned to Department
- 🔄 Under Progress
- 🔍 Investigation
- ✅ Reviewed
- 🎉 Resolved
- 🔒 Closed

---

### 3. **Comment Notification**
**Trigger:** Someone adds a comment on a grievance

**Recipients:**
- ✅ **Relevant parties** (Email + In-App)

**Email Contains:**
- 💬 New comment alert
- 📋 Grievance ID
- 👤 Commenter name and role
- 📝 Comment text
- 🔗 Link to view and reply

---

### 4. **Welcome Email**
**Trigger:** User completes registration and verification

**Email Contains:**
- ✅ Account activation confirmation
- 🎯 What you can do (features list)
- 🔗 Login link
- 🇮🇳 Digital India branding

---

### 5. **OTP Verification Email**
**Trigger:** User registers or resets password

**Email Contains:**
- 🔐 6-digit OTP code
- ⏰ 5-minute validity
- 🔒 Security tips
- ⚠️ Warning about sharing OTP

---

## 🔔 In-App Notification System

### Features:
- ✅ Real-time notifications in portal
- ✅ Unread count badge
- ✅ Notification history (last 50)
- ✅ Mark as read functionality
- ✅ Mark all as read
- ✅ Click to view related grievance

### Notification Types:
1. **assignment** - Case assigned to officer
2. **status_update** - Status changed
3. **comment** - New comment added

---

## 📊 Notification Flow

### **Scenario 1: Admin Assigns Case to Officer**

```
Admin Action:
1. Admin selects grievance
2. Admin assigns to officer
3. Clicks "Assign"

System Actions:
↓
1. Update grievance.assigned_officer_id
2. Update status to "Assigned to Department"
3. Create GrievanceUpdate entry
↓
4. Create in-app notification for OFFICER
   - Title: "🚨 New Case Assigned - Grievance #123"
   - Type: "assignment"
   - Unread badge appears
↓
5. Create in-app notification for CITIZEN
   - Title: "Officer Assigned - Grievance #123"
   - Type: "assignment"
↓
6. Send EMAIL to OFFICER
   - Subject: "🚨 New Case Assigned - Grievance #123"
   - Body: Full case details, complainant info
   - Link to officer portal
↓
7. Send EMAIL to CITIZEN
   - Subject: "Status Update: Grievance #123 - Assigned to Department"
   - Body: Officer details, status change
   - Link to track complaint

Result:
✅ Officer receives email + in-app notification
✅ Citizen receives email + in-app notification
✅ Both can click to view details
```

---

### **Scenario 2: Officer Updates Status**

```
Officer Action:
1. Officer opens case
2. Updates status (e.g., "Under Progress")
3. Adds message: "Site inspection scheduled for tomorrow"
4. Clicks "Update Status"

System Actions:
↓
1. Store old_status = "Assigned to Department"
2. Update grievance.status = "Under Progress"
3. Create GrievanceUpdate entry
↓
4. Create in-app notification for CITIZEN
   - Title: "Status Update - Grievance #123"
   - Message: "Under Progress"
   - Type: "status_update"
↓
5. Send EMAIL to CITIZEN
   - Subject: "Status Update: Grievance #123 - Under Progress"
   - Body:
     * Old Status: Assigned to Department
     * New Status: 🔄 Under Progress
     * Officer: John Doe
     * Message: "Site inspection scheduled for tomorrow"
   - Link to track complaint

Result:
✅ Citizen receives email notification
✅ Citizen sees in-app notification
✅ Citizen can track progress in real-time
```

---

## 🔧 Technical Implementation

### Backend Endpoints:

#### 1. **Admin Assign Officer**
```
POST /admin/assign-officer
Body: {
  "grievance_id": 123,
  "officer_id": 45
}

Response: {
  "message": "Officer assigned successfully",
  "grievance": {...}
}
```

#### 2. **Get Notifications**
```
GET /admin/notifications

Response: {
  "unread_count": 5,
  "notifications": [
    {
      "id": 1,
      "title": "🚨 New Case Assigned",
      "message": "...",
      "notification_type": "assignment",
      "related_grievance_id": 123,
      "is_read": false,
      "created_at": "2026-02-16T10:30:00"
    }
  ]
}
```

#### 3. **Mark Notification as Read**
```
PUT /admin/notifications/1/mark-read

Response: {
  "message": "Notification marked as read"
}
```

#### 4. **Mark All as Read**
```
PUT /admin/notifications/mark-all-read

Response: {
  "message": "All notifications marked as read"
}
```

---

### Database Schema:

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    related_grievance_id INTEGER,
    is_read BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (related_grievance_id) REFERENCES grievances(id)
);
```

---

### Email Service Methods:

```python
# 1. Officer Assignment
EmailService.send_officer_assignment_notification(
    officer_email, officer_name, grievance_id, 
    complaint_text, department, user_name, user_phone
)

# 2. Status Update
EmailService.send_status_update_notification(
    user_email, user_name, grievance_id, 
    old_status, new_status, update_message, 
    department, officer_name
)

# 3. Comment Notification
EmailService.send_comment_notification(
    user_email, grievance_id, commenter_name, comment_text
)

# 4. Welcome Email
EmailService.send_welcome_email(user_email, user_name)

# 5. OTP Email
EmailService.send_otp_email(user_email, otp, user_name)
```

---

## 📱 User Experience

### **Officer Portal:**
```
🔔 Notifications (3)
├─ 🚨 New Case Assigned - Grievance #123
│  "You have been assigned a new case in Public Works..."
│  2 minutes ago | UNREAD
│
├─ 💬 New Comment - Grievance #120
│  "Citizen replied: Thank you for the update..."
│  1 hour ago | READ
│
└─ 📋 Case Resolved - Grievance #118
   "Admin marked your case as resolved..."
   3 hours ago | READ
```

### **Citizen Portal:**
```
🔔 Notifications (2)
├─ 👮 Officer Assigned - Grievance #123
│  "Your complaint has been assigned to John Doe..."
│  5 minutes ago | UNREAD
│
└─ 🔄 Status Update - Grievance #123
   "Status changed to: Under Progress..."
   1 hour ago | READ
```

---

## ✅ Benefits

| Feature | Before | After |
|---------|--------|-------|
| **Officer Awareness** | ❌ Manual check | ✅ Instant email + notification |
| **Citizen Updates** | ❌ Must check portal | ✅ Email + in-app alerts |
| **Response Time** | ❌ Delayed | ✅ Real-time |
| **Communication** | ❌ One-way | ✅ Two-way with notifications |
| **Transparency** | ❌ Limited | ✅ Full visibility |

---

## 🎓 For Demo/Presentation

### Key Points:
1. **Complete Notification System:**
   - Email notifications for all stakeholders
   - In-app notifications for real-time updates
   - Unread count badges

2. **Officer Assignment:**
   - Admin assigns → Officer gets email + notification
   - Citizen informed immediately
   - No manual checking needed

3. **Status Updates:**
   - Officer updates → Citizen gets email + notification
   - Full status history with messages
   - Real-time tracking

4. **Professional Communication:**
   - Branded email templates
   - Clear, informative messages
   - Direct links to relevant pages

---

## 🚀 Result

Your Smart Grievance System now has:
- 📧 **Professional Email Notifications** (Gmail SMTP)
- 🔔 **In-App Notification System** (Real-time)
- 👮 **Officer Assignment Alerts** (Email + In-App)
- 📊 **Status Update Notifications** (Email + In-App)
- 💬 **Comment Notifications** (Email + In-App)
- 🔢 **Unread Count Badges** (Visual indicators)
- ✅ **Mark as Read** (User control)
- 🇮🇳 **Government-Grade Communication** (Professional)

**Feature Status:** ✅ **COMPLETE & LIVE**

**Last Updated:** February 16, 2026
