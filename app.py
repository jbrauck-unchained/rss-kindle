from fastapi import FastAPI, Request
from starlette.responses import FileResponse
import subprocess
import smtplib
import os
import requests
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()  # Load email credentials from .env

app = FastAPI()


MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
KINDLE_EMAIL = os.getenv("KINDLE_EMAIL")
FROM_EMAIL = os.getenv("FROM_EMAIL")

@app.post("/convert")
async def convert_to_epub(request: Request):
    data = await request.json()
    articles = data.get("articles", [])

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

    for article in articles:
        html_content += f"<h1>{article['title']}</h1>\n"
        html_content += f"<p>{article['content']}</p>\n"

    html_content += "</body></html>"

    with open("/app/daily_digest.html", "w") as f:
        f.write(html_content)

    # Convert to EPUB
    subprocess.run(["ebook-convert", "/app/daily_digest.html", "/app/daily_digest.epub"])

    # Send to Kindle
    send_to_kindle("/app/daily_digest.epub")

    return {"message": "Converted & Sent!", "download_link": "/download/daily_digest.epub"}

@app.get("/download/{filename}")
async def download_file(filename: str):
    return FileResponse(f"/app/{filename}")


def send_to_kindle(file_path):
    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    
    files = [("attachment", ("rss_feed.mobi", open(file_path, "rb")))]
    
    data = {
        "from": FROM_EMAIL,
        "to": KINDLE_EMAIL,
        "subject": "Your Daily RSS Feed",
        "text": "Here’s your daily RSS feed for Kindle."
    }

    response = requests.post(url, auth=("api", MAILGUN_API_KEY), files=files, data=data)
    
    if response.status_code == 200:
        print("✅ Email sent successfully!")
    else:
        print(f"❌ Failed to send email: {response.text}")