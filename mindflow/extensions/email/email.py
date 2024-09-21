from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from smtplib import SMTP
import re

def validate(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return email
    raise ValueError("Invalid email address")

class Oemail:
    def __init__(self, mindflow):
        
        special = {"yahoo.com": "smtp.mail.yahoo.com",
                   "outlook.com": "smtp-mail.outlook.com",
                   "hotmail.com": "smtp-mail.outlook.com",
                   "icloud.com": "smtp.mail.me.com"}
        
        config = mindflow.settings.get("oemail", {})
        
        self.email = validate(config.get("email"))
        self.password = config.get("password")
        self.smtp_port = 587
        self.smtp_server = (special.get(server)
                            if special.get(server := self.email.split("@")[1])
                            else server)
        
    def send(self, receiver_email, subject, body, attachments=[], cc=[], bcc=[]):
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg['Cc'] = ', '.join(cc)

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
                server.login(self.sender_email, self.password)
                text = msg.as_string()
                server.sendmail(self.sender_email, to_addrs, text)
                return {"status": f"Email successfully sent to `{receiver_email}`!"}
        except Exception as e:
            return {"status": f'Error: {e}'}
