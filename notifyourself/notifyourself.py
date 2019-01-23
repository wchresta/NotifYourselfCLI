#!/usr/bin/env python

# Copyright (C) 2019 Wanja Chresta
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
try:
    import configparser
except ImportError: # configparser not found; maybe we are python2
    import ConfigParser as configparser

import requests

import os
import sys
import string

DEFAULT_CONFIG_PATH=os.path.join(os.path.expanduser("~"), '.config', 'notifyourself', 'config.ini')
DEFAULT_CONFIGURATION="""# notifYourself configuration
#
# You can define multiple targets with different tokens and use
# the -t flag to choose one. Default is the DEFAULT target.

[DEFAULT]
# Use your notifYourself app to find this token
token=

# [ANOTHER_TARGET]
# token=ANOTHER_TARGETS_TOKEN
"""

ERRNO_CONFIG=1 # Configuration/Argument error
ERRNO_REQUEST=2 # Error while making the request

TOKEN_CHARACTERS=string.ascii_letters + string.digits + "_-:"
TARGET_CHARACTERS=string.ascii_letters + string.digits + "_"

NOTIFYOURSELF_SERVICE="https://us-central1-notifyourself.cloudfunctions.net/notifyourself"

def is_token(token):
    return all(c in TOKEN_CHARACTERS for c in token)

def is_target(target):
    return all(c in TARGET_CHARACTERS for c in target)

def is_printable(s):
    return all(c in string.printable for c in s)

def fail(reason, error_code=ERRNO_CONFIG):
    sys.stderr.write(reason+"\n")
    sys.exit(error_code)

def get_arguments():
    parser = argparse.ArgumentParser(description="Send a notification to your phone")
    parser.add_argument('title', help="Notification title")
    parser.add_argument('body', nargs='?', help="Longer message in the body of the notification")
    target_group = parser.add_mutually_exclusive_group(required=False)
    target_group.add_argument('-T','--token', help="Use this token to send the message")
    target_group.add_argument('-t','--target', default="DEFAULT", help="Send message to this target phone specified in the config file")
    parser.add_argument('--config', default=DEFAULT_CONFIG_PATH, help="Configfile to use instead of default")

    args = parser.parse_args()
    # Sanitize some of the input

    if not is_target(args.target):
        fail("Target must be alphanumerical")

    return args


def write_default_config():
    try:
        # Make sure config folder exists
        os.makedirs(os.path.dirname(DEFAULT_CONFIG_PATH))
        # Write default configuration
        fh = open(DEFAULT_CONFIG_PATH,'w')
        fh.write(DEFAULT_CONFIGURATION)
        fh.close()
    except PermissionError:
        # Something is wrong, but writing default configurations
        # is not that important so fail silently
        pass

def get_token(args, config):
    if args.token:
        # User gave us a token from the command line. Use that one
        return args.token
    else:
        # User hasn't given us a token, but he gave us a target.
        # Read it from the command line
        try:
            return config.get(args.target, "token")
        except configparser.NoSectionError:
            fail("Couldn't find [{}] section in config file {}"
                    .format(args.target, args.config))
        except configparser.NoOptionError:
            fail("Couldn't find token in config file {}"
                    .format(args.config))

def get_config(args):
    config = configparser.ConfigParser()

    # Check if configfile exists
    if os.path.exists(args.config):
        config.read(args.config)
    elif args.config == DEFAULT_CONFIG_PATH:
        # Configfile doesn't exist, so we create one
        write_default_config()

    config.token = get_token(args, config)
  
    # Check if token is a valid token
    if not is_token(config.token):
        fail("Token contains invalid characters. Check configuration")

    # We have sorted out the token. Now check the actual message contents
    config.title = args.title
    config.body = args.body

    # Do some checks regarding the title and body
    if len(config.title) > 200:
        fail("Title is too long; maximal length is 200")
    if not is_printable(config.title):
        fail("Title contains non-printable characters. This is not allowed")
    if config.body is not None:
        if len(config.body) > 500:
            fail("Body is too long; maximal length is 500")
        if not is_printable(config.body):
            fail("Body contains non-printable characters. This is not allowed")

    # Here, we have a valid config.token, config.title and config.body
    # We are ready to go :)
    return config

def send_notification(config):
    request_data = {
        'token': config.token,
        'title': config.title,
    }

    # If a body is give, we send that too
    if config.body is not None:
        request_data['body'] = config.body

    response = requests.post(NOTIFYOURSELF_SERVICE, data=request_data)

    if response.status_code == 200:
        # All good :)
        print("Notification sent")
        return

    # If we reach here; something went wrong. Let's try to figure out what
    if response.status_code == 400:
        fail("Server responsed with an error:\n> {}".format(response.text),
                ERRNO_REQUEST)
    elif response.status_code == 415:
        fail("Protocol error. Something is wrong; maybe try later?", ERRNO_REQUEST)

    # If we reach this; we don't know what's wrong
    fail("Unexpected error. Something is wrong; maybe try later?\n> {}"
            .format(response.text, ERRNO_REQUEST))


def main():
    args = get_arguments()
    config = get_config(args)
    send_notification(config)

if __name__=="__main__":
    main()
