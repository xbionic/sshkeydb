#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Michael Dierks (michael dierks at gmail dot com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#

import sys
import os
import hashlib
import psycopg2
import ConfigParser
import tempfile

# check if the configfile exists, else create one

checkconf = os.path.exists(os.path.expanduser('~/.sshkeydb.conf'))

if checkconf == False:
    print "Configfile not found create a defaultconf"
    config = ConfigParser.RawConfigParser()
    config.add_section('postgresql')
    config.set('postgresql', 'user', os.getenv('USER'))
    config.set('postgresql', 'pass', 'EDITTHIS')
    config.set('postgresql', 'host', 'localhost')
    config.set('postgresql', 'port', '5432')
    with open(os.path.expanduser('~/.sshkeydb.conf'), 'wb') as configfile:
        config.write(configfile)
    sys.exit("Edit your configfile now")

# parse config

config = ConfigParser.ConfigParser()
config.read([os.path.expanduser('~/.sshkeydb.conf')])
databasename=config.get('postgresql','database')
dbuser=config.get('postgresql','user')
dbhost=config.get('postgresql','host')
dbpass=config.get('postgresql','password')
dbport=config.get('postgresql','port')

if sys.version_info < (2, 7):
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--role', '-r', dest='role', help='Which usergroup do you want', default='')
    (options, args) = parser.parse_args()
    theRole=options.role
# Python 2.7 and above
else:
    print "using argparse"
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', '-r', dest='role', help='Which usergroup do you want', default='')
    args = parser.parse_args()
    theRole=args.role


# Connecting section

connectingString = "dbname=%s user=%s password=%s host=%s" % (databasename, dbuser, dbpass, dbhost)

try:
    conn = psycopg2.connect(connectingString);
except psycopg2.OperationalError:
    print "Could not connect to the server"
    sys.exit("ConnectionError")

getRole = "select role, realname, keyfile, keypath, checksum from users where role='%s'" % theRole
cursor = conn.cursor()
cursor.execute(getRole)
myresults = cursor.fetchall()
for key in myresults:
    getKey=key[2]
    keychecksum = hashlib.sha256(getKey).hexdigest()
    print "%s %s" % (key[4], keychecksum)
