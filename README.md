# AA SRP<a name="aa-srp"></a>

[![Badge: Version]][aa srp on pypi]
[![Badge: License]][aa srp license]
[![Badge: Supported Python Versions]][aa srp on pypi]
[![Badge: Supported Django Versions]][aa srp on pypi]
![Badge: pre-commit]
[![Badge: pre-commit.ci status]][pre-commit.ci status]
[![Badge: Code Style: black]][black code formatter documentation]
[![Badge: Support Discord]][support discord]
[![Badge: Automated Tests]][automated tests on github]
[![Badge: Code Coverage]][aa srp on codecov]
[![Badge: Translation Status]][weblate engage]
[![Badge: Contributor Covenant]][code of conduct]

[![Badge: Buy me a coffee]][ppfeufer on ko-fi]

SRP Module for [Alliance Auth]

______________________________________________________________________

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=2 -->

- [Overview](#overview)
  - [Features](#features)
  - [Screenshots](#screenshots)
    - [Dashboard](#dashboard)
    - [Dashboard (View All)](#dashboard-view-all)
    - [Your SRP Requests](#your-srp-requests)
    - [SRP Requests Overview](#srp-requests-overview)
    - [SRP Request Details](#srp-request-details)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Step 1: Install the Package](#step-1-install-the-package)
  - [Step 2: Configure Alliance Auth](#step-2-configure-alliance-auth)
  - [Step 3: Finalizing the Installation](#step-3-finalizing-the-installation)
  - [Step 4: Preload Eve Universe Data](#step-4-preload-eve-universe-data)
  - [Step 5: Setting up Permissions](#step-5-setting-up-permissions)
  - [Step 6: (Optional) Import From Built-in SRP Module](#step-6-optional-import-from-built-in-srp-module)
  - [Step 7: (Optional) Settings for Discord Proxy (If Used)](#step-7-optional-settings-for-discord-proxy-if-used)
- [Permissions](#permissions)
- [Changelog](#changelog)
- [Translation Status](#translation-status)
- [Contributing](#contributing)

<!-- mdformat-toc end -->

______________________________________________________________________

## Overview<a name="overview"></a>

### Features<a name="features"></a>

- Overview of SRP links
- Overview of your own SRP requests and their status
- Accepting kill mails from [zKillboard], [EveTools Killboard] and [EVE-Kill]
- SRP Request administration is mostly done via ajax and without page reloads
- Use modern DataTables with filters where ever they're useful
- Tables fully searchable and sortable
- Mandatory reason on SRP reject
- Notifications in AA with detailed information on SRP rejection
- Discord notification via PM to the user on SRP request approval or rejection, if
  either [AA-Discordbot], [Discord Notify] or [Discord Proxy] is installed
- Notify your SRP team (optional) in their Discord channel about new SRP requests, if
  [AA-Discordbot] or [Discord Proxy] is installed

### Screenshots<a name="screenshots"></a>

#### Dashboard<a name="dashboard"></a>

![Image: AA SRP Dashboard]

#### Dashboard (View All)<a name="dashboard-view-all"></a>

![Image: AA SRP Dashboard (View All)]

#### Your SRP Requests<a name="your-srp-requests"></a>

![Image: Your SRP Requests View]

#### SRP Requests Overview<a name="srp-requests-overview"></a>

![Image: SRP Requests Overview]

#### SRP Request Details<a name="srp-request-details"></a>

![Image: SRP Request Details]

## Installation<a name="installation"></a>

### Prerequisites<a name="prerequisites"></a>

> [!IMPORTANT]
>
> Please make sure you meet all prerequisites before you proceed!

- AA SRP is a plugin for Alliance Auth. If you don't have Alliance Auth running
  already, please install it first before proceeding. (see the official
  [Alliance Auth installation guide] for details)
- AA SRP needs at least Alliance Auth v4.6.0
- AA SRP needs [Eve Universe] to function. Please make sure it is installed, before
  continuing.

### Step 1: Install the Package<a name="step-1-install-the-package"></a>

Make sure you're in the virtual environment (venv) of your Alliance Auth
installation Then install the latest release directly from PyPi.

```shell
pip install aa-srp
```

### Step 2: Configure Alliance Auth<a name="step-2-configure-alliance-auth"></a>

This is fairly simple, just add the following to the `INSTALLED_APPS` of your `local.py`

Configure your AA settings (`local.py`) as follows:

- Add `"eveuniverse",` to `INSTALLED_APPS`
- Add `"aasrp",` to `INSTALLED_APPS`

### Step 3: Finalizing the Installation<a name="step-3-finalizing-the-installation"></a>

Run static files collection and migrations

```shell
python manage.py collectstatic
python manage.py migrate
```

Restart your supervisor services for Auth

### Step 4: Preload Eve Universe Data<a name="step-4-preload-eve-universe-data"></a>

AA SRP utilizes the EveUniverse module, so it doesn't need to ask ESI for ship
information. To set this up, you now need to run the following command.

```shell
python manage.py aasrp_load_eve
```

### Step 5: Setting up Permissions<a name="step-5-setting-up-permissions"></a>

Now it's time to set up access permissions for your new SRP module. You can do so in
your admin backend in the AA SRP section. Read the [Permissions](#permissions)
section for more information about the available permissions.

### Step 6: (Optional) Import From Built-in SRP Module<a name="step-6-optional-import-from-built-in-srp-module"></a>

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

### Step 7: (Optional) Settings for Discord Proxy (If Used)<a name="step-7-optional-settings-for-discord-proxy-if-used"></a>

If you are using [Discord Proxy] to send Discord messages, you can configure the host and port in your `local.py` settings.

| Name                | Description                                      | Default     |
| ------------------- | ------------------------------------------------ | ----------- |
| `DISCORDPROXY_HOST` | Hostname used to communicate with Discord Proxy. | `localhost` |
| `DISCORDPROXY_PORT` | Port used to communicate with Discord Proxy.     | `50051`     |

## Permissions<a name="permissions"></a>

| ID                    | Description                  | Notes                                                                                                       |
| --------------------- | ---------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `basic_access`        | Can access the AA SRP module | Your line members should have this permission.                                                              |
| `create_srp`          | Can create new SRP links     | Your FCs should have this permission.                                                                       |
| `manage_srp`          | Can manage SRP               | Users with this permission can manage the AA SRP Module. Like changing and removing SRP links and requests. |
| `manage_srp_requests` | Can manage SRP requests      | Users with this permission can manage the SRP requests. Like changing and removing SRP requests.            |

## Changelog<a name="changelog"></a>

See [CHANGELOG.md]

## Translation Status<a name="translation-status"></a>

[![Translation status](https://weblate.ppfeufer.de/widget/alliance-auth-apps/aa-srp/multi-auto.svg)](https://weblate.ppfeufer.de/engage/alliance-auth-apps/)

Do you want to help translate this app into your language or improve the existing
translation? - [Join our team of translators][weblate engage]!

## Contributing<a name="contributing"></a>

You want to contribute to this project? That's cool!

Please make sure to read the [Contribution Guidelines].\
(I promise, it's not much, just some basics)

<!-- Links -->

[aa srp license]: https://github.com/ppfeufer/aa-srp/blob/master/LICENSE
[aa srp on codecov]: https://codecov.io/gh/ppfeufer/aa-srp
[aa srp on pypi]: https://pypi.org/project/aa-srp/
[aa-discordbot]: https://github.com/pvyParts/allianceauth-discordbot "AA-Discordbot"
[alliance auth]: https://gitlab.com/allianceauth/allianceauth "Alliance Auth"
[alliance auth installation guide]: https://allianceauth.readthedocs.io/en/latest/installation/allianceauth.html "Alliance Auth installation guide"
[automated tests on github]: https://github.com/ppfeufer/aa-srp/actions/workflows/automated-checks.yml
[badge: automated tests]: https://github.com/ppfeufer/aa-srp/actions/workflows/automated-checks.yml/badge.svg "Automated Tests"
[badge: buy me a coffee]: https://ko-fi.com/img/githubbutton_sm.svg "Buy me a coffee"
[badge: code coverage]: https://codecov.io/gh/ppfeufer/aa-srp/branch/master/graph/badge.svg "Code Coverage"
[badge: code style: black]: https://img.shields.io/badge/code%20style-black-000000.svg "Code Style: black"
[badge: contributor covenant]: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg "Contributor Covenant"
[badge: license]: https://img.shields.io/github/license/ppfeufer/aa-srp "License"
[badge: pre-commit]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white "pre-commit"
[badge: pre-commit.ci status]: https://results.pre-commit.ci/badge/github/ppfeufer/aa-srp/master.svg "pre-commit.ci status"
[badge: support discord]: https://img.shields.io/discord/790364535294132234?label=discord "Support Discord"
[badge: supported django versions]: https://img.shields.io/pypi/djversions/aa-srp?label=django "Supported Django Versions"
[badge: supported python versions]: https://img.shields.io/pypi/pyversions/aa-srp "Supported Python Versions"
[badge: translation status]: https://weblate.ppfeufer.de/widget/alliance-auth-apps/aa-srp/svg-badge.svg "Translation Status"
[badge: version]: https://img.shields.io/pypi/v/aa-srp?label=release "Version"
[black code formatter documentation]: http://black.readthedocs.io/en/latest/
[changelog.md]: https://github.com/ppfeufer/aa-srp/blob/master/CHANGELOG.md "CHANGELOG.md"
[code of conduct]: https://github.com/ppfeufer/aa-srp/blob/master/CODE_OF_CONDUCT.md
[contribution guidelines]: https://github.com/ppfeufer/aa-srp/blob/master/CONTRIBUTING.md "Contribution Guidelines"
[discord notify]: https://gitlab.com/ErikKalkoken/aa-discordnotify "Discord Notify"
[discord proxy]: https://gitlab.com/ErikKalkoken/discordproxy "Discord Proxy"
[eve universe]: https://gitlab.com/ErikKalkoken/django-eveuniverse "Eve Universe"
[eve-kill]: https://eve-kill.com/ "EVE-Kill"
[evetools killboard]: https://kb.evetools.org/ "EveTools Killboard"
[image: aa srp dashboard]: https://raw.githubusercontent.com/ppfeufer/aa-srp/master/docs/images/aa-srp-dashboard.jpg "AA SRP Dashboard"
[image: aa srp dashboard (view all)]: https://raw.githubusercontent.com/ppfeufer/aa-srp/master/docs/images/aa-srp-dashboard-view-all.jpg "AA SRP Dashboard (View All)"
[image: srp request details]: https://raw.githubusercontent.com/ppfeufer/aa-srp/master/docs/images/aa-srp-request-details.jpg "SRP Request Details"
[image: srp requests overview]: https://raw.githubusercontent.com/ppfeufer/aa-srp/master/docs/images/aa-srp-requests-overview.jpg "SRP Requests Overview"
[image: your srp requests view]: https://raw.githubusercontent.com/ppfeufer/aa-srp/master/docs/images/aa-srp-your-requests.jpg "Your SRP Requests View"
[ppfeufer on ko-fi]: https://ko-fi.com/N4N8CL1BY
[pre-commit.ci status]: https://results.pre-commit.ci/latest/github/ppfeufer/aa-srp/master "pre-commit.ci"
[support discord]: https://discord.gg/zmh52wnfvM
[weblate engage]: https://weblate.ppfeufer.de/engage/alliance-auth-apps/
[zkillboard]: https://zkillboard.com/ "zKillboard"
