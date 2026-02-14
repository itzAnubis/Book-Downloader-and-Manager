import pandas as pd
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.responses import FileResponse # Import this

from app.telegram import TelegramService
from app.config import Config
from app.models import BookRecord, ScanResponse

# Global service instance
tg_service = TelegramService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to Telegram
    print("🔌 Connecting to Telegram...")
    await tg_service.start()
    yield
    # Shutdown: Disconnect
    print("🔌 Disconnecting...")
    await tg_service.stop()

app = FastAPI(title="Telegram Book Scanner", lifespan=lifespan)

@app.post("/scan", response_model=ScanResponse)
async def scan_books(limit: int = 50):
    """Trigger a scan of the channel."""
    try:
        new_count = await tg_service.scan_channel(limit)
        return {
            "status": "success", 
            "books_found": limit, 
            "new_records": new_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/books")
async def list_books(search: str = None):
    """Search or list books from the CSV inventory."""
    if not os.path.exists(Config.CSV_PATH):
        return []

    df = pd.read_csv(Config.CSV_PATH)
    df = df.fillna("")

    if search:
        q = search.lower()
        mask = (
            df['cover_title'].str.lower().str.contains(q) | 
            df['cover_author'].str.lower().str.contains(q) |
            df['book_filename'].str.lower().str.contains(q)
        )
        df = df[mask]

    # Convert to list of dicts for JSON response
    results = []
    for _, row in df.iterrows():
        results.append({
            "book_id": int(row['book_id']),
            "title": row['cover_title'],
            "author": row['cover_author'],
            "filename": row['book_filename'],
            "file_size_mb": row['file_size_mb'],
            "cover_path": row['cover_path']
        })
    return results

@app.get("/download/{book_id}")
async def download_book(book_id: int):
    """
    Smart Endpoint:
    - If book is in storage: Sends it instantly.
    - If not: Downloads it first, then sends it.
    """
    file_path = await tg_service.download_if_missing(book_id)
    
    if not file_path:
        raise HTTPException(status_code=404, detail="Book not found")
        
    return FileResponse(
        path=file_path, 
        filename=os.path.basename(file_path), 
        media_type='application/octet-stream'
    )