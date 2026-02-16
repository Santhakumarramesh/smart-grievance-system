# 🇮🇳 Smart Grievance Classification and Resolution Tracking System

An intelligent, secure, and transparent digital platform for automating citizen complaint classification, routing, and tracking across government departments.

---

## 🎯 Features

### Core Functionality
- ✅ **AI-Powered Classification** - TF-IDF + Logistic Regression for automatic department assignment
- ✅ **Multi-Stage Tracking** - 7-stage workflow (Received → Assigned → Under Progress → Investigation → Reviewed → Resolved → Closed)
- ✅ **Role-Based Access** - Citizen, Officer, and Admin dashboards
- ✅ **Real-Time Notifications** - Email updates for all status changes
- ✅ **Timeline Tracking** - Amazon-style progress visualization

### Security & Verification
- ✅ **Email OTP Verification** - Secure account registration
- ✅ **Password Reset** - Multi-step verification process
- ✅ **Content Moderation** - Automatic detection of threatening/abusive language
- ✅ **JWT Authentication** - Secure token-based auth

### User Experience
- ✅ **Multi-Language Support** - 12 Indian languages (English, Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, Assamese)
- ✅ **Language Selector** - Available on all pages
- ✅ **Complaint Translation** - Officers can translate complaints to their preferred language
- ✅ **Image Upload** - Citizens can attach up to 5 images per complaint
- ✅ **Location Tracking** - Exact location required for faster resolution
- ✅ **Comment System** - Two-way communication between citizens and officers
- ✅ **Profile Management** - Photo upload, personal details, DOB, gender

### Design & Accessibility
- ✅ **Professional UI** - Pan-India colorful theme with department-specific colors
- ✅ **Department Showcase** - Daily rotating department highlights (17 departments)
- ✅ **Responsive Design** - Works on desktop, tablet, and mobile
- ✅ **Accessibility** - High contrast, keyboard navigation, screen reader support

---

## 🏛️ Supported Departments (17)

1. Water Supply 💧
2. Electricity ⚡
3. Sanitation 🧹
4. Roads & Infrastructure 🛣️
5. Healthcare 🏥
6. Education 📚
7. Public Transport 🚌
8. Housing 🏘️
9. Police 👮
10. Fire Services 🚒
11. Agriculture 🌾
12. Environment 🌳
13. Revenue 💰
14. Social Welfare 🤝
15. Panchayat Raj 🏛️
16. Urban Development 🏗️
17. Tourism 🗿

---

## 🛠️ Tech Stack

### Backend
- **Python 3.9+**
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database
- **scikit-learn** - ML classification
- **PyJWT** - Authentication

### Frontend
- **Vanilla HTML/CSS/JavaScript**
- **Fetch API** - HTTP requests
- **No external frameworks** - Pure JS

### ML Model
- **TF-IDF Vectorizer** - Text feature extraction
- **Logistic Regression** - Classification
- **64.29% accuracy** on Indian grievance dataset

---

## 📁 Project Structure

```
smart-grievance-system/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration
│   ├── extensions.py          # Database initialization
│   ├── models.py              # Database models
│   ├── seed.py                # Database seeding
│   ├── routes/
│   │   ├── auth.py            # Authentication routes
│   │   ├── grievances.py      # Grievance routes
│   │   └── admin.py           # Admin routes
│   └── services/
│       ├── classifier.py      # ML classification
│       ├── email_service.py   # Email notifications
│       ├── otp_service.py     # OTP generation/verification
│       └── content_moderator.py # Content moderation
├── frontend/
│   ├── index.html             # Citizen dashboard
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── track.html             # Grievance tracking
│   ├── officer.html           # Officer dashboard
│   ├── admin.html             # Admin dashboard
│   ├── profile.html           # User profile
│   ├── forgot-password.html   # Password reset
│   ├── verify-email.html      # Email verification
│   ├── styles.css             # Main styles
│   ├── app.js                 # Main JavaScript
│   ├── translations.js        # Multi-language support
│   ├── language-selector-widget.js  # Language selector
│   ├── complaint-translator.js      # Complaint translation
│   ├── department-backgrounds.css   # Department themes
│   └── department-showcase.js       # Department rotation
├── ml/
│   ├── train.py               # ML model training
│   └── artifacts/
│       ├── model.joblib       # Trained model
│       └── vectorizer.joblib  # TF-IDF vectorizer
├── data/
│   └── indian_grievance_dataset.csv  # Training data
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── GMAIL_SETUP_GUIDE.md       # Gmail SMTP setup
├── FORGOT_PASSWORD_FEATURE.md # Password reset guide
└── DEPARTMENT_BACKGROUNDS_FEATURE.md  # UI customization

```

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/Santhakumarramesh/smart-grievance-system.git
cd smart-grievance-system
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment

Create `.env` file:

