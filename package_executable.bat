pyinstaller xeupiu.py --noconfirm --hidden-import=PySide6 --icon="data/resources/icon.ico"
mkdir dist\xeupiu\data
mkdir dist\xeupiu\data\characters
mkdir dist\xeupiu\data\backgrounds
mkdir dist\xeupiu\data\resources
mkdir dist\xeupiu\data\texts
mkdir dist\xeupiu\data\tmp
mkdir dist\xeupiu\data\log
xcopy /s data\characters dist\xeupiu\data\characters
xcopy /s data\backgrounds dist\xeupiu\data\backgrounds
xcopy /s data\resources dist\xeupiu\data\resources
xcopy /s data\texts dist\xeupiu\data\texts
copy config_generic.json dist\xeupiu\config.json
@echo off
cd dist
powershell -NoProfile -ExecutionPolicy Bypass -Command "$substring = (Get-Content -Path '../config.json' | Select-Object -Index 1 | ForEach-Object { $_.Substring(16,12) }); Rename-Item -Path 'xeupiu' -NewName ('xeupiu_' + $substring)"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$substring = (Get-Content -Path '../config.json' | Select-Object -Index 1 | ForEach-Object { $_.Substring(16,12) }); Copy-Item -Path ('xeupiu_' + $substring) -Destination 'C:\Users\Visitante\Downloads' -Recurse"
