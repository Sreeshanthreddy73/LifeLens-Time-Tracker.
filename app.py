import os
from datetime import datetime, time, date, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

from models import db, User, Activity

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lifelens-secret-key-12345'
# Use cloud DB if available, otherwise fallback to local sqlite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///lifelens.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Ensure tables are created for Vercel/Production
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Helper Functions ---
def calculate_minutes(start, end):
    start_dt = datetime.combine(date.today(), start)
    end_dt = datetime.combine(date.today(), end)
    if end_dt <= start_dt:
        # Handle cases where activity might cross midnight (though form validation should prevent for simple cases)
        return 0
    diff = end_dt - start_dt
    return int(diff.total_seconds() / 60)

# --- Routes ---

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('register'))
        
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check email and password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    activities = Activity.query.filter_by(user_id=current_user.id, date=today).all()
    
    total_min = sum(a.duration_minutes for a in activities)
    productive_min = sum(a.duration_minutes for a in activities if a.category == 'productive')
    neutral_min = sum(a.duration_minutes for a in activities if a.category == 'neutral')
    waste_min = sum(a.duration_minutes for a in activities if a.category == 'waste')
    
    prod_percent = (productive_min / total_min * 100) if total_min > 0 else 0
    
    # Format for charts
    chart_data = {
        'labels': ['Productive', 'Neutral', 'Waste'],
        'values': [productive_min, neutral_min, waste_min]
    }

    # Formatting today's date
    today_date = today.strftime('%B %d, %Y')
    today_val = today.strftime('%Y-%m-%d')
    
    # Weekly Trend & Streak Logic
    last_7_days_data = []
    current_streak = 0
    
    # Calculate Streak (Look back from today)
    temp_date = today
    while True:
        has_productive = Activity.query.filter_by(
            user_id=current_user.id, 
            date=temp_date, 
            category='productive'
        ).first()
        if has_productive:
            current_streak += 1
            temp_date -= timedelta(days=1)
        else:
            break

    # Calculate Trend Data
    for i in range(6, -1, -1):
        target_date = today - timedelta(days=i)
        day_activities = Activity.query.filter_by(user_id=current_user.id, date=target_date).all()
        day_total = sum(a.duration_minutes for a in day_activities)
        day_prod = sum(a.duration_minutes for a in day_activities if a.category == 'productive')
        score = (day_prod / day_total * 100) if day_total > 0 else 0
        last_7_days_data.append({
            'date': target_date.strftime('%a'),
            'score': round(score, 1)
        })

    # Achievements logic
    total_productive_min = db.session.query(func.sum(Activity.duration_minutes)).filter_by(user_id=current_user.id, category='productive').scalar() or 0
    total_entries = Activity.query.filter_by(user_id=current_user.id).count()
    
    achievements = []
    if current_streak >= 3: achievements.append({'icon': '🔥', 'title': 'Consistency King', 'desc': '3+ Day Streak'})
    if total_productive_min >= 600: achievements.append({'icon': '🥈', 'title': 'Deep Worker', 'desc': '10hrs Productive'})
    if total_productive_min >= 3000: achievements.append({'icon': '🥇', 'title': 'Time Lord', 'desc': '50hrs Productive'})
    if total_entries >= 50: achievements.append({'icon': '📊', 'title': 'Data Collector', 'desc': '50 Logs Added'})

    # Career/Care Insight: Projected Yearly Waste
    yearly_waste_hrs = (waste_min * 365) / 60
    total_waste_days = yearly_waste_hrs / 24 # Full 24-hour days
    
    return render_template('dashboard.html', 
                           activities=activities, 
                           total_min=total_min,
                           productive_min=productive_min,
                           neutral_min=neutral_min,
                           waste_min=waste_min,
                           prod_percent=round(prod_percent, 1),
                           chart_data=chart_data,
                           today_date=today_date,
                           today_val=today_val,
                           yearly_waste_hrs=round(yearly_waste_hrs, 1),
                           total_waste_days=round(total_waste_days, 1),
                           weekly_trend=last_7_days_data,
                           streak=current_streak,
                           achievements=achievements)

@app.route('/add_entry', methods=['POST'])
@login_required
def add_entry():
    name = request.form.get('activity_name')
    category = request.form.get('category')
    entry_date_str = request.form.get('date')
    start_time_str = request.form.get('start_time')
    end_time_str = request.form.get('end_time')
    
    if not all([name, category, entry_date_str, start_time_str, end_time_str]):
        flash('All fields are required.', 'warning')
        return redirect(url_for('dashboard'))

    entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
    start_t = datetime.strptime(start_time_str, '%H:%M').time()
    end_t = datetime.strptime(end_time_str, '%H:%M').time()
    
    if end_t <= start_t:
        flash('End time must be after start time.', 'danger')
        return redirect(url_for('dashboard'))
    
    duration = calculate_minutes(start_t, end_t)
    
    new_activity = Activity(
        user_id=current_user.id,
        name=name,
        category=category,
        date=entry_date,
        start_time=start_t,
        end_time=end_t,
        duration_minutes=duration
    )
    
    db.session.add(new_activity)
    db.session.commit()
    flash('Entry added successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/edit_entry/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_entry(id):
    activity = Activity.query.get_or_404(id)
    if activity.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        activity.name = request.form.get('activity_name')
        activity.category = request.form.get('category')
        entry_date_str = request.form.get('date')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        
        if not all([activity.name, activity.category, entry_date_str, start_time_str, end_time_str]):
            flash('All fields are required.', 'warning')
            return redirect(url_for('edit_entry', id=id))

        activity.date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
        start_t = datetime.strptime(start_time_str, '%H:%M').time()
        end_t = datetime.strptime(end_time_str, '%H:%M').time()
        
        if end_t <= start_t:
            flash('End time must be after start time.', 'danger')
            return redirect(url_for('edit_entry', id=id))
        
        activity.start_time = start_t
        activity.end_time = end_t
        activity.duration_minutes = calculate_minutes(start_t, end_t)
        
        db.session.commit()
        flash('Entry updated successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('edit_entry.html', activity=activity)

@app.route('/delete_entry/<int:id>')
@login_required
def delete_entry(id):
    activity = Activity.query.get_or_404(id)
    if activity.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(activity)
    db.session.commit()
    flash('Entry deleted.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/history')
@login_required
def history():
    filter_date_str = request.args.get('date')
    if filter_date_str:
        filter_date = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
        activities = Activity.query.filter_by(user_id=current_user.id, date=filter_date).all()
        selected_date = filter_date
    else:
        activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.date.desc(), Activity.start_time.desc()).all()
        selected_date = None

    # Grouping logic for history overview if no specific date is selected
    daily_stats = db.session.query(
        Activity.date, 
        func.sum(Activity.duration_minutes)
    ).filter_by(user_id=current_user.id).group_by(Activity.date).order_by(Activity.date.desc()).all()

    return render_template('history.html', activities=activities, daily_stats=daily_stats, selected_date=selected_date)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
