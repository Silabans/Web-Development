from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from sqlalchemy import desc
from database import SessionLocal
from models import User, Task
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from analytics import build_dataframe, chart_priority, chart_week
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-dev-fallback")
# converts the key-value pair of user_id in 'session' into a scrambled string (a cookie),
# which acts as an encrypted code to identify users with within their session.

@app.route('/')
def home():
    return  render_template('index.html')

@app.route('/status')
def status():
    return "<h2>All systems are operational.</h2>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method ==  'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        with SessionLocal() as db_session:
            user = db_session.query(User).filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                db_session.close()
                flash(f"Welcome back {username}!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Passwords do not match", "error")
                return "Invalid credentials!\nNote: if you've never created an account before click 'Register' down below!"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        if password != confirm_password:
            return "Passwords do not match"
        
        with SessionLocal() as db_session:
            user_exists = db_session.query(User).filter_by(username=username).first()
            if user_exists:
                db_session.close()
                return "Username already taken!"
            
            new_user = User(
                username=username,
                password=generate_password_hash(password, method='pbkdf2:sha256'))
            
            try:
                db_session.add(new_user)
                db_session.commit()
                return redirect(url_for('login'))
            except Exception as e:
                db_session.rollback()
                return f"An error occurred: {e}"
    
    return render_template("register.html")


@app.route('/add', methods=["POST"])
def add_task():
    if 'user_id' not in session:
        return jsonify({"error": "Not found"}), 403
    
    user_id = session.get('user_id')
    # gets the user id of the current user
    
    content = request.form.get("content")
    priority = request.form.get("priority")
    due_date_str = request.form.get("due_date")
    due_date = date.fromisoformat(due_date_str) if due_date_str else None
    created_at = date.today()
    if not content:
        return jsonify({"error": "Content cannot be empty!"}), 400
    
    with SessionLocal() as db_session:
        try:
            new_task = Task(content=content, priority=int(priority) if priority else 1, due_date=due_date, created_at=created_at, user_id=user_id)
            db_session.add(new_task)
            db_session.commit()
            return jsonify({
                "success": True,
                "id": new_task.id,
                "content": new_task.content,
                "priority": new_task.priority,
                "dueDate": str(new_task.due_date) if new_task.due_date else None,
                "isOverdue": False
            })
        except Exception as e:
            db_session.rollback()
            return jsonify({"error": str(e)}), 500
    
    return redirect(url_for('dashboard'))

@app.route('/edit_task/<int:task_id>', methods=["POST"])
def edit_task(task_id):
    if "user_id" not in session:
        return jsonify({"error": "Not found"}), 404
    
    content = request.form.get("content")
    priority = request.form.get("priority")
    due_date_str = request.form.get("due_date")
    # converts the date from isoformat string to an actual datetime object
    due_date = date.fromisoformat(due_date_str) if due_date_str else None

    with SessionLocal() as db_session:
        # This ensures that the task retrieved is owned by the user by ensuring that user_id matches
        # the id logged into the session.
        task = db_session.query(Task).filter_by(id=task_id, user_id=session['user_id']).first()

        # If the task does not exist or if it does not belong to the user (checked using user_id),
        # inform the user about unauthorized access / task not found.
        if not task:
            return jsonify({"error": "Not found or unauthorized"}), 403
        try:
            task.content = content
            task.priority = priority
            task.due_date = due_date
            db_session.commit()
            return jsonify({
                "success": True, 
                "content": task.content, 
                "priority": task.priority, 
                "dueDate": "| Due Date: " + str(task.due_date) if task.due_date else 'Unspecified',
                "isOverdue": task.due_date and task.due_date < date.today()
                })
        except Exception as e:
            db_session.rollback()
            return jsonify({"error": str(e)}), 403     


@app.route('/delete_task/<int:task_id>', methods=["POST"])
def delete_task(task_id):
    if 'user_id' not in session:
        return jsonify({"error": "Not found"}), 404

    with SessionLocal() as db_session:
        task = db_session.query(Task).filter_by(id=task_id, user_id=session['user_id']).first()
        if not task:
            return jsonify({"error":"Not found or unauthorized"}), 403
        try:
            db_session.delete(task)
            db_session.commit()
            return jsonify({"success": True, "task_id": task_id})
        except Exception as e:
            db_session.rollback()
            return jsonify({"error": str(e)}), 500
        
    
@app.route('/update_task/<int:task_id>', methods=["POST"])
def update_task(task_id):
    if 'user_id' not in session:
        return jsonify({"error": "Not found"}), 404

    with SessionLocal() as db_session:
        task = db_session.query(Task).filter_by(id=task_id, user_id=session['user_id']).first()
        if not task:
            return jsonify({ "error": "Not found or unauthorized" }), 403
        try:
            if task:
                task.isCompleted = not task.isCompleted
                db_session.commit()
                return jsonify({"success": True, "isCompleted": task.isCompleted})
        except Exception as e:
            db_session.rollback()
            return jsonify({"error": str(e)}), 500
        
        

@app.route('/update_last_timer', methods=["POST"])
def update_timer_pref():
    if 'user_id' not in session:
        return "Unauthorized", 401
    
    new_pref = request.json.get('minutes')
    user_id = session['user_id']

    with SessionLocal() as db_session:
        user = db_session.query(User).filter_by(id=user_id).first()
        if user:
            user.last_timer = new_pref
            db_session.commit()
    return "Success", 200

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    if 'user_id' not in session:
        return(redirect(url_for('login')))
    
    user_id = session['user_id']

    with SessionLocal() as db_session:
        # makes a query to the database of the task class of the current session, 
        # returning all task objects associated with the user_id
        today = date.today()
        tasks = db_session.query(Task).filter_by(user_id=user_id).order_by(Task.isCompleted, desc(Task.priority), Task.due_date.nulls_last(), desc(Task.id)).all()
        user = db_session.query(User).filter_by(id=user_id).first()

        for task in tasks:
            task.is_overdue = task.due_date and task.due_date < today

        return render_template('dashboard.html', tasks=tasks, user=user, today=today)

@app.route('/logout')
def logout():
    """Logs user out to ensure data privacy and prevent data collection."""
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    with SessionLocal() as db_session:
        tasks = db_session.query(Task).filter_by(user_id=user_id).all()
        df = build_dataframe(tasks)
        chart1 = chart_priority(df)
        chart2 = chart_week(df)
        return render_template('analytics.html',
                               chart_priority=chart1,
                               chart_week=chart2
                               )
    ...

if __name__ == "__main__":
    app.run(debug=True)