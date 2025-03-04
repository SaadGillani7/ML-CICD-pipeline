import unittest
import os
import sys
import json
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier

# Add the src directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import the Flask app
from src.api.app import app

class TestFlaskAPI(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method"""
        # Create a test model
        self.test_model_path = os.path.abspath('test_model.pkl')
        print(f"Creating test model at: {self.test_model_path}")
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        X = np.random.rand(20, 4)
        y = (X[:, 0] + X[:, 1] > 1).astype(int)
        model.fit(X, y)
        
        # Save the model
        with open(self.test_model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Verify model exists
        print(f"Model file exists: {os.path.exists(self.test_model_path)}")
        
        # Configure Flask test client
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Set environment variable for model path
        os.environ['MODEL_PATH'] = self.test_model_path
        os.environ['MODEL_VERSION'] = 'test-version'
        
        # For debugging, let's print all environment variables
        print(f"MODEL_PATH set to: {os.environ.get('MODEL_PATH')}")
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_predict_endpoint(self):
        """Test the prediction endpoint"""
        # Verify model still exists
        print(f"Before prediction, model exists: {os.path.exists(self.test_model_path)}")
        
        # Prepare test data
        test_data = {
            'features': [0.1, 0.2, 0.3, 0.4]
        }
        
        # Make request
        response = self.client.post(
            '/predict',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Print response for debugging
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('prediction', data)
        self.assertIn('model_version', data)
        self.assertEqual(data['model_version'], 'test-version')
    
    def test_predict_error_handling(self):
        """Test error handling in prediction endpoint"""
        # Prepare invalid test data (missing features)
        test_data = {
            'invalid_key': [0.1, 0.2]
        }
        
        # Make request
        response = self.client.post(
            '/predict',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Print response for debugging
        print(f"Error handling response status: {response.status_code}")
        print(f"Error handling response data: {response.data}")
        
        # Check response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def tearDown(self):
        """Clean up after each test method"""
        # Remove test model
        if os.path.exists(self.test_model_path):
            os.remove(self.test_model_path)
        print(f"After tearDown, model exists: {os.path.exists(self.test_model_path)}")

if __name__ == '__main__':
    unittest.main()