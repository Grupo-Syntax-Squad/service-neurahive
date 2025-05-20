from sqlalchemy.orm import Session
from src.database.get_db import get_db
from src.modules.statistics import GeneralStatistics, UserInteractions
from src.schemas.statistics import (
    GeneralStatisticsRequest,
    GeneralStatisticsResponse,
    UserInteractionsRequest,
    UserInteractionsResponse,
)
from src.schemas.basic_response import BasicResponse
from fastapi import APIRouter, Depends


router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/general", response_model=BasicResponse)
def get_general_statistics(
    params: GeneralStatisticsRequest = Depends(),
    session: Session = Depends(get_db),
) -> BasicResponse[GeneralStatisticsResponse]:
    return GeneralStatistics(session, params).execute()


@router.get("/user", response_model=list[UserInteractionsResponse])
def get_user_interactions(
    params: UserInteractionsRequest,
    db: Session = Depends(get_db)
) -> list[UserInteractionsResponse]:
    return UserInteractions(db, params).execute()
