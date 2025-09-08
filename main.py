import functions_framework
import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# fetch the clients list from GitHub
CONFIG_URL = "https://raw.githubusercontent.com/username/repo/main/clients/clients_config.py"

@functions_framework.http
def hello_http(request):
    sender = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")
    if not sender or not password:
        return "missing email credentials"

    # get CLIENTS list from GitHub
    response = requests.get(CONFIG_URL)
    namespace = {}
    exec(response.text, namespace)
    clients = namespace["CLIENTS"]

    results = []

    for url in clients:
        try:
            response = requests.get(url)
            namespace = {}
            exec(response.text, namespace)  # loads get_portfolio(), recipient_email, client_name
            portfolio = namespace["get_portfolio"]()
            recipient = namespace["recipient_email"]
            client_name = namespace.get("client_name", "Client")
        except Exception as e:
            results.append(f"{url}: failed to load - {e}")
            continue

        # build email
        html = f"<h2>{client_name} Portfolio Allocations</h2><table border='1'><tr><th>Asset</th><th>Allocation</th></tr>"
        for asset, alloc in portfolio.items():
            html += f"<tr><td>{asset}</td><td>{alloc}%</td></tr>"
        html += "</table>"

        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = f"{client_name} Portfolio Update"
        msg.attach(MIMEText(html, "html"))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
            server.quit()
            results.append(f"Email sent to {recipient}")
        except Exception as e:
            results.append(f"Failed to send to {recipient}: {e}")

    return "\n".join(results)
