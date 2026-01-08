"""
Simple Flask server to serve the Vanilla JS dashboard on Heroku.
"""
from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='vanilla-js-app')

@app.route('/')
def index():
    """Serve the main index.html"""
    return send_from_directory('vanilla-js-app', 'index.html')

@app.route('/<path:path>')
def serve_file(path):
    """Serve all other static files (JS, CSS, JSON, etc.)"""
    return send_from_directory('vanilla-js-app', path)

if __name__ == '__main__':
    # Get port from environment variable (Heroku sets this)
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)

