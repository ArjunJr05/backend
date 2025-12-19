# ML Hackathon Evaluation Platform - Backend

FastAPI-based backend for evaluating ML model endpoints in a fair, queue-based system.

## Features

- **Queue Management**: One team evaluated at a time (FIFO)
- **Automatic Evaluation**: Background worker processes submissions
- **Metrics Calculation**: Accuracy, F1 Score, Latency
- **Live Leaderboard**: Real-time ranking updates
- **SQLite Database**: Lightweight, no external dependencies

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── api/
│   │   ├── submit.py           # Endpoint submission API
│   │   ├── status.py           # Queue status API
│   │   └── leaderboard.py      # Leaderboard & results API
│   ├── core/
│   │   ├── evaluator.py        # ML model evaluation engine
│   │   ├── queue_manager.py    # Queue processing logic
│   │   └── worker.py           # Background worker
│   ├── db/
│   │   ├── database.py         # Database operations
│   │   └── models.py           # Pydantic models
│   ├── utils/
│   │   ├── validators.py       # Endpoint validation
│   │   └── http_client.py      # HTTP client for team endpoints
│   └── data/
│       ├── X_test.csv          # Test features
│       ├── y_true.csv          # True labels
│       └── hackathon.db        # SQLite database (auto-created)
├── requirements.txt
├── Dockerfile
└── README.md
```

## Installation

### Option 1: Local Setup

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Docker

```bash
cd backend
docker build -t ml-hackathon-backend .
docker run -p 8000:8000 ml-hackathon-backend
```

### Option 3: Docker Compose (Recommended)

```bash
# From project root
docker-compose up -d
```

## API Endpoints

### 1. Submit Endpoint
**POST** `/submit-endpoint`

Submit your ML model endpoint for evaluation.

**Request Body:**
```json
{
  "team_id": "team_001",
  "team_name": "ML Warriors",
  "endpoint_url": "https://your-model.com/predict"
}
```

**Response:**
```json
{
  "message": "Successfully added to evaluation queue",
  "team_id": "team_001",
  "queue_position": 3
}
```

### 2. Queue Status
**GET** `/queue-status/{team_id}`

Check your team's position and status in the queue.

**Response:**
```json
{
  "team_id": "team_001",
  "status": "QUEUED",
  "position": 3,
  "estimated_wait_time": 15
}
```

**Status Values:**
- `QUEUED`: Waiting in queue
- `EVALUATING`: Currently being evaluated
- `COMPLETED`: Evaluation finished
- `FAILED`: Evaluation failed

### 3. Leaderboard
**GET** `/leaderboard`

Get ranked list of all teams.

**Response:**
```json
[
  {
    "rank": 1,
    "team_id": "team_001",
    "team_name": "ML Warriors",
    "accuracy": 0.95,
    "f1_score": 0.94,
    "latency_ms": 120.5,
    "evaluated_at": "2024-12-18T14:30:00"
  }
]
```

### 4. Team Result
**GET** `/team-result/{team_id}`

Get detailed results for a specific team.

**Response:**
```json
{
  "team_id": "team_001",
  "team_name": "ML Warriors",
  "rank": 1,
  "accuracy": 0.95,
  "f1_score": 0.94,
  "latency_ms": 120.5,
  "status": "COMPLETED",
  "evaluated_at": "2024-12-18T14:30:00"
}
```

## Team Endpoint Requirements

Your ML model endpoint must:

1. **Accept POST requests** with JSON payload:
```json
{
  "inputs": [
    {"feature_0": 0.5, "feature_1": 0.7, ...},
    {"feature_0": 0.3, "feature_1": 0.9, ...}
  ]
}
```

2. **Return predictions** in JSON format:
```json
{
  "predictions": [1, 0, 1, 1, 0]
}
```

3. **Respond within 5 seconds** (timeout)
4. **Use HTTPS** (recommended for production)

## Example Team Endpoint (Flask)

```python
from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    inputs = data['inputs']
    
    # Your ML model prediction logic
    predictions = [1 if np.random.random() > 0.5 else 0 for _ in inputs]
    
    return jsonify({'predictions': predictions})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Configuration

Edit `app/config.py` to customize:

```python
EVALUATION_TIMEOUT = 5          # Seconds to wait for team endpoint
MAX_RETRIES = 1                 # Number of retry attempts
QUEUE_CHECK_INTERVAL = 5        # Seconds between queue checks
```

## Database Schema

### teams
- `team_id` (PK): Unique team identifier
- `team_name`: Team display name
- `endpoint_url`: ML model endpoint URL
- `created_at`: Registration timestamp

### queue
- `team_id` (FK): Reference to teams
- `status`: Current status (QUEUED/EVALUATING/COMPLETED/FAILED)
- `position`: Queue position
- `queued_at`: Queue entry timestamp
- `failure_reason`: Error message if failed

### results
- `team_id` (FK): Reference to teams
- `accuracy`: Model accuracy score
- `f1_score`: F1 score (weighted)
- `latency_ms`: Response time in milliseconds
- `evaluated_at`: Evaluation timestamp

## How It Works

1. **Team Submission**: Team submits endpoint via `/submit-endpoint`
2. **Validation**: System validates endpoint is reachable
3. **Queue Entry**: Team added to FIFO queue
4. **Background Worker**: Continuously checks for next team
5. **Evaluation**: 
   - Sends test data to team endpoint
   - Receives predictions
   - Calculates metrics (accuracy, F1, latency)
6. **Results Storage**: Saves to database
7. **Leaderboard Update**: Rankings automatically updated

## Ranking Logic

Teams are ranked by:
1. **Accuracy** (DESC) - Primary metric
2. **F1 Score** (DESC) - Secondary metric
3. **Evaluation Time** (ASC) - Tiebreaker

## Testing

### Create a dummy endpoint for testing:

```python
# test_endpoint.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    inputs = data['inputs']
    # Return dummy predictions
    predictions = [1] * len(inputs)
    return jsonify({'predictions': predictions})

if __name__ == '__main__':
    app.run(port=5001)
```

Run it:
```bash
python test_endpoint.py
```

Then submit:
```bash
curl -X POST http://localhost:8000/submit-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "test_team",
    "team_name": "Test Team",
    "endpoint_url": "http://localhost:5001/predict"
  }'
```

## Deployment

### Deploy to Render

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: ml-hackathon-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

2. Connect GitHub repo to Render
3. Deploy automatically

### Environment Variables (Production)

Set these in your deployment platform:
- `DATABASE_PATH`: Path to SQLite database
- `EVALUATION_TIMEOUT`: Timeout in seconds
- `QUEUE_CHECK_INTERVAL`: Queue polling interval

## Troubleshooting

### Issue: Queue not processing
- Check background worker is running
- Verify no team stuck in EVALUATING status
- Check logs: `docker-compose logs -f backend`

### Issue: Endpoint validation fails
- Ensure endpoint is publicly accessible
- Check CORS settings on team endpoint
- Verify endpoint returns correct JSON format

### Issue: Database locked
- Only one process should access SQLite
- Use PostgreSQL for production with multiple workers

## Security Considerations

- Rate limit endpoint submissions (add middleware)
- Validate all input data
- Timeout external calls (already implemented)
- Use HTTPS in production
- Add authentication for admin endpoints

## License

MIT License - Free for hackathon use
