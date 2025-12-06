from flask import Flask, request, jsonify
try:
    from flask_cors import CORS as _FlaskCORS
    def CORS(app):
        _FlaskCORS(app)
        return None
except Exception:
    # Minimal fallback if flask_cors isn't installed: set permissive CORS headers
    def CORS(app):
        @app.after_request
        def _cors_response(response):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
            return response
        return None

import requests
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = "tinyllama"

def send_to_ollama(log_text, analysis_type):
    prompts = {
        "apache": "Analyse the following Apache/Nginx logs and provide the summary of overall health status, critical errors, pod/container issues, resource problems, and network/connectivity errors. Categorize the findings.",
        "linux": "Analyse the following RAW Linux system logs and provide the summary of overall health status, critical errors, hardware issues, resource problems, and security alerts. Categorize the findings.",
        "kubernetes": "Analyse the following RAW Kubernetes cluster logs and provide the summary of overall health status, critical errors, pod/container issues, resource problems, and network/connectivity errors. Categorize the findings."
    }
    
    prompt = f"{prompts.get(analysis_type, prompts['apache'])}\n\n{log_text}"
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=300
        )
        response.raise_for_status()
        return response.json().get("response", "No output returned")
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Ollama: {str(e)}"

@app.route('/api/analyze', methods=['POST'])
def analyze_logs():
    try:
        data = request.get_json(silent=True) or {}
        log_text = data.get('log_text', '')
        analysis_type = data.get('analysis_type', 'apache')
        
        if not log_text:
            return jsonify({'error': 'No log text provided'}), 400
        
        analysis = send_to_ollama(log_text, analysis_type)
        
        result = {
            'analysis': analysis,
            'analysis_type': analysis_type,
            'timestamp': datetime.now().isoformat(),
            'log_size': len(log_text)
        }
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-file', methods=['POST'])
def analyze_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        analysis_type = request.form.get('analysis_type', 'apache')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        log_text = file.read().decode('utf-8', errors='ignore')
        analysis = send_to_ollama(log_text, analysis_type)
        
        result = {
            'analysis': analysis,
            'analysis_type': analysis_type,
            'filename': file.filename,
            'timestamp': datetime.now().isoformat(),
            'log_size': len(log_text)
        }
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)