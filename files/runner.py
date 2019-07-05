import argparse
import json
import logging
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-payload', '--payload', help='Payload from queue', required=True)
parser.add_argument('-apiKey', '--apiKey', help='The apiKey of the integration', required=True)
parser.add_argument('-opsgenieUrl', '--opsgenieUrl', help='The url', required=True)
parser.add_argument('-logLevel', '--logLevel', help='Level of log', required=True)
parser.add_argument('-playbook', '--playbook', help='Ansible Playbook', required=True)

args = vars(parser.parse_args())

logging.basicConfig(stream=sys.stdout, level=args['logLevel'])

queue_message_string = args['payload']
queue_message = json.loads(queue_message_string)
api_key = args['apiKey']

def parse_from_details(key):
    if key in alert_from_opsgenie["details"].keys():
        return alert_from_opsgenie["details"][key]
    return ""

alert_id = queue_message["alert"]["alertId"]
entity = queue_message["alert"]['entity']
inventory = "/var/ansible/" + queue_message["alert"]["details"]["inventory"] + ".py"
alert_api_url = args['opsgenieUrl'] + "/v2/alerts/" + alert_id
ansible_dir = "/var/log/runner/" + alert_id
playbook = args['playbook']

import os
# define the name of the directory to be created
path = ansible_dir

# define the access rights
access_rights = 0o755

try:
    os.makedirs(path, access_rights)
except OSError:
    print ("Creation of the directory %s failed" % path)
else:
    print ("Successfully created the directory %s" % path)


import ansible_runner
r = ansible_runner.run(private_data_dir=ansible_dir, limit=entity, inventory=inventory, playbook=playbook, extravars={'alert_api_url': alert_api_url, 'api_key': api_key })
print("{}: {}".format(r.status, r.rc))
print("Final status:")
print(r.stats)
