# create_db.py
from apps import create_app, db
from apps.config import Config  # 혹은 너가 사용하는 config 클래스

app = create_app(Config)

with app.app_context():
    db.create_all()
    print("✅ Tables created successfully.")
