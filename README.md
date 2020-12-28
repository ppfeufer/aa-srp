# AA-SRP

[![Version](https://img.shields.io/pypi/v/aa-srp?label=release)](https://pypi.org/project/aa-srp/)
[![License](https://img.shields.io/badge/license-GPLv3-green)](https://pypi.org/project/aa-srp/)
[![Python](https://img.shields.io/pypi/pyversions/aa-srp)](https://pypi.org/project/aa-srp/)
[![Django](https://img.shields.io/pypi/djversions/aa-srp?label=django)](https://pypi.org/project/aa-srp/)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](http://black.readthedocs.io/en/latest/)

SRP Module for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth)

## Contents

- [Overview](#overview)
    - [Features](#features)
    - [Screenshots](#screenshots)
- [Installation](#overview)
    - [Step 1 - Install the package](#step-1---install-the-package)
    - [Step 2 - Configure Alliance Auth](#step-2---configure-alliance-auth)
    - [Step 3 - Finalize the installation](#step-3---finalize-the-installation)
    - [Step 4 - Import from built-in SRP module](#step-4---import-from-built-in-srp-module)
    - [Step 5 - Set up permissions](#step-5---set-up-permissions)
- [Permissions](#permissions)
- [Changelog](#changelog)

## Overview

### Features

- Overview of SRP links
- Overview of your own SRP requests and their status
- SRP Request administration mostly done via ajax and without page reloads
- Use of modern DataTables with filters where useful
- Tables fully searchable and sortable


### Screenshots

#### Dashboard
![Dashboard](https://raw.githubusercontent.com/ppfeufer/aa-srp/master/aasrp/images/aa-srp-dashboard.jpg)

#### Dashboard (View All)
![Dashboard (View All)](https://raw.githubusercontent.com/ppfeufer/aa-srp/master/aasrp/images/aa-srp-dashboard-view-all.jpg)

#### Your SRP Requests
![Your SRP Requests](https://raw.githubusercontent.com/ppfeufer/aa-srp/master/aasrp/images/aa-srp-your-requests.jpg)

#### SRP Requests Overview
![SRP Requests Overview](https://raw.githubusercontent.com/ppfeufer/aa-srp/master/aasrp/images/aa-srp-requests-overview.jpg)

#### SRP Request Details
![SRP Request Details](https://raw.githubusercontent.com/ppfeufer/aa-srp/master/aasrp/images/aa-srp-request-details.jpg)


## Installation

### Step 1 - Install the package

Make sure you are in the virtual environment (venv) of your Alliance Auth
installation Then install the latest releast directly from PyPi.

```shell
pip install aa-srp
```

### Step 2 - Configure Alliance Auth

This is fairly simple, just add the following to the `INSTALLED_APPS` of your `local.py`

```python
"aasrp",
```

### Step 3 - Finalize the installation

Run  static files collection and migrations

```shell
python manage.py migrate
python manage.py collectstatic
```

### Step 4 - Import from built-in SRP module

**Important:**

Make sure you don't have any open SRP reqests before. All SRP links in the built-in
module will be closed during the import process, to make sure to not import any
duplicates.

The import process can be done at any given time and does not necessarily have to be
at the time of the installation.

To import your SRP information from the buil-in SRP module, run the following command.

```shell
python manage.py aasrp_migrate_srp_data
```

### Step 5 - Set up permissions

Now it's time to set up access permissions for your new SRP module. You can do so in
your admin backend in the AA SRP section. Read the [Permissions](#permissions)
section for more information about the available permissions.


## Permissions

| ID                    | Description                  | Notes                                                                                                       |
|-----------------------|------------------------------|-------------------------------------------------------------------------------------------------------------|
| `basic_access`        | Can access the AA-SRP module | Your line members should have this permission.                                                              |
| `create_srp`          | Can create new SRP links     | Your FCs should have this permission.                                                                       |
| `manage_srp`          | Can manage SRP               | Users with this permission can manage the AA SRP Module. Like changing and removing SRP links and requests. |
| `manage_srp_requests` | Can manage SRP requests      | Users with this permission can manage the SRP requests. Like changing and removing SRP requests.            |


## Changelog

See [CHANGELOG.md](CHANGELOG.md)
