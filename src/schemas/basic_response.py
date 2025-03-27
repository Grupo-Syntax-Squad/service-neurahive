import json
from pydantic import BaseModel
from typing import Optional, TypeVar, Generic
from fastapi import status
from fastapi.responses import Response
from fastapi.encoders import jsonable_encoder

T = TypeVar("T")


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
