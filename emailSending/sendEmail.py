import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

sender_email="shehangunasekara2019@gmail.com"
sender_password ="jnggfnyovndimuax"
recipients_email="shehangunasekara2019@gmail.com"

def sendEmail():
    msg=MIMEMultipart()
    msg['From']=sender_email
    msg['To']=recipients_email
    msg['Subject']="Test Email"

    body="This is a test email"
    msg.attach(MIMEText(body,'plain'))

    filename="emailSending/ED187039.pdf"
    with open(filename,'rb') as f:
        attachment=MIMEApplication(f.read(),_subtype="txt")
        attachment.add_header('Content-Disposition','attachment',filename=filename)
        msg.attach(attachment)

    with smtplib.SMTP('smtp.gmail.com',587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(sender_email,sender_password)
        smtp.send_message(msg)

