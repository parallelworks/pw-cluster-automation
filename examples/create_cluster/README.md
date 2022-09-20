# Creating a cluster with the PW API

The example code in this directory, `main.py` does two things:
1. create a new cluster on a PW account and
2. populate the configuration of the cluster based on the information in `resource.json`.

## Setup to use this example

First, modify `resource.json` to correspond to the username and
project in your PW account.  These correspond to the `"username"`
and `"project"` fields, respectively.  The available projects
on your PW account can be found in the `Project` drop down box
in a cluster resource configuration page under the `Resources`
tab, or in the list of groups under the `Company tab`.

Users can select different clouds to run their clusters, this
choice is specified in the `"type"` field at the top of `resources.json`.
The available options are:
+ `pclusterv2` for AWS,
+ `gclusterv2` for GCE, and
+ `azclusterv2` for Azure.

Finally, your PW account's API key, available under the
`Account` > `API Key` tab needs to be stored in the
`PW_API_KEY` environment variable accessible to Python, e.g.:
```bash
export PW_API_KEY=<yourapikeygoeshere12345>
```

## Running this example

From the command line,
```bash
python main.py
```
should print out the contents of `resource.json`.  The new
resource should be visible nearly immediately in the `Resources`
tab of the PW platform.  The new resource will also be
listed in the `Compute Resources` section of the compute tab
unless `"dockhide": true` in `resource.json`.

