# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/)


## [1.2.2] - 2021-03-14

### Changed

- Notification functions moved to its own module to avoid code duplications


## [1.2.1] - 2021-03-14

### Fixed

- SRP cost info bar removed from user settings tab


## [1.2.0] - 2021-03-14

### Added

- Option for users to disable notifications for this module. When enabled, no
  notifications will be sent at all. Neither in AA itself nor on Discord (if any of
  the Discord apps is active)
- Check if [AA Discord Notify](https://gitlab.com/ErikKalkoken/aa-discordnotify) is
  installed, which picks up on notifications in Auth and relays them to the
  respective user as Discord PM. This way we don't send double notifications to the
  user if [AA-Discordbot](https://github.com/pvyParts/allianceauth-discordbot) is
  installed as well.

### Changed

- Enabled paging for SRP link table on dashboard in "View All" mode


## [1.1.0] - 2021-03-02

### Added

- Option to notify the SRP team in their Discord channel about new SRP requests. (You
  need to have [AA-Discordbot](https://github.com/pvyParts/allianceauth-discordbot)
  installed and configured to use this option)


## [1.0.1] - 2021-02-09

### Fixed

- Discord PM on approval or reject goes to the reviewer instead of the requester (#11)


## [1.0.0] - 2021-02-06

This has now been tested long enough by my corp, it's time to fully release the
module now, so here we go ...

### Important

**If you are updating from an earlier beta-version, please make sure to read through
this changelog, beginning from the beta-version you were using. You might have to do
some manual work, so please update step by step.**

### Fixed

- An issue where too many notifications where created on request accept

### Added

- More details to notifications
- Discord notification via PM to the user on SRP request approval or rejection, if
  [AA-Discordbot](https://github.com/pvyParts/allianceauth-discordbot) is installed


## [0.1.0-beta.16] - 2021-02-06

### Changed

- Migrated SRP request comments (Additional request information and reject information)
  into their own model


## Important Update Instructions

**IMPORTANT**

If you update from v0.1.0-beta.15 or earlier, make sure to read carefully.

In this version the way the SRP request comments are handled has changed. It is no
longer just a simple string in the database table, it is now a proper model. So
you have to an extra steps to migrate your data.

**This needs to be done right after you have updated AA SRP from a version prior
v0.1.0-beta.16.**

### Migrate SRP request comments

To migrate the comments from SRP requests to their own model, simply run
(Make sure you ran migrations before running this command.)

```shell
python manage.py aasrp_migrate_to_comments
```


## [0.1.0-beta.15] - 2021-02-04

### Fixed

- Modal headers


## [0.1.0-beta.14] - 2021-02-02

### Changed

- Form validation moved to the form model instead of view, so the person
  requesting SRP does not have to restart the whole process again if form validation
  fails
- Form error messages formatted


## [0.1.0-beta.13] - 2021-01-27

### Changed

- EVE/UTC tz handling optimized


## [0.1.0-beta.12] - 2021-01-26

### Fixed

- Panel title for overview panel in SRP requests view
- Missing modal for "Delete SRP Request" re-added

### Added

- SRP request details modal in "Your SRP Requests" tab on dashboard view
- SRP request status to details modal


## [0.1.0-beta.11] - 2021-01-26

### Changed

- Modals separated into their own templates
- Wrapped datatables in responsive div
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
