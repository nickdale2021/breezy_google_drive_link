import smtplib
import os
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from os.path import basename

app_mail_id = os.environ.get('APP_MAIL_ID')
app_mail_password = os.environ.get('APP_MAIL_PASSWORD')


def send_mail(name, email, attachments):
    body = f"""
            <html>
            <body><p>Dear {name},</p>
            <p></p>
            <p>Please find the attached file with updated resume URLs</p>
            <p></p>
            <p>Thanks & Regards,<br>
            Breezy Bot<br></p>
            </body></html>
            """
    subject = "Your file from Breezy App"
    print(f'Received request to send logs to {email}')
    if app_mail_id is None or app_mail_password is None:
        print('Not sending mail because email/password is not configured in os variables')
        return None
    print("Creating connection with SMTP host")
    start = time.time()
    session = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
    print("Time taken for connection:", time.time()-start)
    print("Starting TLS service")
    start = time.time()
    session.starttls()
    print("Time taken for TLS:", time.time() - start)
    print("Logging in for Email!")
    start = time.time()
    session.login(app_mail_id, app_mail_password)
    print("Time taken for Login:", time.time() - start)
    print("Logged In!")
    message = MIMEMultipart()
    message['From'] = app_mail_id
    message['To'] = email
    message['Bcc'] = app_mail_id
    message['Subject'] = subject
    message.attach(MIMEText(body, 'html'))
    if len(attachments) > 0:
        for file_name in attachments:
            with open(file_name, "rb") as f:
                part = MIMEApplication(
                    f.read(),
                    Name=basename(file_name)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file_name)
            message.attach(part)
    print("Sending mail!")
    start = time.time()
    session.send_message(message)
    print("Time taken to send mail:", time.time() - start)
    print("Email sent to:", email)
    session.quit()
    # if len(attachments) > 0:
    #     for i in attachments:
    #         if os.path.exists(i):
    #             os.remove(i)


def send_mail_self(attachments):
    body = f"""
            <html>
            <body><p>Dear Self,</p>
            <p></p>
            <p>Please find the attached file with updated resume URLs</p>
            <p></p>
            <p>Thanks & Regards,<br>
            Breezy Bot<br></p>
            </body></html>
            """
    subject = "Your file from Breezy App"
    print(f'Received request to send logs to {app_mail_id}')
    if app_mail_id is None or app_mail_password is None:
        print('Not sending mail because email/password is not configured in os variables')
        return None
    print("Creating connection with SMTP host")
    start = time.time()
    session = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
    print("Time taken for connection:", time.time()-start)
    print("Starting TLS service")
    start = time.time()
    session.starttls()
    print("Time taken for TLS:", time.time() - start)
    print("Logging in for Email!")
    start = time.time()
    session.login(app_mail_id, app_mail_password)
    print("Time taken for Login:", time.time() - start)
    print("Logged In!")
    message = MIMEMultipart()
    message['From'] = app_mail_id
    message['To'] = app_mail_id
    message['Subject'] = subject
    message.attach(MIMEText(body, 'html'))
    if len(attachments) > 0:
        for file_name in attachments:
            with open(file_name, "rb") as f:
                part = MIMEApplication(
                    f.read(),
                    Name=basename(file_name)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file_name)
            message.attach(part)
    print("Sending mail!")
    start = time.time()
    session.send_message(message)
    print("Time taken to send mail:", time.time() - start)
    print("Email sent to:", app_mail_id)
    session.quit()
    # if len(attachments) > 0:
    #     for i in attachments:
    #         if os.path.exists(i):
    #             os.remove(i)
