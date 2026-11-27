#!/bin/bash
echo "Starting NEUROTRADE..."
cd "$(dirname "$0")"
pip install -r requirements.txt --quiet || pip3 install -r requirements.txt --quiet
python3 main.py || python main.py
