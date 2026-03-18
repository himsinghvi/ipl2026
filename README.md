# IPL 2026 Predictor and Fantasy Dashboard

Flask web application for IPL 2026 analytics, match predictions, team/player insights, and a fantasy league experience.

## Features

- Match schedule, points table, and recent/completed match views
- AI-style win probability predictions for upcoming matches
- Predicted top batsmen and bowlers for each upcoming fixture
- Team pages with squad stats, form, and match history
- Player profile pages with batting/bowling analysis
- Fantasy league flow:
  - join/login with username
  - create one team per match (11 players)
  - captain and vice-captain multipliers
  - leaderboard and user profile pages
- JSON prediction API endpoint for match-level probabilities

## Tech Stack

- Python 3.11+
- Flask
- Flask-SQLAlchemy
- SQLite (local database file)
- NumPy, Pandas, scikit-learn (prediction/data support)
- Gunicorn (production serving)

## Project Structure

Main application code is in the `ipl2026/` directory:

- `ipl2026/app.py` - Flask app, routes, template filters, startup logic
- `ipl2026/models.py` - SQLAlchemy models
- `ipl2026/predictor.py` - prediction and analysis utilities
- `ipl2026/seed_data.py` - database seeding and fantasy scoring logic
- `ipl2026/templates/` - Jinja templates
- `ipl2026/static/` - CSS assets
- `ipl2026/requirements.txt` - Python dependencies
- `ipl2026/render.yaml` - Render deployment configuration

## Quick Start (Local)

### 1) Create and activate a virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
cd ipl2026
pip install -r requirements.txt
```

### 3) Run the app

```bash
python app.py
```

The app starts on `http://localhost:5000` by default.

## Database and Seed Data

- The app uses `sqlite:///ipl2026.db`.
- On startup, it automatically:
  - creates tables (if missing)
  - seeds teams, players, matches, scorecards, and fantasy seed data
- No separate migration or seed command is required for first run.

## Key Routes

- `/` - Home dashboard
- `/schedule` - Full schedule with filters
- `/match/<match_id>` - Match details (upcoming or completed analysis)
- `/team/<team_id>` - Team details
- `/player/<player_id>` - Player details
- `/predictions` - Upcoming match predictions
- `/api/predict/<match_id>` - Prediction JSON API
- `/fantasy` - Fantasy home and leaderboard
- `/fantasy/match/<match_id>` - Fantasy match page
- `/fantasy/user/<user_id>` - Fantasy user profile

## Render Deployment

Deployment config exists in `ipl2026/render.yaml`:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
- Python version: `3.11.0`

When deploying from repo root, ensure Render service root directory points to `ipl2026/` (so it can find `app.py` and `requirements.txt`).

## Notes

- `SECRET_KEY` is currently hardcoded in `ipl2026/app.py` for local convenience. For production, set a secure value via environment variable.
- This project is simulation-oriented and uses seeded IPL-style data for analytics/predictions.
