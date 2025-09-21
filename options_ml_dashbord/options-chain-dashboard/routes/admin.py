from flask import Blueprint, render_template, request, jsonify
from options_chain.ml import features, pipelines
from options_chain.ai.assistant import analyze_options_chain

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/options_chain_dashboard', methods=['GET'])
def options_chain_dashboard():
    return render_template('options_chain/dashboard.html')

@admin_bp.route('/api/analyze_options', methods=['POST'])
def analyze_options():
    data = request.json
    analysis_result = analyze_options_chain(data)
    return jsonify(analysis_result)

@admin_bp.route('/api/ml_features', methods=['GET'])
def get_ml_features():
    features_data = features.get_all_features()
    return jsonify(features_data)

@admin_bp.route('/api/train_model', methods=['POST'])
def train_model():
    training_data = request.json
    result = pipelines.train_model(training_data)
    return jsonify(result)

@admin_bp.route('/api/inference', methods=['POST'])
def inference():
    input_data = request.json
    predictions = pipelines.make_inference(input_data)
    return jsonify(predictions)