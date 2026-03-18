"""AI/ML prediction engine for IPL match outcomes and player performance."""
import numpy as np
from models import db, Team, Player, Match, HeadToHead, Scorecard


def get_team_strength(team):
    """Calculate overall team strength score (0-100)."""
    players = Player.query.filter_by(team_id=team.id).all()
    if not players:
        return 50.0

    batting_strength = 0
    bowling_strength = 0
    bat_count = 0
    bowl_count = 0

    for p in players:
        if p.role in ('Batsman', 'Wicket-Keeper', 'All-Rounder'):
            score = (
                (p.batting_avg / 50) * 25 +
                (p.strike_rate / 180) * 25 +
                (p.form_rating / 100) * 30 +
                (min(p.matches_played, 150) / 150) * 20
            )
            batting_strength += score
            bat_count += 1

        if p.role in ('Bowler', 'All-Rounder') and p.wickets_taken > 0:
            eco_score = max(0, (10 - p.economy_rate) / 4) * 25
            avg_score = max(0, (35 - p.bowling_avg) / 35) * 25 if p.bowling_avg > 0 else 12
            score = (
                eco_score +
                avg_score +
                (p.form_rating / 100) * 30 +
                (min(p.matches_played, 150) / 150) * 20
            )
            bowling_strength += score
            bowl_count += 1

    avg_bat = batting_strength / max(1, bat_count)
    avg_bowl = bowling_strength / max(1, bowl_count)
    return min(100, (avg_bat * 0.5 + avg_bowl * 0.5))


def get_head_to_head(team1_id, team2_id):
    """Get head-to-head record between two teams."""
    h2h = HeadToHead.query.filter(
        ((HeadToHead.team1_id == team1_id) & (HeadToHead.team2_id == team2_id)) |
        ((HeadToHead.team1_id == team2_id) & (HeadToHead.team2_id == team1_id))
    ).first()

    if not h2h:
        return {"total": 0, "team1_wins": 0, "team2_wins": 0, "team1_pct": 50}

    if h2h.team1_id == team1_id:
        return {
            "total": h2h.total_matches,
            "team1_wins": h2h.team1_wins,
            "team2_wins": h2h.team2_wins,
            "team1_pct": round(h2h.team1_wins / max(1, h2h.total_matches) * 100, 1)
        }
    else:
        return {
            "total": h2h.total_matches,
            "team1_wins": h2h.team2_wins,
            "team2_wins": h2h.team1_wins,
            "team1_pct": round(h2h.team2_wins / max(1, h2h.total_matches) * 100, 1)
        }


def get_recent_form(team_id, limit=5):
    """Get recent match results for a team."""
    recent_matches = Match.query.filter(
        Match.status == 'completed',
        ((Match.team1_id == team_id) | (Match.team2_id == team_id))
    ).order_by(Match.date.desc()).limit(limit).all()

    wins = sum(1 for m in recent_matches if m.winner_id == team_id)
    total = len(recent_matches)
    return {
        "matches": total,
        "wins": wins,
        "losses": total - wins,
        "form_pct": round(wins / max(1, total) * 100, 1),
        "form_str": ''.join(['W' if m.winner_id == team_id else 'L' for m in recent_matches])
    }


def predict_win_probability(team1, team2):
    """Predict win probability using weighted factors."""
    strength1 = get_team_strength(team1)
    strength2 = get_team_strength(team2)
    h2h = get_head_to_head(team1.id, team2.id)
    form1 = get_recent_form(team1.id)
    form2 = get_recent_form(team2.id)

    # Weighted scoring
    weights = {
        'strength': 0.35,
        'h2h': 0.20,
        'form': 0.25,
        'historical': 0.20,
    }

    strength_score = strength1 / (strength1 + strength2) * 100
    h2h_score = h2h['team1_pct']
    form_score = form1['form_pct'] / max(1, form1['form_pct'] + form2['form_pct']) * 100 if (form1['form_pct'] + form2['form_pct']) > 0 else 50
    hist_score = team1.win_pct_hist / max(1, team1.win_pct_hist + team2.win_pct_hist) * 100 if (team1.win_pct_hist + team2.win_pct_hist) > 0 else 50

    team1_pct = (
        weights['strength'] * strength_score +
        weights['h2h'] * h2h_score +
        weights['form'] * form_score +
        weights['historical'] * hist_score
    )

    team1_pct = max(15, min(85, team1_pct))
    team2_pct = 100 - team1_pct

    return {
        "team1_pct": round(team1_pct, 1),
        "team2_pct": round(team2_pct, 1),
        "factors": {
            "team_strength": {"team1": round(strength1, 1), "team2": round(strength2, 1)},
            "head_to_head": h2h,
            "recent_form": {"team1": form1, "team2": form2},
            "historical_win_pct": {"team1": team1.win_pct_hist, "team2": team2.win_pct_hist},
        }
    }


