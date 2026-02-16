# 🚀 Quick Run Guide - Smart Grievance System

## ⚡ Quick Start (3 Commands)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup (train model + seed database)
python ml/train.py && python -m backend.seed

# 3. Run the application
python backend/app.py
```

Then open: **http://localhost:5000**

---

## 📧 Enable Real Email (Optional)

If you want real email delivery:

1. **Get Gmail App Password**: https://myaccount.google.com/apppasswords

2. **Create .env file**:
```bash
cat > .env << 'EOF'
DEMO_EMAIL_MODE=false
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
EOF
```

3. **Run the app**:
```bash
python backend/app.py
```

---

## 🎯 Test Accounts

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@grievance.gov | admin123 |
| **Officer** | electricity@grievance.gov | officer123 |
| **Citizen** | citizen@example.com | citizen123 |

---

## 🎬 Quick Demo Flow

1. **Login as Citizen** (citizen@example.com / citizen123)
2. **Submit Complaint**: "Street lights not working"
3. **AI Classifies** → Electricity department
4. **Track Progress** → See timeline
5. **Login as Officer** (electricity@grievance.gov / officer123)
6. **Update Status** → Add comment
7. **Check Email** → Notification sent (console in demo mode)

---

## 🔧 Troubleshooting

**Issue**: Module not found
```bash
pip install -r requirements.txt
```

**Issue**: ML model not found
```bash
python ml/train.py
```

**Issue**: Database not found
```bash
python -m backend.seed
```

**Issue**: Port 5000 in use
```bash
export PORT=8000
python backend/app.py
```

---

## 📚 Documentation

- **README.md** - Complete documentation
- **QUICKSTART.md** - Detailed setup guide
- **DEMO_GUIDE.md** - Demo script for professor
- **EMAIL_SETUP.md** - Real email configuration

---

**That's it! Your system is ready!** 🎉
