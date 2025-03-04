from flask import Flask, request, jsonify
import pickle
import os
import numpy as np


app = Flask(__name__)

MODEL_PATH = os.environ.get('MODEL_PATH', 'model.pkl')


# Load model if exists
def load_model():
    try:
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                return pickle.load(f)
        else:
            return None
    except Exception as e:
        app.logger.error(f"Error loading model: {e}")
        return None


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint to make predictions using the ML model"""
    model = load_model()

    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        # Get input data from request
        data = request.get_json()
        features = np.array(data['features']).reshape(1, -1)

        # Make prediction
        prediction = model.predict(features).tolist()

        return jsonify({
            "prediction": prediction,
            "model_version": os.environ.get('MODEL_VERSION', 'unknown')
        }), 200

    except Exception as e:
        app.logger.error(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
