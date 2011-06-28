#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Rico Schiekel (fire at downgra dot de)
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

config = ConfigParser.ConfigParser()

config.read([os.path.expanduser('~/.sshkeydb.conf')])
databasename=config.get('postgresql','database')
dbuser=config.get('postgresql','user')
dbhost=config.get('postgresql','host')
dbpass=config.get('postgresql','password')
dbport=config.get('postgresql','port')

connectingString = "dbname=%s user=%s password=%s host=%s" % (databasename, dbuser, dbpass, dbhost)

# Connecting section
try:
    conn = psycopg2.connect(connectingString);

except psycopg2.OperationalError:
    print "Could not connect to the server" 
    sys.exit("ConnectionError")


# Searching for the ssh key using the default keys

try:
    keypath=os.path.expanduser('~/.ssh/id_rsa.pub')
except:
    keypath=os.path.expanduser('~/.ssh/id_dsa.pub')

# Version switch optparse exists only from Python V2.3 to 2.6

if sys.version_info < (2, 7):
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--key', '-k', dest='keytossh', help='Path to the Key (default: ~/.ssh/id_dsa.pub)', default=keypath)
    parser.add_option('--role', '-r', dest='role', help='Role of the user (default: admin)', default='admin')
    parser.add_option('--realname', '-R', dest='realname', help="Name of the key owner", default='')
    (options, args) = parser.parse_args()
    keypath=options.keytossh
    theRole=options.role
    theName=options.realname
# Python 2.7 and above
else: 
    print "using argparse"
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', '-k', dest='keytossh', help='Path to the Key (default: ~/.ssh/id_dsa.pub)', default=keypath)
    parser.add_argument('--role', '-r', dest='role', help='Role of the user (default: admin)', default='admin')
    parser.add_argument('--realname' '-R', dest='realname', help="Name of the key owner", default='')
    args = parser.parse_args()
#Check if the key exists, make a checksum and read it

try:
    keyssh = open(keypath, 'r')
    keychecksum = hashlib.md5(open(options.keytossh, "rb").read()).hexdigest()
    readFile=keyssh.read()
except IOError:
    print "File not found in %s", keypath
    sys.exit("File not found")

# some Vars
users = ({"key":readFile, "role": options.role, "keySum":keychecksum, "path": keypath, "Ownerm": theName})

# check if the key exists in the database
#checkIfExists = "select keyfile from users where keyfile='%(key)s'" % users


cursor = conn.cursor()

# Database stuff if key not exists insert, else close the db-connection and make a clean exit
try:
    users = ({"key":readFile, "role": options.role, "keySum":keychecksum, "path": keypath, "realname": theName})
    myQuery = "insert into users values ('%(key)s', '%(role)s', '%(keySum)s', '%(path)s', '%(realname)s')" % users
    cursor.execute(myQuery)
    conn.commit()
    print "Commited key successful in the database"
except psycopg2.IntegrityError:
    print "SSH-key exists in the database"
    conn.close()
    sys.exit()

conn.close()
