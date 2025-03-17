from pydantic import BaseModel
from typing import TypeVar, Generic
from fastapi import status
from fastapi.responses import JSONResponse


T = TypeVar("T")


class BasicResponse(BaseModel, Generic[T]):
    data: T | None = None
    message: str | None = None
    status_code: int = status.HTTP_200_OK

    def __call__(self, *args, **kwargs):
        return JSONResponse(
            content={"data": self.data, "message": self.message},
            status_code=self.status_code,
        )
