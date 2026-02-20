#!/usr/bin/env python3
"""
AudioGuide GUI Backend
Flask server for web-based AudioGuide interface
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

# Add AudioGuide to path
audioguide_path = Path(__file__).parent.parent
sys.path.insert(0, str(audioguide_path))

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Configuration
UPLOAD_FOLDER = tempfile.mkdtemp(prefix='audioguide_')
OUTPUT_FOLDER = tempfile.mkdtemp(prefix='audioguide_output_')
ALLOWED_EXTENSIONS = {'wav', 'aiff', 'aif', 'mp3', 'flac', 'ogg', 'm4a'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_audioguide_script(project_data, target_path, corpus_dir, output_path):
    """Generate AudioGuide Python script from GUI settings"""
    
    script_content = f'''#!/usr/bin/env python3
"""
Auto-generated AudioGuide script from GUI
Project: {project_data['name']}
"""

import sys
from pathlib import Path

# Add AudioGuide to path
sys.path.insert(0, r"{audioguide_path}")

# Import AudioGuide modules
from audioguide import defaults, targetfile, corpusfile, concatenate
from audioguide.defaults import *

# Project Configuration
TARGET = targetfile(
    r"{target_path}",
    thresh=-35,
    offsetRise=0.05,
    minSegLen=0.1
)

CORPUS = [
    corpusfile(
        r"{corpus_dir}",
        wholeFile=True,
        normalize=False
    )
]

# Output Configuration
OUTPUT_NAME = r"{output_path}/{project_data['output']['name']}"

# Spectral Reconstruction Settings
'''

    # Add spectral reconstruction settings if enabled
    if project_data['settings']['useSpectral']:
        script_content += f'''
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = {project_data['settings']['wholeFile']}
ENABLE_SPECTRAL_VOLUMEENV = {project_data['settings']['volumeAutomation']}
SPECTRAL_MAX_PARTIALS = {project_data['settings']['maxPartials']}
SPECTRAL_TOLERANCE_CENTS = {project_data['settings']['toleranceCents']}
SPECTRAL_MIN_AMPLITUDE_RATIO = {project_data['settings']['minAmplitude']}
'''

    # Add output format configuration
    output_format = project_data['output']['format']
    if output_format == 'rpp':
        script_content += '''
OUTPUT_RPP = OUTPUT_NAME + ".rpp"
OUTPUT_AUDIO = OUTPUT_NAME + ".wav"
'''
    elif output_format == 'aaf':
        script_content += '''
OUTPUT_AAF = OUTPUT_NAME + ".aaf"
OUTPUT_AUDIO = OUTPUT_NAME + ".wav"
'''
    elif output_format == 'csound':
        script_content += '''
OUTPUT_CSOUND = OUTPUT_NAME + ".csd"
RENDER_CSOUND = True
'''
    elif output_format == 'json':
        script_content += '''
OUTPUT_JSON = OUTPUT_NAME + ".json"
'''

    script_content += '''

# Run AudioGuide
if __name__ == "__main__":
    concatenate()
    print("AudioGuide processing complete!")
'''

    return script_content

@app.route('/')
def index():
    """Serve main GUI page"""
    return render_template('index.html')

@app.route('/run-audioguide', methods=['POST'])
def run_audioguide():
    """Execute AudioGuide with uploaded files and settings"""
    
    try:
        # Get project data
        project_data = json.loads(request.form.get('settings'))
        output_data = json.loads(request.form.get('output'))
        
        # Combine data
        full_project_data = {
            'name': request.form.get('projectName'),
            'settings': project_data,
            'output': output_data
        }
        
        # Handle target file
        target_file = request.files.get('targetFile')
        if not target_file or not allowed_file(target_file.filename):
            return jsonify({'success': False, 'error': 'Invalid target file'})
        
        target_filename = secure_filename(target_file.filename)
        target_path = os.path.join(app.config['UPLOAD_FOLDER'], target_filename)
        target_file.save(target_path)
        
        # Handle corpus files
        corpus_files = request.files.getlist('corpusFiles')
        if not corpus_files:
            return jsonify({'success': False, 'error': 'No corpus files provided'})
        
        # Create corpus directory
        corpus_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'corpus')
        os.makedirs(corpus_dir, exist_ok=True)
        
        # Save corpus files
        corpus_count = 0
        for corpus_file in corpus_files:
            if corpus_file and allowed_file(corpus_file.filename):
                corpus_filename = secure_filename(corpus_file.filename)
                corpus_path = os.path.join(corpus_dir, corpus_filename)
                corpus_file.save(corpus_path)
                corpus_count += 1
        
        if corpus_count == 0:
            return jsonify({'success': False, 'error': 'No valid corpus files found'})
        
        # Create output directory
        project_output_dir = os.path.join(app.config['OUTPUT_FOLDER'], 
                                        secure_filename(full_project_data['name']))
        os.makedirs(project_output_dir, exist_ok=True)
        
        # Generate AudioGuide script
        script_content = create_audioguide_script(
            full_project_data, 
            target_path, 
            corpus_dir, 
            project_output_dir
        )
        
        script_path = os.path.join(app.config['UPLOAD_FOLDER'], 'run_audioguide.py')
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Execute AudioGuide
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=app.config['UPLOAD_FOLDER']
            )
            
            if result.returncode != 0:
                return jsonify({
                    'success': False, 
                    'error': f'AudioGuide execution failed: {result.stderr}'
                })
            
            # Parse output for results
            output_lines = result.stdout.strip().split('\n')
            
            # Find generated files
            generated_files = []
            output_format = full_project_data['output']['format']
            base_name = full_project_data['output']['name']
            
            if output_format == 'rpp':
                rpp_file = os.path.join(project_output_dir, f"{base_name}.rpp")
                wav_file = os.path.join(project_output_dir, f"{base_name}.wav")
                
                if os.path.exists(rpp_file):
                    generated_files.append({
                        'filename': f"{base_name}.rpp",
                        'displayName': 'Reaper Project',
                        'path': rpp_file
                    })
                if os.path.exists(wav_file):
                    generated_files.append({
                        'filename': f"{base_name}.wav", 
                        'displayName': 'Audio File',
                        'path': wav_file
                    })
            
            # Return success with file list
            return jsonify({
                'success': True,
                'duration': '0.0',  # Would need to parse from AudioGuide output
                'segments': '0',    # Would need to parse from AudioGuide output
                'events': '0',      # Would need to parse from AudioGuide output
                'corpusFiles': str(corpus_count),
                'files': generated_files
            })
            
        except subprocess.TimeoutExpired:
            return jsonify({'success': False, 'error': 'Processing timeout (5 minutes)'})
        except Exception as e:
            return jsonify({'success': False, 'error': f'Execution error: {str(e)}'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated files"""
    try:
        # Search for file in output directories
        for root, dirs, files in os.walk(app.config['OUTPUT_FOLDER']):
            if filename in files:
                file_path = os.path.join(root, filename)
                return send_file(file_path, as_attachment=True)
        
        return jsonify({'error': 'File not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'version': '1.0.0'})

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'success': False, 'error': 'File too large (max 500MB)'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🎵 AudioGuide GUI Server")
    print("=" * 40)
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Output folder: {OUTPUT_FOLDER}")
    print("Open http://localhost:5000 in your browser")
    print("=" * 40)
    
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    # Copy index.html to templates if needed
    index_template = templates_dir / 'index.html'
    index_source = Path(__file__).parent / 'static' / 'index.html'
    if not index_template.exists() and index_source.exists():
        shutil.copy2(index_source, index_template)
    
    app.run(host='0.0.0.0', port=5000, debug=True)