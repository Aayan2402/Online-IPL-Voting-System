from flask import Flask, render_template, request, redirect, session, flash
import json, os, hashlib

app = Flask(__name__)
app.secret_key = 'voting_secret_key_2024'

USERS_FILE = 'users.json'
VOTES_FILE = 'votes.json'

TEAMS = ["MI", "GT", "CSK", "RCB", "RR", "SRH", "LSG"]

TEAM_INFO = {
    "MI":  {"name": "Mumbai Indians",       "emoji": "💙", "color": "#1D4E8F"},
    "GT":  {"name": "Gujarat Titans",       "emoji": "🩵", "color": "#1C4C7C"},
    "CSK": {"name": "Chennai Super Kings",  "emoji": "💛", "color": "#F9CD1F"},
    "RCB": {"name": "Royal Challengers",    "emoji": "❤️", "color": "#C8102E"},
    "RR":  {"name": "Rajasthan Royals",     "emoji": "💗", "color": "#E8336D"},
    "SRH": {"name": "Sunrisers Hyderabad",  "emoji": "🧡", "color": "#F26522"},
    "LSG": {"name": "Lucknow Super Giants", "emoji": "🩶", "color": "#A0C4FF"},
}

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def load_votes():
    if not os.path.exists(VOTES_FILE):
        default = {team: 0 for team in TEAMS}
        save_votes(default)
        return default
    with open(VOTES_FILE, 'r') as f:
        return json.load(f)

def save_votes(votes):
    with open(VOTES_FILE, 'w') as f:
        json.dump(votes, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def home():
    if 'username' not in session:
        return redirect('/login')
    return render_template('index.html', username=session['username'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        users = load_users()
        if not username or not password:
            flash('Username aur password dono bharo!', 'error')
        elif username in users:
            flash('Ye username already exist karta hai!', 'error')
        elif len(password) < 4:
            flash('Password kam se kam 4 characters ka hona chahiye!', 'error')
        else:
            users[username] = {'password': hash_password(password), 'has_voted': False}
            save_users(users)
            flash('Registration successful! Ab login karo.', 'success')
            return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        users = load_users()
        if username not in users:
            flash('Username nahi mila!', 'error')
        elif users[username]['password'] != hash_password(password):
            flash('Password galat hai!', 'error')
        else:
            session['username'] = username
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/public-result')

@app.route('/public-result')
def public_result():
    votes = load_votes()
    users = load_users()
    total_votes = sum(votes.values())
    return render_template('public_result.html',
        votes=votes, team_info=TEAM_INFO, teams=TEAMS,
        total_users=len(users), total_votes=total_votes)

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'username' not in session:
        return redirect('/login')
    users = load_users()
    username = session['username']
    if users[username]['has_voted']:
        flash('Aapne already vote kar diya hai!', 'error')
        return redirect('/result')
    if request.method == 'POST':
        choice = request.form.get('candidate')
        votes = load_votes()
        if choice in votes:
            votes[choice] += 1
            save_votes(votes)
            users[username]['has_voted'] = True
            save_users(users)
            flash('Vote successfully submit ho gaya! 🎉', 'success')
            return redirect('/result')
        else:
            flash('Koi team select karo!', 'error')
    return render_template('vote.html', teams=TEAMS, team_info=TEAM_INFO)

@app.route('/result')
def result():
    if 'username' not in session:
        return redirect('/login')
    users = load_users()
    username = session['username']
    votes = load_votes()
    total_votes = sum(votes.values())
    return render_template('result.html',
        votes=votes, team_info=TEAM_INFO, teams=TEAMS,
        has_voted=users[username]['has_voted'], total_votes=total_votes)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