```bash
# Demo Mode (OTPs in console)
DEMO_EMAIL_MODE=true

# For real emails, setup Gmail SMTP:
# DEMO_EMAIL_MODE=false
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-app-password
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USE_TLS=true
# MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### 4. Train ML Model

```bash
cd ml
python train.py
cd ..
```

### 5. Initialize Database

```bash
PYTHONPATH=. python backend/seed.py
```

### 6. Run Application

```bash
PORT=8000 PYTHONPATH=. python backend/app.py
```

### 7. Access Portal

Open browser: **http://localhost:8000**

---

## 👥 Demo Credentials

### Admin
- **Email:** admin@example.com
- **Password:** admin123

### Officer (Water Supply)
- **Email:** officer.water@example.com
- **Password:** officer123

### Citizen
- **Email:** citizen@example.com
- **Password:** citizen123

---

## 📧 Email Setup (Optional)

For real email notifications:

1. **Get Gmail App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Generate password for "Mail"

2. **Update .env:**
   ```bash
   DEMO_EMAIL_MODE=false
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-16-char-app-password
   ```

3. **Restart server**

See `GMAIL_SETUP_GUIDE.md` for detailed instructions.

---

## 🌐 Multi-Language Support

### Available Languages (12)

- English (English)
- हिंदी (Hindi)
- বাংলা (Bengali)
- தமிழ் (Tamil)
- తెలుగు (Telugu)
- मराठी (Marathi)
- ગુજરાતી (Gujarati)
- ಕನ್ನಡ (Kannada)
- മലയാളം (Malayalam)
- ਪੰਜਾਬੀ (Punjabi)
- ଓଡ଼ିଆ (Odia)
- অসমীয়া (Assamese)

### How to Use

1. **Click language selector** (🌐 button) on any page
2. **Select your preferred language**
3. **Page content updates automatically**
4. **Language preference saved** for future visits

### For Officers

- **Translate complaints** using the "🌐 Translate" button
- **View complaints** in your preferred language
- **Understand context** with keyword extraction

---

## 📊 Features by Role

### Citizen
- ✅ Register with email/phone verification
- ✅ Submit complaints with images and location
- ✅ Track complaint status in real-time
- ✅ Receive email notifications
- ✅ Add comments and feedback
- ✅ Manage profile (photo, personal details)
- ✅ Reset password if forgotten
- ✅ Change language preference

### Officer
- ✅ View department-specific complaints
- ✅ Update complaint status
- ✅ Add investigation notes
- ✅ Translate complaints to preferred language
- ✅ Reply to citizen comments
- ✅ View complaint images and location
- ✅ Access officer contact details

### Admin
- ✅ Create officer accounts
- ✅ Assign officers to departments
- ✅ View all complaints across departments
- ✅ Monitor system analytics
- ✅ View flagged/moderated content
- ✅ Access higher authority contacts
- ✅ Manage officer details (office number, email, location)

---

## 🔒 Security Features

- ✅ **Password Hashing** - Werkzeug secure hashing
- ✅ **JWT Tokens** - Secure authentication
- ✅ **OTP Verification** - Email-based verification
- ✅ **Rate Limiting** - 3 OTP requests per hour
- ✅ **Content Moderation** - Automatic threat detection
- ✅ **Input Validation** - Frontend and backend validation
- ✅ **CORS Protection** - Cross-origin request security
- ✅ **SQL Injection Prevention** - SQLAlchemy ORM

---

## 🎨 UI/UX Features

- ✅ **Pan-India Theme** - Tricolor elements, department colors
- ✅ **Department Showcase** - Daily rotating highlights
- ✅ **Floating Icons** - Subtle department representations
- ✅ **Rainbow Banner** - All department colors
- ✅ **Professional Cards** - Modern, clean design
- ✅ **Responsive Layout** - Mobile, tablet, desktop
- ✅ **Smooth Animations** - Hover effects, transitions
- ✅ **Accessibility** - WCAG compliant

---

## 📱 Mobile Support

- ✅ Fully responsive design
- ✅ Touch-friendly interface
- ✅ Optimized for small screens
- ✅ Mobile-first approach
- ✅ Fast loading times

---

## 🧪 Testing

### Manual Testing

1. **Register new user** → Verify email
2. **Submit complaint** → Check classification
3. **Track complaint** → View timeline
4. **Officer login** → Update status
5. **Admin login** → View analytics

### Test Scenarios

- ✅ Registration with OTP
- ✅ Login/logout
- ✅ Complaint submission
- ✅ Status updates
- ✅ Email notifications
- ✅ Password reset
- ✅ Profile updates
- ✅ Language switching
- ✅ Image upload
- ✅ Comment system

---

## 🚀 Deployment

### Local Development

```bash
PORT=8000 PYTHONPATH=. python backend/app.py
```

### Production (Render)

1. **Create Render account**
2. **Connect GitHub repository**
3. **Set environment variables**
4. **Deploy**

See deployment documentation for details.

---

## 📚 Documentation

- **README.md** - This file (overview)
- **GMAIL_SETUP_GUIDE.md** - Email configuration
- **FORGOT_PASSWORD_FEATURE.md** - Password reset guide
- **DEPARTMENT_BACKGROUNDS_FEATURE.md** - UI customization

---

## 🤝 Contributing

This is an academic project. For improvements:

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

---

## 📄 License

This project is for educational purposes.

---

## 👨‍💻 Author

**Santhakumar Ramesh**

- GitHub: [@Santhakumarramesh](https://github.com/Santhakumarramesh)
- Repository: [smart-grievance-system](https://github.com/Santhakumarramesh/smart-grievance-system)

---

## 🙏 Acknowledgments

- **scikit-learn** - Machine learning
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **Government of India** - Department structure and guidelines

---

## 📞 Support

For issues or questions:
1. Check documentation files
2. Review code comments
3. Open GitHub issue

---

## ✅ Status

**Production Ready** ✓

- All features implemented
- Tested and working
- Documentation complete
- Ready for demo/deployment

---

**Built with ❤️ for Digital India Initiative** 🇮🇳
