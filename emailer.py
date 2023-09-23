import feedparser
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

os.environ['SENDER_EMAIL']
# Fetch the RSS feed
rss_url = "https://www.nobsbitcoin.com/rss/"
response = requests.get(rss_url)
feed = feedparser.parse(response.text)

# Create a .txt document with the RSS content
with open("rss_feed.txt", "w", encoding="utf-8") as txt_file:
    for entry in feed.entries:
        content_html = entry.content[0].value
        soup = BeautifulSoup(content_html, 'html.parser')
        plain_text = soup.get_text()
        txt_file.write(entry.title + "\n")
        txt_file.write(entry.description + "\n\n")
        txt_file.write(plain_text + "\n")

# Set up the email
sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('SENDER_PASSWORD')
receiver_email = os.getenv('KINDLE_EMAIL')

subject = "RSS Feed from nobsbitcoin.com"
body = "Please find the attached RSS feed from nobsbitcoin.com."

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain"))

# Attach the .txt file
with open("rss_feed.txt", "rb") as attachment:
    part = MIMEText(attachment.read().decode("utf-8"), "plain")
    part.add_header("Content-Disposition", "attachment; filename=feed.txt")
    msg.attach(part)

# Send the email
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())

# Delete the .txt file after sending
os.remove("rss_feed.txt")
