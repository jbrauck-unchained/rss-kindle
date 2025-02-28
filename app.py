from fastapi import FastAPI, Request
from starlette.responses import FileResponse
import subprocess
import smtplib
import os
import requests
import logging
import traceback
from email.message import EmailMessage
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()  # Load email credentials from .env
logger.info("Environment variables loaded")

app = FastAPI()

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
KINDLE_EMAIL = os.getenv("KINDLE_EMAIL")
FROM_EMAIL = os.getenv("FROM_EMAIL")

logger.info(f"Configuration: MAILGUN_DOMAIN={MAILGUN_DOMAIN}, FROM_EMAIL={FROM_EMAIL}, KINDLE_EMAIL={KINDLE_EMAIL}")

@app.post("/convert")
async def convert_to_epub(request: Request):
    try:
        logger.info("Received convert request")
        data = await request.json()
        articles = data.get("articles", [])
        logger.info(f"Processing {len(articles)} articles")

        # Create formatted HTML file
        html_content = """
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                h1 {
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                p {
                    font-size: 16px;
                    line-height: 1.5;
                }
            </style>
        </head>
        <body>
        """

        for i, article in enumerate(articles):
            logger.info(f"Processing article {i+1}: {article.get('title', 'No title')}")
            html_content += f"<h1>{article.get('title', 'No title')}</h1>\n"
            # Check for either 'content' or 'cleanedContent' field
            content = article.get('content', article.get('cleanedContent', ''))
            if not content:
                logger.warning(f"Article {i+1} has no content")
            html_content += f"<p>{content}</p>\n"

        html_content += "</body></html>"

        html_path = "/app/daily_digest.html"
        epub_path = "/app/daily_digest.epub"
        
        logger.info(f"Writing HTML to {html_path}")
        with open(html_path, "w") as f:
            f.write(html_content)

        # Convert to EPUB
        logger.info("Converting HTML to EPUB")
        result = subprocess.run(
            ["ebook-convert", html_path, epub_path], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"ebook-convert failed: {result.stderr}")
            return {"error": "Failed to convert to EPUB", "details": result.stderr}
        
        logger.info(f"EPUB created at {epub_path}")

        # Send to Kindle
        logger.info("Sending to Kindle")
        send_result = send_to_kindle(epub_path)
        
        if not send_result["success"]:
            logger.error(f"Failed to send to Kindle: {send_result['error']}")
            return {"error": "Failed to send to Kindle", "details": send_result["error"]}
        
        logger.info("Successfully converted and sent to Kindle")
        return {"message": "Converted & Sent!", "download_link": f"/download/daily_digest.epub"}
    
    except Exception as e:
        logger.error(f"Error in convert_to_epub: {str(e)}")
        logger.error(traceback.format_exc())
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/download/{filename}")
async def download_file(filename: str):
    logger.info(f"Download requested for {filename}")
    file_path = f"/app/{filename}"
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return {"error": "File not found"}
    return FileResponse(file_path)

def send_to_kindle(file_path):
    try:
        logger.info(f"Sending {file_path} to Kindle at {KINDLE_EMAIL}")
        url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
        
        if not os.path.exists(file_path):
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        files = [("attachment", ("rss_feed.mobi", open(file_path, "rb")))]
        
        data = {
            "from": FROM_EMAIL,
            "to": KINDLE_EMAIL,
            "subject": "Your Daily RSS Feed",
            "text": "Here's your daily RSS feed for Kindle."
        }

        logger.info("Sending request to Mailgun API")
        response = requests.post(url, auth=("api", MAILGUN_API_KEY), files=files, data=data)
        
        if response.status_code == 200:
            logger.info("✅ Email sent successfully!")
            return {"success": True}
        else:
            error_msg = f"❌ Failed to send email: {response.text}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    except Exception as e:
        error_msg = f"Exception in send_to_kindle: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return {"success": False, "error": error_msg}

@app.get("/")
async def root():
    return {"message": "RSS to Kindle API is running. Use /convert to process articles."}