#!/bin/sh
set -e
python -m src.pipeline
exec python -m streamlit run src/app.py \
  --server.address=0.0.0.0 \
  --server.port="${PORT:-8501}" \
  --server.headless=true \
  --browser.gatherUsageStats=false
