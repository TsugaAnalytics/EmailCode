import functions_framework
import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@functions_framework.http
def hello_http(request):
    url = os.environ.get("PORTFOLIO_URL")
    if not url:
        return "PORTFOLIO_URL environment variable not set"

    response = requests.get(url)
    exec(response.text, globals())  # executes get_portfolio() from client file
    portfolio = get_portfolio()

    html = "<h2>Portfolio Allocations</h2><table border='1'><tr><th>Asset</th><th>Allocation</th></tr>"
    for asset, alloc in portfolio.items():
        html += f"<tr><td>{asset}</td><td>{alloc}%</td></tr>"
    html += "</table>"

    sender = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("jndrmvfbnpfuazav")
    recipient = os.environ.get("RECIPIENT_EMAIL")

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
    return "email sent successfully!"
