import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score
from typing import Dict, Optional, Tuple
from app.config import EVALUATION_TIMEOUT, MAX_RETRIES
from app.utils.http_client import call_team_endpoint
from app.data.test_data import TEST_DATA, GROUND_TRUTH

class Evaluator:
    def __init__(self):
        self.X_test = None
        self.y_true = None
        self.load_test_data()
    
    def load_test_data(self):
        print(f"Loading test data: {len(TEST_DATA)} samples")
        self.X_test = pd.DataFrame(TEST_DATA)
        self.y_true = np.array(GROUND_TRUTH)
        print(f"Test data loaded - Features: {self.X_test.shape[1]}, Samples: {len(self.y_true)}")
        print(f"Class distribution - Legitimate: {sum(self.y_true == 0)}, Fraud: {sum(self.y_true == 1)}")
    
    async def evaluate_team(self, endpoint_url: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        if self.X_test is None or self.y_true is None:
            return False, None, "Test data not loaded"
        
        payload = {
            "inputs": self.X_test.to_dict(orient='records')
        }
        
        response = await call_team_endpoint(
            endpoint_url, 
            payload, 
            timeout=EVALUATION_TIMEOUT, 
            max_retries=MAX_RETRIES
        )
        
        if response is None:
            return False, None, "Failed to get response from endpoint"
        
        if 'predictions' not in response:
            return False, None, "Response missing 'predictions' field"
        
        predictions = response['predictions']
        
        if not isinstance(predictions, list):
            return False, None, "Predictions must be a list"
        
        if len(predictions) != len(self.y_true):
            return False, None, f"Expected {len(self.y_true)} predictions, got {len(predictions)}"
        
        try:
            y_pred = np.array(predictions)
            
            accuracy = accuracy_score(self.y_true, y_pred)
            f1 = f1_score(self.y_true, y_pred, average='binary')
            latency_ms = response.get('latency_ms', 0)
            
            result = {
                'accuracy': float(accuracy),
                'f1_score': float(f1),
                'latency_ms': float(latency_ms)
            }
            
            print(f"Evaluation complete - Accuracy: {accuracy:.4f}, F1: {f1:.4f}, Latency: {latency_ms:.2f}ms")
            
            return True, result, None
            
        except Exception as e:
            return False, None, f"Error calculating metrics: {str(e)}"
