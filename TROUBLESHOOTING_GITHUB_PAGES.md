# 🔧 TROUBLESHOOTING: GitHub Pages Showing README Instead of Website

## Problem:
GitHub Pages is showing the README.md file instead of your actual website (index.html)

## Solution Steps:

### Step 1: Verify GitHub Pages Settings

Go to: https://github.com/Santhakumarramesh/smart-grievance-system/settings/pages

**Make sure these settings are EXACTLY as shown:**

```
Build and deployment
├── Source: Deploy from a branch
├── Branch: main
└── Folder: /docs  ← MUST BE /docs NOT /(root)
```

**If it says "/(root)" - CHANGE IT TO "/docs"**

---

### Step 2: Force GitHub to Rebuild

After changing to `/docs`:

1. Click **"Save"** button
2. Wait 1 minute
3. Go back to Pages settings
4. Change Branch to a different branch (if available) or just click Save again
5. This forces GitHub to rebuild

---

### Step 3: Clear Browser Cache

Your browser might be caching the old README page:

**Windows/Linux:**
- Press `Ctrl + Shift + R` or `Ctrl + F5`

**Mac:**
- Press `Cmd + Shift + R`

**Or use Incognito/Private mode:**
- Right-click on the link → Open in Incognito Window

---

### Step 4: Check the Exact URL

Make sure you're visiting the correct URL:

**✅ CORRECT URL:**
```
https://santhakumarramesh.github.io/smart-grievance-system/
```

**❌ WRONG URL (will show README):**
```
https://github.com/Santhakumarramesh/smart-grievance-system
```

The `.github.io` domain is for the live website!
The plain `github.com` domain shows the repository!

---

### Step 5: Wait for Deployment

GitHub Pages takes 2-5 minutes to build and deploy:

1. Go to: https://github.com/Santhakumarramesh/smart-grievance-system/actions
2. You should see "pages build and deployment" running
3. Wait for the green checkmark ✅
4. Then visit your website

---

### Step 6: Verify Files in /docs Folder

Go to: https://github.com/Santhakumarramesh/smart-grievance-system/tree/main/docs

You should see:
- ✅ index.html (MUST BE PRESENT)
- ✅ styles.css
- ✅ All other HTML/CSS/JS files
- ✅ .nojekyll file (just added)

If you see README.md in /docs - DELETE IT!

---

## Quick Diagnostic:

### Test 1: Check if Pages is Enabled
Visit: https://github.com/Santhakumarramesh/smart-grievance-system/settings/pages

You should see a green box saying:
"Your site is live at https://santhakumarramesh.github.io/smart-grievance-system/"

### Test 2: Check Build Status
Visit: https://github.com/Santhakumarramesh/smart-grievance-system/actions

Look for recent "pages build and deployment" - should be green ✅

### Test 3: Try Direct File Access
Visit: https://santhakumarramesh.github.io/smart-grievance-system/index.html

This should show your website!

---

## Common Issues & Fixes:

### Issue 1: "/(root)" folder selected instead of "/docs"
**Fix:** Go to Settings → Pages → Change folder to "/docs" → Save

### Issue 2: README.md exists in /docs folder
**Fix:** Delete README.md from /docs folder (keep it in root only)

### Issue 3: Jekyll processing the files
**Fix:** .nojekyll file added (already done!) ✅

### Issue 4: Browser cache
**Fix:** Hard refresh (Ctrl+Shift+R) or use Incognito mode

### Issue 5: Wrong URL
**Fix:** Make sure you're visiting `.github.io` not just `github.com`

---

## The Correct Setup:

```
Repository Structure:
├── README.md (in root) ← Shows on GitHub repository page
├── docs/
│   ├── .nojekyll ← Prevents Jekyll processing
│   ├── index.html ← YOUR WEBSITE HOMEPAGE
│   ├── styles.css
│   ├── login.html
│   └── ... (all other frontend files)
```

**GitHub Pages Settings:**
- Source: Deploy from a branch
- Branch: main
- Folder: /docs ← THIS IS CRITICAL!

---

## Test Your Setup:

1. **Repository Page** (README): https://github.com/Santhakumarramesh/smart-grievance-system
   - Should show: README.md documentation

2. **Live Website** (Your App): https://santhakumarramesh.github.io/smart-grievance-system/
   - Should show: Your actual website with homepage

---

## Still Not Working?

### Option A: Disable and Re-enable Pages

1. Go to Settings → Pages
2. Change Source to "None"
3. Click Save
4. Wait 1 minute
5. Change Source back to "Deploy from a branch"
6. Select Branch: main, Folder: /docs
7. Click Save
8. Wait 3-5 minutes

### Option B: Check Actions Log

1. Go to: https://github.com/Santhakumarramesh/smart-grievance-system/actions
2. Click on latest "pages build and deployment"
3. Check for any error messages
4. Share the error if you see one

### Option C: Manual Verification

Run this in your terminal:

```bash
cd "/Users/santhakumar/Desktop/smart greviance system/docs"
ls -la
```

You should see `index.html` - this is your website homepage!

---

## What You Should See:

**When you visit:** https://santhakumarramesh.github.io/smart-grievance-system/

**You should see:**
- 🇮🇳 Smart Grievance Redressal System header
- Government portal design
- Navigation menu
- Homepage with department showcase
- NOT the README documentation!

---

## Summary Checklist:

- [ ] Settings → Pages → Folder is set to "/docs" (not root)
- [ ] Clicked "Save" after changing to /docs
- [ ] Waited 3-5 minutes for deployment
- [ ] Visiting correct URL (.github.io domain)
- [ ] Cleared browser cache (Ctrl+Shift+R)
- [ ] index.html exists in /docs folder
- [ ] .nojekyll file added to /docs
- [ ] No README.md in /docs folder

---

**After following these steps, your website WILL work! 🚀**

The key is: Make sure GitHub Pages is set to deploy from `/docs` folder, not root!