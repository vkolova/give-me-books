import os
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests
from utils import extract_book_preview

sender_email = os.environ.get("SENDER_EMAIL")
password = os.environ.get("SENDER_EMAIL_PASS")


def recommendation_html(rec) -> str:
    authors = [f'<a class="author" href="{url}" target="_blank" style="color:rgba(0,0,0,.7);">{an}</a>' for an, url in rec["authors"].items()]

    return f"""
    <div class="book-card" style="display:inline-flex;margin:15px 25px">
        <div class="left">
            <a class="title" href="{rec['url']}" target="_blank">
                <img src="{rec['cover']}" style="border:1px solid rgba(0,0,0,.17);height:auto;max-width:100px;object-fit:contain"/>
            </a>
        </div>
        <div class="right" style="flex:1;flex-direction:column;padding:0 15px">
            <a class="title" href="{rec['url']}" target="_blank" style="display:block;font-size:32px;font-style:italic;font-weight:500;color:#000;text-decoration:none">{rec["title"]}</a>
            {', '.join(authors)}
            <p class="blurb" style="font-size:14px;margin:15px 0">{rec["blurb"]}...</p>
        </div>
    </div>
    """

def build_email_content(subject: str, recommendations) -> str:
    reccomendations_html = []
    for r in recommendations:
        reccomendations_html.append(recommendation_html(r))

    content = '\n'.join(reccomendations_html)
    return f"""
    <html>
        <body style="margin:0 auto;max-width:97%">
            <h1>{subject}</h1>
            {content}
        </body>
    </html>
    """

def send_recommendations_to_email(book_url: str, receiver_email: str, recommendations=[]) -> None:
    page = requests.get(book_url)
    book = extract_book_preview(page)

    search_title = f"{book['title']}"

    message = MIMEMultipart("alternative")
    message["Subject"] = f"Твоите предложения за книги, като {search_title}..."
    message["From"] = sender_email
    message["To"] = receiver_email

    html = build_email_content(message["Subject"], recommendations)
    message.attach(MIMEText(html, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
