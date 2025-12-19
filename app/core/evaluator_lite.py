from typing import Dict, Optional, Tuple, List
from app.config import EVALUATION_TIMEOUT, MAX_RETRIES
from app.utils.http_client import call_team_endpoint
from app.data.test_data_static import TEST_DATA, GROUND_TRUTH

def accuracy_score(y_true: List, y_pred: List) -> float:
    """Calculate accuracy without sklearn"""
    if len(y_true) != len(y_pred):
        raise ValueError("Length mismatch")
    correct = sum(1 for true, pred in zip(y_true, y_pred) if true == pred)
    return correct / len(y_true)

def f1_score(y_true: List, y_pred: List) -> float:
    """Calculate F1 score without sklearn (binary classification)"""
    tp = sum(1 for true, pred in zip(y_true, y_pred) if true == 1 and pred == 1)
    fp = sum(1 for true, pred in zip(y_true, y_pred) if true == 0 and pred == 1)
    fn = sum(1 for true, pred in zip(y_true, y_pred) if true == 1 and pred == 0)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)

class Evaluator:
    def __init__(self):
        self.X_test = None
        self.y_true = None
        self.load_test_data()
    
    def load_test_data(self):
        print(f"Loading test data: {len(TEST_DATA)} samples")
        self.X_test = TEST_DATA
        self.y_true = GROUND_TRUTH
        print(f"Test data loaded - Samples: {len(self.y_true)}")
        print(f"Class distribution - Legitimate: {sum(1 for y in self.y_true if y == 0)}, Fraud: {sum(1 for y in self.y_true if y == 1)}")
    
    async def evaluate_team(self, endpoint_url: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        if self.X_test is None or self.y_true is None:
            return False, None, "Test data not loaded"
        
        payload = {
            "inputs": self.X_test
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
            accuracy = accuracy_score(self.y_true, predictions)
            f1 = f1_score(self.y_true, predictions)
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
