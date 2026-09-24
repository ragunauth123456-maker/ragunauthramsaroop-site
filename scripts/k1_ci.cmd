@echo off
setlocal
cd /d C:\AgentSwarm\ragunauth-site
python scripts\k1_ci.py
exit /b %ERRORLEVEL%
