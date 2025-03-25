from datetime import datetime
from sqlalchemy import text
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session
from src.schemas.example import (
    GetExampleResponse,
    PostExampleRequest,
    DeleteExampleRequest,
)
from src.schemas.basic_response import BasicResponse
from src.database.models import Example
from fastapi import status


class GetExample:
    def __init__(self, session: Session):
        self._session = session

    def execute(self) -> BasicResponse[list[GetExampleResponse]]:
        self._get_examples()
        self._format_response()
        return BasicResponse(data=self.result)

    def _get_examples(self) -> None:
        with self._session as session:
            query = text("""SELECT * FROM example""")
            result = session.execute(query)
            examples: list[Row] = result.fetchall()
            self.result = [example._asdict() for example in examples]

    def _format_response(self) -> None:
        self.result = [
            GetExampleResponse(
                id=result["id"],
                name=result["name"],
                enabled=result["enabled"],
                created_at=result["created_at"].isoformat(),
                updated_at=result["updated_at"].isoformat(),
            ).model_dump()
            for result in self.result
        ]


class CreateExample:
    def __init__(self, session: Session, example: PostExampleRequest):
        self._session = session
        self._example = example

    def execute(self) -> BasicResponse[None]:
        self._create_example()
        return BasicResponse(
            message="Example created", status_code=status.HTTP_201_CREATED
        )

    def _create_example(self) -> None:
        with self._session as session:
            example = Example(name=self._example.name, updated_at=datetime.now())
            session.add(example)
            session.commit()


class DeleteExample:
    def __init__(self, session: Session, example: DeleteExampleRequest):
        self._session = session
        self._example = example

    def execute(self) -> BasicResponse[None]:
        self._delete_example()
        return BasicResponse(message="Example deleted", status_code=status.HTTP_200_OK)

    def _delete_example(self) -> None:
        with self._session as session:
            query = text(
                """UPDATE example SET enabled = FALSE WHERE id=:id"""
            ).bindparams(id=self._example.id)
            session.execute(query)
