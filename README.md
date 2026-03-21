# IPL 2026 Predictor, Records, and Fantasy Dashboard

Flask web application for IPL 2026 analytics, fixture insights, match prediction, records exploration, and fantasy gameplay.

---

## What This App Includes

- Dashboard with points table, upcoming fixtures, and recent results
- Match pages with:
  - win probability prediction for upcoming matches
  - projected top batsmen and bowlers
  - completed match analysis (top scorer, best bowler, phase splits)
- Team pages with squad and form summaries
- Player pages with batting/bowling/overall analysis
- Records Hub powered by local `deliveries.csv` (no Cricinfo dependency)
- Fantasy League:
  - signup/login (email/mobile + password)
  - create exactly one 11-player team per match
  - captain and vice-captain multipliers
  - leaderboard and user profile
- User prediction saving with confidence percentage
- API endpoint for match prediction JSON

---

## Tech Stack

- Python 3.11+
- Flask
- Flask-SQLAlchemy
- SQLite
- NumPy, Pandas, scikit-learn
- Gunicorn (for production deployment)

---

## Project Structure

Primary code lives in the `cursor/` folder:

- `cursor/app.py` - routes, auth flow, startup bootstrapping
- `cursor/models.py` - SQLAlchemy models
- `cursor/predictor.py` - match and player prediction logic
- `cursor/seed_data.py` - teams/players/schedule seed + fantasy point calculation
- `cursor/records_service.py` - records builder from `deliveries.csv`
- `cursor/templates/` - Jinja templates
- `cursor/static/` - CSS and client assets
- `cursor/requirements.txt` - dependencies
- `cursor/render.yaml` - Render deployment config

---

## Local Setup

### 1) Create and activate virtualenv

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
cd cursor
pip install -r requirements.txt
```

### 3) Run application

```bash
python app.py
```

Open: `http://localhost:5000`

---

## Data and Bootstrapping

On startup, the app automatically:

1. Creates DB schema (`sqlite:///ipl2026.db`)
2. Applies best-effort fantasy auth schema upgrades
3. Seeds:
   - teams
   - players
   - head-to-head history
   - IPL 2026 schedule
   - simulated completed match scorecards
4. Seeds fantasy bot users and teams for completed matches

No separate migration or seeding command is required.

---

## Records Hub (CSV-Based)

The Records page now uses local `deliveries.csv` instead of Cricinfo crawling.

### Expected CSV location

The service checks these paths (first match wins):

- `cursor/deliveries.csv`
- `deliveries.csv` (repo root)
- `deliveries.csv/deliveries.csv` (folder containing the file)

### What records are generated

Current generated datasets include:

- Most Matches Played (batting team)
- Most Team Runs
- Most Runs by Batter
- Most Boundary Runs by Batter
- Most Wickets by Bowler
- Best Economy (minimum 20 overs)
- Most Fielding Dismissals
- Highest Aggregate Matches

All records are cached in `cursor/data/ipl_records_cache.json` with TTL refresh logic.

---

## Prediction System (How It Works)

Prediction logic is in `cursor/predictor.py`.

### 1) Team strength model

For each team, strength is computed from player stats.

- Batting contributors: roles `Batsman`, `Wicket-Keeper`, `All-Rounder`
- Bowling contributors: roles `Bowler`, `All-Rounder` with wickets > 0

Batting score per player:

- `(batting_avg / 50) * 25`
- `(strike_rate / 180) * 25`
- `(form_rating / 100) * 30`
- `(min(matches_played, 150) / 150) * 20`

Bowling score per player:

- `eco_score = max(0, (10 - economy_rate) / 4) * 25`
- `avg_score = max(0, (35 - bowling_avg) / 35) * 25` (or 12 when bowling_avg == 0)
- `+ (form_rating / 100) * 30`
- `+ (min(matches_played, 150) / 150) * 20`

Final team strength:

- `0.5 * average_batting_score + 0.5 * average_bowling_score`
- capped to max 100

### 2) Match win probability model

For upcoming matches, weighted factors:

- Team strength: `35%`
- Head-to-head: `20%`
- Recent form: `25%`
- Historical win%: `20%`

Formula:

- `team1_pct = 0.35*strength_score + 0.20*h2h_score + 0.25*form_score + 0.20*hist_score`
- Output clamp: `15 <= team1_pct <= 85`
- `team2_pct = 100 - team1_pct`

### Prediction Example

Assume:

- `strength_score = 58`
- `h2h_score = 62`
- `form_score = 55`
- `hist_score = 48`

Then:

- `team1_pct = 0.35*58 + 0.20*62 + 0.25*55 + 0.20*48`
- `team1_pct = 20.3 + 12.4 + 13.75 + 9.6 = 56.05`
- Final: `56.1% vs 43.9%`

If computed value is above 85 or below 15, clamp is applied.

### Top performer projections

`predict_top_batsmen()` and `predict_top_bowlers()` rank players using weighted stat formulas and add bounded random variation for expected runs/wickets and confidence.

---

## Fantasy League Rules

Fantasy flow and validation are in `cursor/app.py`, point calculation in `cursor/seed_data.py`.

