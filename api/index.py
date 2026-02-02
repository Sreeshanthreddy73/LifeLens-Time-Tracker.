import sys
import os

# Ensure the parent directory is in the path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel looks for 'app' or 'handler'
handler = app
app = app
