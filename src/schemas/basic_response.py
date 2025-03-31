import json
from pydantic import BaseModel
from typing import Optional, TypeVar, Generic, Union
from fastapi import status
from fastapi.responses import Response
from fastapi.encoders import jsonable_encoder
from src.schemas.agent import AgentResponse

T = TypeVar("T")
A = TypeVar("A", bound=Union[AgentResponse, list[AgentResponse]])


class BasicResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    message: Optional[str] = None
    status_code: int = status.HTTP_200_OK

    def __call__(self) -> Response:
        content = jsonable_encoder({"data": self.data, "message": self.message})

        return Response(
            content=json.dumps(content),
            media_type="application/json",
            status_code=self.status_code,
        )


class GetAgentBasicResponse(BaseModel, Generic[A]):
    data: Optional[A] = None
    message: Optional[str] = None
    status_code: int = status.HTTP_200_OK

    def __call__(self) -> Response:
        content = jsonable_encoder({"data": self.data, "message": self.message})
        return Response(
            content=json.dumps(content),
            media_type="application/json",
            status_code=self.status_code,
        )
