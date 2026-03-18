"""IPL 2026 - AI/ML Prediction, Analytics & Dashboarding Web App."""
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from models import (db, Team, Player, Match, Scorecard, HeadToHead,
                    FantasyUser, FantasyTeam, FantasyTeamPlayer)
from seed_data import seed_database, calc_fantasy_points, seed_fantasy
from predictor import (
    predict_win_probability,
    predict_top_batsmen,
    predict_top_bowlers,
    get_player_analysis,
    get_match_analysis,
    get_recent_form,
)
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ipl2026.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ipl2026-secret-key'

db.init_app(app)

with app.app_context():
    db.create_all()
    seed_database(app)
    seed_fantasy(app)


@app.route('/')
def index():
    teams = Team.query.all()
    upcoming = Match.query.filter_by(status='upcoming').order_by(Match.date).limit(5).all()
    completed = Match.query.filter_by(status='completed').order_by(Match.date.desc()).limit(5).all()
    total_matches = Match.query.count()
    completed_count = Match.query.filter_by(status='completed').count()
    upcoming_count = Match.query.filter_by(status='upcoming').count()

    # Points table calculation
    points_table = []
    for team in teams:
        played = Match.query.filter(
            Match.status == 'completed',
            ((Match.team1_id == team.id) | (Match.team2_id == team.id))
        ).count()
        won = Match.query.filter(Match.status == 'completed', Match.winner_id == team.id).count()
        lost = played - won
        points = won * 2
        nrr = round((won - lost) * 0.25 + (team.matches_won_hist / max(1, team.matches_played_hist) - 0.5) * 0.5, 3)
        points_table.append({
            'team': team,
            'played': played,
            'won': won,
            'lost': lost,
            'points': points,
            'nrr': nrr,
        })
    points_table.sort(key=lambda x: (-x['points'], -x['nrr']))

    # Top performers
    top_batsmen = Player.query.order_by(Player.runs_scored.desc()).limit(5).all()
    top_bowlers = Player.query.filter(Player.wickets_taken > 0).order_by(Player.wickets_taken.desc()).limit(5).all()

    return render_template('index.html',
                           teams=teams,
                           upcoming=upcoming,
                           completed=completed,
                           points_table=points_table,
                           total_matches=total_matches,
                           completed_count=completed_count,
                           upcoming_count=upcoming_count,
                           top_batsmen=top_batsmen,
                           top_bowlers=top_bowlers)


@app.route('/schedule')
def schedule():
    stage_filter = request.args.get('stage', 'all')
    status_filter = request.args.get('status', 'all')
    team_filter = request.args.get('team', 'all')

    query = Match.query
    if stage_filter != 'all':
        query = query.filter_by(stage=stage_filter)
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    if team_filter != 'all':
        team_id = int(team_filter)
        query = query.filter((Match.team1_id == team_id) | (Match.team2_id == team_id))

    matches = query.order_by(Match.date).all()
    teams = Team.query.all()
    return render_template('schedule.html', matches=matches, teams=teams,
                           stage_filter=stage_filter, status_filter=status_filter,
                           team_filter=team_filter)


@app.route('/match/<int:match_id>')
def match_detail(match_id):
    match = Match.query.get_or_404(match_id)
    team1 = db.session.get(Team, match.team1_id)
    team2 = db.session.get(Team, match.team2_id)

    if match.status == 'upcoming':
        prediction = predict_win_probability(team1, team2)
        top_batsmen = predict_top_batsmen(team1.id, team2.id)
        top_bowlers = predict_top_bowlers(team1.id, team2.id)
        team1_players = Player.query.filter_by(team_id=team1.id).all()
        team2_players = Player.query.filter_by(team_id=team2.id).all()
        team1_form = get_recent_form(team1.id)
        team2_form = get_recent_form(team2.id)

        return render_template('match_upcoming.html',
                               match=match, team1=team1, team2=team2,
                               prediction=prediction,
                               top_batsmen=top_batsmen,
                               top_bowlers=top_bowlers,
                               team1_players=team1_players,
                               team2_players=team2_players,
                               team1_form=team1_form,
                               team2_form=team2_form)
    else:
        analysis = get_match_analysis(match)
        return render_template('match_completed.html',
                               match=match, team1=team1, team2=team2,
                               analysis=analysis)


