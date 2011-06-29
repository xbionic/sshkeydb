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
import sshdb
import argparse


# same stuff as in sshkeydeploy.py
sshdb.configCheck()
connectingString = sshdb.parseConfig()
conn = sshdb.connectDB(connectingString)

try:
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', '-r', dest='role', help='Role of the user (default: admin)', default='admin')
    parser.add_argument('--realname', '-R', dest='realname', help='Name of the key owner', default='')
    args = parser.parse_args()
    theRole=args.role
    theName=args.realname
except:
    sys.exit("Wrong commandline arguments")

#fetchedQuery = sshdb.fQuery(conn, getRole)
#sshdb.isKeyPresent(fetchedQuery)
#for key in fetchedQuery:
#    dbkey=sshdb.hashCheck(key[2])
#    if dbkey == key[4]:
#        auth = open(os.path.expanduser('~/.ssh/authorized_keys2'), 'a')
#        for key in auth:
#            if key == key[
#    else:
#        print("Key corrupted")
#        sys.exit("Aborted")

try:
    getRole = "select role, realname, keyfile, keypath, checksum from users where role='%s'" % theRole
    cursor = conn.cursor()
    cursor.execute(getRole)
    myresults = cursor.fetchall()
    for key in myresults:
        getKey=key[2]
        keychecksum = hashlib.sha256(getKey).hexdigest()
        if key[4] == keychecksum:
            print "Checksum ok"
        else:
            print "Checksum is different"
            sys.exit("Aborting")

        auth = open(os.path.expanduser('~/.ssh/authorized_keys2'), 'a')
        auth.write(key[2])
        auth.close()
except:
    print "Database Error"
