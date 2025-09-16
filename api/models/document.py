from pydantic import BaseModel

class DocumentRequest(BaseModel):
    doc_url: str