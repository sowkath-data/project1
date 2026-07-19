from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
import os

from database import Database
from model import AttritionModel

app = Flask(__name__)
CORS(app)

db = Database()
model = AttritionModel()
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
@app.route('/predictions')
def predictions():
    return render_template('predictions.html')
if __name__ == "__main__":
   # In app.py, change the port
     app.run(debug=True, host='127.0.0.1', port=5001)
@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Get dashboard statistics"""
    return jsonify({
        'success': True,
        'stats': {
            'total_employees': 1500,
            'high_risk': 45,
            'medium_risk': 127,
            'low_risk': 1328,
            'best_model': 'Random Forest',
            'model_accuracy': 0.783
        }
    })
    