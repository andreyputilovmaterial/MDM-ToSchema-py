@ECHO OFF

ECHO Clear up dist\...
IF EXIST dist (
    REM -
) ELSE (
    MKDIR dist
)
DEL /F /Q dist\*

ECHO -
ECHO -
ECHO Update program version
ECHO '''For auto-generated files''' > src\GENERATED\__init__.py
ECHO # THIS IS AUTO-GENERATED > src\GENERATED\_VERSION.py
python -c "from datetime import datetime; print(f'# {datetime.now()}')" >> src\GENERATED\_VERSION.py
ECHO _VERSION = ''' >> src\GENERATED\_VERSION.py
git describe --tags --dirty >> src\GENERATED\_VERSION.py
ECHO ''' >> src\GENERATED\_VERSION.py
ECHO Done

@REM ECHO -
@REM ECHO -
@REM ECHO Produce distributable .py bundle - calling pinliner...
@REM REM REM :: comment: please delete .pyc files before every call of the mdmtoolsap_bundle - this is implemented in my fork of the pinliner
@REM @REM python src_dev_build\lib\pinliner\pinliner\pinliner.py src -o dist/mdmtoolsap_bundle.py --verbose
@REM python src_dev_build\lib\pinliner\pinliner\pinliner.py src -o dist/mdmtoolsap_bundle.py
@REM if %ERRORLEVEL% NEQ 0 ( echo ERROR: Failure && pause && exit /b %errorlevel% )
@REM ECHO Done

@REM ECHO -
@REM ECHO -
@REM ECHO Patching mdmtoolsap_bundle.py...
@REM ECHO # ... >> dist/mdmtoolsap_bundle.py
@REM ECHO # print('within mdmtoolsap_bundle') >> dist/mdmtoolsap_bundle.py
@REM REM REM :: no need for this, the root package is loaded automatically
@REM @REM ECHO # import mdmtoolsap_bundle >> dist/mdmtoolsap_bundle.py
@REM ECHO from src import launcher >> dist/mdmtoolsap_bundle.py
@REM ECHO launcher.main() >> dist/mdmtoolsap_bundle.py
@REM ECHO # print('out of mdmtoolsap_bundle') >> dist/mdmtoolsap_bundle.py
@REM ECHO Done

@REM DEL *.pyc
@REM IF EXIST __pycache__ (
@REM DEL /F /Q __pycache__\*
@REM )
@REM IF EXIST __pycache__ (
@REM RMDIR /Q /S __pycache__
@REM )

@REM ECHO Out

ECHO -
ECHO -
ECHO All done, the end

