from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from rembg import remove
from PIL import Image as PILImage
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    images = db.relationship('Image', backref='user', lazy=True)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    processed_filename = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_images = Image.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', images=user_images)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'image' not in request.files:
        flash('No image uploaded')
        return redirect(url_for('dashboard'))
    
    file = request.files['image']
    if file.filename == '':
        flash('No image selected')
        return redirect(url_for('dashboard'))
    
    if file:
        try:
            # Save original image
            filename = f"{current_user.id}_{file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process image to remove background
            input_image = PILImage.open(filepath)
            
            # Convert image to RGB if it's in RGBA mode
            if input_image.mode == 'RGBA':
                input_image = input_image.convert('RGB')
            
            # Remove background
            output_image = remove(input_image)
            
            # Save processed image with transparent background
            processed_filename = f"processed_{filename}"
            processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
            
            # Save as PNG to preserve transparency
            output_image.save(processed_filepath, 'PNG')
            
            # Save to database
            new_image = Image(filename=filename, processed_filename=processed_filename, user_id=current_user.id)
            db.session.add(new_image)
            db.session.commit()
            
            flash('Image processed successfully!')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f'Error processing image: {str(e)}')
            return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 