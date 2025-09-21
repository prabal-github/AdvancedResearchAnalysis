from flask import Blueprint, render_template, request, jsonify
from options_chain.services import get_options_chain_data, analyze_options_data
from options_chain.ml.pipelines.inference_pipeline import run_inference_pipeline

investor_bp = Blueprint('investor', __name__)

@investor_bp.route('/options_chain', methods=['GET'])
def options_chain_dashboard():
    return render_template('options_chain/dashboard.html')

@investor_bp.route('/api/options_chain/data', methods=['GET'])
def options_chain_data():
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({'error': 'Ticker is required'}), 400
    
    data = get_options_chain_data(ticker)
    return jsonify(data)

@investor_bp.route('/api/options_chain/analyze', methods=['POST'])
def analyze_options():
    request_data = request.get_json()
    ticker = request_data.get('ticker')
    if not ticker:
        return jsonify({'error': 'Ticker is required'}), 400
    
    analysis_results = analyze_options_data(ticker)
    return jsonify(analysis_results)

@investor_bp.route('/api/options_chain/inference', methods=['POST'])
def options_inference():
    request_data = request.get_json()
    ticker = request_data.get('ticker')
    if not ticker:
        return jsonify({'error': 'Ticker is required'}), 400
    
    predictions = run_inference_pipeline(ticker)
    return jsonify(predictions)