import requests
import urllib3
from bs4 import BeautifulSoup
import json
import smtplib
import os
from email.mime.text import MIMEText

URL = "https://www.nhg.at/angebot/"

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_known():
    try:
        with open("known_flats.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_known(data):
    with open("known_flats.json", "w") as f:
        json.dump(data, f)

def send_mail(new_items):
    body = "Neue Wohnungen gefunden:\n\n"
    for item in new_items:
        body += f"{item}\n"

    msg = MIMEText(body)
    msg["Subject"] = "Neue GEWOG Wohnung"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASSWORD)
    server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
    server.quit()

def scrape():
    r = requests.get(URL, timeout=30, verify=False)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    items = []
    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        href = a.get("href")
        if text and href and "angebot" in href:
            items.append(f"{text} | {href}")

    return list(set(items))

def main():
    known = load_known()
    current = scrape()

    new = [x for x in current if x not in known]

    if new:
        send_mail(new)

    save_known(current)

if __name__ == "__main__":
    main()