@app.route('/team/<int:team_id>')
def team_detail(team_id):
    team = Team.query.get_or_404(team_id)
    players = Player.query.filter_by(team_id=team_id).all()
    matches = Match.query.filter(
        (Match.team1_id == team_id) | (Match.team2_id == team_id)
    ).order_by(Match.date).all()

    completed_matches = [m for m in matches if m.status == 'completed']
    upcoming_matches = [m for m in matches if m.status == 'upcoming']

    wins = sum(1 for m in completed_matches if m.winner_id == team_id)
    losses = len(completed_matches) - wins

    form = get_recent_form(team_id)

    batsmen = sorted([p for p in players if p.role in ('Batsman', 'Wicket-Keeper', 'All-Rounder')],
                     key=lambda x: x.runs_scored, reverse=True)
    bowlers = sorted([p for p in players if p.wickets_taken > 0],
                     key=lambda x: x.wickets_taken, reverse=True)

    return render_template('team.html',
                           team=team, players=players,
                           completed_matches=completed_matches,
                           upcoming_matches=upcoming_matches,
                           wins=wins, losses=losses, form=form,
                           batsmen=batsmen, bowlers=bowlers)


@app.route('/player/<int:player_id>')
def player_detail(player_id):
    player = Player.query.get_or_404(player_id)
    team = db.session.get(Team, player.team_id)
    analysis = get_player_analysis(player)

    scorecards = Scorecard.query.filter_by(player_id=player_id).all()
    batting_scores = [s for s in scorecards if s.did_bat]
    bowling_figures = [s for s in scorecards if s.did_bowl]

    return render_template('player.html',
                           player=player, team=team, analysis=analysis,
                           batting_scores=batting_scores,
                           bowling_figures=bowling_figures)


@app.route('/predictions')
def predictions():
    upcoming = Match.query.filter_by(status='upcoming').order_by(Match.date).all()
    predictions_list = []
    for match in upcoming[:10]:
        team1 = db.session.get(Team, match.team1_id)
        team2 = db.session.get(Team, match.team2_id)
        pred = predict_win_probability(team1, team2)
        predictions_list.append({
            'match': match,
            'team1': team1,
            'team2': team2,
            'prediction': pred,
        })
    return render_template('predictions.html', predictions=predictions_list)


@app.route('/api/predict/<int:match_id>')
def api_predict(match_id):
    match = Match.query.get_or_404(match_id)
    team1 = db.session.get(Team, match.team1_id)
    team2 = db.session.get(Team, match.team2_id)
    prediction = predict_win_probability(team1, team2)
    return jsonify(prediction)


@app.route('/fantasy')
def fantasy():
    leaderboard = FantasyUser.query.order_by(FantasyUser.total_points.desc()).all()
    completed = Match.query.filter_by(status='completed').order_by(Match.date.desc()).all()
    upcoming = Match.query.filter_by(status='upcoming').order_by(Match.date).limit(10).all()

    match_winners = {}
    for m in completed:
        top_team = (FantasyTeam.query
                    .filter_by(match_id=m.id)
                    .order_by(FantasyTeam.total_points.desc())
                    .first())
        if top_team:
            match_winners[m.id] = top_team

    current_user = None
    if 'fantasy_user_id' in session:
        current_user = db.session.get(FantasyUser, session['fantasy_user_id'])

    return render_template('fantasy.html',
                           leaderboard=leaderboard,
                           completed_matches=completed,
                           upcoming_matches=upcoming,
                           match_winners=match_winners,
                           current_user=current_user)


@app.route('/fantasy/match/<int:match_id>')
def fantasy_match(match_id):
    match = Match.query.get_or_404(match_id)
    team1 = db.session.get(Team, match.team1_id)
    team2 = db.session.get(Team, match.team2_id)
    t1_players = Player.query.filter_by(team_id=team1.id).all()
    t2_players = Player.query.filter_by(team_id=team2.id).all()

    current_user = None
    my_team = None
    if 'fantasy_user_id' in session:
        current_user = db.session.get(FantasyUser, session['fantasy_user_id'])
        if current_user:
            my_team = FantasyTeam.query.filter_by(
                user_id=current_user.id, match_id=match_id).first()

    match_leaderboard = (FantasyTeam.query
                         .filter_by(match_id=match_id)
                         .order_by(FantasyTeam.total_points.desc())
                         .all())

    team_details = {}
    for ft in match_leaderboard:
        team_details[ft.id] = FantasyTeamPlayer.query.filter_by(
            fantasy_team_id=ft.id).order_by(FantasyTeamPlayer.points.desc()).all()

    return render_template('fantasy_match.html',
                           match=match, team1=team1, team2=team2,
                           t1_players=t1_players, t2_players=t2_players,
                           match_leaderboard=match_leaderboard,
                           team_details=team_details,
                           current_user=current_user,
                           my_team=my_team)