def predict_top_batsmen(team1_id, team2_id, top_n=5):
    """Predict top batsmen for the match."""
    players = Player.query.filter(
        Player.team_id.in_([team1_id, team2_id]),
        Player.role.in_(['Batsman', 'Wicket-Keeper', 'All-Rounder'])
    ).all()

    scored = []
    for p in players:
        score = (
            (p.batting_avg / 50) * 25 +
            (p.strike_rate / 180) * 25 +
            (p.form_rating / 100) * 35 +
            (min(p.runs_scored, 5000) / 5000) * 15
        )
        expected_runs = int(p.batting_avg * (p.form_rating / 75) * np.random.uniform(0.7, 1.1))
        expected_sr = round(p.strike_rate * np.random.uniform(0.85, 1.15), 1)
        scored.append({
            "player": p,
            "score": round(score, 1),
            "expected_runs": min(expected_runs, 120),
            "expected_sr": expected_sr,
            "confidence": min(95, round(score + np.random.uniform(-5, 5), 1)),
        })

    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:top_n]


def predict_top_bowlers(team1_id, team2_id, top_n=5):
    """Predict top bowlers for the match."""
    players = Player.query.filter(
        Player.team_id.in_([team1_id, team2_id]),
        Player.role.in_(['Bowler', 'All-Rounder']),
        Player.wickets_taken > 0
    ).all()

    scored = []
    for p in players:
        eco_score = max(0, (10 - p.economy_rate) / 4) * 25
        avg_score = max(0, (35 - p.bowling_avg) / 35) * 25 if p.bowling_avg > 0 else 12
        score = (
            eco_score +
            avg_score +
            (p.form_rating / 100) * 35 +
            (min(p.wickets_taken, 150) / 150) * 15
        )
        expected_wickets = max(0, round(np.random.uniform(0.5, 3.5) * (p.form_rating / 75), 0))
        expected_eco = round(p.economy_rate * np.random.uniform(0.8, 1.2), 2)
        scored.append({
            "player": p,
            "score": round(score, 1),
            "expected_wickets": int(min(expected_wickets, 5)),
            "expected_economy": expected_eco,
            "confidence": min(95, round(score + np.random.uniform(-5, 5), 1)),
        })

    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:top_n]


