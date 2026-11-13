# Deployment Guide — Smart CRM CSAT pipeline and dashboard (flow L8, track DA), tag v1.0

Two services run from one image: **pipeline** (loads the CSV files into a SQLite warehouse once, then exits) and **dashboard** (Streamlit, port 8501). You need only Docker and Git.

## 1. Requirements

- Docker Engine 24+ with Docker Compose v2 (check: `docker compose version`). Windows/macOS: Docker Desktop.
- Git 2.30+ and an internet connection for the first build (downloads `python:3.11-slim` and the pinned Python packages).
- About 2 GB free disk and a free port **8501** (change it with `APP_PORT`, see section 3).
- No Python, no database server and no account are needed. The project uses no secrets.

## 2. Setup steps

1. `git clone --branch v1.0 https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sat-hai-long.git && cd smartcrm-237480201IS02-khao-sat-hai-long`
2. `cp .env.example .env` (Windows PowerShell: `copy .env.example .env`)
3. `docker compose up -d --build` (first build takes about 2–4 minutes; the pipeline then runs for about 5 seconds)

Steps 2 and 3 are the only commands needed to start the system. To stop it: `docker compose down` (keeps the data) or `docker compose down -v` (also deletes the data volume).

## 3. Environment variables

| Name | Meaning | Sample value | Required |
|---|---|---|---|
| `APP_PORT` | Host port of the dashboard (bound to 127.0.0.1 only) | `8501` | no (default 8501) |
| `CSAT_CONFIG` | Pipeline config file for runs *without* Docker; Docker overrides it with `src/config.docker.yaml` | `src/config.yaml` | no |

There are no passwords, tokens or API keys. `.env` is ignored by Git and Docker; only `.env.example` is committed.

## 4. Sample data

The two source files are committed in `data/raw/` and baked into the image — nothing to download. The pipeline service loads them automatically on every `up`:

- `tickets_history.csv`: 7,800 tickets (6,350 closed `DA_DONG` + 1,450 open); `survey_responses.csv`: 2,600 responses.
- Expected result in the warehouse: `fact_survey` = **6,350** rows (2,600 with a response), 0 rejected rows, `dim_center` = 7 (6 centres + "Unknown"), `dim_technician` = 39 (38 + "Unknown").
- To count rows yourself: `docker compose run --rm pipeline python -c "import sqlite3; print(sqlite3.connect('/var/lib/csat/csat.db').execute('select count(*) from fact_survey').fetchone()[0])"` → `6350`.
- There is no login: the dashboard is open to anyone who can reach `http://localhost:8501`.

## 5. Verify it works

| # | Command / action | Expected result |
|---|---|---|
| 1 | `docker compose ps -a` (wait up to 30 s after `up`) | `dashboard` is **healthy**; `pipeline` is `Exited (0)` |
| 2 | `docker compose logs pipeline` | contains `fact_survey = 6350 dòng` and `stg_ticket 7800 = fact 6350 + loại 0 + chưa đóng 1450  -> ĐẠT` |
| 3 | `curl -s http://localhost:8501/_stcore/health` (Windows: `curl.exe`) | `ok` |
| 4 | Open http://localhost:8501 | 4 metric cards and 2 charts. Default filter "12 tháng gần nhất": 3.90 · 68.9% · 1.220 responses · 41.7%. Choose "Toàn kỳ": 3.92 · 70.0% · 2.600 · 40.9% |
| 5 | `docker compose run --rm pipeline python -m pytest -q src` | `19 passed` |
| 6 | `docker compose run --rm pipeline` (second run) | `fact_survey = 6350 dòng` again — no duplicated rows |

Tested with: Docker 28.1.1 (Docker Desktop, Windows) — white-machine test on 13/11/2026: fresh clone of `main` (commit `ea00824`) into an empty folder, then `cp .env.example .env` and `docker compose up -d --build`; all six checks above passed.

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| `port is already allocated` | Set `APP_PORT=8502` in `.env`, run `docker compose up -d` again, open port 8502 |
| Dashboard shows "Không tải được dữ liệu" | The pipeline did not finish: `docker compose logs pipeline`, fix the cause, then `docker compose up -d` |
| Old data or partial run | `docker compose down -v` then `docker compose up -d --build` |
| Build cannot download packages | Check the internet/proxy setting of Docker, then rerun step 3 |
| No Docker available | Fallback without Docker: Python 3.11+, see README section 3 (venv, `pip install -r requirements.txt`, `python -m src.pipeline`, `python -m streamlit run src/app.py`) |

## 7. Optional: public deployment (Render)

The same Dockerfile is deployed as a Render Web Service (Free plan, Docker runtime).

1. Create a Render account and connect the GitHub repository.
2. New → Web Service → select the repository, branch `main`, runtime Docker, region Singapore, instance type Free.
3. Docker Command: `sh -c "python -m src.pipeline && python -m streamlit run src/app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false"`
4. Environment variable: `CSAT_CONFIG=src/config.docker.yaml`. No secrets are used.
5. Health check path: `/_stcore/health`.
6. Open the Render URL and verify the 4 metric cards and 2 charts (same values as section 5, check 4).

Notes: the Free plan sleeps after about 15 minutes without traffic, so the first request after sleep can take about a minute. The data is rebuilt from the CSV files on every start. The dashboard has no login, so anyone with the URL can view it (the data is pseudonymised).

Live URL: <<ĐIỀN: link Render, ví dụ https://smartcrm-csat.onrender.com>>
