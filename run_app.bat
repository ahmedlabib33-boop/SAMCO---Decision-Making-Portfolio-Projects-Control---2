@echo off
echo Starting SAMCO – Project Intelligence Hub on port 1978...
python -m streamlit run app.py --server.port 1978 --server.address 0.0.0.0
pause