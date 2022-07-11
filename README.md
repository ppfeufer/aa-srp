# AA-SRP

[![Version](https://img.shields.io/pypi/v/aa-srp?label=release)](https://pypi.org/project/aa-srp/)
[![License](https://img.shields.io/github/license/ppfeufer/aa-srp)](https://github.com/ppfeufer/aa-srp/blob/master/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/aa-srp)](https://pypi.org/project/aa-srp/)
[![Django](https://img.shields.io/pypi/djversions/aa-srp?label=django)](https://pypi.org/project/aa-srp/)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](http://black.readthedocs.io/en/latest/)
[![Discord](https://img.shields.io/discord/790364535294132234?label=discord)](https://discord.gg/zmh52wnfvM)
[![Checks](https://github.com/ppfeufer/aa-srp/actions/workflows/automated-checks.yml/badge.svg)](https://github.com/ppfeufer/aa-srp/actions/workflows/automated-checks.yml)
[![codecov](https://codecov.io/gh/ppfeufer/aa-srp/branch/master/graph/badge.svg?token=D63TU2TBIW)](https://codecov.io/gh/ppfeufer/aa-srp)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](https://github.com/ppfeufer/aa-srp/blob/master/CODE_OF_CONDUCT.md)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/N4N8CL1BY)

SRP Module for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth)


## Contents

- [Overview](#overview)
    - [Features](#features)
    - [Screenshots](#screenshots)
- [Installation](#overview)
    - [Step 1 - Install the package](#step-1---install-the-package)
    - [Step 2 - Configure Alliance Auth](#step-2---configure-alliance-auth)
    - [Step 3 - Finalize the installation](#step-3---finalize-the-installation)
    - [Step 4 - Preload Eve Universe data](#step-4---preload-eve-universe-data)
    - [Step 5 - Set up permissions](#step-5---set-up-permissions)
    - [Step 6 - (Optional) Import from built-in SRP module](#step-6---optional-import-from-built-in-srp-module)
- [Permissions](#permissions)
- [Settings](#settings)
- [Changelog](#changelog)
- [Contributing](#contributing)


## Overview

### Features

- Overview of SRP links
- Overview of your own SRP requests and their status
- Accepting kill mails from [zKillboard](https://zkillboard.com/) and
  [EveTools Killboard](https://kb.evetools.org/)
- SRP Request administration mostly done via ajax and without page reloads
- Use modern DataTables with filters where ever they are useful
- Tables fully searchable and sortable
- Mandatory reason on SRP reject
- Notifications in AA with detailed information on SRP rejection
- Discord notification via PM to the user on SRP request approval or rejection, if
  either [AA-Discordbot](https://github.com/pvyParts/allianceauth-discordbot),
  [AA-Discord Notify](https://gitlab.com/ErikKalkoken/aa-discordnotify) or
  [Discord Proxy](https://gitlab.com/ErikKalkoken/discordproxy) is installed
- Notify your SRP team (optional) in their Doscord channel about new SRP requests, if
  [AA-Discordbot](https://github.com/pvyParts/allianceauth-discordbot) is installed


### Screenshots

#### Dashboard

![AA SRP Dashboard](https://raw.githubusercontent.com/ppfeufer/aa-srp/master/aasrp/images/aa-srp-dashboard.jpg "AA SRP Dashboard")


#### Dashboard (View All)

![AA SRP Dashboard (View All)](https://raw.githubusercontent.com/ppfeufer/aa-srp/master/aasrp/images/aa-srp-dashboard-view-all.jpg "AA SRP Dashboard (View All)")


#### Your SRP Requests

![Your SRP Requests View](https://raw.githubusercontent.com/ppfeufer/aa-srp/master/aasrp/images/aa-srp-your-requests.jpg "Your SRP Requests View")


#### SRP Requests Overview

![SRP Requests Overview](https://raw.githubusercontent.com/ppfeufer/aa-srp/master/aasrp/images/aa-srp-requests-overview.jpg "SRP Requests Overview")


#### SRP Request Details

![SRP Request Details](https://raw.githubusercontent.com/ppfeufer/aa-srp/master/aasrp/images/aa-srp-request-details.jpg "SRP Request Details")


## Installation

**Important**: Please make sure you meet all preconditions before you proceed:

- AA SRP is a plugin for Alliance Auth. If you don't have Alliance Auth running
  already, please install it first before proceeding. (see the official
  [AA installation guide](https://allianceauth.readthedocs.io/en/latest/installation/allianceauth.html) for details)
- AA SRP needs the app [django-eveuniverse](https://gitlab.com/ErikKalkoken/django-eveuniverse)
  to function. Please make sure it is installed, before continuing.


### Step 1 - Install the package

Make sure you are in the virtual environment (venv) of your Alliance Auth
installation Then install the latest release directly from PyPi.

```shell
pip install aa-srp
```


### Step 2 - Configure Alliance Auth

This is fairly simple, just add the following to the `INSTALLED_APPS` of your `local.py`

Configure your AA settings (`local.py`) as follows:

- Add `"eveuniverse",` to `INSTALLED_APPS`
- Add `"aasrp",` to `INSTALLED_APPS`


### Step 3 - Finalize the installation

Run  static files collection and migrations

```shell
python manage.py collectstatic
python manage.py migrate
```

Restart your supervisor services for Auth


### Step 4 - Preload Eve Universe data

AA SRP utilizes the EveUniverse module, so it doesn't need to ask ESI for ship
information. To set this up, you now need to run the following command.

```shell
python manage.py aasrp_load_eve
```

### Step 5 - Set up permissions

Now it's time to set up access permissions for your new SRP module. You can do so in
your admin backend in the AA SRP section. Read the [Permissions](#permissions)
section for more information about the available permissions.


### Step 6 - (Optional) Import from built-in SRP module

**This step is only needed when you have been using the built-in SRP module until now.**

Make sure you don't have any open SRP requests before. All SRP links in the built-in
module will be closed during the import process, to make sure to not import any
duplicates.

The import process can be done at any given time and does not necessarily have to be
during the installation.

To import your SRP information from the built-in SRP module, run the following command.

```shell
python manage.py aasrp_migrate_srp_data
```


## Permissions

| ID                    | Description                  | Notes                                                                                                       |
|-----------------------|------------------------------|-------------------------------------------------------------------------------------------------------------|
| `basic_access`        | Can access the AA-SRP module | Your line members should have this permission.                                                              |
| `create_srp`          | Can create new SRP links     | Your FCs should have this permission.                                                                       |
| `manage_srp`          | Can manage SRP               | Users with this permission can manage the AA SRP Module. Like changing and removing SRP links and requests. |
| `manage_srp_requests` | Can manage SRP requests      | Users with this permission can manage the SRP requests. Like changing and removing SRP requests.            |


## Settings

| Key                              | Description                                                                                                                                                                                                                                                                                    | Type  | Default  |
|----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|----------|
| `AASRP_SRP_TEAM_DISCORD_CHANNEL` | ID of the Discord channel of your SRP team. If set, your SRP team will be notified (no ping to prevent ping spam) about new SRP requests in their channel. (You need to have [AA-Discordbot](https://github.com/pvyParts/allianceauth-discordbot) installed and configured to use this option) | int   | `None`   |


## Changelog

See [CHANGELOG.md](https://github.com/ppfeufer/aa-srp/blob/master/CHANGELOG.md)


## Contributing

You want to contribute to this project? That's cool!

Please make sure to read the [contribution guidelines](https://github.com/ppfeufer/aa-srp/blob/master/CONTRIBUTING.md)
(I promise, it's not much, just some basics)
