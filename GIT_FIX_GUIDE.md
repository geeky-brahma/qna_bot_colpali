# Fixing Git Push Issues

## Issue Summary
GitHub blocked your push for two reasons:
1. **Secrets detected** - Google OAuth credentials in VERCEL_DEPLOYMENT.md
2. **Large files** - embeddings_town_planning_architecture.pt (60.92 MB)

## ✅ Fixed
- Removed actual OAuth credentials from VERCEL_DEPLOYMENT.md (replaced with placeholders)
- Added `*.pt` and `*.pth` to .gitignore to exclude large model files

## 🔧 Steps to Fix and Push Successfully

### Step 1: Reset the Last Commit (Keep Your Changes)

```powershell
# Undo the commit but keep all changes
git reset --soft HEAD~1
```

### Step 2: Unstage the Large Files

```powershell
# Remove large .pt files from staging
git reset HEAD inference-backend/debug_downloads/*.pt
```

### Step 3: Re-add Files and Commit

```powershell
# Add all files except those in .gitignore
git add .

# Commit with a clean message
git commit -m "Initial commit - ready for deployment"
```

### Step 4: Push to GitHub

```powershell
git push -u origin main
```

---

## Alternative: If Push Still Fails

If you already made multiple commits with secrets, use this approach:

### Option A: Force Delete and Start Fresh (Nuclear Option)

```powershell
# Remove the .git folder
Remove-Item -Recurse -Force .git

# Reinitialize git
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/geeky-brahma/qna_bot_colpali.git
git push -u origin main --force
```

### Option B: Clean Git History (Recommended)

```powershell
# Install BFG Repo Cleaner (if not installed)
# Download from: https://rtyley.github.io/bfg-repo-cleaner/

# Or use git filter-repo (better option)
pip install git-filter-repo

# Remove the secrets file from history
git filter-repo --path VERCEL_DEPLOYMENT.md --invert-paths

# Re-add the corrected file
git add VERCEL_DEPLOYMENT.md
git commit -m "Add deployment docs with placeholder credentials"

# Force push
git push origin main --force
```

---

## 🔒 Security Best Practices

### 1. Never Commit Secrets
- ✅ Use `.env` files (already in .gitignore)
- ✅ Use placeholder values in documentation
- ✅ Store real secrets in:
  - Vercel dashboard (for frontend)
  - GitHub Secrets (for CI/CD)
  - GCP Secret Manager (for backend)

### 2. Environment Files to Check

Before committing, verify these files don't contain secrets:

```powershell
# Check for exposed secrets
git grep -i "GOCSPX"
git grep -i "apps.googleusercontent.com"
git grep -i "client_secret"
```

### 3. Files Already Protected

These are in .gitignore and won't be committed:
- `frontend/.env.local` - Local environment variables
- `*.pt`, `*.pth` - Large model files
- `__pycache__/` - Python cache
- `node_modules/` - Node dependencies

---

## 📦 Handling Large Files

For the large .pt files (embeddings), you have options:

### Option 1: Don't Commit Them (Recommended)
```powershell
# Already in .gitignore, they won't be committed
# Store them in:
# - Google Cloud Storage
# - AWS S3
# - Download programmatically in deployment
```

### Option 2: Use Git LFS
```powershell
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.pt"
git lfs track "*.pth"

# Add and commit
git add .gitattributes
git add *.pt
git commit -m "Add model files with Git LFS"
git push
```

---

## ✅ Verification Checklist

Before pushing:
- [ ] VERCEL_DEPLOYMENT.md has placeholder credentials
- [ ] No `.env` or `.env.local` files staged
- [ ] Large `.pt` files not staged (check with `git status`)
- [ ] Run: `git diff --cached` to review what's being committed
- [ ] No secrets in committed files

---

## 🚀 After Successful Push

1. **Deploy to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Import your repository
   - Set environment variables in Vercel dashboard

2. **Set Real Secrets in Vercel:**
   - GOOGLE_CLIENT_ID
   - GOOGLE_CLIENT_SECRET
   - NEXTAUTH_SECRET
   - NEXT_PUBLIC_API_URL

3. **Never commit these to git again!**

---

## Quick Reference

```powershell
# Check what's staged
git status

# Check what will be committed
git diff --cached

# Unstage a file
git reset HEAD <file>

# Unstage all files
git reset

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Check for secrets
git grep -E "(GOCSPX|apps.googleusercontent.com|client_secret)"
```

---

**Start with Step 1 above to fix your current issue!**
