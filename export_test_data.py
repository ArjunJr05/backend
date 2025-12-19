from app.data.test_data import TEST_DATA, GROUND_TRUTH
import json

with open('test_data_static.json', 'w') as f:
    json.dump({
        'test_data': TEST_DATA,
        'ground_truth': GROUND_TRUTH
    }, f, indent=2)

print(f"Exported {len(TEST_DATA)} test samples")
