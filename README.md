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

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) for dependency management.
- A Telegram API key and hash (see [Telegram's documentation](https://core.telegram.org/api/obtaining_api_id)).
- **Ollama**: For OCR functionalities, ensure Ollama is installed and running, and the necessary OCR models are downloaded.

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
   Create a `.env` file in the root directory with your Telegram API credentials:
   ```
   API_ID=your_api_id
   API_HASH=your_api_hash
   BOT_TOKEN=your_bot_token 
   CHANNEL_NAME=your_channel_name
   ```

4. **Run the application:**
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`.

## To-Do

- [ ] **Dockerize the application**: Create a `Dockerfile` for easy containerization and deployment.
- [ ] **Deploy the application**: Deploy to a cloud service (e.g., Heroku, AWS, Google Cloud).
- [ ] **CI/CD Pipeline**: Implement a continuous integration and deployment pipeline (e.g., using GitHub Actions).
- [ ] **Recommendation System**: Develop a simple ML-based recommendation system to suggest books based on user downloads or ratings.
- [ ] **Web Interface**: Build a simple front-end website (e.g., using React or Vue.js) to interact with the API.