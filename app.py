# app.py - The main brain of CyberNews

from flask import Flask, render_template

# Create the Flask application
app = Flask(__name__)

# This is a "route" - it tells Flask what to do when someone visits "/"
# "/" means the homepage (e.g., http://your-ip/)
@app.route('/')
def home():
    return render_template('index.html')

# Only runs this block if we execute app.py directly
if __name__ == '__main__':
    # host='0.0.0.0' means "accept connections from anywhere"
    # This lets your friends reach it (temporarily - we'll use Nginx later)
    app.run(host='0.0.0.0', port=5000, debug=True)
