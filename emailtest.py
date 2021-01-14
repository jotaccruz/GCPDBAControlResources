import smtplib
import pandas as pd
import logging

from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import argparse
from googleapiclient.discovery import build #cloud api client library
import json
from datetime import datetime
from dateutil import relativedelta as rdelta
import config
from string import Template

def sendemail(message,proj):
    print(message)
    me = 'juan.cruz2@telusinternational.com'
    you = 'juan.cruz2@telusinternational.com'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = proj + f' - Google Compute Engine - Be aware of!!!'
    msg['From'] = 'GCP-ResourceControl@telusinternational.com'
    msg['To'] = 'juan.cruz2@telusinternational.com'

    part0 = MIMEText("""Hello DBA Team\n\nPlease be aware of this following:\n\n""",'plain')
    part1 = MIMEText(""""We strive to achieve cost efficiency for Telus International, avoiding unnecessary charges""",'plain')

    msg.attach(part1)

    s = smtplib.SMTP('172.17.64.124')
    sent = s.send_message(msg)
    s.quit()

    return sent


def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None


def list_zones(compute, project):
    result = compute.zones().list(project=project).execute()
    return result['items'] if 'items' in result else None

def months_between(start_date,end_date):
    rd = rdelta.relativedelta(end_date,start_date)
    message="{0.years} years and {0.months} months".format(rd)
    return message

def email(project_id='ti-is-devenv-01', bucket_name='dba-freenas', zone='us-west1-b', name='test', wait=True):
    project=config.config_vars['project_id']

    current_time = datetime.utcnow()
    log_message = Template('Cloud Function was triggered on $time')
    logging.info(log_message.safe_substitute(time=current_time))

    compute = build('compute','v1', cache_discovery=False)
    zones = list_zones(compute, project)
    vmsTakeCare = []
    vmTakeCare = {}
    print('Compute Engine VMs in project %s:' % (project))
    for zone in zones:
        instances = list_instances(compute, project, zone['name'])
        if instances:
            for items in instances:
                for nics in items['networkInterfaces']:
                    if 'accessConfigs' in nics:
                        for access in nics['accessConfigs']:
                            if access['name'] == 'External NAT':
                                if 'natIP' in access:
                                    vmTakeCare = {}
                                    if 'labels' in items:
                                        if 'owner' in items['labels']:
                                            if items['labels']['owner']== 'dba':
                                                vmTakeCare['Zone']=zone['name']
                                                vmTakeCare['Instance']=items['name']
                                                vmTakeCare['natIP']=access['natIP']
                                                vmTakeCare['Owner']=items['labels']['owner']
                                                vmTakeCare['LastStartTimes']=datetime.fromisoformat(items['lastStartTimestamp']).date()
                                                vmTakeCare['IsPreemptible']=items['scheduling']['preemptible']
                                                vmTakeCare['Months']=months_between(datetime.fromisoformat(items['lastStartTimestamp']).date(),datetime.now().date())
                                                if vmTakeCare['IsPreemptible']== 'True':
                                                    vmTakeCare['MonthlyCost($)']='1.46'
                                                else:
                                                    vmTakeCare['MonthlyCost($)']='2.92'
                                                if vmTakeCare:
                                                    vmsTakeCare.append(vmTakeCare)
                                    else:
                                        if items['name'].startswith('db'):
                                            vmTakeCare['Zone']=zone['name']
                                            vmTakeCare['Instance']=items['name']
                                            vmTakeCare['natIP']=access['natIP']
                                            vmTakeCare['Owner']='Unknow'
                                            vmTakeCare['LastStartTimes']=datetime.fromisoformat(items['lastStartTimestamp']).date()
                                            vmTakeCare['IsPreemptible']=items['scheduling']['preemptible']
                                            vmTakeCare['Months']=months_between(datetime.fromisoformat(items['lastStartTimestamp']).date(),datetime.now().date())
                                            if vmTakeCare['IsPreemptible']== 'True':
                                                vmTakeCare['MonthlyCost($)']='1.46'
                                            else:
                                                vmTakeCare['MonthlyCost($)']='2.92'
                                            if vmTakeCare:
                                                vmsTakeCare.append(vmTakeCare)
    sent = sendemail(vmsTakeCare,project)
    print(sent)
    #logging.info('GCP Compute Engine Verification Complete.')

def printer():
    sent=sendemail("Hola","Hola")
    print(sent)

printer()
email('ti-is-devenv-01', 'dba-freenas', 'us-west1-b', 'test', wait=True)
