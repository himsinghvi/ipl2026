"""Utilities for building IPL records from local deliveries CSV."""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List

import pandas as pd

SOURCE_STATUS = "csv"

CACHE_TTL_SECONDS = 24 * 60 * 60

BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "data"
CACHE_DIR.mkdir(exist_ok=True)
CACHE_FILE = CACHE_DIR / "ipl_records_cache.json"
DELIVERIES_PATH_CANDIDATES = [
    BASE_DIR / "deliveries.csv",
    BASE_DIR.parent / "deliveries.csv",
    BASE_DIR.parent / "deliveries.csv" / "deliveries.csv",
]

CATEGORY_KEYWORDS = {
    "year-wise": ["year", "season", "tournament by season", "year wise"],
    "team-wise": ["team", "teams", "partnership", "wins", "franchise"],
    "player-wise": ["player", "players", "individual", "career", "captain"],
    "batting": ["batting", "runs", "batsman", "fours", "sixes", "strike rate", "hundred", "fifty"],
    "bowling": ["bowling", "wicket", "economy", "bowler", "maidens", "five wicket"],
    "keeping": ["wicketkeeper", "wicket-keeper", "keeping", "dismissal", "stumping", "catches"],
}

def _get_category(text: str) -> str:
    normalized = (text or "").lower()
    for category, words in CATEGORY_KEYWORDS.items():
        if any(word in normalized for word in words):
            return category
    return "other"


def _read_deliveries_csv() -> pd.DataFrame:
    for path in DELIVERIES_PATH_CANDIDATES:
        if path.exists() and path.is_file():
            return pd.read_csv(path)
    joined_paths = ", ".join(str(path) for path in DELIVERIES_PATH_CANDIDATES)
    raise FileNotFoundError(f"Could not find deliveries CSV. Checked: {joined_paths}")


def _rows_from_frame(frame: pd.DataFrame) -> List[Dict]:
    if frame.empty:
        return []
    normalized = frame.fillna("").astype(str)
    return normalized.to_dict(orient="records")


