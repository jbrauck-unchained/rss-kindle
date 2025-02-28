from fastapi import FastAPI, Request
from starlette.responses import FileResponse
import subprocess
import os
import requests
import logging
import traceback
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()  # Load email credentials from .env
logger.info("Environment variables loaded")

app = FastAPI()

# Gmail credentials
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
KINDLE_EMAIL = os.getenv("KINDLE_EMAIL")

logger.info(f"Configuration: GMAIL_USER={GMAIL_USER}, KINDLE_EMAIL={KINDLE_EMAIL}")

@app.post("/convert")
async def convert_to_epub(request: Request):
    try:
        logger.info("Received convert request")
        data = await request.json()
        articles = data.get("articles", [])
        logger.info(f"Processing {len(articles)} articles")

        # Get current date for filename
        today = datetime.now().strftime("%Y-%m-%d")
        base_filename = f"Digest_{today}"
        
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

        # Add title with date
        html_content += f"<h1>Daily Digest - {today}</h1>\n"

        for i, article in enumerate(articles):
            logger.info(f"Processing article {i+1}: {article.get('title', 'No title')}")
            html_content += f"<h1>{article.get('title', 'No title')}</h1>\n"
            # Check for either 'content' or 'cleanedContent' field
            content = article.get('content', article.get('cleanedContent', ''))
            if not content:
                logger.warning(f"Article {i+1} has no content")
            html_content += f"<p>{content}</p>\n"

        html_content += "</body></html>"

        html_path = f"/app/{base_filename}.html"
        epub_path = f"/app/{base_filename}.epub"
        mobi_path = f"/app/{base_filename}.mobi"
        
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
        
        # Convert to MOBI (Kindle format)
        logger.info("Converting EPUB to MOBI")
        result = subprocess.run(
            ["ebook-convert", epub_path, mobi_path], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"ebook-convert to MOBI failed: {result.stderr}")
            return {"error": "Failed to convert to MOBI", "details": result.stderr}
        
        logger.info(f"MOBI created at {mobi_path}")

        # Send to Kindle
        logger.info("Sending to Kindle")
        send_result = send_to_kindle_gmail(mobi_path, base_filename)
        
        if not send_result["success"]:
            logger.error(f"Failed to send to Kindle: {send_result['error']}")
            return {"error": "Failed to send to Kindle", "details": send_result["error"]}
        
        logger.info("Successfully converted and sent to Kindle")
        return {"message": "Converted & Sent!", "download_link": f"/download/{base_filename}.mobi"}
    
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

def send_to_kindle_gmail(file_path, base_filename):
    try:
        logger.info(f"Sending {file_path} to Kindle at {KINDLE_EMAIL}")
        
        if not os.path.exists(file_path):
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = KINDLE_EMAIL
        msg['Subject'] = f"Daily Digest - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Attach the body text
        body = "Here's your daily RSS feed for Kindle."
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach the file with the date-based filename
        with open(file_path, 'rb') as file:
            attachment = MIMEApplication(file.read(), Name=f"{base_filename}.mobi")
        
        attachment['Content-Disposition'] = f'attachment; filename="{base_filename}.mobi"'
        msg.attach(attachment)
        
        # Connect to Gmail SMTP server
        logger.info("Connecting to Gmail SMTP server")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login to Gmail
        logger.info("Logging in to Gmail")
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        
        # Send the email
        logger.info("Sending email")
        server.send_message(msg)
        server.quit()
        
        logger.info("✅ Email sent successfully!")
        return {"success": True}
    
    except Exception as e:
        error_msg = f"Exception in send_to_kindle_gmail: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return {"success": False, "error": error_msg}

@app.get("/")
async def root():
    return {"message": "RSS to Kindle API is running. Use /convert to process articles."}