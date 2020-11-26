@echo off
rem   just kills stray local chromedriver.exe instances.
rem   useful if you are trying to clean your project, and your ide is complaining.

for /f %%a in ('TaskList ^| FIND /I /C "Ulti.exe"') do set count1=%%a


taskkill /im chrome.exe /f

for /f %%a in ('TaskList ^| FIND /I /C "Ulti.exe"') do set count2=%%a
echo %count1% - %count2% Processes Killed

pause