# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.message import EmailMessage

# Open the plain text file whose name is in textfile for reading.
msg = EmailMessage()
msg.set_content("Hello")

# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = f'The contents of '
msg['From'] = 'juan.cruz2@telusinternational.com'
msg['To'] = 'juan.cruz2@telusinternational.com'

# Send the message via our own SMTP server.
s = smtplib.SMTP('172.17.64.124')
s.send_message(msg)
s.quit()
