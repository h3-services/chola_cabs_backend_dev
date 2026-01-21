@echo off
echo 🚀 Deploying to Hostinger VPS...

REM SSH and deploy
ssh -o StrictHostKeyChecking=no root@72.62.196.30 "cd /root/cab_app && git pull origin main && systemctl restart cab-api && systemctl status cab-api --no-pager -l"

echo.
echo ✅ Deployment completed!
echo 📋 New odometer endpoints deployed:
echo    PATCH /api/v1/trips/{trip_id}/odometer-start
echo    PATCH /api/v1/trips/{trip_id}/odometer-end
echo.
echo 🌐 Test at: http://72.62.196.30:8000/docs
pause