@echo off
python -m venv venv1
call venv1\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
