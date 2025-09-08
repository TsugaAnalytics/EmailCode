import functions_framework
import requests
import os
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@functions_framework.http
def hello_http(request):
    # --- get sender info ---
    sender = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")
    if not sender or not password:
        return "missing email environment variables"

    # --- get config from GitHub ---
    config_url = os.environ.get("CLIENTS_CONFIG_URL")
    if not config_url:
        return "CLIENTS_CONFIG_URL environment variable not set"

    response = requests.get(config_url)
    if response.status_code != 200:
        return f"failed to fetch config: {response.text}"
    clients_config = json.loads(response.text)

    results = []

    # --- loop through all clients ---
    for client_name, info in clients_config.items():
        file_url = os.environ.get(f"{client_name.upper()}_URL") or info["file"]
        recipient = info["email"]

        try:
            # fetch and execute portfolio file
            portfolio_response = requests.get(file_url)
            exec(portfolio_response.text, globals())
            portfolio = get_portfolio()
        except Exception as e:
            results.append(f"{client_name}: failed to load portfolio - {e}")
            continue

        # format email
        html = "<h2>Portfolio Allocations</h2><table border='1'><tr><th>Asset</th><th>Allocation</th></tr>"
        for asset, alloc in portfolio.items():
            html += f"<tr><td>{asset}</td><td>{alloc}%</td></tr>"
        html += "</table>"

        # send email
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
            results.append(f"{client_name}: email sent successfully")
        except Exception as e:
            results.append(f"{client_name}: failed to send email - {e}")

    return "\n".join(results)
