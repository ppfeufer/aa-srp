# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/)


## [0.1.0-beta.11] - 2021-01-26

### Changed

- Modals separated into their own templates
- Wrappd datatables in responsive div
- Moved useragent to constants
- JS re-organized


## [0.1.0-beta.10] - 2021-01-11

### Added

- Fleet name to overview in SRP link view

### Fixed

- Module call in init file


## [0.1.0-beta.9] - 2021-01-06

### Added

- Mandatory reason on SRP reject
- Type hints to classes and functions


## [0.1.0-beta.8] - 2021-01-06

### Fixed

- Filter dropdowns for character again -.-


## [0.1.0-beta.7] - 2021-01-06

### Fixed

- Character portrait formatting
- zKillboard link with icon in request detail modal
- Filter dropdowns for character


## [0.1.0-beta.6] - 2021-01-05

### Added

- Character portraits and ship icons


## [0.1.0-beta.5] - 2021-01-05

### Changed

- Ship is now a proper EveType model instead of just a string


## Important Update Instructions

**IMPORTANT**

If you update from v0.1.0-beta.4 or earlier, make sure to read carefully.

In this version the way the SRP ship is handled has changed. It is no longer just a
simple string in the database, it is now a proper EveType model. So you have to do
some extra steps to migrate your data.

**This needs to be done right after you have updated AA SRP from a version prior
v0.1.0-beta.5.**

### Step 1 - Install EveUniverse

This should be done automatically with the update, but there is still a bit of
manual work to it. First you need to add the EveUniverse module to your
`INSTALLED_APPS` in your `loca.py`.

- Add `"eveuniverse",` to `INSTALLED_APPS`


### Step 2 - Static collection and migration

Now that EveUniverse is installed, you need to run the static collection and
migration. Don't forget to restart your supervisor afterwards.

```shell
python manage.py collectstatic
```

```shell
python manage.py migrate
```

Restart your supervisor services for Auth

### Step 3 - Import ship information from ESI

This is where the magic happens. You are now ready to import the ship information
from ESI.

```shell
python manage.py aasrp_load_eve
```


### Step 4 - Migrate your SRP data

Now that we have all the needed information, your SRP data needs to be updated. This
is just another simple command.

```shell
python manage.py aasrp_update_db_relations
```


## [0.1.0-beta.4] - 2020-12-28

### Fixed

- Permissions on "Edit AAR Link" view some ajax requests


## [0.1.0-beta.3] - 2020-12-28

- First public beta release
