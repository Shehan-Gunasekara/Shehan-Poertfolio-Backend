import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

sender_password =os.environ.get('SENDER_PASSWORD')
recipients_email=os.environ.get('SENDER_EMAIL')

def sendEmail(senderName, senderEmail, message, file):
    msg=MIMEMultipart()
    msg['From']=senderEmail
    msg['To']=recipients_email
    msg['Subject']="Portfolio Email from "+senderName

    body=message+"\n\n sender Email: "+senderEmail+"\n sender Name: "+senderName+"\n"
    msg.attach(MIMEText(body,'plain'))
    if file!=None: 
        attachment=MIMEApplication(file.read(),_subtype="txt")
        attachment.add_header('Content-Disposition','attachment',filename=file.filename)
        msg.attach(attachment)

    with smtplib.SMTP('smtp.gmail.com',587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(recipients_email,sender_password)
        smtp.send_message(msg)

