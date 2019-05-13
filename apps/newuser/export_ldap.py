"""
export_ldap.py

Use this script to export the info from the LDAP server.

Move the outputs of the script to the fixtures directory to run them with the newuser test suite.

https://ldap3.readthedocs.io/mocking.html#a-complete-example
"""
import json
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, MOCK_SYNC

INFO_OUTPUT = "csua_ldap_info.json"
SCHEMA_OUTPUT = "csua_ldap_schema.json"
ENTRIES_OUTPUT = "csua_ldap_entries.json"

if __name__ == "__main__":
    REAL_SERVER = "ldaps://ldap.csua.berkeley.edu"

    # Retrieve server info and schema from a real server
    server = Server(REAL_SERVER, get_info=ALL)
    connection = Connection(server, auto_bind=True)

    # Store server info and schema to json files
    server.info.to_file(INFO_OUTPUT)
    server.schema.to_file(SCHEMA_OUTPUT)

    # Read entries from a portion of the DIT from real server and store them in a json file
    if connection.search(
        "dc=csua,dc=berkeley,dc=edu", "(objectclass=*)", attributes=ALL_ATTRIBUTES
    ):
        raw_entries = connection.response_to_json(raw=True)
        entries = json.loads(raw_entries)
        filtered_entries = {
            "entries": [
                i
                for i in entries["entries"]
                if "posixAccount" not in i["attributes"]["objectClass"]
                # don't add the accounts
            ]
        }
        with open(ENTRIES_OUTPUT, "w") as f:
            json.dump(filtered_entries, f, indent=2)
    else:
        raise RuntimeError("ldap search failed!")

        # Close the connection to the real server
    connection.unbind()

    # Create a fake server from the info and schema json files
    fake_server = Server.from_definition(
        "csua_mock", INFO_OUTPUT, SCHEMA_OUTPUT
    )

    # Create a MockSyncStrategy connection to the fake server
    fake_connection = Connection(fake_server, client_strategy=MOCK_SYNC)

    # Populate the DIT of the fake server
    fake_connection.strategy.entries_from_json(ENTRIES_OUTPUT)

    # Add a fake user for Simple binding
    fake_connection.strategy.add_entry(
        "cn=django_test_user,ou=People,dc=csua,dc=berkeley,dc=edu",
        {"uid": "django_test_user", "userPassword": "P4SSW0RD!"},
    )

    # Bind to the fake server
    fake_connection.bind()
