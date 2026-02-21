# Telegram Book Downloader & Manager

This project is a FastAPI-based application to scan a Telegram channel for book files (PDF, EPUB, etc.), manage an inventory, and provide a simple API for searching and downloading them.

## Features

- **Telegram Channel Scanner**: Scans a specified Telegram channel for new book files.
- **Book Inventory**: Stores book metadata (title, author, filename) in a local CSV file.
- **FastAPI Endpoints**:
    - `/scan`: Triggers a new scan of the Telegram channel.
    - `/books`: Lists or searches for books in the inventory.
    - `/download/{book_id}`: Downloads a specific book by its ID.
- **On-Demand Downloads**: Books are downloaded from Telegram only when requested, saving local storage space.

## Recent Updates (February 21, 2026)

- **Cloud Storage Integration**: Implemented `R2Storage` class to interface with Cloudflare R2 for storing and retrieving book files. This significantly reduces local storage dependency and improves scalability.
- **OCR and TTS Integration**: Added OCR capabilities to extract text from book covers and integrated a Text-to-Speech (TTS) service to generate audio previews.
- **Refactored Application Structure**: Reorganized the project into `app` and `app_` directories for better separation of concerns, with `app` containing the main FastAPI application and `app_` holding utilities and services.
- **Enhanced Download Logic**: The `/download` endpoint now intelligently checks if a book exists in cloud storage before downloading it from Telegram, optimizing bandwidth and response times.
- **Configuration Management**: Centralized configuration in `app/config.py` for easier management of environment variables and application settings.

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) for dependency management.
- A Telegram API key and hash (see [Telegram's documentation](https://core.telegram.org/api/obtaining_api_id)).
- **Ollama**: For OCR functionalities, ensure Ollama is installed and running, and the necessary OCR models are downloaded.
- **Cloudflare R2 Account**: For cloud storage functionality.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/telegram-books.git
   cd telegram-books
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Set up your environment:**
   Create a `.env` file in the root directory with your Telegram and R2 credentials:
   ```
   API_ID=your_api_id
   API_HASH=your_api_hash
   BOT_TOKEN=your_bot_token 
   CHANNEL_NAME=your_channel_name
   R2_ACCOUNT_ID=your_r2_account_id
   R2_ACCESS_KEY_ID=your_r2_access_key_id
   R2_SECRET_ACCESS_KEY=your_r2_secret_access_key
   ```

4. **Run the application:**
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`.
