@echo off
echo Activation de l'environnement virtuel...
call myenv\Scripts\activate

echo Installation de PyInstaller...
pip install pyinstaller

echo Compilation de l'application...
pyinstaller courSup.spec

echo Compilation terminée!
pause
