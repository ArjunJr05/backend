import numpy as np
from sklearn.datasets import make_classification

np.random.seed(42)

X, y = make_classification(
    n_samples=1000,
    n_features=10,
    n_informative=8,
    n_redundant=2,
    n_classes=2,
    weights=[0.9, 0.1],
    flip_y=0.05,
    random_state=42
)

TEST_DATA = []
for i in range(len(X)):
    TEST_DATA.append({
        'transaction_id': f'TXN_{i:04d}',
        'amount': float(X[i][0]),
        'time_of_day': float(X[i][1]),
        'merchant_category': float(X[i][2]),
        'distance_from_home': float(X[i][3]),
        'distance_from_last_transaction': float(X[i][4]),
        'ratio_to_median_purchase': float(X[i][5]),
        'repeat_retailer': float(X[i][6]),
        'used_chip': float(X[i][7]),
        'used_pin': float(X[i][8]),
        'online_order': float(X[i][9])
    })

GROUND_TRUTH = y.tolist()

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
