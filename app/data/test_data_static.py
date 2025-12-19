import json
import os

# Load pre-generated test data
current_dir = os.path.dirname(__file__)
json_path = os.path.join(current_dir, '../../test_data_static.json')

with open(json_path, 'r') as f:
    data = json.load(f)
    TEST_DATA = data['test_data']
    GROUND_TRUTH = data['ground_truth']

FEATURE_NAMES = [
    'amount',
    'time_of_day',
    'merchant_category',
    'distance_from_home',
    'distance_from_last_transaction',
    'ratio_to_median_purchase',
    'repeat_retailer',
    'used_chip',
    'used_pin',
    'online_order'
]
