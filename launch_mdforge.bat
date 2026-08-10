@echo off
setlocal
rem Lanceur MDForge (coquille) : orchestre les outils de compilation documentaire.
rem Aujourd'hui, MDForge delegue a MDDOCX via son propre lanceur.
call "%~dp0Mddocx\launch_mddocx.bat"
endlocal
