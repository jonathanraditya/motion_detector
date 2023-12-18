ECHO Starting Firefox browser instances cleaner ...

:infloop
ECHO Killing Firefox Processes
date /t & time /t
@ECHO OFF
taskkill/im firefox.exe
ECHO Firefox processes cleanup finished. Sleep for half the day.
timeout 40000
goto infloop
