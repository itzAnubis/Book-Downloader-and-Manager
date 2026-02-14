import re
import ollama
from app.config import Config

def clean_text(text):
    if not text: return "Unknown"
    return text.strip().replace('**', '').replace('__', '').strip('"').strip("'")

def parse_ocr_response(response_text):
    title = "Unknown"
    author = "Unknown"
    
    title_match = re.search(r"Title:\s*(.+?)(?=\n|Author:|$)", response_text, re.IGNORECASE | re.DOTALL)
    author_match = re.search(r"Author:\s*(.+?)(?=\n|$)", response_text, re.IGNORECASE | re.DOTALL)
    
    if title_match:
        title = clean_text(title_match.group(1).replace('\n', ' '))
    if author_match:
        author = clean_text(author_match.group(1).replace('\n', ' '))
        
    return title, author

async def get_ocr_metadata(image_path: str):
    """Async wrapper for Ollama OCR"""
    prompt = (
        "You are an expert OCR system. Extract the Book Title and the Author's Name "
        "from this cover. Respond ONLY in the following format:\n"
        "Title: [Name]\n"
        "Author: [Name]"
    )
    
    try:
        client = ollama.AsyncClient()
        response = await client.chat(
            model=Config.OLLAMA_MODEL,
            messages=[{'role': 'user', 'content': prompt, 'images': [image_path]}]
        )
        return parse_ocr_response(response['message']['content'])
    except Exception as e:
        print(f"⚠️ OCR Error: {e}")
        return "Unknown", "Unknown"