@echo off
REM Git Push Script for Windows

echo 🚀 Pushing code to GitHub...
echo.

cd /d d:\cab_ap

REM Initialize git if not already done
if not exist .git (
    echo Initializing Git repository...
    git init
    git remote add origin https://github.com/h3-services/chola_cabs_backend_dev.git
)

REM Add all files
echo Adding files...
git add .

REM Commit changes
echo Committing changes...
git commit -m "Add file upload functionality for KYC documents and vehicle photos"

REM Push to GitHub
echo Pushing to GitHub...
git branch -M main
git push -u origin main --force

echo.
echo ✅ Code pushed successfully!
echo 📝 Repository: https://github.com/h3-services/chola_cabs_backend_dev
pause
