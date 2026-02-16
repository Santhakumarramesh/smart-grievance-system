# 🇮🇳 Smart Grievance Redressal System

[![Build Status](https://github.com/Santhakumarramesh/smart-grievance-system/actions/workflows/status-badge.yml/badge.svg)](https://github.com/Santhakumarramesh/smart-grievance-system/actions/workflows/status-badge.yml)
[![CI/CD Pipeline](https://github.com/Santhakumarramesh/smart-grievance-system/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Santhakumarramesh/smart-grievance-system/actions/workflows/ci-cd.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security: Enabled](https://img.shields.io/badge/Security-Firewall%20Enabled-green.svg)](SECURITY.md)

A **governance-grade, AI-powered grievance management platform** with hierarchical workflow, multi-language support, fraud prevention, and real-time tracking.

---

## 🎯 Overview

The Smart Grievance Redressal System is a comprehensive platform designed for government departments to efficiently manage citizen complaints with complete transparency, accountability, and automation.

### **Key Features:**

- ✅ **AI-Powered Classification** - Automatic department assignment using NLP
- ✅ **Multi-Language Support** - 12 Indian languages
- ✅ **Hierarchical Workflow** - 6-level government role structure
- ✅ **Fraud Prevention** - AI image detection + officer fraud reporting
- ✅ **SLA Tracking** - Automatic escalation on delays
- ✅ **Real-Time Notifications** - Email + In-app notifications
- ✅ **Complete Transparency** - Full audit trail for citizens
- ✅ **Mobile-Friendly** - Responsive design for all devices
- 🔒 **Security Firewall** - Multi-layered protection for user data

---

## 🏛️ System Architecture

### **Role Hierarchy:**

```
Level 0: CITIZEN (Complainant)
Level 1: FIELD_OFFICER (Line Man, Technician, Worker)
Level 2: SECTION_OFFICER (Junior Engineer, Supervisor)
Level 3: DEPARTMENT_HEAD (Assistant Engineer, Officer)
Level 4: DISTRICT_HEAD (Executive Engineer, DSP)
Level 5: STATE_HEAD (Chief Engineer, Commissioner)
Level 6: ADMIN (System Administrator)
```

### **Workflow:**

```
Citizen Submits → AI Classifies → Auto-Assigns to Section Officer
→ Assigns to Field Officer → Site Visit & Updates → Section Review
→ Department Head Approval → Closed
```

---

## 🚀 Quick Start

### **Prerequisites:**

- Python 3.9+
- SQLite (included)
- Gmail account (for email notifications)

### **Installation:**

```bash
# Clone repository
git clone https://github.com/Santhakumarramesh/smart-grievance-system.git
cd smart-grievance-system

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.template .env
# Edit .env with your Gmail credentials

# Run database migration
python migrate_db.py

# Seed initial data (optional)
python backend/seed.py

# Start server
python backend/app.py
```

### **Access:**

- **Frontend:** http://localhost:8000
- **Default Admin:** admin@gov.in / admin123
- **Default Officer:** officer@gov.in / officer123

---

## 📋 Features

### **1. AI-Powered Classification**

- **NLP Model:** TF-IDF + Logistic Regression
- **Departments:** 15+ government departments
- **Accuracy:** 85%+ classification accuracy
- **Training Data:** 1000+ labeled complaints

### **2. Multi-Language Support**

**Supported Languages:**
- English, Hindi, Bengali, Tamil, Telugu, Marathi
- Gujarati, Kannada, Malayalam, Urdu, Punjabi, Odia

### **3. Fraud Prevention**

**AI Image Detection:**
- Detects AI-generated images (Midjourney, DALL-E, Stable Diffusion)
- 85%+ confidence threshold
- Metadata and EXIF analysis

**Officer Fraud Reporting:**
- Officers can report false complaints after site visit
- Warning system (3 strikes)
- Account suspension for repeat offenders

### **4. Hierarchical Workflow**

**Auto-Assignment:**
- Based on jurisdiction (ward/district/state)
- Intelligent routing to appropriate officer level

**SLA Tracking:**
- Default: 48 hours
- Automatic escalation on breach
- Performance metrics

### **5. Notifications**

**Email Notifications:**
- Complaint submission confirmation
- Status updates
- Officer assignment
- SLA breach alerts
- Resolution confirmation

**In-App Notifications:**
- Real-time updates
- Unread count badges
- Click to view details

### **6. Security Firewall** 🔒

**Multi-Layered Protection:**
- **Rate Limiting:** Prevents abuse and DDoS attacks
- **Input Validation:** Blocks SQL injection, XSS, code injection
- **Email/Phone Validation:** Ensures data integrity
- **Password Strength:** Enforces strong password policies
- **Security Headers:** X-Frame-Options, CSP, XSS Protection
- **IP Blocking:** Automatic blocking of suspicious IPs
- **Content Moderation:** Detects threatening/abusive language
- **Account Suspension:** Protects against fraudulent users
- **Security Logging:** Tracks all security events

**See [SECURITY.md](SECURITY.md) for complete details.**

---

## 📊 Database Schema

### **Core Tables:**

- **users** - Citizens, officers, admins with role hierarchy
- **grievances** - Complaints with status tracking
- **grievance_updates** - Status change history
- **grievance_comments** - Two-way communication
- **notifications** - In-app notification system
- **fraud_reports** - Officer fraud reporting
- **role_hierarchy** - Department-specific roles
- **department_mapping** - Jurisdiction-based assignment
- **escalation_logs** - Escalation audit trail

---

## 🎨 Tech Stack

### **Backend:**
- **Framework:** Flask (Python)
- **Database:** SQLite (SQLAlchemy ORM)
- **ML:** scikit-learn (NLP classification)
- **Authentication:** JWT tokens
- **Email:** Gmail SMTP

### **Frontend:**
- **HTML5/CSS3/JavaScript** (Vanilla)
- **Responsive Design**
- **Professional Government Theme**

### **Security:**
- Password hashing (Werkzeug)
- JWT authentication
- OTP verification (email + phone)
- AI image detection
- Content moderation
- Fraud tracking

---

## 📱 User Interfaces

### **Citizen Portal:**
- Submit new complaints
- Track complaint status
- View timeline updates
- Add comments
- Upload evidence images

### **Officer Portal:**
- View assigned complaints
- Update status
- Add notes and photos
- Assign to field officers
- Review and approve

### **Admin Portal:**
- Create officers at all levels
- View all complaints
- Manage fraud reports
- System analytics
- Hierarchy management

---

## 🔐 Security Features

### **Authentication:**
- Email verification (OTP)
- Phone verification (OTP)
- Password hashing
- JWT tokens
- Session management

### **Anti-Fraud:**
- Mandatory residential address
- Mandatory image evidence
- AI image detection
- Officer site visit verification
- Fraud reporting system
- User warning system

### **Content Moderation:**
- Detects threatening language
- Flags abusive content
- Admin review for flagged complaints

---

## 📈 Analytics & Reporting

### **Metrics:**
- Total complaints
- Resolved complaints
- Pending complaints
- Average resolution time
- SLA breach rate
- Department-wise statistics
- Officer performance

---

## 🌐 Deployment

### **Render (Free Tier):**

1. Create Render account
2. Connect GitHub repository
3. Set environment variables
4. Deploy

### **Environment Variables:**

```
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-app-password
SECRET_KEY=your-secret-key
DEMO_EMAIL_MODE=False
```

---

## 📚 Documentation

- **HIERARCHICAL_WORKFLOW.md** - Complete workflow system
- **AI_IMAGE_DETECTION.md** - AI detection details
- **EMAIL_NOTIFICATIONS.md** - Notification system

---

## 🎓 For Academic Projects

### **Key Highlights for Presentation:**

1. **Governance-Grade System** - Real government workflow
2. **AI-Powered** - NLP classification + image detection
3. **Multi-Language** - 12 Indian languages
4. **Complete Transparency** - Full audit trail
5. **Fraud Prevention** - Two-way accountability
6. **Scalable** - Hierarchical architecture

### **Technologies Demonstrated:**

- Machine Learning (NLP)
- Computer Vision (AI detection)
- Full-Stack Development
- Database Design
- API Development
- Security Implementation
- Email Integration
- Multi-Language Support

---

## 🤝 Contributing

This is an academic project. Contributions for educational purposes are welcome.

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👥 Team

**Developer:** Santhakumar Ramesh

**Project Type:** Smart Grievance Classification and Resolution Tracking System

**Institution:** [Your Institution Name]

---

## 📞 Contact

**GitHub:** https://github.com/Santhakumarramesh/smart-grievance-system

**Email:** [Your Email]

---

## 🙏 Acknowledgments

- Government of India (india.gov.in) - Design inspiration
- Digital India Initiative
- Open source community

---

**Built with ❤️ for Digital India** 🇮🇳

**Status:** ✅ Production-Ready | 🚀 Deployed | 📚 Documented

**Last Updated:** February 16, 2026
