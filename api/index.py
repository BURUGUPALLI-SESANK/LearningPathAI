import sys
import os

# Add the path_generator directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'path_generator'))

# Import the Flask app
from app import app

# Vercel serverless function handler
app = app
