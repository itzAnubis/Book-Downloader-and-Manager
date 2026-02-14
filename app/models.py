from pydantic import BaseModel
from typing import Optional

class BookRecord(BaseModel):
    book_id: int
    title: str
    author: str
    filename: str
    file_size_mb: float
    cover_path: Optional[str] = None

class ScanResponse(BaseModel):
    status: str
    books_found: int
    new_records: int