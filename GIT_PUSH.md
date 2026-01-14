# 📤 Push Code to GitHub

## Option 1: Using the Script (Easiest)

Double-click `push_to_github.bat` or run:
```cmd
cd d:\cab_ap
push_to_github.bat
```

## Option 2: Manual Commands

### Step 1: Open PowerShell/CMD in project folder
```cmd
cd d:\cab_ap
```

### Step 2: Initialize Git (if not done)
```bash
git init
git remote add origin https://github.com/PraveenCoder2007/cab_app.git
```

### Step 3: Add and Commit
```bash
git add .
git commit -m "Add file upload functionality for KYC documents and vehicle photos"
```

### Step 4: Push to GitHub
```bash
git branch -M main
git push -u origin main --force
```

## 🔐 If Asked for Credentials

### Option A: Use Personal Access Token
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo`
4. Copy the token
5. Use token as password when pushing

### Option B: Use GitHub CLI
```bash
# Install GitHub CLI first
winget install GitHub.cli

# Login
gh auth login

# Push
git push
```

## ✅ Verify

After pushing, check: https://github.com/PraveenCoder2007/cab_app

## 📝 What's Being Pushed

New files:
- `app/routers/uploads.py` - File upload endpoints
- `docs/api/uploads.md` - Upload API documentation
- `deploy.sh` - VPS deployment script
- `DEPLOYMENT.md` - Deployment guide
- `WINDOWS_SETUP.md` - Local setup guide
- `setup_uploads.sh` - Upload setup script
- `UPLOAD_SETUP.md` - Upload instructions

Updated files:
- `app/main.py` - Added uploads router and static file serving
- `.env.example` - Added upload configuration
- `.gitignore` - Added uploads directory
- `README.md` - Already has deployment info

## 🚫 Not Being Pushed (Protected)

- `.env` - Your actual credentials
- `venv/` - Virtual environment
- `uploads/` - Uploaded files
- `__pycache__/` - Python cache
- `*.db` - Database files

## 🔄 Future Updates

```bash
cd d:\cab_ap
git add .
git commit -m "Your update message"
git push
```
