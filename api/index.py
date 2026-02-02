import sys
import os

# Ensure the parent directory is in the path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Vercel looks for 'app' or 'handler'
try:
    from app import app
    handler = app
except Exception as e:
    # Fallback to a simple Flask app specific for error reporting
    from flask import Flask
    import traceback
    
    app = Flask(__name__)
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return f"<h1>App Startup Error</h1><pre>{traceback.format_exc()}</pre>", 500
    
    handler = app

