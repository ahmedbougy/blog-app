import pytest
from app import app, db, User, Post

@pytest.fixture(autouse=True)
def clean_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app.test_client()

def test_user_password_hashing():
    with app.app_context():
        # 1. إنشاء مستخدم
        user = User(username="ahmed_test")
        user.set_password("secret123")
        
        # 2. حفظه في قاعدة البيانات الوهمية
        db.session.add(user)
        db.session.commit()
        
        # 3. البحث عنه
        found_user = User.query.filter_by(username="ahmed_test").first()
        
        # 4. التحقق
        assert found_user is not None
        assert found_user.username == "ahmed_test"
        assert found_user.password != "secret123"  # يجب أن تكون مشفرة!
        assert found_user.check_password("secret123") is True
        assert found_user.check_password("wrongpassword") is False

def test_post_creation():
    with app.app_context():
        # 1. إنشاء مستخدم
        user = User(username="poster")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()
        
        # 2. إنشاء مقال
        post = Post(title="My Test Post", content="This is a test content", user_id=user.id)
        db.session.add(post)
        db.session.commit()
        
        # 3. البحث عن المقال
        found_post = Post.query.filter_by(title="My Test Post").first()
        
        # 4. التحقق
        assert found_post is not None
        assert found_post.title == "My Test Post"
        assert found_post.content == "This is a test content"
        assert found_post.user_id == user.id
        
        # 5. التحقق من العلاقة
        assert found_post.author.username == "poster"
        assert user.posts[0].title == "My Test Post"

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'My Blog Posts' in response.data

def test_register(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'newpass123'
    }, follow_redirects=True)
    assert response.status_code == 200
    # بعد التسجيل، يجب أن يوجهنا لصفحة تسجيل الدخول
    assert b'Login' in response.data

def test_login(client):
    # 1. إنشاء مستخدم أولاً (في قاعدة البيانات الوهمية)
    with app.app_context():
        user = User(username="loginuser")
        user.set_password("loginpass")
        db.session.add(user)
        db.session.commit()
    
    # 2. محاولة تسجيل الدخول
    response = client.post('/login', data={
        'username': 'loginuser',
        'password': 'loginpass'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # بعد تسجيل الدخول، يجب أن يوجهنا للـ Dashboard
    assert b'Welcome' in response.data or b'Dashboard' in response.data

def test_create_post(client):
    # 1. إنشاء مستخدم وتسجيل الدخول
    with app.app_context():
        user = User(username="poster2")
        user.set_password("posterpass")
        db.session.add(user)
        db.session.commit()
    
    client.post('/login', data={'username': 'poster2', 'password': 'posterpass'})
    
    # 2. إنشاء مقال
    response = client.post('/create', data={
        'title': 'Test Post from Route',
        'content': 'This is content.'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Test Post from Route' in response.data