### Team creation constraints

For each match:

- Exactly 11 players must be selected
- Captain and vice-captain are mandatory and must be different
- Maximum 7 players from one real team
- One fantasy team per user per match (new save replaces previous team)

### Authentication rules

- Signup requires:
  - username (3-30 chars, letters/numbers/underscore)
  - password (minimum 8 chars)
  - at least one of email or mobile
- Login supports email, mobile, or username identifier

### Prediction save rules

When saving winner prediction:

- user must be logged in
- match must be upcoming
- predicted team must be one of the two teams in that match
- confidence is clamped to `[0, 100]`

---

## Fantasy Points Calculation

`calc_fantasy_points(scorecards, is_captain, is_vice_captain)` uses these rules:

### Batting

- `+1` per run
- `+1` per four
- `+2` per six
- Milestones:
  - `+4` for 25+
  - `+8` for 50+
  - `+16` for 100+
- Duck penalty: `-2` if out for 0
- Strike-rate adjustment (if balls >= 10):
  - `+6` for SR >= 170
  - `+4` for SR >= 150
  - `-2` for SR < 80
  - `-4` for SR < 60

### Bowling

- `+25` per wicket
- Wicket haul bonus:
  - `+8` for 3 wickets
  - `+12` for 4 wickets
  - `+16` for 5 wickets
- `+12` per maiden over
- Economy adjustment (if overs_bowled >= 2):
  - `+6` if economy < 5
  - `+4` if economy < 6
  - `-2` if economy > 10
  - `-4` if economy > 11

### Fielding

- `+8` per catch
- `+12` per run-out

### Multipliers

- Captain: total points `x2`
- Vice-captain: total points `x1.5` (integer conversion in code)

### Fantasy Example 1 (Captain)

Player match stats:

- Batting: 64 (45), 6 fours, 2 sixes
- Bowling: 4 overs, 28 runs, 2 wickets, 1 maiden
- Fielding: 1 catch
- Role: Captain

Points:

- Batting base: `64 + 6 + (2*2) = 74`
- Batting milestone: `+8` (50+)
- Strike rate: `64/45*100 = 142.2` => no SR bonus/penalty
- Bowling: `2*25 = 50`
- Maiden: `+12`
- Economy: `28/4 = 7.0` => no eco bonus/penalty
- Fielding: `+8`
- Subtotal: `74 + 8 + 50 + 12 + 8 = 152`
- Captain multiplier: `152 * 2 = 304`

Final = **304 points**

### Fantasy Example 2 (Vice-Captain)

Player match stats:

- Batting: 18 (12), 2 fours, 1 six
- Bowling: 3 overs, 13 runs, 3 wickets, 0 maiden
- Fielding: 0
- Role: Vice-captain

Points:

- Batting: `18 + 2 + 2 = 22` (no milestone)
- Strike rate: `18/12*100 = 150` => `+4`
- Bowling wickets: `3*25 = 75`
- 3W bonus: `+8`
- Economy: `13/3 = 4.33` => `+6`
- Subtotal: `22 + 4 + 75 + 8 + 6 = 115`
- Vice-captain: `int(115 * 1.5) = 172`

Final = **172 points**

---

## Main Routes

- `/` - dashboard
- `/schedule` - fixtures with filters
- `/match/<match_id>` - upcoming prediction or completed analysis
- `/team/<team_id>` - team profile
- `/player/<player_id>` - player profile
- `/predictions` - prediction center
- `/predictions/save` - save/update user prediction
- `/api/predict/<match_id>` - prediction JSON
- `/records` - CSV-powered records hub
- `/fantasy` - fantasy home/leaderboard
- `/fantasy/match/<match_id>` - build/view fantasy teams
- `/fantasy/user/<user_id>` - user fantasy profile
- `/auth/signup` - signup endpoint
- `/auth/login` - login endpoint
- `/fantasy/logout` - logout

---

## API Example

`GET /api/predict/<match_id>`

Returns:

```json
{
  "team1_pct": 56.1,
  "team2_pct": 43.9,
  "factors": {
    "team_strength": {"team1": 71.4, "team2": 66.8},
    "head_to_head": {"total": 26, "team1_wins": 15, "team2_wins": 11, "team1_pct": 57.7},
    "recent_form": {"team1": {"matches": 5, "wins": 3, "losses": 2, "form_pct": 60.0, "form_str": "WLWWL"}, "team2": {"matches": 5, "wins": 2, "losses": 3, "form_pct": 40.0, "form_str": "LLWWL"}},
    "historical_win_pct": {"team1": 54.2, "team2": 49.6}
  }
}
```

---

## Deployment (Render)

`cursor/render.yaml` is configured for deployment:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
- Python version: `3.11.0`

Set Render root directory to `cursor/` so it can locate `app.py`.

---

## Important Notes

- This project is simulation-oriented with seeded historical-like data plus generated scorecards.
- Prediction outputs are heuristic/weighted analytics, not betting advice.
- `SECRET_KEY` is hardcoded for local development convenience; use env-based secret management in production.
