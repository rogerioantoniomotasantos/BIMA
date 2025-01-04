# app.py
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
from main import process_gltf_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Process GLTF file
        process_gltf_file(file_path, app.config['OUTPUT_FOLDER'])

        # Paths for output files
        ifc_path = os.path.join(app.config['OUTPUT_FOLDER'], "MultiElementIfc.ifc")
        excel_path = os.path.join(app.config['OUTPUT_FOLDER'], "assigned_parameters.xlsx")

        return render_template('download.html', ifc_file="MultiElementIfc.ifc", excel_file="assigned_parameters.xlsx")

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
