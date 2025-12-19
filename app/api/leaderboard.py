from fastapi import APIRouter, HTTPException
from typing import List
from app.db.models import LeaderboardEntry, TeamResultResponse, QueueStatus
from app.db.firebase_service import get_leaderboard, get_team_result

router = APIRouter()

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard_data():
    return get_leaderboard()

@router.get("/team-result/{team_id}", response_model=TeamResultResponse)
async def get_team_result_data(team_id: str):
    result = get_team_result(team_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return TeamResultResponse(
        team_id=result["team_id"],
        team_name=result["team_name"],
        rank=result.get("rank"),
        accuracy=result.get("accuracy"),
        f1_score=result.get("f1_score"),
        latency_ms=result.get("latency_ms"),
        status=QueueStatus(result["status"]) if result.get("status") else QueueStatus.QUEUED,
        evaluated_at=result.get("evaluated_at")
    )
