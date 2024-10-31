from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from smtplib import SMTP
import re

from ...utils import ROOT_DIR
from pathlib import Path

from typing import TypedDict

class EmailKwargs(TypedDict):
    email: str
    password: str

def validate(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return email
    raise ValueError("Invalid email address")

class Email:
    def __init__(self, email: str = None, password: str = None):
        
        special = {"yahoo.com": "smtp.mail.yahoo.com",
                   "outlook.com": "smtp-mail.outlook.com",
                   "hotmail.com": "smtp-mail.outlook.com",
                   "icloud.com": "smtp.mail.me.com"}
        
        if email is None or password is None:
            raise KeyError(f"Missing credentials for `email` extension!\n{email} {password}")
        
        self.email = validate(email)
        self.password = password
        self.smtp_port = 587
        self.smtp_server = (special.get(server)
                            if special.get(server := self.email.split("@")[1])
                            else "smtp." + server)
        
    @staticmethod
    def load_instructions():
        with open(Path(ROOT_DIR, "extensions", "email", "docs", "instructions.md"), "r") as f:
            return f.read()
        
    def send(self, receiver_email, subject, body, attachments=[], cc=[], bcc=[]):
        msg = MIMEMultipart()
        
        try:
            msg['To'] = validate(receiver_email)
        except Exception as e:
            return {"status": f'Error: {e}'}
        
        msg['From'] = self.email
        msg['Subject'] = subject
        
        try:
            msg['Cc'] = ', '.join([validate(addr) for addr in cc])
        except Exception as e:
            return {"status": f'Error: {e}'}

        msg.attach(MIMEText(body, 'plain'))

        for file in attachments:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(file, 'rb').read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={file}')
            msg.attach(part)

        to_addrs = [receiver_email] + cc + bcc

        try:
            with SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                text = msg.as_string()
                server.sendmail(self.email, to_addrs, text)
                return {"status": f"Email successfully sent to `{receiver_email}`!"}
        except Exception as e:
            return {"status": f'Error: {e}'}
