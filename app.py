"""IPL 2026 - AI/ML Prediction, Analytics & Dashboarding Web App."""
import os
import random
import re
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from models import (db, Team, Player, Match, Scorecard, HeadToHead,
                    FantasyUser, FantasyTeam, FantasyTeamPlayer, UserPrediction)
from seed_data import seed_database, calc_fantasy_points, seed_fantasy
from predictor import (
    predict_win_probability,
    predict_top_batsmen,
    predict_top_bowlers,
    get_player_analysis,
    get_match_analysis,
    get_recent_form,
)
from records_service import get_records_payload
from datetime import datetime
from datetime import timedelta
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ipl2026.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ipl2026-secret-key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

db.init_app(app)


def ensure_fantasy_auth_schema():
    """Best-effort schema upgrades for auth fields on existing SQLite DBs."""
    inspector = inspect(db.engine)
    tables = set(inspector.get_table_names())
    if 'fantasy_users' in tables:
        columns = {col['name'] for col in inspector.get_columns('fantasy_users')}
        alter_statements = []
        if 'email' not in columns:
            alter_statements.append("ALTER TABLE fantasy_users ADD COLUMN email VARCHAR(120)")
        if 'mobile_number' not in columns:
            alter_statements.append("ALTER TABLE fantasy_users ADD COLUMN mobile_number VARCHAR(20)")
        if 'password_hash' not in columns:
            alter_statements.append("ALTER TABLE fantasy_users ADD COLUMN password_hash VARCHAR(255)")
        if 'last_login_at' not in columns:
            alter_statements.append("ALTER TABLE fantasy_users ADD COLUMN last_login_at DATETIME")
        for sql in alter_statements:
            db.session.execute(text(sql))

        # Unique indexes permit many NULL values and prevent duplicates for real signups.
        db.session.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_fantasy_users_email ON fantasy_users(email)"
        ))
        db.session.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_fantasy_users_mobile_number ON fantasy_users(mobile_number)"
        ))
        db.session.commit()


def current_fantasy_user():
    user_id = session.get('fantasy_user_id')
    if not user_id:
        return None
    user = db.session.get(FantasyUser, user_id)
    if not user:
        session.pop('fantasy_user_id', None)
    return user


def normalize_email(value):
    return (value or '').strip().lower()


def normalize_mobile(value):
    return re.sub(r'\D', '', value or '')


def valid_username(value):
    return bool(re.fullmatch(r'[A-Za-z0-9_]{3,30}', value or ''))


