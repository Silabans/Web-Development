from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import SessionLocal
from models import User, Task
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super-secret-app-do-not-share"
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

        db_session = SessionLocal()
        user = db_session.query(User).filter_by(username=username).first()

        if user:
            if user.password == password:
                session['user_id'] = user.id
                db_session.close()
                #print(f"Welcome back, {username}!")
                return redirect(url_for('dashboard'))
        
        db_session.close()
        return """Invalid credentials!
        Note: if you've never created an account before click 'Register' down below!""" 
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
            
            new_user = User(username=username, password=password)
            
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
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    # gets the user id of the current user
    
    content = request.form.get("content")
    priority = request.form.get("priority")
    due_date = request.form.get("due_date")
    if not content:
        return "Task content cannot be empty!", 400
    
    with SessionLocal() as db_session:
        try:
            new_task = Task(content=content, priority=int(priority) if priority else 1, due_date=due_date, user_id=user_id)
            
            db_session.add(new_task)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            return f"An error occurred: {e}"
    
    return redirect(url_for('dashboard'))

@app.route('/delete_task/<int:task_id>', methods=["POST"])
def delete_task(task_id):

    with SessionLocal() as db_session:
        task_to_delete = db_session.get(Task, task_id)
        try:
            db_session.delete(task_to_delete)
            db_session.commit()
            return redirect(url_for('dashboard'))
        except Exception as e:
            return f"There was a problem in deleting the task: {e}"
        
    
@app.route('/update_task/<int:task_id>', methods=["POST"])
def update_task(task_id):
    with SessionLocal() as db_session:
        task = db_session.get(Task, task_id)
        try:
            if task:
                task.isCompleted = not task.isCompleted
                db_session.commit()
        except Exception as e:
            return f"Something went wrong: {e}"
        
        return redirect(url_for('dashboard'))



@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    if 'user_id' not in session:
        return(redirect(url_for('login')))
    
    user_id = session['user_id']

    with SessionLocal() as local_session:
        # makes a query to the database of the task class of the current session, 
        # returning all task objects associated with the user_id
        tasks = local_session.query(Task).filter_by(user_id=user_id).all()
        return render_template('dashboard.html', tasks=tasks)

@app.route('/logout')
def logout():
    """Logs user out to ensure data privacy and prevent data collection."""
    session.pop('user_id', None)
    return redirect(url_for('login'))


#@app.route('complete-task/<int:task-id>')


if __name__ == "__main__":
    app.run(debug=True)