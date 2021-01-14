#Python 3.8.6
#Service Account: mssql-restore-test@ti-is-devenv-01.iam.gserviceaccount.com
#SET GOOGLE_APPLICATION_CREDENTIALS=C:\pythonVE\GCPResourceControl\ti-is-devenv-01-e494bc35aeae.json
#Install it as a Cloud Function
#gcloud functions deploy GCPResourceControl --entry-point main --runtime python37 --trigger-resource GCPResourceControlTopic --trigger-event google.pubsub.topic.publish --timeout 540s
#https://cloud.google.com/blog/products/application-development/how-to-schedule-a-recurring-python-script-on-gcp
#gcloud scheduler jobs create pubsub GCPResourceControl --schedule "0 */1 * * *" --topic GCPResourceControlTopic --message-body "This is a job that I run per hour!"
#https://cloud.google.com/community/tutorials/cloud-functions-rate-limiting
#Firebase
#https://medium.com/@wenxuan0923/upload-data-to-firebase-cloud-firestore-with-10-line-of-python-code-1877690a55c6
#https://rakibul.net/fb-realtime-db-python
#https://morioh.com/p/4dca3ded4cea

from emailmodule import *
import argparse
from googleapiclient.discovery import build #cloud api client library
import json
from datetime import datetime
from dateutil import relativedelta as rdelta
import config
from string import Template

# [START list_instances]
def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None
# [END list_instances]
# list_instances(cloudsql,"ti-is-devenv-01","us-west1-b")

# [START list_zones]
def list_zones(compute, project):
    result = compute.zones().list(project=project).execute()
    return result['items'] if 'items' in result else None
# [END list_instances]
# list_instances(cloudsql,"ti-is-devenv-01","us-west1-b")


# [START months_between]
def months_between(start_date,end_date):
    rd = rdelta.relativedelta(end_date,start_date)
    message="{0.years} years and {0.months} months".format(rd)
    return message
# [END months_between]
# months_between(datetime,datetime)

#Enable it if you want to try the script independent
# [START run]
def main(project_id='ti-is-devenv-01', email_dl='juan.cruz2@telusinternational.com', smtphost='172.17.64.124', wait=True):
    # Construct the service object for the interacting with the Cloud SQL Admin API.
    project=config.config_vars['project_id']
    #try:
    current_time = datetime.utcnow()
    log_message = Template('Function was triggered on $time')
    logging.info(log_message.safe_substitute(time=current_time))

    compute = build('compute','v1', cache_discovery=False)
    zones = list_zones(compute, project)
    vmsTakeCare = []
    vmTakeCare = {}
    #print('Compute Engine VMs in project %s:' % (project))
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
                                                vmTakeCare['External_IP']=access['natIP']
                                                vmTakeCare['Owner']=items['labels']['owner']
                                                vmTakeCare['Last_Start_Times']=datetime.fromisoformat(items['lastStartTimestamp']).date().strftime('%d/%m/%Y')
                                                vmTakeCare['Is_Preemptible']=items['scheduling']['preemptible']
                                                vmTakeCare['Months']=months_between(datetime.fromisoformat(items['lastStartTimestamp']).date(),datetime.now().date())
                                                if vmTakeCare['Is_Preemptible']== 'True':
                                                    vmTakeCare['Monthly_Cost']='1.46'
                                                else:
                                                    vmTakeCare['Monthly_Cost']='2.92'
                                                #if vmTakeCare:
                                                #    vmsTakeCare[items['name']]=vmTakeCare
                                                if vmTakeCare:
                                                    vmsTakeCare.append(vmTakeCare)
                                                #print('Zone %s:' % ( zone['name']))
                                                #print(items['name'])
                                                #print(access['natIP'])
                                                #print('owner:' + items['labels']['owner'])
                                                #print('lastStartTimestamp:' + items['lastStartTimestamp'])
                                                #print(vmTakeCare)
                                                #print(type(vmTakeCare))
                                    else:
                                        if items['name'].startswith('db'):
                                            vmTakeCare['Zone']=zone['name']
                                            vmTakeCare['Instance']=items['name']
                                            vmTakeCare['External_IP']=access['natIP']
                                            vmTakeCare['Owner']='dba'
                                            vmTakeCare['Last_Start_Times']=datetime.fromisoformat(items['lastStartTimestamp']).date().strftime('%d/%m/%Y')
                                            vmTakeCare['Is_Preemptible']=items['scheduling']['preemptible']
                                            vmTakeCare['Months']=months_between(datetime.fromisoformat(items['lastStartTimestamp']).date(),datetime.now().date())
                                            if vmTakeCare['Is_Preemptible']== 'True':
                                                vmTakeCare['Monthly_Cost']='1.46'
                                            else:
                                                vmTakeCare['Monthly_Cost']='2.92'
                                            #if vmTakeCare:
                                            #    vmsTakeCare[items['name']]=vmTakeCare
                                            if vmTakeCare:
                                                vmsTakeCare.append(vmTakeCare)
                                            #print('Zone %s:' % ( zone['name']))
                                            #print(items['name'])
                                            #print(access['natIP'])
                                            #print('owner:' + 'Unknow')
                                            #print('lastStartTimestamp:' + items['lastStartTimestamp'])
                                        else:
                                            vmTakeCare['Zone']=zone['name']
                                            vmTakeCare['Instance']=items['name']
                                            vmTakeCare['External_IP']=access['natIP']
                                            vmTakeCare['Owner']='Unknow'
                                            vmTakeCare['Last_Start_Times']=datetime.fromisoformat(items['lastStartTimestamp']).date().strftime('%d/%m/%Y')
                                            vmTakeCare['Is_Preemptible']=items['scheduling']['preemptible']
                                            vmTakeCare['Months']=months_between(datetime.fromisoformat(items['lastStartTimestamp']).date(),datetime.now().date())
                                            if vmTakeCare['Is_Preemptible']== 'True':
                                                vmTakeCare['Monthly_Cost']='1.46'
                                            else:
                                                vmTakeCare['Monthly_Cost']='2.92'
                                            #if vmTakeCare:
                                            #    vmsTakeCare[items['name']]=vmTakeCare
                                            if vmTakeCare:
                                                vmsTakeCare.append(vmTakeCare)

    sent = sendemail(vmsTakeCare,project,smtphost,email_dl)
    logging.info('GCP Compute Engine Verification Complete.')

    #except Exception as error:
    #    log_message = Template('$error').substitute(error=error)
    #    logging.error(log_message)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--project_id', default='ti-is-denvenv-01', help='Your Google Cloud project ID.')
    #parser.add_argument('--bucket_name', default='bucketname', help='Your Google Cloud Storage bucket name.')
    #parser.add_argument('--zone', default='us-west1-b', help='Cloud SQL zone to deploy to.')
    parser.add_argument('--email_dl', default='juan.cruz2@telusinternational.com', help='DL to send notification.')
    parser.add_argument('--smtphost', default='172.17.64.124', help='Email server')

    args = parser.parse_args()

    #main(args.project_id, args.bucket_name, args.zone, args.name, args.smtphost)
    main(args.project_id, args.email_dl, args.smtphost)
# [END run]
#python main.py --email_dl juan.cruz2@telusinternational.com --project_id ti-is-devenv-01
