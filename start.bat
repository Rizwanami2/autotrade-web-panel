@echo off
title Trading Bot Web Panel
cd /d "%~dp0"
python -m pip install -r requirements.txt --quiet
python main.py
pause
