# 🚀 GitHub Push Guide - Workflow Files

## ⚠️ Issue: Personal Access Token Missing `workflow` Scope

Your current GitHub Personal Access Token (PAT) doesn't have permission to create/update workflow files.

---

## ✅ Solution: Update Your GitHub Token

### Option 1: Update Token Scope (Recommended)

1. **Go to GitHub Settings:**
   - Visit: https://github.com/settings/tokens
   - Or: GitHub.com → Profile Picture → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Find Your Current Token:**
   - Look for the token you're using for this repository
   - Click "Edit" or create a new token

3. **Add Required Scopes:**
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows) **← ADD THIS**
   - ✅ `write:packages` (optional, for package publishing)

4. **Generate/Update Token:**
   - Click "Update token" or "Generate token"
   - **IMPORTANT:** Copy the new token immediately (you won't see it again!)

5. **Update Git Credentials:**
   ```bash
   # On macOS, update keychain
   git credential-osxkeychain erase
   host=github.com
   protocol=https
   [Press Enter twice]
   
   # Next time you push, enter your username and NEW token as password
   ```

### Option 2: Push Without Workflow Files (Quick Fix)

If you need to push immediately without workflows:

```bash
cd "/Users/santhakumar/Desktop/smart greviance system"

# Temporarily remove workflow files from staging
git reset HEAD .github/workflows/

# Commit without workflows
git commit -m "feat: Add deployment scripts and documentation"

# Push
git push origin main

# Add workflows later when token is updated
git add .github/workflows/
git commit -m "feat: Add GitHub Actions CI/CD workflows"
git push origin main
```

### Option 3: Manual Upload (Alternative)

1. **Push non-workflow files first:**
   ```bash
   cd "/Users/santhakumar/Desktop/smart greviance system"
   git reset HEAD .github/workflows/
   git commit -m "feat: Add deployment scripts"
   git push origin main
   ```

2. **Manually create workflows on GitHub:**
   - Go to your repository on GitHub
   - Click "Actions" tab
   - Click "New workflow" or "set up a workflow yourself"
   - Copy content from `.github/workflows/ci-cd.yml`
   - Commit directly on GitHub
   - Repeat for `status-badge.yml`

---

## 📝 Current Changes Ready to Push

Your commit includes:
- ✅ `.github/workflows/ci-cd.yml` - Complete CI/CD pipeline
- ✅ `.github/workflows/status-badge.yml` - Build status badge
- ✅ `DEPLOYMENT.md` - Comprehensive deployment guide
- ✅ `README.md` - Updated with new badges
- ✅ `run.py` - Application entry point
- ✅ `create_demo_hierarchy.py` - Demo user creation script

---

## 🔄 After Updating Token

Once you have a token with `workflow` scope:

```bash
cd "/Users/santhakumar/Desktop/smart greviance system"

# Push all changes
git push origin main

# Verify workflows are uploaded
# Go to: https://github.com/Santhakumarramesh/smart-grievance-system/actions
```

---

## ✅ Verify GitHub Actions

After successful push:

1. **Go to Actions Tab:**
   - https://github.com/Santhakumarramesh/smart-grievance-system/actions

2. **You Should See:**
   - 🟢 Build Status workflow running
   - 🟢 CI/CD Pipeline workflow running

3. **Check Workflow Status:**
   - Click on a workflow run
   - See all jobs executing
   - Download artifacts after completion

---

## 🎯 What Happens After Push

When you push with workflows enabled:

1. **Automatic Triggers:**
   - Push to `main` → Both workflows run
   - Pull request → Workflows run for validation

2. **Workflow Jobs Execute:**
   - Code quality checks
   - Security scans
   - Tests
   - Health checks
   - Deployment package creation

3. **Results Available:**
   - Build status badge updates automatically
   - Artifacts available for download
   - Detailed logs for each job

---

## 🆘 Still Having Issues?

### Check Token Permissions
```bash
# Test if token has workflow scope
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/user
```

### Alternative: Use SSH Instead
```bash
# Switch to SSH authentication (no token needed)
git remote set-url origin git@github.com:Santhakumarramesh/smart-grievance-system.git
git push origin main
```

### Contact Support
- GitHub Support: https://support.github.com
- Repository Issues: https://github.com/Santhakumarramesh/smart-grievance-system/issues

---

## 📚 Additional Resources

- [GitHub PAT Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

**Ready to proceed?** Update your token and push! 🚀
