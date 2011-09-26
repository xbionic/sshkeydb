#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Michael Dierks (michael dot dierks at gmail dot com)
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
import ConfigParser
import sshdb
import argparse


def main():
    configPresent = sshdb.configCheck()
    if configPresent != 0:
        sys.exit("No configfile found, please use \
        sshdbconfig.py to create a default config")
    # parse config und connect
    connectingString = sshdb.parseConfig()
    if connectingString[0] == 1:
        sys.exit("Please edit your configfile")
    if connectingString[0] == 'postgresql':
        conn = sshdb.connectpsql(connectingString[1])
    if connectingString[0] == 'mysql':
        import MySQLdb
        conn = MySQLdb.connect(read_default_file="~/sshkeydb.conf")

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--role', '-r', dest='',
        help='Role of the user (default: admin)', default='')
        parser.add_argument('--realname', '-R', dest='realname',
        help='Name of the key owner', default='')
        parser.add_argument('--revoke', dest='revoke',
        help='Revoke (boolean (true/false)', default='false')
        parser.add_argument('--listkey', '-l', dest='listing',
        help='listkeys', default='')
        args = parser.parse_args()
        theRole = args.role
        theName = args.realname
        theRevoke = args.revoke
        theListing = args.listing
    except:
        sys.exit("Wrong commandline arguments")

    try:
        if TheListing == None:
            print "moo"
        else:
            print TheListing
    except:
        print "the fuck"

main()
