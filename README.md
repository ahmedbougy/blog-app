# 📝 Blog App

A full-stack blog application built with Python, Flask, and PostgreSQL. Users can register, log in, write posts, react (like/dislike), and comment on posts.

🔗 **Live Demo:** [https://blog-app-ahmed.onrender.com](https://blog-app-ahmed.onrender.com)

## Features

- **Authentication:** Secure register/login/logout (Flask-Login + password hashing).
- **Posts:** Full CRUD (Create, Read, Update, Delete) with authorization.
- **Reactions:** Like/Dislike system.
- **Comments:** Add and delete comments.
- **UI:** Modern responsive design (Glassmorphism + Particle Canvas).
- **Testing:** 6 tests covering models and routes (`pytest`).

## Tech Stack

- **Backend:** Python, Flask, SQLAlchemy, Flask-Login.
- **Database:** PostgreSQL (Production) / SQLite (Local).
- **Frontend:** HTML, CSS, Vanilla JS, Jinja2.
- **Deployment:** Render.
- **Testing:** pytest.

## Local Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/ahmedbougy/blog-app.git
   cd blog-app