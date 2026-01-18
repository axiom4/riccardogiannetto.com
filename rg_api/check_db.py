import os
import django
import sys

# Set up Django environment manually since we are not using manage.py directly
# But wait, I can just use manage.py shell if I pass the command into stdin or use a dedicated script.

def check_db():
    try:
        from analytics.models import UserSession
        print(f"UserSession count: {UserSession.objects.count()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
