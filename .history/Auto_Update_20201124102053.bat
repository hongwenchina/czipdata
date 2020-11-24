@echo off
REM %DATE:~0,10%  2020/11/24
set dd=%DATE:~0,10%
set tt=%time:~0,8%
set hour=%tt:~0,2%
REM change file directory
cd /d %~dp0
echo =======================================================
echo          Starting automatic update czipdata
echo =======================================================
REM python ./IP_Sync/ip_Sync.py
echo =======================================================
echo          Starting automatic git commit push
echo =======================================================
REM start git script 
echo %~dp0
git add .
git status -s
git commit -m "定时同步 %dd:/=-% %tt%"
git push origin main
git push Gitee main
pause