def get_player_analysis(player):
    """Get detailed analysis of a player."""
    analysis = {
        "player": player,
        "batting_rating": 0,
        "bowling_rating": 0,
        "overall_rating": 0,
        "strengths": [],
        "weaknesses": [],
    }

    # Batting analysis
    if player.runs_scored > 0:
        bat_score = (
            min(100, (player.batting_avg / 45) * 30 +
            (player.strike_rate / 170) * 30 +
            (player.form_rating / 100) * 40)
        )
        analysis["batting_rating"] = round(bat_score, 1)

        if player.strike_rate > 145:
            analysis["strengths"].append("Explosive batting with high strike rate")
        if player.batting_avg > 35:
            analysis["strengths"].append("Consistent run scorer with excellent average")
        if player.sixes > 50:
            analysis["strengths"].append("Power hitter - clears boundaries regularly")
        if player.fifties > 10:
            analysis["strengths"].append("Big match temperament - multiple half centuries")
        if player.strike_rate < 120 and player.role == 'Batsman':
            analysis["weaknesses"].append("Below par strike rate for T20")
        if player.batting_avg < 22 and player.role in ('Batsman', 'Wicket-Keeper'):
            analysis["weaknesses"].append("Inconsistent with the bat")

    # Bowling analysis
    if player.wickets_taken > 0:
        eco_pct = max(0, min(100, (10 - player.economy_rate) / 4 * 100))
        avg_pct = max(0, min(100, (35 - player.bowling_avg) / 35 * 100)) if player.bowling_avg > 0 else 50
        bowl_score = (eco_pct * 0.3 + avg_pct * 0.3 + player.form_rating * 0.4)
        analysis["bowling_rating"] = round(bowl_score, 1)

        if player.economy_rate < 7.0:
            analysis["strengths"].append("Economical bowler - restricts run flow")
        if player.bowling_avg < 24:
            analysis["strengths"].append("Excellent wicket-taking ability")
        if player.economy_rate > 8.5:
            analysis["weaknesses"].append("Expensive bowling - leaks runs")
        if player.bowling_avg > 35:
            analysis["weaknesses"].append("Struggles to pick up wickets regularly")

    if player.form_rating > 75:
        analysis["strengths"].append("In outstanding current form")
    elif player.form_rating < 55:
        analysis["weaknesses"].append("Currently in poor form")

    if not analysis["weaknesses"]:
        analysis["weaknesses"].append("No significant weaknesses identified")

    # Overall rating
    if analysis["batting_rating"] > 0 and analysis["bowling_rating"] > 0:
        analysis["overall_rating"] = round((analysis["batting_rating"] * 0.5 + analysis["bowling_rating"] * 0.5), 1)
    elif analysis["batting_rating"] > 0:
        analysis["overall_rating"] = analysis["batting_rating"]
    else:
        analysis["overall_rating"] = analysis["bowling_rating"]

    return analysis


def get_match_analysis(match):
    """Get detailed analysis of a completed match."""
    scorecards = Scorecard.query.filter_by(match_id=match.id).all()

    batting_cards_t1 = [s for s in scorecards if s.did_bat and s.team_id == match.team1_id]
    batting_cards_t2 = [s for s in scorecards if s.did_bat and s.team_id == match.team2_id]
    bowling_cards_t1 = [s for s in scorecards if s.did_bowl and s.team_id == match.team1_id]
    bowling_cards_t2 = [s for s in scorecards if s.did_bowl and s.team_id == match.team2_id]

    # Top scorer and best bowler
    all_batting = batting_cards_t1 + batting_cards_t2
    all_bowling = bowling_cards_t1 + bowling_cards_t2

    top_scorer = max(all_batting, key=lambda x: x.runs) if all_batting else None
    best_bowler = max(all_bowling, key=lambda x: (x.wickets, -x.runs_given)) if all_bowling else None

    # Run rate per over estimation
    t1_score_parts = match.team1_score.split('/') if match.team1_score else ['0', '0']
    t2_score_parts = match.team2_score.split('/') if match.team2_score else ['0', '0']
    t1_total = int(t1_score_parts[0])
    t2_total = int(t2_score_parts[0])

    # Phase-wise scoring simulation
    t1_pp = int(t1_total * np.random.uniform(0.25, 0.40))
    t1_middle = int(t1_total * np.random.uniform(0.30, 0.40))
    t1_death = t1_total - t1_pp - t1_middle

    t2_pp = int(t2_total * np.random.uniform(0.25, 0.40))
    t2_middle = int(t2_total * np.random.uniform(0.30, 0.40))
    t2_death = t2_total - t2_pp - t2_middle

    return {
        "batting_t1": sorted(batting_cards_t1, key=lambda x: x.runs, reverse=True),
        "batting_t2": sorted(batting_cards_t2, key=lambda x: x.runs, reverse=True),
        "bowling_t1": sorted(bowling_cards_t1, key=lambda x: x.wickets, reverse=True),
        "bowling_t2": sorted(bowling_cards_t2, key=lambda x: x.wickets, reverse=True),
        "top_scorer": top_scorer,
        "best_bowler": best_bowler,
        "phases": {
            "team1": {"powerplay": t1_pp, "middle": t1_middle, "death": t1_death},
            "team2": {"powerplay": t2_pp, "middle": t2_middle, "death": t2_death},
        },
        "total_fours_t1": sum(s.fours for s in batting_cards_t1),
        "total_sixes_t1": sum(s.sixes for s in batting_cards_t1),
        "total_fours_t2": sum(s.fours for s in batting_cards_t2),
        "total_sixes_t2": sum(s.sixes for s in batting_cards_t2),
    }
