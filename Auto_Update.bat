@ECHO OFF
IF "%1" == "h" GOTO begin
mshta vbscript:createobject("wscript.shell").run("%~nx0 h",0)(window.close)&&exit
:begin
@ECHO OFF 
TITLE =��ʱͬ������czipdata By A76YYYY
REM %DATE:~0,10%  2020/11/24
SET dd=%DATE:~0,10%
SET tt=%time:~0,8%
SET hour=%tt:~0,2%
SET ymd=%dd:/=-%
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
SET Log=log\Auto_Update_%ymd%.log
(ECHO =======================================================
ECHO          Starting automatic update czipdata
ECHO =======================================================
python ./IP_Sync/ip_Sync.py
ECHO =======================================================
ECHO          Starting automatic git commit push
ECHO =======================================================
REM start git script 
ECHO %~dp0
git add .
git status -s
git commit -m "��ʱͬ�� %dd:/=-% %tt%"
git push origin main
git push Gitee main
)>"%Log%"