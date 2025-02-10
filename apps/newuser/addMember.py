#! /usr/local/bin/python3

# See /root/root-work/auto-list-update for group name query script and README

import json
import os
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Scopes required for accessing Google Groups (Cloud Identity API)
SCOPES = ["https://www.googleapis.com/auth/cloud-identity.groups"]

# Path to the Service Account JSON key file
SERVICE_ACCOUNT_FILE = "/webserver/csua-backend/csua-rso-mail-manager-a2ae498a619c.json"

# The google group's ID, found by using list users with the google group email
# this is the ID for: csua-members@lists.berkeley.edu
GROUP_NAME = "groups/01tuee740igmbim"


def authenticate():
    # Authenticate using a service account
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return creds


def create_service():
    creds = authenticate()
    service = build("cloudidentity", "v1", credentials=creds)
    return service


def create_google_group_membership(service, member_key):
    try:
        membership = {
            "preferredMemberKey": {"id": member_key},
            "roles": [{"name": "MEMBER"}],
        }
        response = (
            service.groups()
            .memberships()
            .create(parent=GROUP_NAME, body=membership)
            .execute()
        )
        print(response)
    except Exception as e:
        print(e)


def add_member(email):
    # Add an email to the Google Group
    service = create_service()
    create_google_group_membership(service, email)


def main():
    add_member(sys.argv[1])


if __name__ == "__main__":
    sys.exit(main())
