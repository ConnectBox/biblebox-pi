[![Build Status](https://travis-ci.org/ConnectBox/connectbox-pi.svg?branch=master)](https://travis-ci.org/ConnectBox/connectbox-pi)

# The Well version of ConnectBox

The Well is a variant of ConnectBox that adds Moodle Learning Management System (v. 3.9.3), PHP (v. 7.4) and PostgreSQL (vv 9.6) to bring training system and learning content to the ConnectBox platform.

Summary Of Changes:
* ConnectBox Ansible roles are updated to build ConnectBox with Moodle, PHP and PostgreSQL
* Refer to Relay Trust Moodle Repo for Documentation Of Changes
* Default Moodle PostgreSQL database is located in this repo under ansible/roles/ansible-postgresql/templates/
* Legacy Connectbox File Serving is now at {{{hostname}}}.cb such that Moodle is http://connectbox and Admin is http://connectbox.cb/admin
* (There will be more as this gets built out)

# ConnectBox

ConnectBox is a media sharing device based on small form factor computers including the Raspberry Pi 3, Raspberry Pi Zero W, NanoPi NEO, Orange Pi Zero and Pine64.

# Making a ConnectBox

See [docs/deployment.md](docs/deployment.md)

# Connectbox setup and administration

See [docs/administration.md](docs/administration.md)

# Developing the ConnectBox Software

See [docs/development.md](docs/development.md)

# MicroSD Card Images/Releases
See [https://github.com/ConnectBox/connectbox-pi/releases/](https://github.com/ConnectBox/connectbox-pi/releases/)
