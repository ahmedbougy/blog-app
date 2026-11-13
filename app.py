from flask import Flask , render_template , request , url_for , redirect , flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash , check_password_hash 
from sqlalchemy.exc import IntegrityError
import os 
from dotenv import load_dotenv
app = Flask(__name__)
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'blog.db')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-fallback-key')

if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://") :
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer , primary_key=True)
    username = db.Column(db.String(80), unique=True , nullable=False)
    password = db.Column(db.String(120) , nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref= 'posts' )

    def __repr__(self):
        return f'<Post {self.title}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        new_user = User(username=username)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()

            flash(
                'Account created successfully! You can now log in.', 'success'
            )# ستظهر فور وصوله لصفحة login
    
            return redirect(url_for('login'))  # توجيه إلى صفحة تسجيل الدخول

        except IntegrityError:
            db.session.rollback()
            flash(f"Error: Username '{username}' already exists!", 'danger')
            return redirect(url_for('register'))  # إعادة توجيه لنفس صفحة التسجيل

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else :
            flash('Invalid username or password!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        new_post = Post(title=title, content=content, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('create_post.html')

@app.route('/delete/<int:post_id>')
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id :
        return "You are not allowed to delete this post!", 403

    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/edit/<int:post_id>', methods=['GET','POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id :
        return "You are not allowed to edit this post!", 403

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        db.session.commit()
        return redirect(url_for('home'))

    # 4. إذا فتح الصفحة للتو (GET): نعرض النموذج مع تعبئة البيانات الحالية مسبقاً
    return render_template('edit_post.html', post=post)

with app.app_context():
    db.create_all()
if __name__ == '__main__' :
    app.run(debug=True)