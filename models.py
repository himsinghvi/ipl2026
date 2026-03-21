from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10), nullable=False, unique=True)
    color = db.Column(db.String(7), default='#000000')
    logo_emoji = db.Column(db.String(10), default='🏏')
    home_ground = db.Column(db.String(200))
    titles_won = db.Column(db.Integer, default=0)
    matches_played_hist = db.Column(db.Integer, default=0)
    matches_won_hist = db.Column(db.Integer, default=0)
    players = db.relationship('Player', backref='team', lazy=True)

    @property
    def win_pct_hist(self):
        if self.matches_played_hist == 0:
            return 0
        return round(self.matches_won_hist / self.matches_played_hist * 100, 1)


class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    role = db.Column(db.String(30))  # Batsman, Bowler, All-Rounder, Wicket-Keeper
    batting_style = db.Column(db.String(30))
    bowling_style = db.Column(db.String(50))
    nationality = db.Column(db.String(50))
    is_overseas = db.Column(db.Boolean, default=False)
    # Historical aggregated stats
    matches_played = db.Column(db.Integer, default=0)
    runs_scored = db.Column(db.Integer, default=0)
    balls_faced = db.Column(db.Integer, default=0)
    batting_avg = db.Column(db.Float, default=0.0)
    strike_rate = db.Column(db.Float, default=0.0)
    fifties = db.Column(db.Integer, default=0)
    hundreds = db.Column(db.Integer, default=0)
    fours = db.Column(db.Integer, default=0)
    sixes = db.Column(db.Integer, default=0)
    wickets_taken = db.Column(db.Integer, default=0)
    balls_bowled = db.Column(db.Integer, default=0)
    runs_conceded = db.Column(db.Integer, default=0)
    bowling_avg = db.Column(db.Float, default=0.0)
    economy_rate = db.Column(db.Float, default=0.0)
    best_bowling = db.Column(db.String(10), default='0/0')
    catches = db.Column(db.Integer, default=0)
    stumpings = db.Column(db.Integer, default=0)
    # Current form rating (0-100)
    form_rating = db.Column(db.Float, default=50.0)


class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    match_number = db.Column(db.Integer)
    team1_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    venue = db.Column(db.String(200))
    city = db.Column(db.String(100))
    date = db.Column(db.DateTime, nullable=False)
    stage = db.Column(db.String(30), default='League')  # League, Qualifier, Eliminator, Final
    status = db.Column(db.String(20), default='upcoming')  # upcoming, live, completed
    # Result fields (filled after match)
    toss_winner_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    toss_decision = db.Column(db.String(10))  # bat, field
    winner_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    win_margin = db.Column(db.String(50))
    team1_score = db.Column(db.String(20))
    team2_score = db.Column(db.String(20))
    potm_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=True)

    team1 = db.relationship('Team', foreign_keys=[team1_id])
    team2 = db.relationship('Team', foreign_keys=[team2_id])
    toss_winner = db.relationship('Team', foreign_keys=[toss_winner_id])
    winner = db.relationship('Team', foreign_keys=[winner_id])
    potm = db.relationship('Player', foreign_keys=[potm_id])
    scorecards = db.relationship('Scorecard', backref='match', lazy=True)


class Scorecard(db.Model):
    __tablename__ = 'scorecards'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    # Batting
    runs = db.Column(db.Integer, default=0)
    balls = db.Column(db.Integer, default=0)
    fours = db.Column(db.Integer, default=0)
    sixes = db.Column(db.Integer, default=0)
    did_bat = db.Column(db.Boolean, default=False)
    how_out = db.Column(db.String(100), default='Did not bat')
    # Bowling
    overs_bowled = db.Column(db.Float, default=0.0)
    runs_given = db.Column(db.Integer, default=0)
    wickets = db.Column(db.Integer, default=0)
    maidens = db.Column(db.Integer, default=0)
    did_bowl = db.Column(db.Boolean, default=False)
    # Fielding
    catches_taken = db.Column(db.Integer, default=0)
    run_outs = db.Column(db.Integer, default=0)

    player = db.relationship('Player', foreign_keys=[player_id])
    team = db.relationship('Team', foreign_keys=[team_id])


class HeadToHead(db.Model):
    __tablename__ = 'head_to_head'
    id = db.Column(db.Integer, primary_key=True)
    team1_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    total_matches = db.Column(db.Integer, default=0)
    team1_wins = db.Column(db.Integer, default=0)
    team2_wins = db.Column(db.Integer, default=0)
    no_results = db.Column(db.Integer, default=0)

    team1 = db.relationship('Team', foreign_keys=[team1_id])
    team2 = db.relationship('Team', foreign_keys=[team2_id])


class FantasyUser(db.Model):
    __tablename__ = 'fantasy_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    mobile_number = db.Column(db.String(20), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    avatar_emoji = db.Column(db.String(10), default='🏏')
    total_points = db.Column(db.Integer, default=0)
    matches_played = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)
    teams = db.relationship('FantasyTeam', backref='user', lazy=True)


class FantasyTeam(db.Model):
    __tablename__ = 'fantasy_teams'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fantasy_users.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    total_points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    players = db.relationship('FantasyTeamPlayer', backref='fantasy_team', lazy=True,
                              cascade='all, delete-orphan')
    match = db.relationship('Match', foreign_keys=[match_id])

    __table_args__ = (
        db.UniqueConstraint('user_id', 'match_id', name='uq_user_match'),
    )


class FantasyTeamPlayer(db.Model):
    __tablename__ = 'fantasy_team_players'
    id = db.Column(db.Integer, primary_key=True)
    fantasy_team_id = db.Column(db.Integer, db.ForeignKey('fantasy_teams.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    is_captain = db.Column(db.Boolean, default=False)
    is_vice_captain = db.Column(db.Boolean, default=False)
    points = db.Column(db.Integer, default=0)
    player = db.relationship('Player', foreign_keys=[player_id])


class UserPrediction(db.Model):
    __tablename__ = 'user_predictions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fantasy_users.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    predicted_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    confidence = db.Column(db.Integer, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('FantasyUser', foreign_keys=[user_id])
    match = db.relationship('Match', foreign_keys=[match_id])
    predicted_team = db.relationship('Team', foreign_keys=[predicted_team_id])

    __table_args__ = (
        db.UniqueConstraint('user_id', 'match_id', name='uq_user_prediction_match'),
    )
