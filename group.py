#!/usr/bin/python

import os
import time
import sys
import requests
import json
import base64
import getopt

from client import Client

###############################################################
# Inputs required to run. Specify here or in the environment. #
###############################################################
# PW_PLATFORM_HOST is the Parallel Works ACTIVATE platform you are connecting to.
# For example, for sites starting with https://activate.parallel.works
# this setting would be "activate.parallel.works"

#os.environ['PW_PLATFORM_HOST'] = 'activate.parallel.works'

# PW_API_KEY should be set to your API key, you can generate a new key
# by clicking on your username in the Parallel Works ACTIVATE platform,
# go to the Authentication tab, click on API Keys, and choose to add a key.
# Copy the generated key and copy it here, or set it in your environment directly.

#os.environ['PW_API_KEY'] = "pwt_..."

def usage(state):
    if state is None:
        exit_value = 0
    elif state == "error":
        exit_value = 1
    else:
        exit_value = 2

    print('Usage: %s [add|del|delete] group user' % os.path.basename(__file__) )
    print('  Modifies a group to adds or remove a user via the Parallel Works API.')
    print('  Requires PW_PLATFORM_HOST and PW_API_KEY to be set in the environment.')
    print('  The environment variables can also be set in this script, see commented lines.')
    sys.exit(exit_value)

if __name__ == '__main__':
   # get input settings
    if os.environ.get('PW_PLATFORM_HOST') is not None:
        pw_url = 'https://' + os.environ['PW_PLATFORM_HOST']
    else:
        pw_url = 'https://activate.parallel.works'
    print(f'Updating the platform at: {pw_url}')
    if os.environ.get('PW_API_KEY') is not None:
        apikey = os.environ['PW_API_KEY']
    else:
        print('The PW_API_KEY environment variable is not set.')
        usage("error")

   # check for the help flag
    opts, args = getopt.getopt(sys.argv[1:], "help", ["help"])
    for o, a in opts:
        if o in ('-h', '-help', '--help'):
            usage(None)
        else:
            print("Unknown option.")
            usage("error")
    if len(sys.argv) < 4 or len(sys.argv) > 4:
        usage("error")

    command, group, user = sys.argv[1:]

    print(f'command: {command}\n  group: {group}\n   user: {user}')

    if command not in ("add", "del", "delete"):
        print(f'Unknown command "{command}"')
        usage("error")

    c = Client(pw_url, apikey)

    if command == "add":
        output = c.add_to_group(group, user)
        print(output)
    elif command in ("del", "delete"):
        output = c.delete_from_group(group, user)
        print(output)

# some other things you can do with this script
'''
    namedGroup = c.get_group("rtx-aws")
    print(namedGroup)

    groupID = c.get_gid("rtx-aws")
    print(groupID)
'''