def _build_csv_datasets() -> List[Dict]:
    df = _read_deliveries_csv()

    numeric_columns = ["batsman_runs", "extra_runs", "total_runs", "is_wicket", "over", "ball"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    def _make_dataset(dataset_id: str, title: str, category: str, table_df: pd.DataFrame) -> Dict:
        rows = _rows_from_frame(table_df)
        headers = list(table_df.columns)
        return {
            "id": dataset_id,
            "title": title,
            "category": category,
            "page_title": "Deliveries CSV",
            "source_url": "",
            "headers": headers,
            "rows": rows,
            "row_count": len(rows),
        }

    datasets: List[Dict] = []

    matches_per_team = (
        df.groupby("batting_team")["match_id"]
        .nunique()
        .reset_index(name="Matches")
        .rename(columns={"batting_team": "Team"})
        .sort_values(["Matches", "Team"], ascending=[False, True])
        .head(12)
    )
    datasets.append(_make_dataset("csv-1", "Most Matches Played (Batting Team)", "team-wise", matches_per_team))

    team_runs = (
        df.groupby("batting_team")["total_runs"]
        .sum()
        .reset_index(name="Runs")
        .rename(columns={"batting_team": "Team"})
        .sort_values(["Runs", "Team"], ascending=[False, True])
        .head(12)
    )
    datasets.append(_make_dataset("csv-2", "Most Team Runs", "team-wise", team_runs))

    batter_runs = (
        df.groupby("batter")
        .agg(Runs=("batsman_runs", "sum"), Balls=("ball", "count"), Match_Count=("match_id", "nunique"))
        .reset_index()
        .rename(columns={"batter": "Player"})
    )
    batter_runs["Strike_Rate"] = ((batter_runs["Runs"] / batter_runs["Balls"]) * 100).round(2)
    batter_runs = batter_runs.sort_values(["Runs", "Player"], ascending=[False, True]).head(20)
    datasets.append(_make_dataset("csv-3", "Most Runs by Batter", "batting", batter_runs))

    batter_boundaries = (
        df[df["batsman_runs"].isin([4, 6])]
        .groupby(["batter", "batsman_runs"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
        .rename(columns={"batter": "Player", 4: "Fours", 6: "Sixes"})
    )
    if "Fours" not in batter_boundaries.columns:
        batter_boundaries["Fours"] = 0
    if "Sixes" not in batter_boundaries.columns:
        batter_boundaries["Sixes"] = 0
    batter_boundaries["Boundary_Runs"] = batter_boundaries["Fours"] * 4 + batter_boundaries["Sixes"] * 6
    batter_boundaries = batter_boundaries.sort_values(["Boundary_Runs", "Player"], ascending=[False, True]).head(20)
    datasets.append(_make_dataset("csv-4", "Most Boundary Runs by Batter", "player-wise", batter_boundaries))

    bowler_wickets = (
        df[
            (df["is_wicket"] == 1)
            & (~df["dismissal_kind"].fillna("").isin(["run out", "retired hurt", "obstructing the field"]))
        ]
        .groupby("bowler")
        .size()
        .reset_index(name="Wickets")
        .rename(columns={"bowler": "Bowler"})
        .sort_values(["Wickets", "Bowler"], ascending=[False, True])
        .head(20)
    )
    datasets.append(_make_dataset("csv-5", "Most Wickets by Bowler", "bowling", bowler_wickets))

    balls_per_bowler = (
        df[~df["extras_type"].fillna("").str.lower().eq("wides")]
        .groupby("bowler")
        .size()
        .reset_index(name="Legal_Balls")
        .rename(columns={"bowler": "Bowler"})
    )
    runs_per_bowler = (
        df.groupby("bowler")["total_runs"]
        .sum()
        .reset_index(name="Runs_Conceded")
        .rename(columns={"bowler": "Bowler"})
    )
    economy = balls_per_bowler.merge(runs_per_bowler, on="Bowler", how="inner")
    economy["Overs"] = (economy["Legal_Balls"] / 6).round(1)
    economy = economy[economy["Overs"] >= 20]
    economy["Economy"] = (economy["Runs_Conceded"] / (economy["Legal_Balls"] / 6)).round(2)
    economy = economy.sort_values(["Economy", "Bowler"], ascending=[True, True]).head(20)
    datasets.append(_make_dataset("csv-6", "Best Economy (Min 20 Overs)", "bowling", economy))

    fielding = (
        df[(df["is_wicket"] == 1) & (~df["fielder"].fillna("").isin(["", "NA"]))]
        .groupby(["fielder", "dismissal_kind"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
        .rename(columns={"fielder": "Player"})
    )
    dismissal_columns = [c for c in fielding.columns if c != "Player"]
    if dismissal_columns:
        fielding["Dismissals"] = fielding[dismissal_columns].sum(axis=1)
    else:
        fielding["Dismissals"] = 0
    fielding = fielding.sort_values(["Dismissals", "Player"], ascending=[False, True]).head(20)
    datasets.append(_make_dataset("csv-7", "Most Fielding Dismissals", "keeping", fielding))

    matches_overview = (
        df.groupby("match_id")
        .agg(
            Total_Runs=("total_runs", "sum"),
            Wickets=("is_wicket", "sum"),
            Batting_Teams=("batting_team", "nunique"),
            Bowlers_Used=("bowler", "nunique"),
            Batters_Used=("batter", "nunique"),
        )
        .reset_index()
        .rename(columns={"match_id": "Match_ID"})
        .sort_values(["Total_Runs", "Match_ID"], ascending=[False, True])
        .head(20)
    )
    datasets.append(_make_dataset("csv-8", "Highest Aggregate Matches", "year-wise", matches_overview))

    return datasets


def _extract_years(_: List[Dict]) -> List[str]:
    # Deliveries CSV does not contain explicit season/year in this dataset.
    return []


def _extract_teams(datasets: List[Dict]) -> List[str]:
    teams = set()
    possible_team_columns = {"Team", "batting_team", "bowling_team"}
    for dataset in datasets:
        for row in dataset.get("rows", []):
            for key, value in row.items():
                if key in possible_team_columns and value:
                    teams.add(str(value))
    return sorted(teams, key=str.lower)


def _extract_players(datasets: List[Dict]) -> List[str]:
    candidates = Counter()
    invalid_tokens = {"team", "runs", "wickets", "year", "season", "matches", "average", "economy"}
    for dataset in datasets:
        for row in dataset.get("rows", []):
            for value in row.values():
                text = str(value).strip()
                if not text or len(text) < 4 or len(text) > 40:
                    continue
                if any(ch.isdigit() for ch in text):
                    continue
                if "," in text:
                    continue
                lower = text.lower()
                if any(token == lower for token in invalid_tokens):
                    continue
                # Basic player-like heuristic.
                if len(text.split()) in {2, 3} and all(part[:1].isalpha() for part in text.split()):
                    candidates[text] += 1

    team_values = set(_extract_teams(datasets))
    filtered = [name for name, count in candidates.most_common(300) if name not in team_values and count >= 1]
    return sorted(set(filtered))[:120]


def _build_payload(datasets: List[Dict], source_status: str, notices: List[str]) -> Dict:
    for item in datasets:
        if not item.get("category"):
            item["category"] = _get_category(item.get("title", ""))

    category_order = ["year-wise", "team-wise", "player-wise", "batting", "bowling", "keeping", "other"]
    category_counts = {category: 0 for category in category_order}
    total_rows = 0
    for item in datasets:
        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1
        total_rows += int(item.get("row_count", len(item.get("rows", []))))

    payload = {
        "generated_at": int(time.time()),
        "source_status": source_status,
        "notices": notices,
        "summary": {
            "total_tables": len(datasets),
            "total_rows": total_rows,
            "category_counts": category_counts,
        },
        "filters": {
            "years": _extract_years(datasets),
            "teams": _extract_teams(datasets),
            "players": _extract_players(datasets),
            "categories": category_order,
        },
        "datasets": datasets,
    }
    return payload


def get_records_payload(force_refresh: bool = False) -> Dict:
    if CACHE_FILE.exists() and not force_refresh:
        try:
            cached = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            generated = int(cached.get("generated_at", 0))
            if (time.time() - generated) < CACHE_TTL_SECONDS:
                return cached
        except (ValueError, OSError):
            pass

    notices = []
    try:
        datasets = _build_csv_datasets()
        payload = _build_payload(
            datasets=datasets,
            source_status=SOURCE_STATUS,
            notices=notices,
        )
        payload["notices"].append("Records are generated from local file: deliveries.csv")
    except Exception as exc:  # pragma: no cover - defensive fallback
        payload = _build_payload(
            datasets=[],
            source_status="error",
            notices=[f"Failed to build records from deliveries.csv: {exc}"],
        )

    try:
        CACHE_FILE.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")
    except OSError:
        pass

    return payload
