# -*- coding: utf-8 -*-
###
# (C) Copyright (2012-2017) Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###

from pprint import pprint
from hpOneView.oneview_client import OneViewClient
from hpOneView.exceptions import HPOneViewException
from config_loader import try_load_from_file

# This example is compatible only for C7000 enclosures

config = {
    "ip": "<oneview_ip>",
    "credentials": {
        "userName": "<username>",
        "password": "<password>"
    }
}

# Declare a CA signed certificate file path.
certificate_file = ""

# Try load config from a file (if there is a config file)
config = try_load_from_file(config)

# The hostname, enclosure group URI, username, and password must be set on the configuration file
options = {
    "enclosureGroupUri": config['enclosure_group_uri'],
    "hostname": config['enclosure_hostname'],
    "username": config['enclosure_username'],
    "password": config['enclosure_password'],
    "licensingIntent": "OneView"
}

oneview_client = OneViewClient(config)

# Add an Enclosure
enclosure = oneview_client.enclosures.add(options)
enclosure_uri = enclosure['uri']
print("Added enclosure '{name}'.\n  URI = '{uri}'".format(**enclosure))

# Perform a patch operation, replacing the name of the enclosure
enclosure_name = enclosure['name'] + "-Updated"
print("Updating the enclosure to have a name of " + enclosure_name)
enclosure = oneview_client.enclosures.patch(enclosure_uri, 'replace', '/name', enclosure_name)
print("  Done.\n  URI = '{uri}', name = {name}".format(**enclosure))

# Find the recently added enclosure by name
print("Find an enclosure by name")
enclosure = oneview_client.enclosures.get_by('name', enclosure['name'])[0]
print("  URI = '{uri}'".format(**enclosure))

# Get by URI
print("Find an enclosure by URI")
enclosure = oneview_client.enclosures.get(enclosure_uri)
pprint(enclosure)

# Get all enclosures
print("Get all enclosures")
enclosures = oneview_client.enclosures.get_all()
for enc in enclosures:
    print('  {name}'.format(**enc))

# Update configuration
print("Reapplying the appliance's configuration on the enclosure")
try:
    oneview_client.enclosures.update_configuration(enclosure_uri)
    print("  Done.")
except HPOneViewException as e:
    print(e.msg)

print("Retrieve the environmental configuration data for the enclosure")
try:
    environmental_configuration = oneview_client.enclosures.get_environmental_configuration(enclosure_uri)
    print("  Enclosure calibratedMaxPower = {calibratedMaxPower}".format(**environmental_configuration))
except HPOneViewException as e:
    print(e.msg)

# Refresh the enclosure
print("Refreshing the enclosure")
try:
    refresh_state = {"refreshState": "RefreshPending"}
    enclosure = oneview_client.enclosures.refresh_state(enclosure_uri, refresh_state)
    print("  Done")
except HPOneViewException as e:
    print(e.msg)

# Get the enclosure script
print("Get the enclosure script")
try:
    script = oneview_client.enclosures.get_script(enclosure_uri)
    pprint(script)
except HPOneViewException as e:
    print(e.msg)

# Buid the SSO URL parameters
print("Build the SSO (Single Sign-On) URL parameters for the enclosure")
try:
    sso_url_parameters = oneview_client.enclosures.get_sso(enclosure_uri, 'Active')
    pprint(sso_url_parameters)
except HPOneViewException as e:
    print(e.msg)

# Get Statistics specifying parameters
print("Get the enclosure statistics")
try:
    enclosure_statistics = oneview_client.enclosures.get_utilization(enclosure_uri,
                                                                     fields='AveragePower',
                                                                     filter='startDate=2016-06-30T03:29:42.000Z',
                                                                     view='day')
    pprint(enclosure_statistics)
except HPOneViewException as e:
    print(e.msg)

# Create a Certificate Signing Request (CSR) for the enclosure.
bay_number = 1  # Required for C7000 enclosure
csr_data = {
    "type": "CertificateDtoV2",
    "organization": "",
    "organizationalUnit": "",
    "locality": "",
    "state": "",
    "country": "",
    "commonName": ""
}
try:
    oneview_client.enclosures.generate_csr(csr_data, enclosure_uri, bay_number=bay_number)
    print("Generated CSR for the enclosure.")
except HPOneViewException as e:
    print(e.msg)

# Get the certificate Signing Request (CSR) that was generated by previous POST.
try:
    csr = oneview_client.enclosures.get_csr(enclosure_uri, bay_number=bay_number)
    with open('enclosure.csr', 'w') as csr_file:
            csr_file.write(csr["base64Data"])
    print("Saved CSR(generated by previous POST) to 'enclosure.csr' file")
except HPOneViewException as e:
    print(e.msg)

try:
    # Get Enclosure by scope_uris
    if oneview_client.api_version >= 600:
        enclosures_by_scope_uris = oneview_client.enclosures.get_all(scope_uris="\"'/rest/scopes/3bb0c754-fd38-45af-be8a-4d4419de06e9'\"")
        if len(enclosures_by_scope_uris) > 0:
            print("Found %d Enclosures" % (len(enclosures_by_scope_uris)))
            i = 0
            while i < len(enclosures_by_scope_uris):
                print("Found Enclosures by scope_uris: '%s'.\n  uri = '%s'" % (enclosures_by_scope_uris[i]['name'], enclosures_by_scope_uris[i]['uri']))
                i += 1
            pprint(enclosures_by_scope_uris)
        else:
            print("No Enclosures Group found.")
except HPOneViewException as e:
    print(e.msg)

# Import a CA signed certificate to the enclosure.
try:
    # This action requires a certificate(CA signed) file path to be declared.
    if certificate_file:
        with open(certificate_file, "r") as file_object:
            certificate = file_object.read()

        certificate_data = {
            "type": "CertificateDataV2",
            "base64Data": certificate
        }

        oneview_client.enclosures.import_certificate(certificate_data, enclosure_uri, bay_number=bay_number)
        print("Imported Signed Certificate  to the enclosure.")
except HPOneViewException as e:
    print(e.msg)

# Remove the recently added enclosure
oneview_client.enclosures.remove(enclosure)
print("Enclosure removed successfully")
