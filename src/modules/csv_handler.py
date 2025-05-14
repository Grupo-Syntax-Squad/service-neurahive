from csv import DictReader
from io import StringIO
from typing import Any
from fastapi import UploadFile


class KnowledgeBaseHandler:
    def __init__(self, file: UploadFile) -> None:
        self._file = file
        self._contents: bytes | None = None
        self._decoded_contents: str | None = None
        self._csv_reader: DictReader | None = None  # type: ignore[type-arg]
        self._questions: list[str] | None = None
        self._answers: list[str] | None = None

    async def execute(self) -> dict[str, list[str]]:  # type: ignore[return]
        try:
            self._verify_file_type()
            await self._read_file()
            self._decode_contents()
            self._initialize_csv_reader()
            self._initialize_questions_and_answers()
            self._get_questions_and_answers()
            self._validate_questions_and_answers()
            if self._questions and self._answers:
                return {"questions": self._questions, "answers": self._answers}
        except Exception as e:
            print(f"Erro ao fazer o tratamento da base de conhecimento: {e}")
            raise e

    def _verify_file_type(self) -> None:
        if self._file.filename and not self._file.filename.endswith(".csv"):
            raise ValueError("Apenas arquivos .csv são permitidos.")

    async def _read_file(self) -> None:
        self._contents = await self._file.read()

    def _decode_contents(self) -> None:
        if self._contents:
            try:
                self._decoded_contents = self._contents.decode("utf-8")
            except UnicodeDecodeError:
                self._decoded_contents = self._contents.decode("latin-1")

    def _initialize_csv_reader(self) -> None:
        self._csv_reader = DictReader(StringIO(self._decoded_contents))

    def _initialize_questions_and_answers(self) -> None:
        self._questions = []
        self._answers = []

    def _get_questions_and_answers(self) -> None:
        if self._csv_reader and self._questions and self._answers:
            for row in self._csv_reader:
                question = self._get_question(row)
                answer = self._get_answer(row)

                if not question or not answer:
                    raise ValueError(
                        "O arquivo CSV está vazio ou mal formatado. Utilizar arquivo com colunas 'Pergunta' e 'Resposta'"
                    )

                self._questions.append(question)
                self._answers.append(answer)

    def _get_question(self, row: dict[str, Any]) -> str | None:
        return (
            row.get("pergunta")
            or row.get("Pergunta")
            or row.get("perguntas")
            or row.get("Perguntas")
        )

    def _get_answer(self, row: dict[str, Any]) -> str | None:
        return (
            row.get("resposta")
            or row.get("Resposta")
            or row.get("respostas")
            or row.get("Respostas")
        )

    def _validate_questions_and_answers(self) -> None:
        if self._questions and self._answers:
            if len(self._questions) != len(self._answers):
                raise ValueError(
                    "Arquivo com quantidade de perguntas diferente da quantidade de respostas"
                )
