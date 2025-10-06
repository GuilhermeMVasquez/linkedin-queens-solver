from flask import Flask, render_template, request, send_from_directory
import os
import subprocess

app = Flask(__name__, static_folder='static')

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return "No file uploaded", 400

    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Run your Python script
    subprocess.run(["python3", "queens_solver.py", filepath], check=True)

    # Expecting queens_solver.py to produce "solution.png" in the static folder
    return "success"

@app.route('/solution')
def get_solution():
    return send_from_directory('static', 'solution.png')

if __name__ == '__main__':
    app.run(debug=True)