def valid_email(value):
    return bool(re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', value or ''))


def valid_mobile(value):
    return bool(re.fullmatch(r'\d{10,15}', value or ''))


def get_safe_next_url(default_endpoint='fantasy'):
    next_url = (request.form.get('next') or request.args.get('next') or '').strip()
    if next_url.startswith('/') and not next_url.startswith('//'):
        return next_url
    return url_for(default_endpoint)

with app.app_context():
    db.create_all()
    ensure_fantasy_auth_schema()
    seed_database(app)
    seed_fantasy(app)


@app.before_request
def refresh_session():
    if 'fantasy_user_id' in session:
        session.permanent = True


@app.context_processor
def inject_auth_user():
    user = current_fantasy_user()
    account_predictions = []
    account_fantasy_teams = []
    if user:
        account_predictions = (UserPrediction.query
                               .filter_by(user_id=user.id)
                               .order_by(UserPrediction.updated_at.desc())
                               .limit(8)
                               .all())
        account_fantasy_teams = (FantasyTeam.query
                                 .filter_by(user_id=user.id)
                                 .order_by(FantasyTeam.created_at.desc())
                                 .limit(8)
                                 .all())
    return {
        'auth_user': user,
        'account_predictions': account_predictions,
        'account_fantasy_teams': account_fantasy_teams,
    }


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
    current_user = current_fantasy_user()
    current_predictions = {}
    if current_user:
        saved_predictions = UserPrediction.query.filter_by(user_id=current_user.id).all()
        current_predictions = {pred.match_id: pred for pred in saved_predictions}

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
    return render_template('predictions.html',
                           predictions=predictions_list,
                           current_user=current_user,
                           current_predictions=current_predictions)


@app.route('/records')
def records():
    force_refresh = request.args.get('refresh') == '1'
    records_payload = get_records_payload(force_refresh=force_refresh)
    return render_template(
        'records.html',
        records_payload=records_payload,
        force_refresh=force_refresh,
    )


@app.route('/api/predict/<int:match_id>')
def api_predict(match_id):
    match = Match.query.get_or_404(match_id)
    team1 = db.session.get(Team, match.team1_id)
    team2 = db.session.get(Team, match.team2_id)
    prediction = predict_win_probability(team1, team2)
    return jsonify(prediction)


@app.route('/predictions/save', methods=['POST'])
def save_prediction():
    user = current_fantasy_user()
    if not user:
        flash('Please login to save your predictions.', 'danger')
        return redirect(url_for('fantasy'))

    match_id = request.form.get('match_id', type=int)
    predicted_team_id = request.form.get('predicted_team_id', type=int)
    confidence = request.form.get('confidence', type=int, default=50)

    if not match_id or not predicted_team_id:
        flash('Please choose a match and winner team.', 'danger')
        return redirect(url_for('predictions'))

    match = Match.query.get_or_404(match_id)
    if match.status != 'upcoming':
        flash('Predictions can only be updated for upcoming matches.', 'warning')
        return redirect(url_for('predictions'))

    if predicted_team_id not in (match.team1_id, match.team2_id):
        flash('Invalid team selected for this match.', 'danger')
        return redirect(url_for('predictions'))

    confidence = max(0, min(100, confidence))

    entry = UserPrediction.query.filter_by(user_id=user.id, match_id=match.id).first()
    if entry:
        entry.predicted_team_id = predicted_team_id
        entry.confidence = confidence
    else:
        entry = UserPrediction(
            user_id=user.id,
            match_id=match.id,
            predicted_team_id=predicted_team_id,
            confidence=confidence,
        )
        db.session.add(entry)

    db.session.commit()
    flash('Prediction saved for your account.', 'success')
    return redirect(url_for('predictions'))


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

    current_user = current_fantasy_user()

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

    current_user = current_fantasy_user()
    my_team = None
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


@app.route('/auth/signup', methods=['POST'])
def auth_signup():
    username = (request.form.get('username') or '').strip()
    email = normalize_email(request.form.get('email'))
    mobile_number = normalize_mobile(request.form.get('mobile_number'))
    password = request.form.get('password') or ''
    confirm_password = request.form.get('confirm_password') or ''

    redirect_target = get_safe_next_url()

    if not valid_username(username):
        flash('Username must be 3-30 chars (letters, numbers, underscore only).', 'danger')
        return redirect(redirect_target)
    if not email and not mobile_number:
        flash('Please provide at least one login option: email or mobile number.', 'danger')
        return redirect(redirect_target)
    if email and not valid_email(email):
        flash('Please enter a valid email address.', 'danger')
        return redirect(redirect_target)
    if mobile_number and not valid_mobile(mobile_number):
        flash('Mobile number must be 10-15 digits.', 'danger')
        return redirect(redirect_target)
    if len(password) < 8:
        flash('Password must be at least 8 characters.', 'danger')
        return redirect(redirect_target)
    if password != confirm_password:
        flash('Passwords do not match.', 'danger')
        return redirect(redirect_target)

    if FantasyUser.query.filter_by(username=username).first():
        flash('Username already taken. Please choose another username.', 'danger')
        return redirect(redirect_target)
    if email and FantasyUser.query.filter_by(email=email).first():
        flash('Email is already registered. Please login.', 'danger')
        return redirect(redirect_target)
    if mobile_number and FantasyUser.query.filter_by(mobile_number=mobile_number).first():
        flash('Mobile number is already registered. Please login.', 'danger')
        return redirect(redirect_target)

    emojis = ['🏏', '🏆', '⭐', '🎯', '💎', '🦁', '🐯', '🦅']
    user = FantasyUser(
        username=username,
        email=email or None,
        mobile_number=mobile_number or None,
        password_hash=generate_password_hash(password),
        avatar_emoji=random.choice(emojis),
        last_login_at=datetime.utcnow(),
    )
    db.session.add(user)
    db.session.commit()

    session['fantasy_user_id'] = user.id
    session.permanent = True
    flash(f'Welcome to IPL Fantasy League, {username}!', 'success')
    return redirect(redirect_target)


@app.route('/auth/login', methods=['POST'])
def auth_login():
    identifier = (request.form.get('identifier') or '').strip()
    password = request.form.get('password') or ''
    redirect_target = get_safe_next_url()

    if not identifier or not password:
        flash('Please enter email/mobile and password.', 'danger')
        return redirect(redirect_target)

    normalized_email = normalize_email(identifier)
    normalized_mobile = normalize_mobile(identifier)

    user = FantasyUser.query.filter(
        (FantasyUser.email == normalized_email) |
        (FantasyUser.mobile_number == normalized_mobile) |
        (FantasyUser.username == identifier)
    ).first()
    if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
        flash('Invalid credentials. Please try again.', 'danger')
        return redirect(redirect_target)

    user.last_login_at = datetime.utcnow()
    db.session.commit()
    session['fantasy_user_id'] = user.id
    session.permanent = True
    flash(f'Welcome back, {user.username}!', 'success')
    return redirect(redirect_target)


@app.route('/fantasy/join', methods=['POST'])
def fantasy_join():
    flash('Username-only login is removed. Please use Signup/Login.', 'warning')
    return redirect(url_for('fantasy'))


@app.route('/fantasy/logout')
def fantasy_logout():
    session.pop('fantasy_user_id', None)
    flash('Logged out of Fantasy League.', 'info')
    return redirect(get_safe_next_url())


@app.route('/fantasy/create-team', methods=['POST'])
def fantasy_create_team():
    user = current_fantasy_user()
    if not user:
        flash('Please login to the Fantasy League first.', 'danger')
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
