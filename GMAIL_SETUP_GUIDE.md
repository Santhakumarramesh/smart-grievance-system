# 📧 Gmail SMTP Setup - Step-by-Step Guide

## 🎯 Goal
Set up Gmail SMTP so you receive **real OTP emails** in your Gmail inbox (not console).

---

## ⚡ Quick Setup (2 Methods)

### Method 1: Automated Script (Easiest)

```bash
cd "/Users/santhakumar/Desktop/smart greviance system"
./setup_gmail_smtp.sh
```

The script will:
1. Ask for your Gmail address
2. Ask for your Gmail App Password
3. Configure everything automatically
4. Restart the server
5. ✅ Done!

---

### Method 2: Manual Setup

Follow the detailed steps below.

---

## 📋 Step-by-Step Manual Setup

### Step 1: Enable 2-Step Verification (If Not Already Enabled)

1. **Go to:** https://myaccount.google.com/security

2. **Scroll to "How you sign in to Google"**

3. **Click "2-Step Verification"**

4. **If not enabled:**
   - Click "Get Started"
   - Follow the setup process
   - Verify with your phone number
   - Complete setup

5. **If already enabled:**
   - You'll see "2-Step Verification is on"
   - Proceed to Step 2

---

### Step 2: Generate Gmail App Password

1. **Go to:** https://myaccount.google.com/apppasswords

2. **Sign in** if prompted

3. **You should see "App passwords" page**

4. **Select app:** Choose **"Mail"**

5. **Select device:** Choose **"Other (Custom name)"**

6. **Enter name:** Type **"Smart Grievance System"**

7. **Click "Generate"**

8. **Copy the password:**
   ```
   Example shown: abcd efgh ijkl mnop
   
   ⚠️ IMPORTANT: Remove ALL spaces!
   
   Use this: abcdefghijklmnop
   ```

9. **Save it somewhere safe!** You won't be able to see it again.

---

### Step 3: Update .env File

**Option A: Use the script (easier)**
```bash
./setup_gmail_smtp.sh
```

**Option B: Edit manually**

1. **Open .env file:**
   ```bash
   cd "/Users/santhakumar/Desktop/smart greviance system"
   nano .env
   ```

