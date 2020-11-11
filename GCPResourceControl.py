#Service Account: mssql-restore-test@ti-is-devenv-01.iam.gserviceaccount.com
#SET GOOGLE_APPLICATION_CREDENTIALS=C:\pythonVE\gcp-alerts-management\ti-is-devenv-01-e494bc35aeae.json

import argparse
from googleapiclient.discovery import build #cloud api client library
import json

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

#Enable it if you want to try the script independent
# [START run]
def main(project, bucket, zone, sqlinstance_name, wait=True):
    # Construct the service object for the interacting with the Cloud SQL Admin API.
    compute = build('compute','v1')
    zones = list_zones(compute, project)
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
                                    if 'labels' in items:
                                        if 'owner' in items['labels']:
                                            if items['labels']['owner']== 'dba':
                                                print('Zone %s:' % ( zone['name']))
                                                print(items['name'])
                                                print(access['natIP'])
                                                print('owner:' + items['labels']['owner'])
                                                print('lastStartTimestamp:' + items['lastStartTimestamp'])
                                    else:
                                        if items['name'].startswith('db'):
                                            print('Zone %s:' % ( zone['name']))
                                            print(items['name'])
                                            print(access['natIP'])
                                            print('lastStartTimestamp:' + items['lastStartTimestamp'])


    if wait:
        input()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('project_id', help='Your Google Cloud project ID.')
    parser.add_argument('bucket_name', help='Your Google Cloud Storage bucket name.')
    parser.add_argument('--zone', default='us-west1-a', help='Cloud SQL zone to deploy to.')
    parser.add_argument('--name', default='sql1', help='New instance name.')

    args = parser.parse_args()

    main(args.project_id, args.bucket_name, args.zone, args.name)
# [END run]
#python GCPResourceControl.py --name sqlrestore --zone us-west1-b ti-is-devenv-01 dba-freenas
