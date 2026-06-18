import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
from werkzeug.utils import secure_filename
import database
import career_engine

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'career_guidance_chatbot_super_secret_key_987654')

# File Upload Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB max limit

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
database.init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Authentication Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    # Fetch user data
    user = database.get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    return render_template('index.html', user=user, quiz_questions=career_engine.QUIZ_QUESTIONS)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
            
        user_id = database.register_user(username, email, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            flash('Registration successful! Welcome.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Username or Email already exists.', 'danger')
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('login.html')
            
        user = database.check_user_credentials(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- API ROUTES ---

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"status": "error", "message": "Missing message content."}), 400
        
    user_message = data['message'].strip()
    user_id = session['user_id']
    
    if not user_message:
        return jsonify({"status": "error", "message": "Empty message."}), 400
        
    # Save user message to database
    database.save_chat_message(user_id, 'user', user_message)
    
    # Get Career Guidance Bot response with history context for Groq
    user_history = database.get_chat_history(user_id)
    bot_response = career_engine.get_chat_response(user_message, history=user_history)
    
    # Save bot response to database
    database.save_chat_message(user_id, 'bot', bot_response)
    
    return jsonify({
        "status": "success",
        "response": bot_response
    })

@app.route('/api/history', methods=['GET'])
@login_required
def api_history():
    user_id = session['user_id']
    history = database.get_chat_history(user_id)
    return jsonify({
        "status": "success",
        "history": history
    })

@app.route('/api/clear_history', methods=['POST'])
@login_required
def api_clear_history():
    user_id = session['user_id']
    database.clear_chat_history(user_id)
    return jsonify({
        "status": "success",
        "message": "Chat history cleared successfully."
    })

@app.route('/api/upload_resume', methods=['POST'])
@login_required
def api_upload_resume():
    if 'resume' not in request.files:
        return jsonify({"status": "error", "message": "No file part in request."}), 400
        
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No file selected."}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Unique name to prevent conflicts
        temp_filename = f"user_{session['user_id']}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        
        try:
            file.save(file_path)
            # Run analysis
            analysis = career_engine.analyze_resume(file_path)
            
            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
                
            if "error" in analysis:
                return jsonify({"status": "error", "message": analysis["error"]}), 400
                
            return jsonify({
                "status": "success",
                "analysis": analysis
            })
        except Exception as e:
            # Clean up in case of crash
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({"status": "error", "message": f"Server error processing resume: {str(e)}"}), 500
            
    return jsonify({"status": "error", "message": "Invalid file format. Only .txt and .pdf are allowed."}), 400

@app.route('/api/quiz', methods=['POST'])
@login_required
def api_quiz():
    data = request.get_json()
    if not data or 'answers' not in data:
        return jsonify({"status": "error", "message": "Missing answers data."}), 400
        
    answers = data['answers']
    user_id = session['user_id']
    
    # Evaluate answers
    recommended_career_key, scores = career_engine.evaluate_quiz(answers)
    recommended_career_title = career_engine.CAREER_DATA[recommended_career_key]['title']
    
    # Save to Database
    scores_json = json.dumps(scores)
    result_id = database.save_quiz_result(user_id, recommended_career_title, scores_json)
    
    return jsonify({
        "status": "success",
        "result_id": result_id,
        "recommended_career": recommended_career_title,
        "career_key": recommended_career_key,
        "scores": scores
    })

@app.route('/report/<int:result_id>')
@login_required
def view_report(result_id):
    result = database.get_quiz_result_by_id(result_id)
    if not result:
        flash("Report not found.", "danger")
        return redirect(url_for('index'))
        
    # Security check: Ensure the report belongs to the logged-in user
    if result['user_id'] != session['user_id']:
        flash("You are not authorized to view this report.", "danger")
        return redirect(url_for('index'))
        
    # Determine the career key from the recommended career title
    career_key = None
    for k, v in career_engine.CAREER_DATA.items():
        if v['title'] == result['recommended_career']:
            career_key = k
            break
            
    # Fallback to software developer if key not found
    if not career_key:
        career_key = 'software_developer'
        
    career_details = career_engine.CAREER_DATA[career_key]
    scores = json.loads(result['scores'])
    
    # Calculate percentage for progress bars
    max_possible_score = 24  # Max potential score across quiz dimensions
    formatted_scores = {}
    for title_key, score_val in scores.items():
        title_label = career_engine.CAREER_DATA[title_key]['title']
        # Normalize score percentage
        percentage = min(int((score_val / 15) * 100), 100) # 15 is reasonable max quiz score per career
        formatted_scores[title_label] = percentage

    return render_template(
        'report.html', 
        result=result, 
        career_details=career_details, 
        scores=formatted_scores
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
