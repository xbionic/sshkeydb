#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import os
import hashlib
import psycopg2
import ConfigParser

# Connecting section
try:
    conn = psycopg2.connect("dbname=sshkey user=USERNAME password=PASSWORD host=localhost");

except psycopg2.OperationalError:
    print "Could not connect to the server" 
    sys.exit("ConnectionError")

# Get the homedir
currentUser=os.getenv('HOME')


# Searching for the ssh key using the default keys

try:
    keypath="%s/.ssh/id_rsa.pub" % currentUser
except:
    keypath="%s/.ssh/id_rsa.pub" % currentUser
IOError:
    print "File not found"
    sys.exit("File not found")

# Version switch optparse exists in Python V2.3 to 2.6

if sys.version_info < (2, 7):
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--key', '-k', dest='keytossh', help='Path to the Key (default: ~/.ssh/id_dsa.pub)', default=keypath)
    parser.add_option('--role', '-r', dest='role', help='Role of the user (default: admin)', default='admin')
    parser.add_option('--realname' '-R', dest='realname', help="Name of the key owner", default='')
    (options, args) = parser.parse_args()
    keypath=options.keytossh
    theRole=options.role
    theName=options.realname
# Python 2.7 and above
else: 
    print "using argparse"
    import argparse

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
checkIfExists = "select keyfile from users where keyfile='%(key)s'" % users


cursor = conn.cursor()

# Database stuff if key not exists insert, else close the db-connection and make a clean exit
try:
    cursor.execute(myQuery)
    conn.commit()
    print "Commited key successful in the database"
except psycopg2.IntegrityError:
    print "SSH-key exists in the database"
    conn.close()
    sys.exit()

conn.close()
