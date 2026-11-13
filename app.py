from flask import Flask , render_template_string , request , url_for , redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash , check_password_hash 
from sqlalchemy.exc import IntegrityError
import os 

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR,'blog.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my-super-secret-key-change-me'

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
     # بناء صفحة HTML بسيطة
    html = "<h1>My Blog</h1>"
    html += "<p><a href='/login'>Login</a> | <a href='/register'>Register</a></p>"
    
    for post in posts:
        html += f"<hr>"
        html += f"<h2>{post.title}</h2>"
        html += f"<p>{post.content}</p>"
        html += f"<small>By: {post.author.username}</small>"
        if current_user.is_authenticated and current_user.id == post.user_id :
            html += f"<a href='/delete/{post.id}'>Delete</a>"
            html += f"<a href='/edit/{post.id}'>Edit</a>"
    return html

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

            return f"User {username} registered successfully!"
        
        except IntegrityError:
            db.session.rollback()
            return f"Error: Username '{username}' already exists!"

    return render_template_string('''
        <h1>Register</h1>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Register</button>
        </form>
    ''')

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
            return 'Invalid username or password!'

    return render_template_string('''
        <h1>Login</h1>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <p><a href="/register">Don't have an account? Register here.</a></p>
    ''')

@app.route('/dashboard')
@login_required
def dashboard():
    return f"""
        <h1>Welcome, {current_user.username}!</h1>
        <p><a href="/create">Write a New Post</a></p>
        <p><a href="/logout">Logout</a></p>
    """

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

    return render_template_string('''
        <h1>Create a New Post</h1>
        <form method="POST">
            <input type="text" name="title" placeholder="Post Title" required><br><br>
            <textarea name="content" placeholder="Write your content here..." rows="5" cols="40" required></textarea><br><br>
            <button type="submit">Publish</button>
        </form>
        <p><a href="/">Back to Dashboard</a></p>    
''')

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
    return render_template_string(f'''
        <h1>Edit Post</h1>
        <form method="POST">
            <input type="text" name="title" value="{post.title}" required><br><br>
            <textarea name="content" rows="5" required>{post.content}</textarea><br><br>
            <button type="submit">Update</button>
        </form>
        <p><a href="/">Cancel</a></p>
    ''')
if __name__ == '__main__' :
    with app.app_context():
        db.create_all()
    app.run(debug=True)