@app.route('/fantasy/join', methods=['POST'])
def fantasy_join():
    username = request.form.get('username', '').strip()
    if not username or len(username) < 3:
        flash('Username must be at least 3 characters.', 'danger')
        return redirect(url_for('fantasy'))

    user = FantasyUser.query.filter_by(username=username).first()
    if user:
        session['fantasy_user_id'] = user.id
        flash(f'Welcome back, {username}!', 'success')
    else:
        emojis = ['🏏', '🏆', '⭐', '🎯', '💎', '🦁', '🐯', '🦅']
        import random
        user = FantasyUser(username=username,
                           avatar_emoji=random.choice(emojis))
        db.session.add(user)
        db.session.commit()
        session['fantasy_user_id'] = user.id
        flash(f'Welcome to IPL Fantasy League, {username}!', 'success')

    return redirect(request.referrer or url_for('fantasy'))


@app.route('/fantasy/logout')
def fantasy_logout():
    session.pop('fantasy_user_id', None)
    flash('Logged out of Fantasy League.', 'info')
    return redirect(url_for('fantasy'))


@app.route('/fantasy/create-team', methods=['POST'])
def fantasy_create_team():
    if 'fantasy_user_id' not in session:
        flash('Please join the Fantasy League first.', 'danger')
        return redirect(url_for('fantasy'))

    user = db.session.get(FantasyUser, session['fantasy_user_id'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('fantasy'))

    match_id = request.form.get('match_id', type=int)
    match = Match.query.get_or_404(match_id)

    existing = FantasyTeam.query.filter_by(user_id=user.id, match_id=match_id).first()
    if existing:
        db.session.delete(existing)
        db.session.flush()

    player_ids = request.form.getlist('players', type=int)
    captain_id = request.form.get('captain', type=int)
    vice_captain_id = request.form.get('vice_captain', type=int)

    if len(player_ids) != 11:
        flash('You must select exactly 11 players.', 'danger')
        return redirect(url_for('fantasy_match', match_id=match_id))

    if not captain_id or not vice_captain_id:
        flash('You must select a Captain and Vice Captain.', 'danger')
        return redirect(url_for('fantasy_match', match_id=match_id))

    if captain_id == vice_captain_id:
        flash('Captain and Vice Captain must be different.', 'danger')
        return redirect(url_for('fantasy_match', match_id=match_id))

    t1_count = Player.query.filter(Player.id.in_(player_ids),
                                   Player.team_id == match.team1_id).count()
    t2_count = Player.query.filter(Player.id.in_(player_ids),
                                   Player.team_id == match.team2_id).count()
    if t1_count > 7 or t2_count > 7:
        flash('Maximum 7 players allowed from one team.', 'danger')
        return redirect(url_for('fantasy_match', match_id=match_id))

    ft = FantasyTeam(user_id=user.id, match_id=match_id)
    db.session.add(ft)
    db.session.flush()

    team_total = 0
    for pid in player_ids:
        is_c = pid == captain_id
        is_vc = pid == vice_captain_id

        pts = 0
        if match.status == 'completed':
            scs = Scorecard.query.filter_by(match_id=match_id, player_id=pid).all()
            pts = calc_fantasy_points(scs, is_c, is_vc)

        ftp = FantasyTeamPlayer(
            fantasy_team_id=ft.id,
            player_id=pid,
            is_captain=is_c,
            is_vice_captain=is_vc,
            points=pts,
        )
        db.session.add(ftp)
        team_total += pts

    ft.total_points = team_total

    user_total = db.session.query(
        db.func.coalesce(db.func.sum(FantasyTeam.total_points), 0)
    ).filter(FantasyTeam.user_id == user.id, FantasyTeam.id != ft.id).scalar()
    user.total_points = user_total + team_total
    user.matches_played = FantasyTeam.query.filter_by(user_id=user.id).count()

    db.session.commit()
    flash(f'Team created for Match #{match.match_number}!', 'success')
    return redirect(url_for('fantasy_match', match_id=match_id))


@app.route('/fantasy/user/<int:user_id>')
def fantasy_user_profile(user_id):
    user = FantasyUser.query.get_or_404(user_id)
    user_teams = (FantasyTeam.query
                  .filter_by(user_id=user_id)
                  .order_by(FantasyTeam.total_points.desc())
                  .all())
    return render_template('fantasy_user.html', user=user, user_teams=user_teams)


@app.template_filter('datefmt')
def datefmt(value, fmt='%d %b %Y'):
    if isinstance(value, datetime):
        return value.strftime(fmt)
    return value


@app.template_filter('timefmt')
def timefmt(value, fmt='%I:%M %p'):
    if isinstance(value, datetime):
        return value.strftime(fmt)
    return value


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
