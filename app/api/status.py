from fastapi import APIRouter, HTTPException
from app.db.models import QueueStatusResponse
from app.db.firebase_service import get_queue_status
from app.config import QUEUE_CHECK_INTERVAL

router = APIRouter()

@router.get("/queue-status/{team_id}", response_model=QueueStatusResponse)
async def get_status(team_id: str):
    queue_entry = get_queue_status(team_id)
    
    if not queue_entry:
        raise HTTPException(status_code=404, detail="Team not found in queue")
    
    estimated_wait = None
    if queue_entry.position and queue_entry.position > 1:
        estimated_wait = (queue_entry.position - 1) * QUEUE_CHECK_INTERVAL
    
    return QueueStatusResponse(
        team_id=queue_entry.team_id,
        status=queue_entry.status,
        position=queue_entry.position,
        estimated_wait_time=estimated_wait,
        failure_reason=queue_entry.failure_reason
    )
