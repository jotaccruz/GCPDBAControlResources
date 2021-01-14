# Import smtplib for the actual sending function
import smtplib
import pandas as pd
import logging
import json

# Import database module.
import firebase_admin
from firebase_admin import db
from firebase_admin import credentials

# Import the email modules we'll need
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Open the plain text file whose name is in textfile for reading.
def sendemail(message,proj,smtphost,email_dl):

    # me == the sender's email address
    # you == the recipient's email address
    me = 'GCP-ResourceControl@telusinternational.com'
    #you = 'juan.cruz2@telusinternational.com'
    you = email_dl

    msg = MIMEMultipart('alternative')
    msg['Subject'] = proj + f' - GCE - External IPs assigned Report'
    msg['From'] = me
    msg['To'] = you

    #msg = EmailMessage()

    df = pd.DataFrame(message)

    # Fetch the service account key JSON file contents
    #cred = credentials.Certificate('C:\\pythonVE\\GCPResourceControl\\ti-is-devenv-01-firebase-adminsdk-9jsq8-efb770c294.json')

    # Initialize the app with a service account, granting admin privileges
    #firebase_admin.initialize_app(cred, {
    #    'databaseURL': 'https://ti-is-devenv-01.firebaseio.com'
    #})

    # As an admin, the app has access to read and write all data, regradless of Security Rules
    #ref = db.reference('/')
    #print(ref.get())

    #users_ref = ref.child('CloudSQLs')

    #test={'to': ['juan.cruz2@telusinternational.com'],
    #'message': {
    #    'subject': 'Hello from Firebase!',
    #    'text': 'This is the plaintext section of the email body.',
    #    'html': 'This is the <code>HTML</code> section of the email body.',
    #}}

    #users_ref.set(test)
    #print(json)
    #print(message)

    #df = df.fillna(' ').T

    #msg.set_content("""Hello DBA Team\n\nPlease be aware of this following:\n\n""" + df.to_html())

    part0 = MIMEText("""Hello DBA Team\n\nPlease be aware of this following:\n\n""",'plain')
    part1 = MIMEText(""""We strive to achieve cost efficiency for Telus International, avoiding unnecessary charges""",'plain')
    part2 = MIMEText(df.sort_values(by=['Owner'], ascending=False).reset_index(drop=True).to_html(),'html')

    msg.attach(part1)
    msg.attach(part2)

    # Send the message via our own SMTP server.

    try:
        server = smtplib.SMTP(smtphost)
    except:
        print("Wrong")

    sent = server.send_message(msg)
    server.quit()

    return sent