2. **Replace ALL content with:**
   ```bash
   # Email Configuration
   DEMO_EMAIL_MODE=false
   FORMSPREE_ENDPOINT=https://formspree.io/f/xpqjrqde

   # Gmail SMTP Configuration
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-16-char-app-password
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

3. **Replace these values:**
   - `your-email@gmail.com` → Your actual Gmail address
   - `your-16-char-app-password` → The app password from Step 2 (NO SPACES!)

4. **Example:**
   ```bash
   MAIL_USERNAME=john.doe@gmail.com
   MAIL_PASSWORD=abcdefghijklmnop
   MAIL_DEFAULT_SENDER=john.doe@gmail.com
   ```

5. **Save and exit:**
   - Press `Ctrl + X`
   - Press `Y`
   - Press `Enter`

---

### Step 4: Restart Server

```bash
cd "/Users/santhakumar/Desktop/smart greviance system"
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 2
PORT=8000 PYTHONPATH=. python backend/app.py
```

**Look for this in the output:**
```
📧 Demo Mode: False  ← Must be False!
```

If it says `True`, check your .env file again.

---

### Step 5: Test It!

1. **Go to:** http://localhost:8000/register.html

2. **Register with YOUR REAL GMAIL:**
   ```
   First Name: Test
   Last Name: User
   Email: your-actual-email@gmail.com  ← YOUR Gmail!
   Phone: 9876543210
   Date of Birth: 2000-01-01
   Gender: Male
   Password: Test@123
   Confirm Password: Test@123
   ```

3. **Click "Register"**

4. **Check your Gmail inbox!** 📧

5. **Look for email:**
   ```
   From: your-email@gmail.com
   Subject: Your OTP for Smart Grievance System Verification
   
   Your One-Time Password (OTP) is:
   
   456789  ← Copy this!
   ```

6. **Enter OTP** on verification page

7. **Click "Verify Email"**

8. ✅ **Success!**

---

## 🔍 Verification Checklist

Before testing, verify:

- [ ] 2-Step Verification is enabled on Gmail
- [ ] Generated Gmail App Password (16 characters)
- [ ] Copied app password WITHOUT spaces
- [ ] Updated .env file with correct email
- [ ] Updated .env file with correct app password
- [ ] Set `DEMO_EMAIL_MODE=false`
- [ ] Restarted server
- [ ] Server shows "Demo Mode: False"

---

## 🐛 Troubleshooting

### Problem 1: "Can't find App Passwords option"

**Cause:** 2-Step Verification not enabled

**Solution:**
1. Go to: https://myaccount.google.com/security
2. Enable "2-Step Verification"
3. Complete setup with phone verification
4. Go back to: https://myaccount.google.com/apppasswords

---

### Problem 2: "Email not received"

**Check these:**

1. **Check Spam/Junk folder** 📁
   - Gmail might filter it initially
   - Mark as "Not Spam" if found

2. **Verify .env settings:**
   ```bash
   cat .env
   ```
   
   Should show:
   ```
   DEMO_EMAIL_MODE=false  ← Must be false!
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=abcdefghijklmnop  ← No spaces!
   ```

3. **Check server logs:**
   ```bash
   tail -50 ~/.cursor/projects/*/terminals/17.txt
   ```
   
   Look for:
   ```
   ✓ Email sent via Gmail to user@example.com  ← Success!
   ```
   
   OR
   ```
   ⚠ Gmail SMTP failed: [error message]  ← Problem!
   ```

4. **Test Gmail credentials:**
   ```bash
   cd "/Users/santhakumar/Desktop/smart greviance system"
   python3 << 'EOF'
   import smtplib
   
   # Replace with YOUR credentials
   username = "your-email@gmail.com"
   password = "your-app-password"
   
   try:
       server = smtplib.SMTP('smtp.gmail.com', 587)
       server.starttls()
       server.login(username, password)
       print("✅ Gmail login successful!")
       server.quit()
   except Exception as e:
       print(f"❌ Gmail login failed: {e}")
   EOF
   ```

---

### Problem 3: "Authentication failed"

**Causes:**
- Wrong app password
- Spaces in app password
- Using regular password instead of app password
- Wrong email address

**Solution:**
1. Generate NEW app password
2. Copy it WITHOUT spaces
3. Update .env file
4. Restart server

---

### Problem 4: "Still showing Demo Mode"

**Check:**
```bash
cat .env | grep DEMO_EMAIL_MODE
```

Should show:
```
DEMO_EMAIL_MODE=false
```

If it shows `true`, change it to `false` and restart server.

---

## 📧 What Emails Will Be Sent?

### 1. **OTP Email** (Registration)
```
Subject: Your OTP for Smart Grievance System Verification

Your One-Time Password (OTP) is:

    456789

• Valid for 5 minutes
• Don't share with anyone
```

### 2. **Welcome Email** (After Verification)
```
Subject: Welcome to Smart Grievance System 🇮🇳

Your account has been successfully created and verified.

You can now:
✓ Submit grievances
✓ Track complaints
✓ Receive updates
```

### 3. **Forgot Password OTP**
```
Subject: Your OTP for Smart Grievance System Verification

Your One-Time Password (OTP) is:

    123456

• Valid for 5 minutes
```

### 4. **Password Reset Confirmation**
```
Subject: Password Reset Successful

Your password has been successfully reset.

If you didn't request this, contact us immediately.
```

### 5. **Grievance Updates**
```
Subject: Grievance #123 - Status Update: Under Progress

Your grievance has been updated:

Complaint ID: #123
Department: Water Supply
Status: Under Progress

[Track Your Complaint]
```

### 6. **Comment Notifications**
```
Subject: New Comment on Grievance #123

A new comment has been added to your grievance:

From: Officer Name
Comment: We are investigating the issue...

[View & Reply]
```

---

## 🎬 Demo Preparation

### Before Demo:

1. **Setup Gmail SMTP** (follow steps above)

2. **Test with your email:**
   - Register test account
   - Verify OTP received in Gmail
   - Confirm all emails working

3. **Prepare demo account:**
   - Use a real email you can access
   - Have Gmail open on phone or another tab

4. **Practice the flow:**
   - Register → Check email → Enter OTP → Verify

---

### During Demo:

**Setup:**
- Browser on main screen
- Gmail on phone or side screen
- Keep both visible

**Script:**

> "Let me demonstrate the registration process with email verification..."

1. **Fill registration form** with real email

> "When I click Register, the system sends a verification code to my email..."

2. **Click Register**

> "Here's the email with my OTP..."

3. **Show Gmail on phone/screen** with OTP email

> "The OTP is time-limited for security - valid for only 5 minutes..."

4. **Enter OTP** from email

> "And now my account is verified!"

5. **Show verification success**

> "I also receive a welcome email confirming my account creation..."

6. **Show welcome email**

> "Now I can login and submit complaints, and I'll receive email updates for every status change..."

7. **Login and show dashboard**

**Key Points to Mention:**
- ✅ Real email verification (not demo)
- ✅ Time-limited OTP (5 minutes)
- ✅ Secure authentication
- ✅ Email notifications for all updates
- ✅ Professional email templates
- ✅ Mobile-friendly

---

## 📊 Email Limits

**Gmail Free Account:**
- **500 emails per day**
- **100 emails per hour** (approx)

**For your demo:**
- Registration: 2 emails (OTP + Welcome)
- Password Reset: 2 emails (OTP + Confirmation)
- Complaint: 2 emails (Received + Assigned)
- Updates: 1 email per update
- Comments: 1 email per comment

**Example:**
- 10 registrations = 20 emails
- 20 complaints = 40 emails
- 30 updates = 30 emails
- **Total: 90 emails** (well within limit!)

---

## ✅ Quick Commands

### Setup Gmail SMTP:
```bash
cd "/Users/santhakumar/Desktop/smart greviance system"
./setup_gmail_smtp.sh
```

### Check Configuration:
```bash
cat .env
```

### Restart Server:
```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null
PORT=8000 PYTHONPATH=. python backend/app.py &
```

### Check Server Logs:
```bash
tail -f ~/.cursor/projects/*/terminals/17.txt
```

### Test Gmail Login:
```bash
python3 -c "import smtplib; s=smtplib.SMTP('smtp.gmail.com',587); s.starttls(); s.login('YOUR_EMAIL','YOUR_APP_PASSWORD'); print('✅ Success!'); s.quit()"
```

### Switch Back to Demo Mode:
```bash
./enable_demo_otp.sh
```

---

## 🎯 Summary

**To get real Gmail OTPs:**

1. ✅ Enable 2-Step Verification
2. ✅ Generate Gmail App Password
3. ✅ Run `./setup_gmail_smtp.sh`
4. ✅ Enter Gmail credentials
5. ✅ Test with real email
6. ✅ Done!

**Result:**
- 📧 OTPs sent to real Gmail
- 📧 Welcome emails sent
- 📧 Password reset emails sent
- 📧 Grievance update emails sent
- 📧 Comment notification emails sent

**For Demo:**
- Show Gmail on phone/screen
- Demonstrate real email functionality
- Professional presentation
- No terminal needed!

🎉 **Much better than console OTP!**
