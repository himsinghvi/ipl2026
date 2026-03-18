"""Seed database with IPL 2026 teams, players, schedule, and simulated completed match data.
Data sourced from iplt20.com official squad pages and confirmed BCCI schedule (March 2026).
"""
import random
from datetime import datetime, timedelta
from models import (db, Team, Player, Match, Scorecard, HeadToHead,
                    FantasyUser, FantasyTeam, FantasyTeamPlayer)

random.seed(2026)

TEAMS = [
    {"name": "Chennai Super Kings", "short_name": "CSK", "color": "#FCCA06", "logo_emoji": "🦁",
     "home_ground": "MA Chidambaram Stadium, Chennai", "titles_won": 5, "mp": 248, "mw": 135},
    {"name": "Mumbai Indians", "short_name": "MI", "color": "#004BA0", "logo_emoji": "🛡️",
     "home_ground": "Wankhede Stadium, Mumbai", "titles_won": 5, "mp": 257, "mw": 148},
    {"name": "Royal Challengers Bengaluru", "short_name": "RCB", "color": "#EC1C24", "logo_emoji": "👑",
     "home_ground": "M. Chinnaswamy Stadium, Bengaluru", "titles_won": 1, "mp": 257, "mw": 127},
    {"name": "Kolkata Knight Riders", "short_name": "KKR", "color": "#3A225D", "logo_emoji": "⚔️",
     "home_ground": "Eden Gardens, Kolkata", "titles_won": 3, "mp": 253, "mw": 135},
    {"name": "Delhi Capitals", "short_name": "DC", "color": "#17479E", "logo_emoji": "🏛️",
     "home_ground": "Arun Jaitley Stadium, Delhi", "titles_won": 0, "mp": 244, "mw": 109},
    {"name": "Punjab Kings", "short_name": "PBKS", "color": "#ED1B24", "logo_emoji": "🗡️",
     "home_ground": "PCA New Stadium, New Chandigarh", "titles_won": 0, "mp": 245, "mw": 116},
    {"name": "Rajasthan Royals", "short_name": "RR", "color": "#EA1A85", "logo_emoji": "👸",
     "home_ground": "Barsapara Cricket Stadium, Guwahati", "titles_won": 1, "mp": 229, "mw": 111},
    {"name": "Sunrisers Hyderabad", "short_name": "SRH", "color": "#FF822A", "logo_emoji": "☀️",
     "home_ground": "Rajiv Gandhi Intl Stadium, Hyderabad", "titles_won": 1, "mp": 198, "mw": 98},
    {"name": "Gujarat Titans", "short_name": "GT", "color": "#1C1C1C", "logo_emoji": "🔱",
     "home_ground": "Narendra Modi Stadium, Ahmedabad", "titles_won": 1, "mp": 66, "mw": 42},
    {"name": "Lucknow Super Giants", "short_name": "LSG", "color": "#A72056", "logo_emoji": "🦊",
     "home_ground": "BRSABV Ekana Cricket Stadium, Lucknow", "titles_won": 0, "mp": 62, "mw": 31},
]

