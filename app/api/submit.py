from fastapi import APIRouter, HTTPException, Depends, Request
from app.db.models import TeamSubmission, SubmitResponse, QueueStatus
from app.db.firebase_service import add_team, add_to_queue, get_queue_status
from app.utils.validators import validate_endpoint
from app.core.auth import get_current_user, TokenData

router = APIRouter()

@router.post("/submit-endpoint", response_model=SubmitResponse)
async def submit_endpoint(request: Request, submission: TeamSubmission, current_user: TokenData = Depends(get_current_user)):
    print(f"Submit endpoint called for team: {submission.team_id}")
    print(f"Authorization header: {request.headers.get('authorization', 'NOT FOUND')}")
    is_valid, message = await validate_endpoint(submission.endpoint_url)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid endpoint: {message}")
    
    queue_status = get_queue_status(submission.team_id)
    
    if queue_status and queue_status.status in [QueueStatus.QUEUED, QueueStatus.EVALUATING]:
        raise HTTPException(
            status_code=400, 
            detail=f"Team is already {queue_status.status.value}. Please wait for current evaluation to complete."
        )
    
    add_team(submission.team_id, submission.team_name, submission.endpoint_url, current_user.uid)
    
    position = add_to_queue(submission.team_id)
    
    return SubmitResponse(
        message="Successfully added to evaluation queue",
        team_id=submission.team_id,
        queue_position=position
    )
