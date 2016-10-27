# -*- coding: utf-8 -*-
###
# (C) Copyright (2012-2016) Hewlett Packard Enterprise Development LP
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
from config_loader import try_load_from_file

config = {
    "ip": "172.16.102.59",
    "credentials": {
        "userName": "administrator",
        "password": ""
    }
}

# Try load config from a file (if there is a config file)
config = try_load_from_file(config)

oneview_client = OneViewClient(config)

print("Get all Scopes")
scopes = oneview_client.scopes.get_all()
pprint(scopes)

information = {
    "addedResourceUris": ["/rest/ethernet-networks/e801b73f-b4e8-4b32-b042-36f5bac2d60f"],
    "removedResourceUris": ["/rest/ethernet-networks/390bc9f9-cdd5-4c70-b38f-cf04e64f5c72"]
}

information_swap = {
    "removedResourceUris": ["/rest/ethernet-networks/e801b73f-b4e8-4b32-b042-36f5bac2d60f"],
    "addedResourceUris": ["/rest/ethernet-networks/390bc9f9-cdd5-4c70-b38f-cf04e64f5c72"]
}

if scopes:
    # Gets the first Scope
    uri = scopes[0]["uri"]

    # Add/Remove
    print("Add/Remove resource to/from scope")
    drives = oneview_client.scopes.update_resource_assignments(uri, information)
    pprint(drives)

    # Add/Remove (Invert)
    print("Remove a resource from the Scope and add other")
    drives = oneview_client.scopes.update_resource_assignments(uri, information_swap)
    pprint(drives)
