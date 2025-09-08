import functions_framework
import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# list of clients: (raw github url, recipient email)
clients = [
    (os.environ.get("CLIENT1_URL"), "client1@example.com"),
    (os.environ.get("CLIENT2_URL"), "client2@example.com"),
    # add more as needed
]

@functions_framework.http
def hello_http(request):
    sender = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")

    for url, recipient in clients:
        if not url:
            continue
        response = requests.get(url)
        exec(response.text, globals())
        portfolio = get_portfolio()

        html = "<h2>Portfolio Allocations</h2><table border='1'><tr><th>Asset</th><th>Allocation</th></tr>"
        for asset, alloc in portfolio.items():
            html += f"<tr><td>{asset}</td><td>{alloc}%</td></tr>"
        html += "</table>"

        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = "Portfolio Update"
        msg.attach(MIMEText(html, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()

    return "emails sent successfully!"
