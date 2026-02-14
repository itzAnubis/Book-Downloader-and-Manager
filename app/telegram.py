import os
import pandas as pd
from telethon import TelegramClient
from app.config import Config
from app.ocr import get_ocr_metadata

class TelegramService:
    def __init__(self):
        self.client = TelegramClient(Config.SESSION_NAME, Config.API_ID, Config.API_HASH)

    async def start(self):
        await self.client.start()

    async def stop(self):
        await self.client.disconnect()

    async def scan_channel(self, limit=50):
        """Scans channel and updates CSV using Double-Buffer matching."""
        print(f"🚀 Scanning {Config.CHANNEL_NAME}...")
        
        # 1. Load existing IDs to avoid duplicates
        existing_ids = set()
        if os.path.exists(Config.CSV_PATH):
            # Read only the book_id column to check existence
            try:
                existing_df = pd.read_csv(Config.CSV_PATH, usecols=['book_id'])
                existing_ids = set(existing_df['book_id'].tolist())
            except ValueError:
                # Handle case where CSV might be empty or corrupt
                existing_ids = set()

        all_records = []
        unpaired_books = []
        unpaired_images = []

        # Iterate messages (Newest -> Oldest)
        async for message in self.client.iter_messages(Config.CHANNEL_NAME, limit=limit):
            
            # --- CASE A: BOOK ---
            if message.document:
                if message.id in existing_ids:
                    continue 

                filename = message.file.name if message.file.name else f"book_{message.id}{message.file.ext}"
                
                # Create Record
                record = {
                    'book_id': message.id,
                    'book_filename': filename,
                    'cover_title': "Unknown",
                    'cover_author': "Unknown",
                    'cover_path': None,
                    'image_id': None,
                    'file_size_mb': round(message.file.size / (1024 * 1024), 2),
                    'date': message.date.strftime('%Y-%m-%d %H:%M:%S')
                }
                all_records.append(record)

                # Check for waiting image in 'unpaired_images'
                match_found = False
                for img_msg in unpaired_images:
                    # Proximity Check (within 3 messages)
                    if abs(img_msg.id - message.id) <= 3:
                        await self._process_match(record, img_msg)
                        unpaired_images.remove(img_msg) # REMOVE matched image
                        match_found = True
                        break
                
                if not match_found:
                    unpaired_books.append(record) # Add to queue

            # --- CASE B: IMAGE ---
            elif message.photo:
                match_found = False
                # Check for waiting book in 'unpaired_books'
                for book_rec in unpaired_books:
                    if abs(book_rec['book_id'] - message.id) <= 3:
                        await self._process_match(book_rec, message)
                        unpaired_books.remove(book_rec) # REMOVE matched book
                        match_found = True
                        break
                
                if not match_found:
                    unpaired_images.append(message)

        # 2. Save updates
        # Filter out records that were found but might not be fully complete (optional)
        # We save everything in 'all_records'
        if all_records:
            df_new = pd.DataFrame(all_records)
            
            # Strictly enforce column order
            cols = ['book_id', 'book_filename', 'cover_title', 'cover_author', 'cover_path', 'image_id', 'file_size_mb', 'date']
            
            # Ensure all columns exist even if empty
            for col in cols:
                if col not in df_new.columns:
                    df_new[col] = None
                    
            df_new = df_new[cols]
            
            if os.path.exists(Config.CSV_PATH):
                df_new.to_csv(Config.CSV_PATH, mode='a', header=False, index=False)
            else:
                df_new.to_csv(Config.CSV_PATH, index=False)
            
        return len(all_records)

    async def _process_match(self, book_record, image_message):
        """Downloads cover, runs OCR, updates record object"""
        filename = f"{book_record['book_id']}.jpg"
        
        # Absolute path for saving
        full_path = os.path.join(Config.COVERS_DIR, filename)
        # Relative path for CSV (e.g., 'covers/123.jpg')
        relative_path = os.path.join("covers", filename)
        
        print(f"   ⬇️  Downloading cover for Book {book_record['book_id']}...")
        await image_message.download_media(file=full_path)
        
        title, author = await get_ocr_metadata(full_path)
        
        book_record['image_id'] = image_message.id
        book_record['cover_path'] = relative_path
        book_record['cover_title'] = title
        book_record['cover_author'] = author
        print(f"   ✨ OCR: {title} | {author}")

    async def download_book(self, book_id: int):
        try:
            msg = await self.client.get_messages(Config.CHANNEL_NAME, ids=book_id)
            if msg and msg.document:
                filename = msg.file.name if msg.file.name else f"book_{book_id}.pdf"
                path = os.path.join(Config.DOWNLOADS_DIR, filename)
                
                if os.path.exists(path):
                    return path
                    
                await msg.download_media(file=path)
                return path
        except Exception as e:
            print(f"Download Error: {e}")
            return None

    # Inside app/telegram.py

    async def download_if_missing(self, book_id: int):
        """
        Smart Download:
        1. Checks if file exists in 'downloads/'
        2. If yes -> Returns path
        3. If no -> Downloads from Telegram -> Returns path
        """
        try:
            # 1. Get Message Info (Lightweight)
            msg = await self.client.get_messages(Config.CHANNEL_NAME, ids=book_id)
            if not msg or not msg.document:
                return None
            
            # Determine Filename
            filename = msg.file.name if msg.file.name else f"book_{book_id}.pdf"
            file_path = os.path.join(Config.DOWNLOADS_DIR, filename)

            # 2. Check Cache (The "Store" Logic)
            if os.path.exists(file_path):
                print(f"⚡ Cache Hit: Serving {filename} from disk.")
                return file_path

            # 3. Download if missing
            print(f"📥 Cache Miss: Downloading {filename} from Telegram...")
            path = await msg.download_media(file=file_path)
            return path
            
        except Exception as e:
            print(f"Download Error: {e}")
            return None