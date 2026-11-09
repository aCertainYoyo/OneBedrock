@echo off
title OneBedrock Client
echo Starting OneBedrock Client...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo Error launching OneBedrock. Please verify Python is installed.
    pause
)
