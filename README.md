# AA SRP

[![Badge: Version]][AA SRP on Pypi]
[![Badge: License]][AA SRP License]
[![Badge: Supported Python Versions]][AA SRP on Pypi]
[![Badge: Supported Django Versions]][AA SRP on Pypi]
![Badge: pre-commit]
[![Badge: Code Style: black]][black code formatter documentation]
[![Badge: Support Discord]][Support Discord]
[![Badge: Automated Tests]][Automated Tests on GitHub]
[![Badge: Code Coverage]][AA SRP on Codecov]
[![Badge: Translation Status]][Weblate Engage]
[![Badge: Contributor Covenant]][Code of Conduct]

[![Badge: Buy me a coffee]][ppfeufer on ko-fi]

SRP Module for [Alliance Auth]


---

<!-- TOC -->
* [AA SRP](#aa-srp)
  * [Overview](#overview)
    * [Features](#features)
    * [Screenshots](#screenshots)
      * [Dashboard](#dashboard)
      * [Dashboard (View All)](#dashboard-view-all)
      * [Your SRP Requests](#your-srp-requests)
      * [SRP Requests Overview](#srp-requests-overview)
      * [SRP Request Details](#srp-request-details)
  * [Installation](#installation)
    * [Step 1: Install the Package](#step-1-install-the-package)
    * [Step 2: Configure Alliance Auth](#step-2-configure-alliance-auth)
    * [Step 3: Finalizing the Installation](#step-3-finalizing-the-installation)
    * [Step 4: Preload Eve Universe Data](#step-4-preload-eve-universe-data)
    * [Step 5: Setting up Permissions](#step-5-setting-up-permissions)
    * [Step 6: (Optional) Import From Built-in SRP Module](#step-6-optional-import-from-built-in-srp-module)
  * [Permissions](#permissions)
  * [Changelog](#changelog)
  * [Contributing](#contributing)
<!-- TOC -->

---


## Overview

### Features

- Overview of SRP links
- Overview of your own SRP requests and their status
- Accepting kill mails from [zKillboard] and [EveTools Killboard]
- SRP Request administration is mostly done via ajax and without page reloads
- Use modern DataTables with filters where ever they're useful
- Tables fully searchable and sortable
- Mandatory reason on SRP reject
- Notifications in AA with detailed information on SRP rejection
- Discord notification via PM to the user on SRP request approval or rejection, if
  either [AA-Discordbot], [Discord Notify] or [Discord Proxy] is installed
- Notify your SRP team (optional) in their Discord channel about new SRP requests, if
  [AA-Discordbot] or [Discord Proxy] is installed


### Screenshots

#### Dashboard

![Image: AA SRP Dashboard]


#### Dashboard (View All)

![Image: AA SRP Dashboard (View All)]


#### Your SRP Requests

![Image: Your SRP Requests View]


#### SRP Requests Overview

![Image: SRP Requests Overview]


#### SRP Request Details

![Image: SRP Request Details]


## Installation

**Important**: Please make sure you meet all preconditions before you proceed:

- AA SRP is a plugin for Alliance Auth. If you don't have Alliance Auth running
  already, please install it first before proceeding. (see the official
  [Alliance Auth installation guide] for details)
- AA SRP needs [Eve Universe] to function. Please make sure it is installed, before
  continuing.


### Step 1: Install the Package

Make sure you're in the virtual environment (venv) of your Alliance Auth
installation Then install the latest release directly from PyPi.

```shell
pip install aa-srp
```


### Step 2: Configure Alliance Auth

This is fairly simple, just add the following to the `INSTALLED_APPS` of your `local.py`

Configure your AA settings (`local.py`) as follows:

- Add `"eveuniverse",` to `INSTALLED_APPS`
- Add `"aasrp",` to `INSTALLED_APPS`


### Step 3: Finalizing the Installation

Run static files collection and migrations

```shell
python manage.py collectstatic
python manage.py migrate
```

Restart your supervisor services for Auth


### Step 4: Preload Eve Universe Data

AA SRP utilizes the EveUniverse module, so it doesn't need to ask ESI for ship
information. To set this up, you now need to run the following command.

```shell
python manage.py aasrp_load_eve
```

### Step 5: Setting up Permissions

Now it's time to set up access permissions for your new SRP module. You can do so in
your admin backend in the AA SRP section. Read the [Permissions](#permissions)
section for more information about the available permissions.


### Step 6: (Optional) Import From Built-in SRP Module

**This step is only needed when you have been using the built-in SRP module until now.**

Make sure you don't have any open SRP requests before. All SRP links in the built-in
module will be closed during the import process, to make sure to not import any
duplicates.

The import process can be done at any given time and doesn't necessarily have to be
during the installation.

To import your SRP information from the built-in SRP module, run the following command.

```shell
python manage.py aasrp_migrate_srp_data
```


## Permissions

| ID                    | Description                  | Notes                                                                                                       |
|-----------------------|------------------------------|-------------------------------------------------------------------------------------------------------------|
| `basic_access`        | Can access the AA SRP module | Your line members should have this permission.                                                              |
| `create_srp`          | Can create new SRP links     | Your FCs should have this permission.                                                                       |
| `manage_srp`          | Can manage SRP               | Users with this permission can manage the AA SRP Module. Like changing and removing SRP links and requests. |
| `manage_srp_requests` | Can manage SRP requests      | Users with this permission can manage the SRP requests. Like changing and removing SRP requests.            |


## Changelog

See [CHANGELOG.md]


## Contributing

You want to contribute to this project? That's cool!

Please make sure to read the [Contribution Guidelines] (I promise, it's not much,
just some basics)


<!-- Images -->
[Badge: Version]: https://img.shields.io/pypi/v/aa-srp?label=release "Version"
[Badge: License]: https://img.shields.io/github/license/ppfeufer/aa-srp "License"
[Badge: Supported Python Versions]: https://img.shields.io/pypi/pyversions/aa-srp "Supported Python Versions"
[Badge: Supported Django Versions]: https://img.shields.io/pypi/djversions/aa-srp?label=django "Supported Django Versions"
[Badge: pre-commit]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white "pre-commit"
[Badge: Code Style: black]: https://img.shields.io/badge/code%20style-black-000000.svg "Code Style: black"
[Badge: Support Discord]: https://img.shields.io/discord/790364535294132234?label=discord "Support Discord"
[Badge: Automated Tests]: https://github.com/ppfeufer/aa-srp/actions/workflows/automated-checks.yml/badge.svg "Automated Tests"
[Badge: Code Coverage]: https://codecov.io/gh/ppfeufer/aa-srp/branch/master/graph/badge.svg "Code Coverage"
[Badge: Contributor Covenant]: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg "Contributor Covenant"
[Badge: Buy me a coffee]: https://ko-fi.com/img/githubbutton_sm.svg "Buy me a coffee"
[Badge: Translation Status]: https://weblate.ppfeufer.de/widgets/alliance-auth-apps/-/aa-srp/svg-badge.svg "Translation Status"

[Image: AA SRP Dashboard]: https://raw.githubusercontent.com/ppfeufer/aa-srp/master/aasrp/docs/screenshots/aa-srp-dashboard.jpg "AA SRP Dashboard"
[Image: AA SRP Dashboard (View All)]: https://raw.githubusercontent.com/ppfeufer/aa-srp/master/aasrp/docs/screenshots/aa-srp-dashboard-view-all.jpg "AA SRP Dashboard (View All)"
[Image: Your SRP Requests View]: https://raw.githubusercontent.com/ppfeufer/aa-srp/master/aasrp/docs/screenshots/aa-srp-your-requests.jpg "Your SRP Requests View"
[Image: SRP Requests Overview]: https://raw.githubusercontent.com/ppfeufer/aa-srp/master/aasrp/docs/screenshots/aa-srp-requests-overview.jpg "SRP Requests Overview"
[Image: SRP Request Details]: https://raw.githubusercontent.com/ppfeufer/aa-srp/master/aasrp/docs/screenshots/aa-srp-request-details.jpg "SRP Request Details"

<!-- Links -->
[AA SRP on Pypi]: https://pypi.org/project/aa-srp/
[AA SRP on Codecov]: https://codecov.io/gh/ppfeufer/aa-srp
[AA SRP License]: https://github.com/ppfeufer/aa-srp/blob/master/LICENSE
[black code formatter documentation]: http://black.readthedocs.io/en/latest/
[Support Discord]: https://discord.gg/zmh52wnfvM
[Automated Tests on GitHub]: https://github.com/ppfeufer/aa-srp/actions/workflows/automated-checks.yml
[Code of Conduct]: https://github.com/ppfeufer/aa-srp/blob/master/CODE_OF_CONDUCT.md
[ppfeufer on ko-fi]: https://ko-fi.com/N4N8CL1BY
[Weblate Engage]: https://weblate.ppfeufer.de/engage/alliance-auth-apps/

[Alliance Auth]: https://gitlab.com/allianceauth/allianceauth "Alliance Auth"
[Alliance Auth installation guide]: https://allianceauth.readthedocs.io/en/latest/installation/allianceauth.html "Alliance Auth installation guide"
[zKillboard]: https://zkillboard.com/ "zKillboard"
[EveTools Killboard]: https://kb.evetools.org/ "EveTools Killboard"
[AA-Discordbot]: https://github.com/pvyParts/allianceauth-discordbot "AA-Discordbot"
[Discord Notify]: https://gitlab.com/ErikKalkoken/aa-discordnotify "Discord Notify"
[Discord Proxy]: https://gitlab.com/ErikKalkoken/discordproxy "Discord Proxy"
[Eve Universe]: https://gitlab.com/ErikKalkoken/django-eveuniverse "Eve Universe"
[CHANGELOG.md]: https://github.com/ppfeufer/aa-srp/blob/master/CHANGELOG.md "CHANGELOG.md"
[Contribution Guidelines]: (https://github.com/ppfeufer/aa-srp/blob/master/CONTRIBUTING.md "Contribution Guidelines"
