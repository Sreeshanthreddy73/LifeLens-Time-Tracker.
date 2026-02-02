import os
from datetime import datetime, time, date, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

from models import db, User, Activity

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lifelens-secret-key-12345'

# Robust DB detection for Vercel/Production
db_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    # On Vercel, only /tmp is writable. Use it for local SQLite to avoid crashes.
    is_vercel = os.environ.get('VERCEL') == '1'
    if is_vercel:
        db_path = os.path.join('/tmp', 'lifelens.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lifelens.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/init-db')
def init_db():
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    masked_uri = uri.split('@')[-1] if '@' in uri else uri
    try:
        with app.app_context():
            # WARNING: This deletes all data! Needed to resize the password column.
            db.drop_all()
            db.create_all()
        return f"Database Reset Success! Tables dropped and recreated.<br>Using: {masked_uri}<br><a href='/register'>Go to Register</a>"
    except Exception as e:
        return f"Database Error!<br>Error: {str(e)}<br>Using URI: {masked_uri}<br>Double check your Vercel Storage settings."

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@app.errorhandler(500)
def internal_error(error):
    import traceback
    return f"<pre>{traceback.format_exc()}</pre>", 500

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
            flash('Invalid email or password.', 'danger')
            
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
    
    today_date = today.strftime('%B %d, %Y')
    today_val = today.strftime('%Y-%m-%d')
    
    # Simple Streak Calc for Header (Optional)
    current_streak = 0
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

    return render_template('dashboard.html', 
                           activities=activities, 
                           total_min=total_min,
                           productive_min=productive_min,
                           neutral_min=neutral_min,
                           waste_min=waste_min,
                           prod_percent=round(prod_percent, 1),
                           today_date=today_date,
                           today_val=today_val,
                           streak=current_streak)

@app.route('/add_activity_page')
@login_required
def add_activity_page():
    today = date.today()
    today_val = today.strftime('%Y-%m-%d')
    activities = Activity.query.filter_by(user_id=current_user.id, date=today).all()
    return render_template('add_activity.html', today_val=today_val, activities=activities)

@app.route('/reports')
@login_required
def reports():
    today = date.today()
    today_date = today.strftime('%B %d, %Y')
    
    # Last 7 Days Data for Distribution to make it more of a "Report"
    last_7_days_activities = Activity.query.filter(
        Activity.user_id == current_user.id,
        Activity.date >= today - timedelta(days=6)
    ).all()
    
    # Weekly Trend Logic
    last_7_days_data = []
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

    # Distribution based on Today (to match original) or 7 Days? 
    # Let's stick to Today for now to ensure consistency with what the user expects from "moving" the charts.
    todays_activities = Activity.query.filter_by(user_id=current_user.id, date=today).all()
    prod_min = sum(a.duration_minutes for a in todays_activities if a.category == 'productive')
    neutral_min = sum(a.duration_minutes for a in todays_activities if a.category == 'neutral')
    waste_min = sum(a.duration_minutes for a in todays_activities if a.category == 'waste')
    
    chart_data = {
        'labels': ['Productive', 'Neutral', 'Waste'],
        'values': [prod_min, neutral_min, waste_min]
    }
    
    # Waste Insight
    yearly_waste_hrs = (waste_min * 365) / 60
    total_waste_days = yearly_waste_hrs / 24

    return render_template('reports.html',
                           today_date=today_date,
                           chart_data=chart_data,
                           weekly_trend=last_7_days_data,
                           waste_min=waste_min,
                           yearly_waste_hrs=round(yearly_waste_hrs, 1),
                           total_waste_days=round(total_waste_days, 1))

@app.route('/achievements')
@login_required
def achievements():
    today = date.today()
    current_streak = 0
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
            
    total_productive_min = db.session.query(func.sum(Activity.duration_minutes)).filter_by(user_id=current_user.id, category='productive').scalar() or 0
    total_entries = Activity.query.filter_by(user_id=current_user.id).count()
    
    achievements_list = []
    if current_streak >= 3: achievements_list.append({'icon': '🔥', 'title': 'Consistency King', 'desc': '3+ Day Streak'})
    if total_productive_min >= 600: achievements_list.append({'icon': '🥈', 'title': 'Deep Worker', 'desc': '10hrs Productive'})
    if total_productive_min >= 3000: achievements_list.append({'icon': '🥇', 'title': 'Time Lord', 'desc': '50hrs Productive'})
    if total_entries >= 50: achievements_list.append({'icon': '📊', 'title': 'Data Collector', 'desc': '50 Logs Added'})
    
    return render_template('achievements.html', achievements=achievements_list)

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
    search_query = request.args.get('search')
    
    query = Activity.query.filter_by(user_id=current_user.id)
    
    if filter_date_str:
        filter_date = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
        query = query.filter_by(date=filter_date)
        selected_date = filter_date
    else:
        selected_date = None
        
    if search_query:
        query = query.filter(Activity.name.ilike(f'%{search_query}%'))

    activities = query.order_by(Activity.date.desc(), Activity.start_time.desc()).all()

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
