@echo off
if "%1" == "h" goto begin
mshta vbscript:createobject("wscript.shell").run("%~nx0 h",0)(window.close)&&exit
:begin
@echo off 
title =��ʱͬ������czipdata By A76YYYY
REM %DATE:~0,10%  2020/11/24
set dd=%DATE:~0,10%
set tt=%time:~0,8%
set hour=%tt:~0,2%
set ymd=%dd:/=-%
REM change file directory
CD /d %~dp0
REM �ж�logĿ¼�Ƿ���ڣ�����������򴴽�
SET logFolder=log
IF NOT EXIST %logFolder% (
REM  ����logĿ¼ ���ڵ�ǰλ�ô���logĿ¼��
ECHO %logFolder%Ŀ¼�����ڣ��Ѵ�����Ŀ¼��
MD %logFolder%
)
REM create log file
set Log=log\Auto_Update_%ymd%.log
(echo =======================================================
echo          Starting automatic update czipdata
echo =======================================================
python ./IP_Sync/ip_Sync.py
echo =======================================================
echo          Starting automatic git commit push
echo =======================================================
REM start git script 
echo %~dp0
git add .
git status -s
git commit -m "��ʱͬ�� %dd:/=-% %tt%"
git push origin main
git push Gitee main
)>"%Log%"
pause