# Real IPL 2026 squads sourced from iplt20.com (March 2026)
# Stats are approximate career IPL figures through end of IPL 2025
PLAYERS_DATA = {
    "CSK": [
        {"name": "Ruturaj Gaikwad", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm off break", "nationality": "India", "overseas": False, "mp": 75, "runs": 2500, "bf": 1850, "avg": 37.3, "sr": 135.1, "50s": 17, "100s": 2, "4s": 245, "6s": 90, "wk": 4, "bb": 200, "rc": 170, "ba": 42.5, "eco": 5.1, "best": "1/10", "form": 80},
        {"name": "MS Dhoni", "role": "Wicket-Keeper", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 272, "runs": 5300, "bf": 3900, "avg": 38.5, "sr": 135.9, "50s": 24, "100s": 0, "4s": 370, "6s": 255, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 50},
        {"name": "Sanju Samson", "role": "Wicket-Keeper", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 158, "runs": 4600, "bf": 3250, "avg": 30.7, "sr": 141.5, "50s": 24, "100s": 3, "4s": 370, "6s": 215, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 76},
        {"name": "Shivam Dube", "role": "All-Rounder", "batting_style": "Left-hand", "bowling_style": "Left-arm medium", "nationality": "India", "overseas": False, "mp": 75, "runs": 1600, "bf": 1050, "avg": 28.1, "sr": 152.4, "50s": 8, "100s": 0, "4s": 110, "6s": 100, "wk": 10, "bb": 280, "rc": 370, "ba": 37.0, "eco": 7.93, "best": "2/20", "form": 72},
        {"name": "Dewald Brevis", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm leg break", "nationality": "South Africa", "overseas": True, "mp": 22, "runs": 450, "bf": 320, "avg": 22.5, "sr": 140.6, "50s": 2, "100s": 0, "4s": 40, "6s": 28, "wk": 2, "bb": 60, "rc": 80, "ba": 40.0, "eco": 8.0, "best": "1/15", "form": 68},
        {"name": "Sarfaraz Khan", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 12, "runs": 280, "bf": 200, "avg": 28.0, "sr": 140.0, "50s": 2, "100s": 0, "4s": 28, "6s": 14, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 70},
        {"name": "Khaleel Ahmed", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Left-arm fast-medium", "nationality": "India", "overseas": False, "mp": 48, "runs": 25, "bf": 35, "avg": 5.0, "sr": 71.4, "50s": 0, "100s": 0, "4s": 2, "6s": 1, "wk": 50, "bb": 1020, "rc": 1280, "ba": 25.6, "eco": 7.53, "best": "3/21", "form": 67},
        {"name": "Noor Ahmad", "role": "Bowler", "batting_style": "Left-hand", "bowling_style": "Left-arm chinaman", "nationality": "Afghanistan", "overseas": True, "mp": 15, "runs": 10, "bf": 18, "avg": 3.3, "sr": 55.6, "50s": 0, "100s": 0, "4s": 1, "6s": 0, "wk": 18, "bb": 330, "rc": 380, "ba": 21.1, "eco": 6.91, "best": "3/18", "form": 72},
        {"name": "Nathan Ellis", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast-medium", "nationality": "Australia", "overseas": True, "mp": 20, "runs": 15, "bf": 20, "avg": 5.0, "sr": 75.0, "50s": 0, "100s": 0, "4s": 1, "6s": 0, "wk": 22, "bb": 432, "rc": 540, "ba": 24.5, "eco": 7.5, "best": "4/22", "form": 70},
        {"name": "Rahul Chahar", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm leg break", "nationality": "India", "overseas": False, "mp": 72, "runs": 45, "bf": 55, "avg": 4.5, "sr": 81.8, "50s": 0, "100s": 0, "4s": 3, "6s": 2, "wk": 70, "bb": 1530, "rc": 1780, "ba": 25.4, "eco": 6.98, "best": "4/17", "form": 66},
        {"name": "Jamie Overton", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm fast", "nationality": "England", "overseas": True, "mp": 8, "runs": 150, "bf": 95, "avg": 25.0, "sr": 157.9, "50s": 1, "100s": 0, "4s": 12, "6s": 10, "wk": 8, "bb": 168, "rc": 220, "ba": 27.5, "eco": 7.86, "best": "2/25", "form": 65},
    ],
    "MI": [
        {"name": "Rohit Sharma", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm off break", "nationality": "India", "overseas": False, "mp": 255, "runs": 6600, "bf": 4800, "avg": 29.7, "sr": 137.5, "50s": 44, "100s": 2, "4s": 575, "6s": 290, "wk": 15, "bb": 480, "rc": 420, "ba": 28.0, "eco": 5.25, "best": "1/6", "form": 65},
        {"name": "Suryakumar Yadav", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm medium", "nationality": "India", "overseas": False, "mp": 130, "runs": 4100, "bf": 2700, "avg": 35.3, "sr": 151.9, "50s": 27, "100s": 1, "4s": 350, "6s": 215, "wk": 2, "bb": 60, "rc": 70, "ba": 35.0, "eco": 7.0, "best": "1/15", "form": 83},
        {"name": "Hardik Pandya", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm fast-medium", "nationality": "India", "overseas": False, "mp": 130, "runs": 2400, "bf": 1620, "avg": 28.6, "sr": 148.1, "50s": 9, "100s": 0, "4s": 165, "6s": 140, "wk": 65, "bb": 1550, "rc": 1980, "ba": 30.5, "eco": 7.66, "best": "3/17", "form": 77},
        {"name": "Tilak Varma", "role": "Batsman", "batting_style": "Left-hand", "bowling_style": "Right-arm off break", "nationality": "India", "overseas": False, "mp": 50, "runs": 1400, "bf": 980, "avg": 33.3, "sr": 142.9, "50s": 9, "100s": 1, "4s": 125, "6s": 58, "wk": 4, "bb": 144, "rc": 175, "ba": 43.8, "eco": 7.29, "best": "1/18", "form": 82},
        {"name": "Quinton de Kock", "role": "Wicket-Keeper", "batting_style": "Left-hand", "bowling_style": "-", "nationality": "South Africa", "overseas": True, "mp": 100, "runs": 3400, "bf": 2440, "avg": 35.4, "sr": 139.3, "50s": 24, "100s": 2, "4s": 320, "6s": 140, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 75},
        {"name": "Jasprit Bumrah", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast", "nationality": "India", "overseas": False, "mp": 145, "runs": 85, "bf": 100, "avg": 5.7, "sr": 85.0, "50s": 0, "100s": 0, "4s": 7, "6s": 3, "wk": 175, "bb": 3200, "rc": 3350, "ba": 19.1, "eco": 6.28, "best": "5/10", "form": 92},
        {"name": "Trent Boult", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Left-arm fast", "nationality": "New Zealand", "overseas": True, "mp": 82, "runs": 45, "bf": 65, "avg": 4.5, "sr": 69.2, "50s": 0, "100s": 0, "4s": 5, "6s": 1, "wk": 92, "bb": 1830, "rc": 2080, "ba": 22.6, "eco": 6.82, "best": "4/18", "form": 74},
        {"name": "Will Jacks", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm off break", "nationality": "England", "overseas": True, "mp": 18, "runs": 500, "bf": 320, "avg": 31.3, "sr": 156.3, "50s": 3, "100s": 0, "4s": 42, "6s": 30, "wk": 8, "bb": 210, "rc": 260, "ba": 32.5, "eco": 7.43, "best": "2/18", "form": 76},
        {"name": "Deepak Chahar", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm medium-fast", "nationality": "India", "overseas": False, "mp": 85, "runs": 220, "bf": 195, "avg": 13.8, "sr": 112.8, "50s": 0, "100s": 0, "4s": 20, "6s": 9, "wk": 90, "bb": 1830, "rc": 2200, "ba": 24.4, "eco": 7.21, "best": "4/13", "form": 62},
        {"name": "Naman Dhir", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm medium", "nationality": "India", "overseas": False, "mp": 16, "runs": 400, "bf": 255, "avg": 33.3, "sr": 156.9, "50s": 2, "100s": 0, "4s": 34, "6s": 24, "wk": 3, "bb": 60, "rc": 75, "ba": 25.0, "eco": 7.5, "best": "1/12", "form": 74},
        {"name": "Shardul Thakur", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm medium-fast", "nationality": "India", "overseas": False, "mp": 102, "runs": 550, "bf": 385, "avg": 15.3, "sr": 142.9, "50s": 0, "100s": 0, "4s": 42, "6s": 32, "wk": 80, "bb": 2050, "rc": 2650, "ba": 33.1, "eco": 7.76, "best": "3/20", "form": 60},
    ],
    "RCB": [
        {"name": "Virat Kohli", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm medium", "nationality": "India", "overseas": False, "mp": 260, "runs": 8700, "bf": 6350, "avg": 37.7, "sr": 137.0, "50s": 55, "100s": 8, "4s": 740, "6s": 300, "wk": 4, "bb": 132, "rc": 140, "ba": 35.0, "eco": 6.36, "best": "1/5", "form": 84},
        {"name": "Rajat Patidar", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 42, "runs": 1250, "bf": 850, "avg": 35.7, "sr": 147.1, "50s": 7, "100s": 1, "4s": 115, "6s": 60, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 79},
        {"name": "Phil Salt", "role": "Wicket-Keeper", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "England", "overseas": True, "mp": 28, "runs": 900, "bf": 550, "avg": 36.0, "sr": 163.6, "50s": 6, "100s": 1, "4s": 80, "6s": 55, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 85},
        {"name": "Devdutt Padikkal", "role": "Batsman", "batting_style": "Left-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 58, "runs": 1600, "bf": 1200, "avg": 30.2, "sr": 133.3, "50s": 9, "100s": 1, "4s": 160, "6s": 52, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 70},
        {"name": "Tim David", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm off break", "nationality": "Australia", "overseas": True, "mp": 42, "runs": 950, "bf": 570, "avg": 28.8, "sr": 166.7, "50s": 4, "100s": 0, "4s": 58, "6s": 70, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 73},
        {"name": "Krunal Pandya", "role": "All-Rounder", "batting_style": "Left-hand", "bowling_style": "Left-arm orthodox", "nationality": "India", "overseas": False, "mp": 105, "runs": 1600, "bf": 1170, "avg": 21.6, "sr": 136.8, "50s": 5, "100s": 0, "4s": 110, "6s": 68, "wk": 65, "bb": 1920, "rc": 2250, "ba": 34.6, "eco": 7.03, "best": "3/19", "form": 66},
        {"name": "Venkatesh Iyer", "role": "All-Rounder", "batting_style": "Left-hand", "bowling_style": "Right-arm medium", "nationality": "India", "overseas": False, "mp": 52, "runs": 1200, "bf": 850, "avg": 27.3, "sr": 141.2, "50s": 6, "100s": 1, "4s": 108, "6s": 54, "wk": 12, "bb": 400, "rc": 440, "ba": 36.7, "eco": 6.6, "best": "2/20", "form": 71},
        {"name": "Josh Hazlewood", "role": "Bowler", "batting_style": "Left-hand", "bowling_style": "Right-arm fast", "nationality": "Australia", "overseas": True, "mp": 40, "runs": 18, "bf": 28, "avg": 3.6, "sr": 64.3, "50s": 0, "100s": 0, "4s": 1, "6s": 0, "wk": 42, "bb": 870, "rc": 940, "ba": 22.4, "eco": 6.48, "best": "3/24", "form": 75},
        {"name": "Bhuvneshwar Kumar", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm medium-fast", "nationality": "India", "overseas": False, "mp": 175, "runs": 320, "bf": 320, "avg": 8.9, "sr": 100.0, "50s": 0, "100s": 0, "4s": 27, "6s": 9, "wk": 178, "bb": 3880, "rc": 3950, "ba": 22.2, "eco": 6.11, "best": "4/14", "form": 63},
        {"name": "Yash Dayal", "role": "Bowler", "batting_style": "Left-hand", "bowling_style": "Left-arm fast-medium", "nationality": "India", "overseas": False, "mp": 35, "runs": 35, "bf": 45, "avg": 7.0, "sr": 77.8, "50s": 0, "100s": 0, "4s": 3, "6s": 1, "wk": 38, "bb": 756, "rc": 940, "ba": 24.7, "eco": 7.46, "best": "3/18", "form": 68},
        {"name": "Jacob Bethell", "role": "All-Rounder", "batting_style": "Left-hand", "bowling_style": "Right-arm off break", "nationality": "England", "overseas": True, "mp": 5, "runs": 120, "bf": 80, "avg": 24.0, "sr": 150.0, "50s": 1, "100s": 0, "4s": 10, "6s": 7, "wk": 2, "bb": 48, "rc": 55, "ba": 27.5, "eco": 6.88, "best": "1/8", "form": 70},
    ],
    "KKR": [
        {"name": "Ajinkya Rahane", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 110, "runs": 2800, "bf": 2100, "avg": 28.6, "sr": 133.3, "50s": 17, "100s": 0, "4s": 270, "6s": 80, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 65},
        {"name": "Rinku Singh", "role": "Batsman", "batting_style": "Left-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 55, "runs": 1300, "bf": 870, "avg": 33.3, "sr": 149.4, "50s": 6, "100s": 0, "4s": 100, "6s": 70, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 81},
        {"name": "Sunil Narine", "role": "All-Rounder", "batting_style": "Left-hand", "bowling_style": "Right-arm off break", "nationality": "West Indies", "overseas": True, "mp": 185, "runs": 1700, "bf": 1100, "avg": 17.3, "sr": 154.5, "50s": 4, "100s": 1, "4s": 110, "6s": 120, "wk": 175, "bb": 4200, "rc": 4450, "ba": 25.4, "eco": 6.36, "best": "4/21", "form": 78},
        {"name": "Varun Chakravarthy", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm leg break", "nationality": "India", "overseas": False, "mp": 62, "runs": 25, "bf": 35, "avg": 4.2, "sr": 71.4, "50s": 0, "100s": 0, "4s": 2, "6s": 1, "wk": 68, "bb": 1380, "rc": 1540, "ba": 22.6, "eco": 6.7, "best": "5/17", "form": 82},
        {"name": "Matheesha Pathirana", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast", "nationality": "Sri Lanka", "overseas": True, "mp": 32, "runs": 35, "bf": 40, "avg": 5.8, "sr": 87.5, "50s": 0, "100s": 0, "4s": 3, "6s": 1, "wk": 42, "bb": 696, "rc": 780, "ba": 18.6, "eco": 6.72, "best": "4/28", "form": 84},
        {"name": "Harshit Rana", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast", "nationality": "India", "overseas": False, "mp": 25, "runs": 60, "bf": 50, "avg": 10.0, "sr": 120.0, "50s": 0, "100s": 0, "4s": 5, "6s": 3, "wk": 28, "bb": 528, "rc": 660, "ba": 23.6, "eco": 7.5, "best": "3/24", "form": 74},
        {"name": "Rachin Ravindra", "role": "All-Rounder", "batting_style": "Left-hand", "bowling_style": "Left-arm orthodox", "nationality": "New Zealand", "overseas": True, "mp": 22, "runs": 520, "bf": 370, "avg": 28.9, "sr": 140.5, "50s": 3, "100s": 0, "4s": 50, "6s": 22, "wk": 12, "bb": 360, "rc": 420, "ba": 35.0, "eco": 7.0, "best": "2/22", "form": 70},
        {"name": "Cameron Green", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm fast-medium", "nationality": "Australia", "overseas": True, "mp": 18, "runs": 420, "bf": 290, "avg": 26.3, "sr": 144.8, "50s": 2, "100s": 0, "4s": 38, "6s": 20, "wk": 12, "bb": 288, "rc": 365, "ba": 30.4, "eco": 7.6, "best": "2/20", "form": 69},
        {"name": "Rahul Tripathi", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 90, "runs": 2200, "bf": 1580, "avg": 27.5, "sr": 139.2, "50s": 11, "100s": 0, "4s": 195, "6s": 88, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 63},
        {"name": "Ramandeep Singh", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm medium", "nationality": "India", "overseas": False, "mp": 25, "runs": 300, "bf": 200, "avg": 18.8, "sr": 150.0, "50s": 1, "100s": 0, "4s": 22, "6s": 18, "wk": 6, "bb": 144, "rc": 180, "ba": 30.0, "eco": 7.5, "best": "2/18", "form": 64},
        {"name": "Angkrish Raghuvanshi", "role": "Batsman", "batting_style": "Left-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 12, "runs": 220, "bf": 170, "avg": 22.0, "sr": 129.4, "50s": 1, "100s": 0, "4s": 22, "6s": 10, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 60},
    ],
    "DC": [
        {"name": "KL Rahul", "role": "Wicket-Keeper", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 135, "runs": 4900, "bf": 3600, "avg": 40.8, "sr": 136.1, "50s": 40, "100s": 4, "4s": 440, "6s": 170, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 73},
        {"name": "Axar Patel", "role": "All-Rounder", "batting_style": "Left-hand", "bowling_style": "Left-arm orthodox", "nationality": "India", "overseas": False, "mp": 92, "runs": 1100, "bf": 770, "avg": 19.3, "sr": 142.9, "50s": 3, "100s": 0, "4s": 65, "6s": 60, "wk": 75, "bb": 1920, "rc": 2250, "ba": 30.0, "eco": 7.03, "best": "3/21", "form": 73},
        {"name": "Mitchell Starc", "role": "Bowler", "batting_style": "Left-hand", "bowling_style": "Left-arm fast", "nationality": "Australia", "overseas": True, "mp": 38, "runs": 50, "bf": 60, "avg": 5.6, "sr": 83.3, "50s": 0, "100s": 0, "4s": 5, "6s": 2, "wk": 42, "bb": 810, "rc": 980, "ba": 23.3, "eco": 7.26, "best": "3/22", "form": 74},
        {"name": "Kuldeep Yadav", "role": "Bowler", "batting_style": "Left-hand", "bowling_style": "Left-arm chinaman", "nationality": "India", "overseas": False, "mp": 80, "runs": 55, "bf": 65, "avg": 5.5, "sr": 84.6, "50s": 0, "100s": 0, "4s": 5, "6s": 2, "wk": 82, "bb": 1710, "rc": 1870, "ba": 22.8, "eco": 6.56, "best": "4/14", "form": 80},
        {"name": "Tristan Stubbs", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "South Africa", "overseas": True, "mp": 25, "runs": 580, "bf": 370, "avg": 29.0, "sr": 156.8, "50s": 3, "100s": 0, "4s": 40, "6s": 38, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 72},
        {"name": "David Miller", "role": "Batsman", "batting_style": "Left-hand", "bowling_style": "-", "nationality": "South Africa", "overseas": True, "mp": 120, "runs": 2950, "bf": 2000, "avg": 31.4, "sr": 147.5, "50s": 13, "100s": 0, "4s": 180, "6s": 180, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 68},
        {"name": "Karun Nair", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 65, "runs": 1400, "bf": 1050, "avg": 24.1, "sr": 133.3, "50s": 7, "100s": 0, "4s": 130, "6s": 45, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 66},
        {"name": "T Natarajan", "role": "Bowler", "batting_style": "Left-hand", "bowling_style": "Left-arm medium-fast", "nationality": "India", "overseas": False, "mp": 45, "runs": 25, "bf": 35, "avg": 4.2, "sr": 71.4, "50s": 0, "100s": 0, "4s": 2, "6s": 1, "wk": 45, "bb": 972, "rc": 1180, "ba": 26.2, "eco": 7.28, "best": "4/29", "form": 67},
        {"name": "Abishek Porel", "role": "Wicket-Keeper", "batting_style": "Left-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 18, "runs": 400, "bf": 295, "avg": 25.0, "sr": 135.6, "50s": 2, "100s": 0, "4s": 35, "6s": 20, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 65},
        {"name": "Mukesh Kumar", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm medium-fast", "nationality": "India", "overseas": False, "mp": 30, "runs": 18, "bf": 28, "avg": 3.6, "sr": 64.3, "50s": 0, "100s": 0, "4s": 1, "6s": 0, "wk": 33, "bb": 648, "rc": 815, "ba": 24.7, "eco": 7.55, "best": "3/25", "form": 62},
        {"name": "Prithvi Shaw", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 48, "runs": 1050, "bf": 780, "avg": 23.3, "sr": 134.6, "50s": 5, "100s": 0, "4s": 115, "6s": 35, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 58},
    ],
    "PBKS": [
        {"name": "Shreyas Iyer", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm leg break", "nationality": "India", "overseas": False, "mp": 120, "runs": 3600, "bf": 2600, "avg": 33.0, "sr": 138.5, "50s": 22, "100s": 1, "4s": 305, "6s": 130, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 80},
        {"name": "Marcus Stoinis", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm medium-fast", "nationality": "Australia", "overseas": True, "mp": 52, "runs": 1000, "bf": 690, "avg": 25.6, "sr": 144.9, "50s": 5, "100s": 0, "4s": 70, "6s": 55, "wk": 20, "bb": 540, "rc": 670, "ba": 33.5, "eco": 7.44, "best": "2/23", "form": 71},
        {"name": "Arshdeep Singh", "role": "Bowler", "batting_style": "Left-hand", "bowling_style": "Left-arm fast-medium", "nationality": "India", "overseas": False, "mp": 62, "runs": 22, "bf": 32, "avg": 3.7, "sr": 68.8, "50s": 0, "100s": 0, "4s": 2, "6s": 0, "wk": 68, "bb": 1380, "rc": 1610, "ba": 23.7, "eco": 7.0, "best": "5/32", "form": 80},
        {"name": "Yuzvendra Chahal", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm leg break", "nationality": "India", "overseas": False, "mp": 150, "runs": 65, "bf": 85, "avg": 4.6, "sr": 76.5, "50s": 0, "100s": 0, "4s": 5, "6s": 3, "wk": 195, "bb": 3360, "rc": 3780, "ba": 19.4, "eco": 6.75, "best": "5/40", "form": 73},
        {"name": "Marco Jansen", "role": "All-Rounder", "batting_style": "Left-hand", "bowling_style": "Left-arm fast-medium", "nationality": "South Africa", "overseas": True, "mp": 20, "runs": 250, "bf": 175, "avg": 17.9, "sr": 142.9, "50s": 1, "100s": 0, "4s": 20, "6s": 15, "wk": 22, "bb": 432, "rc": 540, "ba": 24.5, "eco": 7.5, "best": "3/20", "form": 74},
        {"name": "Lockie Ferguson", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast", "nationality": "New Zealand", "overseas": True, "mp": 30, "runs": 20, "bf": 25, "avg": 4.0, "sr": 80.0, "50s": 0, "100s": 0, "4s": 2, "6s": 0, "wk": 35, "bb": 636, "rc": 770, "ba": 22.0, "eco": 7.26, "best": "3/18", "form": 75},
        {"name": "Shashank Singh", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm medium", "nationality": "India", "overseas": False, "mp": 28, "runs": 550, "bf": 350, "avg": 27.5, "sr": 157.1, "50s": 3, "100s": 0, "4s": 35, "6s": 35, "wk": 2, "bb": 48, "rc": 60, "ba": 30.0, "eco": 7.5, "best": "1/10", "form": 72},
        {"name": "Nehal Wadhera", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 18, "runs": 400, "bf": 280, "avg": 26.7, "sr": 142.9, "50s": 2, "100s": 0, "4s": 30, "6s": 22, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 69},
        {"name": "Prabhsimran Singh", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 25, "runs": 550, "bf": 370, "avg": 25.0, "sr": 148.6, "50s": 3, "100s": 1, "4s": 55, "6s": 30, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 65},
        {"name": "Harpreet Brar", "role": "All-Rounder", "batting_style": "Left-hand", "bowling_style": "Left-arm orthodox", "nationality": "India", "overseas": False, "mp": 30, "runs": 200, "bf": 150, "avg": 13.3, "sr": 133.3, "50s": 0, "100s": 0, "4s": 14, "6s": 10, "wk": 25, "bb": 600, "rc": 720, "ba": 28.8, "eco": 7.2, "best": "3/19", "form": 63},
        {"name": "Azmatullah Omarzai", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm fast-medium", "nationality": "Afghanistan", "overseas": True, "mp": 8, "runs": 180, "bf": 120, "avg": 22.5, "sr": 150.0, "50s": 1, "100s": 0, "4s": 15, "6s": 10, "wk": 7, "bb": 156, "rc": 200, "ba": 28.6, "eco": 7.69, "best": "2/22", "form": 68},
    ],
    "RR": [
        {"name": "Yashasvi Jaiswal", "role": "Batsman", "batting_style": "Left-hand", "bowling_style": "Right-arm leg break", "nationality": "India", "overseas": False, "mp": 55, "runs": 1900, "bf": 1280, "avg": 38.0, "sr": 148.4, "50s": 12, "100s": 2, "4s": 190, "6s": 82, "wk": 1, "bb": 30, "rc": 35, "ba": 35.0, "eco": 7.0, "best": "1/12", "form": 87},
        {"name": "Riyan Parag", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm leg break", "nationality": "India", "overseas": False, "mp": 62, "runs": 1100, "bf": 780, "avg": 23.4, "sr": 141.0, "50s": 4, "100s": 0, "4s": 82, "6s": 48, "wk": 10, "bb": 360, "rc": 450, "ba": 45.0, "eco": 7.5, "best": "2/16", "form": 72},
        {"name": "Shimron Hetmyer", "role": "Batsman", "batting_style": "Left-hand", "bowling_style": "-", "nationality": "West Indies", "overseas": True, "mp": 58, "runs": 1200, "bf": 760, "avg": 30.8, "sr": 157.9, "50s": 5, "100s": 0, "4s": 75, "6s": 70, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 70},
        {"name": "Ravindra Jadeja", "role": "All-Rounder", "batting_style": "Left-hand", "bowling_style": "Left-arm orthodox", "nationality": "India", "overseas": False, "mp": 225, "runs": 2950, "bf": 2100, "avg": 27.1, "sr": 140.5, "50s": 9, "100s": 0, "4s": 210, "6s": 138, "wk": 155, "bb": 4900, "rc": 3980, "ba": 25.7, "eco": 7.1, "best": "5/16", "form": 73},
        {"name": "Sam Curran", "role": "All-Rounder", "batting_style": "Left-hand", "bowling_style": "Left-arm medium-fast", "nationality": "England", "overseas": True, "mp": 60, "runs": 650, "bf": 455, "avg": 18.1, "sr": 142.9, "50s": 1, "100s": 0, "4s": 48, "6s": 32, "wk": 60, "bb": 1300, "rc": 1570, "ba": 26.2, "eco": 7.25, "best": "4/11", "form": 73},
        {"name": "Jofra Archer", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast", "nationality": "England", "overseas": True, "mp": 40, "runs": 80, "bf": 65, "avg": 8.0, "sr": 123.1, "50s": 0, "100s": 0, "4s": 8, "6s": 4, "wk": 48, "bb": 876, "rc": 970, "ba": 20.2, "eco": 6.64, "best": "3/15", "form": 78},
        {"name": "Dhruv Jurel", "role": "Wicket-Keeper", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 18, "runs": 400, "bf": 285, "avg": 26.7, "sr": 140.4, "50s": 2, "100s": 0, "4s": 35, "6s": 17, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 70},
        {"name": "Tushar Deshpande", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast-medium", "nationality": "India", "overseas": False, "mp": 48, "runs": 55, "bf": 60, "avg": 9.2, "sr": 91.7, "50s": 0, "100s": 0, "4s": 5, "6s": 2, "wk": 55, "bb": 1050, "rc": 1360, "ba": 24.7, "eco": 7.77, "best": "4/33", "form": 66},
        {"name": "Ravi Bishnoi", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm leg break", "nationality": "India", "overseas": False, "mp": 55, "runs": 18, "bf": 22, "avg": 3.6, "sr": 81.8, "50s": 0, "100s": 0, "4s": 1, "6s": 0, "wk": 58, "bb": 1180, "rc": 1330, "ba": 22.9, "eco": 6.76, "best": "4/16", "form": 74},
        {"name": "Sandeep Sharma", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm medium-fast", "nationality": "India", "overseas": False, "mp": 100, "runs": 110, "bf": 130, "avg": 6.9, "sr": 84.6, "50s": 0, "100s": 0, "4s": 9, "6s": 3, "wk": 108, "bb": 2160, "rc": 2540, "ba": 23.5, "eco": 7.06, "best": "4/20", "form": 59},
        {"name": "Nandre Burger", "role": "Bowler", "batting_style": "Left-hand", "bowling_style": "Left-arm fast-medium", "nationality": "South Africa", "overseas": True, "mp": 14, "runs": 12, "bf": 18, "avg": 4.0, "sr": 66.7, "50s": 0, "100s": 0, "4s": 1, "6s": 0, "wk": 16, "bb": 264, "rc": 340, "ba": 21.3, "eco": 7.73, "best": "3/24", "form": 66},
    ],
    "SRH": [
        {"name": "Travis Head", "role": "Batsman", "batting_style": "Left-hand", "bowling_style": "Right-arm off break", "nationality": "Australia", "overseas": True, "mp": 28, "runs": 1050, "bf": 640, "avg": 41.9, "sr": 164.1, "50s": 6, "100s": 2, "4s": 105, "6s": 62, "wk": 1, "bb": 30, "rc": 30, "ba": 30.0, "eco": 6.0, "best": "1/10", "form": 88},
        {"name": "Heinrich Klaasen", "role": "Wicket-Keeper", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "South Africa", "overseas": True, "mp": 30, "runs": 1100, "bf": 660, "avg": 42.3, "sr": 166.7, "50s": 8, "100s": 1, "4s": 88, "6s": 76, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 86},
        {"name": "Pat Cummins", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast", "nationality": "Australia", "overseas": True, "mp": 42, "runs": 220, "bf": 165, "avg": 14.7, "sr": 133.3, "50s": 0, "100s": 0, "4s": 16, "6s": 12, "wk": 45, "bb": 918, "rc": 1100, "ba": 24.4, "eco": 7.19, "best": "4/34", "form": 75},
        {"name": "Abhishek Sharma", "role": "All-Rounder", "batting_style": "Left-hand", "bowling_style": "Left-arm orthodox", "nationality": "India", "overseas": False, "mp": 42, "runs": 1050, "bf": 700, "avg": 28.4, "sr": 150.0, "50s": 5, "100s": 1, "4s": 85, "6s": 62, "wk": 10, "bb": 300, "rc": 350, "ba": 35.0, "eco": 7.0, "best": "2/15", "form": 77},
        {"name": "Ishan Kishan", "role": "Wicket-Keeper", "batting_style": "Left-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 90, "runs": 2400, "bf": 1740, "avg": 28.6, "sr": 137.9, "50s": 15, "100s": 1, "4s": 215, "6s": 115, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 70},
        {"name": "Nitish Kumar Reddy", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm medium", "nationality": "India", "overseas": False, "mp": 22, "runs": 520, "bf": 360, "avg": 28.9, "sr": 144.4, "50s": 3, "100s": 0, "4s": 45, "6s": 25, "wk": 12, "bb": 288, "rc": 360, "ba": 30.0, "eco": 7.5, "best": "2/18", "form": 76},
        {"name": "Liam Livingstone", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm leg break", "nationality": "England", "overseas": True, "mp": 35, "runs": 800, "bf": 500, "avg": 25.8, "sr": 160.0, "50s": 3, "100s": 0, "4s": 50, "6s": 55, "wk": 10, "bb": 300, "rc": 375, "ba": 37.5, "eco": 7.5, "best": "2/18", "form": 70},
        {"name": "Harshal Patel", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm medium-fast", "nationality": "India", "overseas": False, "mp": 115, "runs": 380, "bf": 300, "avg": 11.9, "sr": 126.7, "50s": 0, "100s": 0, "4s": 28, "6s": 20, "wk": 130, "bb": 2460, "rc": 3020, "ba": 23.2, "eco": 7.37, "best": "5/27", "form": 70},
        {"name": "Brydon Carse", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm fast-medium", "nationality": "England", "overseas": True, "mp": 5, "runs": 60, "bf": 40, "avg": 15.0, "sr": 150.0, "50s": 0, "100s": 0, "4s": 5, "6s": 3, "wk": 5, "bb": 108, "rc": 130, "ba": 26.0, "eco": 7.22, "best": "2/20", "form": 65},
        {"name": "Jaydev Unadkat", "role": "Bowler", "batting_style": "Left-hand", "bowling_style": "Left-arm medium-fast", "nationality": "India", "overseas": False, "mp": 100, "runs": 200, "bf": 200, "avg": 7.4, "sr": 100.0, "50s": 0, "100s": 0, "4s": 18, "6s": 6, "wk": 95, "bb": 2100, "rc": 2600, "ba": 27.4, "eco": 7.43, "best": "3/15", "form": 60},
        {"name": "Shivam Mavi", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast", "nationality": "India", "overseas": False, "mp": 28, "runs": 30, "bf": 35, "avg": 5.0, "sr": 85.7, "50s": 0, "100s": 0, "4s": 3, "6s": 1, "wk": 25, "bb": 576, "rc": 750, "ba": 30.0, "eco": 7.81, "best": "3/22", "form": 62},
    ],
    "GT": [
        {"name": "Shubman Gill", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm leg break", "nationality": "India", "overseas": False, "mp": 85, "runs": 2800, "bf": 2020, "avg": 36.4, "sr": 138.6, "50s": 18, "100s": 2, "4s": 265, "6s": 98, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 82},
        {"name": "Jos Buttler", "role": "Wicket-Keeper", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "England", "overseas": True, "mp": 92, "runs": 3400, "bf": 2340, "avg": 39.1, "sr": 145.3, "50s": 19, "100s": 4, "4s": 300, "6s": 180, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 76},
        {"name": "Rashid Khan", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm leg break", "nationality": "Afghanistan", "overseas": True, "mp": 118, "runs": 650, "bf": 375, "avg": 15.5, "sr": 173.3, "50s": 0, "100s": 0, "4s": 32, "6s": 52, "wk": 128, "bb": 2580, "rc": 2680, "ba": 20.9, "eco": 6.23, "best": "4/24", "form": 84},
        {"name": "Kagiso Rabada", "role": "Bowler", "batting_style": "Left-hand", "bowling_style": "Right-arm fast", "nationality": "South Africa", "overseas": True, "mp": 68, "runs": 90, "bf": 90, "avg": 9.0, "sr": 100.0, "50s": 0, "100s": 0, "4s": 9, "6s": 4, "wk": 80, "bb": 1480, "rc": 1680, "ba": 21.0, "eco": 6.81, "best": "4/21", "form": 80},
        {"name": "Mohammed Siraj", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast-medium", "nationality": "India", "overseas": False, "mp": 82, "runs": 55, "bf": 75, "avg": 5.5, "sr": 73.3, "50s": 0, "100s": 0, "4s": 5, "6s": 1, "wk": 88, "bb": 1780, "rc": 2150, "ba": 24.4, "eco": 7.25, "best": "4/21", "form": 72},
        {"name": "Washington Sundar", "role": "All-Rounder", "batting_style": "Left-hand", "bowling_style": "Right-arm off break", "nationality": "India", "overseas": False, "mp": 60, "runs": 550, "bf": 420, "avg": 16.7, "sr": 131.0, "50s": 1, "100s": 0, "4s": 38, "6s": 22, "wk": 38, "bb": 1180, "rc": 1310, "ba": 34.5, "eco": 6.66, "best": "3/15", "form": 67},
        {"name": "Sai Sudharsan", "role": "Batsman", "batting_style": "Left-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 28, "runs": 850, "bf": 630, "avg": 35.4, "sr": 134.9, "50s": 6, "100s": 0, "4s": 78, "6s": 30, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 75},
        {"name": "Rahul Tewatia", "role": "All-Rounder", "batting_style": "Left-hand", "bowling_style": "Right-arm leg break", "nationality": "India", "overseas": False, "mp": 95, "runs": 1500, "bf": 1060, "avg": 22.1, "sr": 141.5, "50s": 3, "100s": 0, "4s": 85, "6s": 85, "wk": 32, "bb": 1080, "rc": 1380, "ba": 43.1, "eco": 7.67, "best": "2/14", "form": 64},
        {"name": "Jason Holder", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm fast-medium", "nationality": "West Indies", "overseas": True, "mp": 48, "runs": 450, "bf": 320, "avg": 18.0, "sr": 140.6, "50s": 1, "100s": 0, "4s": 30, "6s": 25, "wk": 40, "bb": 960, "rc": 1200, "ba": 30.0, "eco": 7.5, "best": "3/25", "form": 65},
        {"name": "Shahrukh Khan", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 30, "runs": 450, "bf": 300, "avg": 20.5, "sr": 150.0, "50s": 2, "100s": 0, "4s": 25, "6s": 30, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 64},
        {"name": "Glenn Phillips", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm off break", "nationality": "New Zealand", "overseas": True, "mp": 15, "runs": 350, "bf": 220, "avg": 25.0, "sr": 159.1, "50s": 2, "100s": 0, "4s": 25, "6s": 22, "wk": 3, "bb": 72, "rc": 85, "ba": 28.3, "eco": 7.08, "best": "1/10", "form": 68},
    ],
    "LSG": [
        {"name": "Rishabh Pant", "role": "Wicket-Keeper", "batting_style": "Left-hand", "bowling_style": "-", "nationality": "India", "overseas": False, "mp": 112, "runs": 3600, "bf": 2450, "avg": 35.3, "sr": 146.9, "50s": 19, "100s": 1, "4s": 310, "6s": 165, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 80},
        {"name": "Nicholas Pooran", "role": "Wicket-Keeper", "batting_style": "Left-hand", "bowling_style": "-", "nationality": "West Indies", "overseas": True, "mp": 55, "runs": 1250, "bf": 850, "avg": 27.2, "sr": 147.1, "50s": 5, "100s": 1, "4s": 78, "6s": 88, "wk": 0, "bb": 0, "rc": 0, "ba": 0, "eco": 0, "best": "-", "form": 72},
        {"name": "Mitchell Marsh", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm fast-medium", "nationality": "Australia", "overseas": True, "mp": 38, "runs": 780, "bf": 555, "avg": 25.2, "sr": 140.5, "50s": 4, "100s": 0, "4s": 60, "6s": 38, "wk": 14, "bb": 396, "rc": 500, "ba": 35.7, "eco": 7.58, "best": "2/12", "form": 67},
        {"name": "Wanindu Hasaranga", "role": "All-Rounder", "batting_style": "Right-hand", "bowling_style": "Right-arm leg break", "nationality": "Sri Lanka", "overseas": True, "mp": 35, "runs": 220, "bf": 175, "avg": 14.7, "sr": 125.7, "50s": 0, "100s": 0, "4s": 16, "6s": 11, "wk": 45, "bb": 756, "rc": 860, "ba": 19.1, "eco": 6.83, "best": "5/18", "form": 78},
        {"name": "Anrich Nortje", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast", "nationality": "South Africa", "overseas": True, "mp": 52, "runs": 35, "bf": 45, "avg": 5.8, "sr": 77.8, "50s": 0, "100s": 0, "4s": 3, "6s": 1, "wk": 60, "bb": 1100, "rc": 1300, "ba": 21.7, "eco": 7.09, "best": "4/10", "form": 73},
        {"name": "Mohammad Shami", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast-medium", "nationality": "India", "overseas": False, "mp": 102, "runs": 105, "bf": 125, "avg": 5.3, "sr": 84.0, "50s": 0, "100s": 0, "4s": 11, "6s": 3, "wk": 115, "bb": 2200, "rc": 2520, "ba": 21.9, "eco": 6.88, "best": "4/11", "form": 72},
        {"name": "Aiden Markram", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm off break", "nationality": "South Africa", "overseas": True, "mp": 45, "runs": 1000, "bf": 750, "avg": 26.3, "sr": 133.3, "50s": 6, "100s": 0, "4s": 88, "6s": 38, "wk": 6, "bb": 200, "rc": 220, "ba": 36.7, "eco": 6.6, "best": "1/15", "form": 65},
        {"name": "Ayush Badoni", "role": "Batsman", "batting_style": "Right-hand", "bowling_style": "Right-arm leg break", "nationality": "India", "overseas": False, "mp": 30, "runs": 700, "bf": 490, "avg": 28.0, "sr": 142.9, "50s": 4, "100s": 0, "4s": 52, "6s": 35, "wk": 3, "bb": 72, "rc": 90, "ba": 30.0, "eco": 7.5, "best": "1/12", "form": 68},
        {"name": "Avesh Khan", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast-medium", "nationality": "India", "overseas": False, "mp": 65, "runs": 45, "bf": 55, "avg": 5.6, "sr": 81.8, "50s": 0, "100s": 0, "4s": 3, "6s": 1, "wk": 62, "bb": 1350, "rc": 1690, "ba": 27.3, "eco": 7.51, "best": "4/24", "form": 63},
        {"name": "Mayank Yadav", "role": "Bowler", "batting_style": "Right-hand", "bowling_style": "Right-arm fast", "nationality": "India", "overseas": False, "mp": 8, "runs": 5, "bf": 8, "avg": 2.5, "sr": 62.5, "50s": 0, "100s": 0, "4s": 0, "6s": 0, "wk": 10, "bb": 168, "rc": 190, "ba": 19.0, "eco": 6.79, "best": "3/14", "form": 75},
        {"name": "Mohsin Khan", "role": "Bowler", "batting_style": "Left-hand", "bowling_style": "Left-arm fast-medium", "nationality": "India", "overseas": False, "mp": 18, "runs": 12, "bf": 18, "avg": 4.0, "sr": 66.7, "50s": 0, "100s": 0, "4s": 1, "6s": 0, "wk": 20, "bb": 372, "rc": 420, "ba": 21.0, "eco": 6.77, "best": "3/20", "form": 68},
    ],
}

VENUES = [
    ("M. Chinnaswamy Stadium", "Bengaluru"),
    ("Wankhede Stadium", "Mumbai"),
    ("Barsapara Cricket Stadium", "Guwahati"),
    ("PCA New Stadium", "New Chandigarh"),
    ("BRSABV Ekana Cricket Stadium", "Lucknow"),
    ("Eden Gardens", "Kolkata"),
    ("MA Chidambaram Stadium", "Chennai"),
    ("Arun Jaitley Stadium", "Delhi"),
    ("Narendra Modi Stadium", "Ahmedabad"),
    ("Rajiv Gandhi Intl Cricket Stadium", "Hyderabad"),
]

TEAM_SHORT_NAMES = ["CSK", "MI", "RCB", "KKR", "DC", "PBKS", "RR", "SRH", "GT", "LSG"]

# Team index map: CSK=0, MI=1, RCB=2, KKR=3, DC=4, PBKS=5, RR=6, SRH=7, GT=8, LSG=9
# Confirmed first 20 fixtures from BCCI (source: iplt20.com / cricketwebs.com)
CONFIRMED_SCHEDULE = [
    {"mn": 1, "date": "2026-03-28 19:30", "home": 2, "away": 7, "venue": 0},   # RCB vs SRH, Bengaluru
    {"mn": 2, "date": "2026-03-29 19:30", "home": 1, "away": 3, "venue": 1},   # MI vs KKR, Mumbai
    {"mn": 3, "date": "2026-03-30 19:30", "home": 6, "away": 0, "venue": 2},   # RR vs CSK, Guwahati
    {"mn": 4, "date": "2026-03-31 19:30", "home": 5, "away": 8, "venue": 3},   # PBKS vs GT, New Chandigarh
    {"mn": 5, "date": "2026-04-01 19:30", "home": 9, "away": 4, "venue": 4},   # LSG vs DC, Lucknow
    {"mn": 6, "date": "2026-04-02 19:30", "home": 3, "away": 7, "venue": 5},   # KKR vs SRH, Kolkata
    {"mn": 7, "date": "2026-04-03 19:30", "home": 0, "away": 5, "venue": 6},   # CSK vs PBKS, Chennai
    {"mn": 8, "date": "2026-04-04 15:30", "home": 4, "away": 1, "venue": 7},   # DC vs MI, Delhi
    {"mn": 9, "date": "2026-04-04 19:30", "home": 8, "away": 6, "venue": 8},   # GT vs RR, Ahmedabad
    {"mn": 10, "date": "2026-04-05 15:30", "home": 7, "away": 9, "venue": 9},  # SRH vs LSG, Hyderabad
    {"mn": 11, "date": "2026-04-05 19:30", "home": 2, "away": 0, "venue": 0},  # RCB vs CSK, Bengaluru
    {"mn": 12, "date": "2026-04-06 19:30", "home": 3, "away": 5, "venue": 5},  # KKR vs PBKS, Kolkata
    {"mn": 13, "date": "2026-04-07 19:30", "home": 6, "away": 1, "venue": 2},  # RR vs MI, Guwahati
    {"mn": 14, "date": "2026-04-08 19:30", "home": 4, "away": 8, "venue": 7},  # DC vs GT, Delhi
    {"mn": 15, "date": "2026-04-09 19:30", "home": 3, "away": 9, "venue": 5},  # KKR vs LSG, Kolkata
    {"mn": 16, "date": "2026-04-10 19:30", "home": 6, "away": 2, "venue": 2},  # RR vs RCB, Guwahati
    {"mn": 17, "date": "2026-04-11 15:30", "home": 5, "away": 7, "venue": 3},  # PBKS vs SRH, New Chandigarh
    {"mn": 18, "date": "2026-04-11 19:30", "home": 0, "away": 4, "venue": 6},  # CSK vs DC, Chennai
    {"mn": 19, "date": "2026-04-12 15:30", "home": 9, "away": 8, "venue": 4},  # LSG vs GT, Lucknow
    {"mn": 20, "date": "2026-04-12 19:30", "home": 1, "away": 2, "venue": 1},  # MI vs RCB, Mumbai
]


def generate_schedule():
    """Generate IPL 2026 schedule: 20 confirmed + remaining generated + 4 playoffs."""
    matches = []

    for fix in CONFIRMED_SCHEDULE:
        matches.append({
            "match_number": fix["mn"],
            "team1_idx": fix["home"],
            "team2_idx": fix["away"],
            "venue": VENUES[fix["venue"]][0],
            "city": VENUES[fix["venue"]][1],
            "date": datetime.strptime(fix["date"], "%Y-%m-%d %H:%M"),
            "stage": "League",
        })

    played_pairs = set()
    for fix in CONFIRMED_SCHEDULE:
        played_pairs.add((fix["home"], fix["away"]))

    remaining_pairs = []
    for i in range(10):
        for j in range(10):
            if i != j and (i, j) not in played_pairs:
                remaining_pairs.append((i, j))

    random.shuffle(remaining_pairs)
    remaining_pairs = remaining_pairs[:54]

    match_num = 21
    current_date = datetime(2026, 4, 14, 19, 30)
    matches_on_day = 0

    for t1_idx, t2_idx in remaining_pairs:
        venue_idx = t1_idx % len(VENUES)
        venue, city = VENUES[venue_idx]

        if matches_on_day >= 2:
            current_date += timedelta(days=1)
            matches_on_day = 0

        if matches_on_day == 1:
            match_time = current_date.replace(hour=15, minute=30)
        else:
            match_time = current_date.replace(hour=19, minute=30)

        matches.append({
            "match_number": match_num,
            "team1_idx": t1_idx,
            "team2_idx": t2_idx,
            "venue": venue,
            "city": city,
            "date": match_time,
            "stage": "League",
        })
        match_num += 1
        matches_on_day += 1

    playoff_start = current_date + timedelta(days=5)
    playoff_stages = ["Qualifier 1", "Eliminator", "Qualifier 2", "Final"]
    playoff_venues = [
        ("PCA New Stadium", "New Chandigarh"),
        ("PCA New Stadium", "New Chandigarh"),
        ("Narendra Modi Stadium", "Ahmedabad"),
        ("M. Chinnaswamy Stadium", "Bengaluru"),
    ]
    for i, stage in enumerate(playoff_stages):
        t1 = random.choice(range(10))
        t2 = random.choice([x for x in range(10) if x != t1])
        matches.append({
            "match_number": match_num,
            "team1_idx": t1,
            "team2_idx": t2,
            "venue": playoff_venues[i][0],
            "city": playoff_venues[i][1],
            "date": playoff_start + timedelta(days=i * 2),
            "stage": stage,
        })
        match_num += 1

    return matches


def simulate_scorecard(match, team1_players, team2_players, winner_id, team1_id, team2_id):
    """Simulate batting/bowling scorecard for a completed match."""
    scorecards = []
    is_team1_winner = (winner_id == team1_id)

    for batting_team_players, bowling_team_players, is_winner, team_id, opp_team_id in [
        (team1_players, team2_players, is_team1_winner, team1_id, team2_id),
        (team2_players, team1_players, not is_team1_winner, team2_id, team1_id),
    ]:
        total_runs = random.randint(140, 220) if not is_winner else random.randint(145, 225)
        total_wickets = random.randint(3, 10)

        batsmen = [p for p in batting_team_players if p.role in ('Batsman', 'Wicket-Keeper', 'All-Rounder')]
        if len(batsmen) < 5:
            batsmen = batting_team_players[:7]

        remaining_runs = total_runs
        batters_used = min(len(batsmen), random.randint(6, 10))
        dismissals = ['b', 'c', 'lbw', 'st', 'run out', 'c&b']

        for i, batter in enumerate(batsmen[:batters_used]):
            if i == batters_used - 1:
                runs = max(0, remaining_runs)
            else:
                max_share = max(1, remaining_runs // max(1, (batters_used - i)))
                base = int(max_share * (batter.form_rating / 100))
                runs = random.randint(0, max(1, base + 20))
                runs = min(runs, remaining_runs)
            remaining_runs -= runs
            balls = max(1, int(runs / (batter.strike_rate / 100))) if batter.strike_rate > 0 else random.randint(5, 25)
            balls = max(1, balls + random.randint(-3, 5))
            fours = min(runs // 4, random.randint(0, max(1, runs // 6)))
            sixes = min((runs - fours * 4) // 6, random.randint(0, max(1, runs // 12)))

            is_out = i < total_wickets
            how_out = random.choice(dismissals) if is_out else 'not out'

            sc = Scorecard(
                player_id=batter.id, team_id=team_id,
                runs=runs, balls=balls, fours=fours, sixes=sixes,
                did_bat=True, how_out=how_out,
            )
            scorecards.append(sc)

        opp_bowlers = [p for p in bowling_team_players if p.role in ('Bowler', 'All-Rounder')]
        if len(opp_bowlers) < 3:
            opp_bowlers = bowling_team_players[-5:]

        total_overs = 20.0
        remaining_overs = total_overs
        remaining_wk = total_wickets

        for i, bowler in enumerate(opp_bowlers[:min(len(opp_bowlers), 6)]):
            if i == min(len(opp_bowlers), 6) - 1:
                overs = remaining_overs
                wk = remaining_wk
            else:
                overs = round(random.uniform(2, 4), 1)
                overs = min(overs, remaining_overs)
                wk = random.randint(0, min(3, remaining_wk))
            remaining_overs = max(0, remaining_overs - overs)
            remaining_wk = max(0, remaining_wk - wk)

            eco = bowler.economy_rate if bowler.economy_rate > 0 else random.uniform(6, 10)
            runs_given = int(overs * (eco + random.uniform(-1.5, 1.5)))
            runs_given = max(0, runs_given)
            maidens = 1 if random.random() < 0.15 else 0

            sc = Scorecard(
                player_id=bowler.id, team_id=opp_team_id,
                overs_bowled=overs, runs_given=runs_given, wickets=wk,
                maidens=maidens, did_bowl=True,
            )
            scorecards.append(sc)

    return scorecards


def seed_database(app):
    """Seed the database with all IPL 2026 data."""
    with app.app_context():
        db.create_all()

        if Team.query.first():
            return

        teams = []
        for t in TEAMS:
            team = Team(
                name=t["name"], short_name=t["short_name"], color=t["color"],
                logo_emoji=t["logo_emoji"], home_ground=t["home_ground"],
                titles_won=t["titles_won"],
                matches_played_hist=t["mp"], matches_won_hist=t["mw"],
            )
            db.session.add(team)
            teams.append(team)
        db.session.flush()

        all_players = {}
        for short_name, players_list in PLAYERS_DATA.items():
            team = next(t for t in teams if t.short_name == short_name)
            team_players = []
            for p in players_list:
                player = Player(
                    name=p["name"], team_id=team.id, role=p["role"],
                    batting_style=p["batting_style"], bowling_style=p["bowling_style"],
                    nationality=p["nationality"], is_overseas=p["overseas"],
                    matches_played=p["mp"], runs_scored=p["runs"], balls_faced=p["bf"],
                    batting_avg=p["avg"], strike_rate=p["sr"], fifties=p["50s"],
                    hundreds=p["100s"], fours=p["4s"], sixes=p["6s"],
                    wickets_taken=p["wk"], balls_bowled=p["bb"], runs_conceded=p["rc"],
                    bowling_avg=p["ba"], economy_rate=p["eco"], best_bowling=p["best"],
                    form_rating=p["form"],
                )
                db.session.add(player)
                team_players.append(player)
            all_players[short_name] = team_players
        db.session.flush()

        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                total = random.randint(18, 35)
                t1w = random.randint(int(total * 0.3), int(total * 0.7))
                h2h = HeadToHead(
                    team1_id=teams[i].id, team2_id=teams[j].id,
                    total_matches=total, team1_wins=t1w,
                    team2_wins=total - t1w, no_results=0,
                )
                db.session.add(h2h)

        schedule = generate_schedule()
        today = datetime(2026, 4, 15)

        for m in schedule:
            t1 = teams[m["team1_idx"]]
            t2 = teams[m["team2_idx"]]

            is_completed = m["date"] < today
            status = "completed" if is_completed else "upcoming"

            match = Match(
                match_number=m["match_number"],
                team1_id=t1.id, team2_id=t2.id,
                venue=m["venue"], city=m["city"],
                date=m["date"], stage=m["stage"], status=status,
            )

            if is_completed:
                winner = random.choice([t1, t2])
                match.toss_winner_id = random.choice([t1.id, t2.id])
                match.toss_decision = random.choice(["bat", "field"])
                match.winner_id = winner.id
                margin_type = random.choice(["runs", "wickets"])
                if margin_type == "runs":
                    match.win_margin = f"{random.randint(5, 45)} runs"
                else:
                    match.win_margin = f"{random.randint(2, 8)} wickets"

                t1_total = random.randint(130, 220)
                t1_wk = random.randint(3, 10)
                if winner == t1:
                    t2_total = t1_total - random.randint(5, 40) if margin_type == "runs" else random.randint(130, t1_total)
                else:
                    t2_total = t1_total + random.randint(1, 10) if margin_type == "wickets" else t1_total + random.randint(5, 40)
                t2_wk = random.randint(2, 10)

                match.team1_score = f"{t1_total}/{t1_wk}"
                match.team2_score = f"{t2_total}/{t2_wk}"

                sn1 = t1.short_name
                sn2 = t2.short_name
                potm_pool = all_players.get(sn1, []) + all_players.get(sn2, [])
                if potm_pool:
                    match.potm_id = random.choice(potm_pool).id

            db.session.add(match)
            db.session.flush()

            if is_completed:
                sn1 = t1.short_name
                sn2 = t2.short_name
                t1_players = all_players.get(sn1, [])
                t2_players = all_players.get(sn2, [])
                if t1_players and t2_players:
                    cards = simulate_scorecard(match, t1_players, t2_players, match.winner_id, t1.id, t2.id)
                    for sc in cards:
                        sc.match_id = match.id
                        db.session.add(sc)

        db.session.commit()


FANTASY_USERS_DATA = [
    {"username": "CricketKing99", "emoji": "👑"},
    {"username": "SixMachine", "emoji": "💥"},
    {"username": "SpinWizard", "emoji": "🌀"},
    {"username": "PaceBowlerX", "emoji": "🔥"},
    {"username": "BoundaryHunter", "emoji": "🎯"},
    {"username": "WicketMaster", "emoji": "⚡"},
    {"username": "RunChaser07", "emoji": "🏃"},
    {"username": "StumpBreaker", "emoji": "🪵"},
    {"username": "CoverDrive44", "emoji": "🏏"},
    {"username": "YorkerKing", "emoji": "🎳"},
    {"username": "SlipCatcher", "emoji": "🧤"},
    {"username": "PowerPlay", "emoji": "💪"},
]


def calc_fantasy_points(scorecards, is_captain=False, is_vice_captain=False):
    """Calculate Dream11-style fantasy points for a player in a match."""
    pts = 0
    for sc in scorecards:
        if sc.did_bat:
            pts += sc.runs
            pts += sc.fours
            pts += sc.sixes * 2
            if sc.runs >= 100:
                pts += 16
            elif sc.runs >= 50:
                pts += 8
            elif sc.runs >= 25:
                pts += 4
            if sc.runs == 0 and sc.how_out not in ('not out', 'Did not bat'):
                pts -= 2
            if sc.balls >= 10:
                sr = sc.runs / sc.balls * 100 if sc.balls > 0 else 0
                if sr >= 170:
                    pts += 6
                elif sr >= 150:
                    pts += 4
                elif sr < 60:
                    pts -= 4
                elif sr < 80:
                    pts -= 2
        if sc.did_bowl:
            pts += sc.wickets * 25
            if sc.wickets >= 5:
                pts += 16
            elif sc.wickets >= 4:
                pts += 12
            elif sc.wickets >= 3:
                pts += 8
            pts += sc.maidens * 12
            if sc.overs_bowled >= 2:
                eco = sc.runs_given / sc.overs_bowled if sc.overs_bowled > 0 else 99
                if eco < 5:
                    pts += 6
                elif eco < 6:
                    pts += 4
                elif eco > 11:
                    pts -= 4
                elif eco > 10:
                    pts -= 2
        pts += sc.catches_taken * 8
        pts += sc.run_outs * 12

    if is_captain:
        pts *= 2
    elif is_vice_captain:
        pts = int(pts * 1.5)
    return pts


def seed_fantasy(app):
    """Seed fantasy league data with bot users and their team selections."""
    with app.app_context():
        if FantasyUser.query.first():
            return

        random.seed(42)

        users = []
        for u in FANTASY_USERS_DATA:
            user = FantasyUser(username=u["username"], avatar_emoji=u["emoji"])
            db.session.add(user)
            users.append(user)
        db.session.flush()

        completed_matches = Match.query.filter_by(status='completed').order_by(Match.date).all()

        for match in completed_matches:
            t1_players = Player.query.filter_by(team_id=match.team1_id).all()
            t2_players = Player.query.filter_by(team_id=match.team2_id).all()
            all_match_players = t1_players + t2_players

            if len(all_match_players) < 11:
                continue

            match_scorecards = Scorecard.query.filter_by(match_id=match.id).all()
            sc_by_player = {}
            for sc in match_scorecards:
                sc_by_player.setdefault(sc.player_id, []).append(sc)

            for user in users:
                max_per_team = 7
                pool1 = list(t1_players)
                pool2 = list(t2_players)
                random.shuffle(pool1)
                random.shuffle(pool2)

                from_t1 = random.randint(4, min(max_per_team, len(pool1)))
                from_t2 = 11 - from_t1
                if from_t2 > len(pool2):
                    from_t2 = len(pool2)
                    from_t1 = 11 - from_t2

                selected = pool1[:from_t1] + pool2[:from_t2]
                if len(selected) < 11:
                    remaining = [p for p in all_match_players if p not in selected]
                    selected += remaining[:11 - len(selected)]
                selected = selected[:11]

                captain = random.choice(selected)
                vc = random.choice([p for p in selected if p != captain])

                ft = FantasyTeam(user_id=user.id, match_id=match.id)
                db.session.add(ft)
                db.session.flush()

                team_total = 0
                for player in selected:
                    is_c = player.id == captain.id
                    is_vc = player.id == vc.id
                    player_scorecards = sc_by_player.get(player.id, [])
                    pts = calc_fantasy_points(player_scorecards, is_c, is_vc)

                    ftp = FantasyTeamPlayer(
                        fantasy_team_id=ft.id, player_id=player.id,
                        is_captain=is_c, is_vice_captain=is_vc, points=pts,
                    )
                    db.session.add(ftp)
                    team_total += pts

                ft.total_points = team_total
                user.total_points += team_total
                user.matches_played += 1

        db.session.commit()
