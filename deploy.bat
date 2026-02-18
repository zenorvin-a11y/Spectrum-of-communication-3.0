@echo off
echo Deploying to Render...
echo.

git add .
git commit -m "Update application"
git push origin main

echo.
echo Done! Check Render dashboard.
pause
