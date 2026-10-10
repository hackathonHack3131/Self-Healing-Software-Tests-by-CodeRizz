@echo off
set MVN_HOME=C:\Users\ratho\apache-maven-3.9.9
if exist "%MVN_HOME%\bin\mvn.cmd" (
    "%MVN_HOME%\bin\mvn.cmd" %*
) else (
    mvn %*
)
