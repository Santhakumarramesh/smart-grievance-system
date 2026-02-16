# 🇮🇳 Smart Grievance Classification & Resolution Tracking System

An intelligent, AI-powered grievance redressal portal for Indian government departments with automatic complaint classification, multi-language support, and real-time tracking.

## ✨ Features

- 🤖 **AI-Powered Classification** - Automatic department assignment using NLP (64% accuracy)
- 🔐 **Secure Authentication** - JWT-based auth with OTP verification
- 🌐 **Multi-Language Support** - 12 Indian languages (Hindi, Tamil, Telugu, Bengali, etc.)
- 📊 **Real-Time Tracking** - Amazon-style timeline tracking
- 💬 **Two-Way Communication** - Comments between citizens and officers
- 📧 **Email Notifications** - Automatic updates on status changes
- 👥 **Role-Based Access** - Citizen, Officer, and Admin dashboards
- 📈 **Analytics Dashboard** - Department-wise statistics and resolution metrics

## 🚀 Quick Start

### 1. Run the Application

**macOS/Linux:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

### 2. Open in Browser

Visit: **http://localhost:8000**

### 3. Test Accounts

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@grievance.gov | admin123 |
| **Officer** | electricity@grievance.gov | officer123 |
| **Citizen** | citizen@example.com | citizen123 |

## 📋 Manual Setup

If the automatic script doesn't work:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train ML model
python ml/train.py

# 3. Setup database
python -m backend.seed

# 4. Run application
PORT=8000 PYTHONPATH=. python backend/app.py
```

## 🎯 Demo Flow

1. **Login as Citizen** → Submit a complaint (e.g., "Street lights not working")
2. **AI Classification** → Automatically assigns to "Streetlights" department
3. **Track Progress** → View timeline with status updates
4. **Login as Officer** → Update status and add comments
5. **Email Notifications** → Citizen receives updates (console in demo mode)
6. **Two-Way Communication** → Both parties can add comments

## 🏛️ Supported Departments

- Water Supply
- Electricity
- Sanitation & Solid Waste
- Sewerage & Drainage
- Roads & Potholes
- Streetlights
- Traffic
- Police
- Cyber Crime
- Public Health
- Food Safety
- Education
- Land & Revenue
- Ration Card / PDS
- RTO / Transport
- Telecom / Network
- Environment

## 🌍 Supported Languages

English, Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Urdu, Punjabi, Odia

## 📧 Enable Real Email (Optional)

To enable real email notifications:

1. **Get Gmail App Password**: https://myaccount.google.com/apppasswords

2. **Create `.env` file**:
```bash
DEMO_EMAIL_MODE=false
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
```

3. **Restart the application**

## 🛠️ Tech Stack

**Backend:**
- Python 3.13
- Flask
- SQLAlchemy (SQLite)
- scikit-learn (TF-IDF + Logistic Regression)
- JWT Authentication

**Frontend:**
- HTML5, CSS3, JavaScript
- Responsive Design
- Multi-language UI

**ML Model:**
- TF-IDF Vectorizer
- Logistic Regression
- 208 training samples
- 17 department categories

## 📁 Project Structure

```
smart-grievance-system/
├── backend/              # Flask backend
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   └── models.py        # Database models
├── frontend/            # HTML/CSS/JS frontend
├── ml/                  # Machine learning
│   ├── train.py        # Model training
│   └── artifacts/      # Trained models
├── data/               # Datasets & configs
├── start.sh/bat        # Startup scripts
└── requirements.txt    # Dependencies
```

## 🔄 Grievance Workflow

1. **Received** - Complaint submitted
2. **Assigned to Department** - AI classification
3. **Under Progress** - Officer working on it
4. **Investigation** - Detailed review
5. **Reviewed** - Supervisor check
6. **Resolved** - Issue fixed
7. **Closed** - Case completed

## 📊 Admin Features

- Create officers for departments
- View analytics (status-wise, department-wise)
- Monitor average resolution time
- System-wide statistics

## 🔒 Security Features

- Password hashing (Werkzeug)
- JWT token authentication
- OTP verification
- Role-based access control
- SQL injection protection

## 🚀 Deployment

Ready for deployment on:
- Render (free tier)
- Heroku
- AWS
- Any Python hosting platform

See `Procfile` and `runtime.txt` for deployment configuration.

## 📝 License

MIT License - See LICENSE file

## 👨‍💻 Development

Built as a demonstration of:
- Full-stack development
- AI/ML integration
- Government digital services
- Multi-language support
- Real-time tracking systems

---

**Made with ❤️ for Digital India**
