import os
import sqlite3
import uuid
import zipfile
import shutil
import random
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import io
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # just for flash messages
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOAD_DIR = os.path.join(DATA_DIR, 'uploads')
DB_PATH = os.path.join(DATA_DIR, 'app.db')

os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS files (
            file_id TEXT PRIMARY KEY,
            file_path TEXT NOT NULL,
            title TEXT NOT NULL,
            last_viewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    files = conn.execute('SELECT * FROM files').fetchall()
    conn.close()
    ads = random.sample(['img1.png', 'img2.png', 'img3.png', 'img4.png'], 2)
    return render_template('index.html', files=files, ads=ads)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    title = request.form.get('title', file.filename)
    file_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    file_path = os.path.join('uploads', f"{file_id}_{filename}")
    full_path = os.path.join(DATA_DIR, file_path)
    
    file.save(full_path)
    
    conn = get_db_connection()
    conn.execute('INSERT INTO files (file_id, file_path, title) VALUES (?, ?, ?)', (file_id, file_path, title))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

def do_read(file_id):
    conn = get_db_connection()
    file_record = conn.execute('SELECT file_path FROM files WHERE file_id = ?', (file_id,)).fetchone()
    conn.close()
    
    if not file_record:
        return "File not found in DB (do_read)", 404
        
    full_path = os.path.join(DATA_DIR, file_record['file_path'])
    try:
        return send_file(full_path)
    except Exception as e:
        return f"Error reading file: {str(e)}", 500

@app.route('/read/<file_id>')
def read_file(file_id):
    conn = get_db_connection()
    file_record = conn.execute('SELECT file_path FROM files WHERE file_id = ?', (file_id,)).fetchone()
    
    if not file_record:
        conn.close()
        return "File not found", 404
        
    file_path = file_record['file_path']
    full_path = os.path.abspath(os.path.join(DATA_DIR, file_path))
    
    if not full_path.startswith(os.path.abspath(UPLOAD_DIR) + '/'):
        conn.close()
        return "Path traversal detected!", 403

    conn.execute('UPDATE files SET last_viewed = CURRENT_TIMESTAMP WHERE file_id = ?', (file_id,))
    conn.commit()
    conn.close()
    
    return do_read(file_id)

@app.route('/export')
def export_state():
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        if os.path.exists(DB_PATH):
            zf.write(DB_PATH, 'app.db')
        for root, _, files in os.walk(UPLOAD_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, DATA_DIR)
                zf.write(file_path, arcname)
                
    memory_file.seek(0)
    return send_file(memory_file, download_name='state.zip', as_attachment=True)

@app.route('/import', methods=['POST'])
def import_state():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
        
    if file:
        data_dir_abs = os.path.abspath(DATA_DIR)
        try:
            with zipfile.ZipFile(file, 'r') as zf:
                for member in zf.infolist():
                    member_path = os.path.abspath(
                        os.path.join(data_dir_abs, member.filename)
                    )
                    if not member_path.startswith(data_dir_abs + os.sep):
                        flash('Invalid zip: path traversal detected')
                        return redirect(url_for('index'))

                if os.path.exists(DB_PATH):
                    os.remove(DB_PATH)
                if os.path.exists(UPLOAD_DIR):
                    shutil.rmtree(UPLOAD_DIR)
                os.makedirs(UPLOAD_DIR, exist_ok=True)

                zf.extractall(data_dir_abs)
        except zipfile.BadZipFile:
            flash('Invalid zip file')
            return redirect(url_for('index'))

        flash('Imported successfully')
        return redirect(url_for('index'))

