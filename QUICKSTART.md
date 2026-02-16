# ⚡ Quick Start Guide

## 🎯 One-Command Start

### macOS/Linux
```bash
./start.sh
```

### Windows
```bash
start.bat
```

Then open: **http://localhost:8000**

---

## 🔑 Test Accounts

| Role | Email | Password | Purpose |
|------|-------|----------|---------|
| **Citizen** | citizen@example.com | citizen123 | Submit complaints |
| **Officer** | electricity@grievance.gov | officer123 | Handle complaints |
| **Admin** | admin@grievance.gov | admin123 | Manage system |

---

## 🎬 5-Minute Demo

### Step 1: Submit a Complaint (as Citizen)
1. Login: `citizen@example.com` / `citizen123`
2. Fill complaint: "Street lights not working in my area"
3. Select location
4. Submit
5. **AI assigns to "Streetlights" department automatically**

### Step 2: Track Your Complaint
1. Click "Track Complaints"
2. View timeline (Amazon-style)
3. See status updates
4. Add comments

### Step 3: Handle Complaint (as Officer)
1. Logout and login as: `streetlights@grievance.gov` / `officer123`
2. View assigned complaints
3. Click "Update Status"
4. Change status to "Under Progress"
5. Add message: "Team dispatched to location"
6. **Citizen receives email notification**

### Step 4: Two-Way Communication
1. Officer adds comment: "What is the exact pole number?"
2. Citizen replies: "Pole #234 near park"
3. Both receive email notifications

### Step 5: Admin Dashboard
1. Login as: `admin@grievance.gov` / `admin123`
2. View analytics
3. Create new officers
4. Monitor resolution times

---

## 📧 Enable Real Email

By default, emails print to console. To send real emails:

### 1. Get Gmail App Password
Visit: https://myaccount.google.com/apppasswords

### 2. Create `.env` file
```bash
DEMO_EMAIL_MODE=false
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

### 3. Restart
```bash
./start.sh
```

---

## 🌐 Change Language

1. Click language dropdown (top-right)
2. Select from 12 Indian languages
3. UI translates instantly

---

## 🛠️ Troubleshooting

### Port 5000 already in use?
The app automatically uses port 8000. If that's also busy:
```bash
PORT=9000 PYTHONPATH=. python backend/app.py
```

### Dependencies not installed?
```bash
pip install -r requirements.txt
```

### ML model missing?
```bash
python ml/train.py
```

### Database not found?
```bash
python -m backend.seed
```

---

## 📱 Access from Phone

If running on your computer and want to test from phone:

1. Find your computer's IP (e.g., 192.168.1.3)
2. On phone, visit: `http://192.168.1.3:8000`
3. Login and test!

---

## 🎓 For Professors/Reviewers

### Quick Demo Script
1. **Show AI Classification**: Submit "Water leaking" → Auto-assigns to "Water Supply"
2. **Show Multi-Language**: Switch to Hindi/Tamil
3. **Show Real-Time Tracking**: Timeline updates
4. **Show Two-Way Communication**: Comments feature
5. **Show Analytics**: Admin dashboard statistics

### Key Highlights
- ✅ No paid APIs (100% free)
- ✅ AI-powered (64% accuracy)
- ✅ 12 Indian languages
- ✅ 17 government departments
- ✅ Production-ready code
- ✅ Deployable on Render

---

**Need help?** Check `README.md` for detailed documentation.
