import asyncio
from app.db.firebase_service import get_next_in_queue, update_queue_status, get_team_endpoint, save_result
from app.db.models import QueueStatus
from app.core.evaluator import Evaluator

evaluator = Evaluator()

async def process_queue():
    team_id = get_next_in_queue()
    
    if not team_id:
        return
    
    update_queue_status(team_id, QueueStatus.EVALUATING)
    
    endpoint_url = get_team_endpoint(team_id)
    
    if not endpoint_url:
        update_queue_status(team_id, QueueStatus.FAILED, "Endpoint URL not found")
        return
    
    try:
        success, result, error = await evaluator.evaluate_team(endpoint_url)
        
        if success and result:
            save_result(team_id, result["accuracy"], result["f1_score"], result["latency_ms"])
            update_queue_status(team_id, QueueStatus.COMPLETED)
        else:
            update_queue_status(team_id, QueueStatus.FAILED, error or "Evaluation failed")
        
    except Exception as e:
        update_queue_status(team_id, QueueStatus.FAILED, str(e))
