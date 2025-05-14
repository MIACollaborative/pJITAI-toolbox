# create_db.py
# Only use this if mysql db is not created using setup.sh
# 1) Try, source setup.sh -> 2) If it doesn't work then, python create_db.py -> 3) Check shether db has been created
# In most cases, ./setup.sh will successfully create MySQL db.
from apps import create_app, db
from apps.config import Config

app = create_app(Config)

with app.app_context():
    db.create_all()
    print("✅ Tables created successfully.")
