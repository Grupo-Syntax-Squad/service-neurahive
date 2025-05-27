import csv
import json
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas.knowledge_base import (
    PostKnowledgeBaseResponse,
    GetKnowledgeBaseResponse,
    GetKnowledgeBaseMetadataResponse,
)
from src.database.models import KnowledgeBase
from src.schemas.basic_response import BasicResponse
from io import StringIO
from typing import List


class UploadKnowledgeBase:
    def __init__(self, file: UploadFile, name: str, session: Session):
        self.file = file
        self.name = name
        self.session = session

    async def execute(self) -> PostKnowledgeBaseResponse:
        if self.file.filename and not self.file.filename.endswith((".csv", ".txt")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only .csv and .txt files are allowed",
            )

        contents = await self.file.read()
        try:
            decoded = contents.decode("utf-8")
        except UnicodeDecodeError:
            decoded = contents.decode("latin-1")

        csv_reader = csv.DictReader(StringIO(decoded))

        questions, answers = [], []

        for row in csv_reader:
            question = row.get("pergunta") or row.get("Pergunta")
            answer = row.get("resposta") or row.get("Resposta")

            if question is not None and answer is not None:
                questions.append(question.strip())
                answers.append(answer.strip())

        kb = KnowledgeBase(
            name=self.name,
            data=json.dumps({"questions": questions, "answers": answers}),
        )
        self.session.add(kb)
        self.session.commit()
        self.session.refresh(kb)

        return PostKnowledgeBaseResponse(id=kb.id, name=kb.name)


class ReadKnowledgeBase:
    def __init__(self, session: Session, knowledge_base_id: int):
        self.session = session
        self.knowledge_base_id = knowledge_base_id

    def execute(self) -> BasicResponse[GetKnowledgeBaseResponse]:
        knowledge_base = self.read_knowledge_base()
        if knowledge_base:
            return BasicResponse(data=knowledge_base)
        raise HTTPException(
            detail="Base de conhecimento não encontrada",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    def read_knowledge_base(self) -> GetKnowledgeBaseResponse | None:
        with self.session as db:
            knowledge_base = db.get(KnowledgeBase, self.knowledge_base_id)
            if knowledge_base:
                return GetKnowledgeBaseResponse(
                    id=knowledge_base.id,
                    name=knowledge_base.name,
                    data=knowledge_base.data,  # type: ignore[arg-type]
                )
            return None


class ListKnowledgeBases:
    def __init__(self, session: Session):
        self.session = session

    def execute(self) -> BasicResponse[List[GetKnowledgeBaseMetadataResponse]]:
        knowledge_bases = self.list_knowledge_bases()
        return BasicResponse(data=knowledge_bases)

    def list_knowledge_bases(self) -> List[GetKnowledgeBaseMetadataResponse]:
        with self.session as db:
            knowledge_bases = db.query(KnowledgeBase).all()
            return [
                GetKnowledgeBaseMetadataResponse(
                    id=kb.id,
                    name=kb.name,
                )
                for kb in knowledge_bases
            ]
        

class CheckFilename:
    def __init__(self, session: Session, filename: str):
        self.session = session
        self.filename = filename

    def execute(self) -> BasicResponse[bool]:
        with self.session as db:            
            in_use = db.query(KnowledgeBase).filter_by(name=self.filename).first()
            return BasicResponse(data=not in_use)
