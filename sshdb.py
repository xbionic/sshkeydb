import ConfigParser
import hashlib
import sys
import os
import psycopg2

config = ConfigParser.RawConfigParser()
def configCheck():
    checkconf = os.path.exists(os.path.expanduser('~/.sshkeydb.conf'))
    if checkconf == False:
        print "Configfile not found create a defaultconf"
        config.add_section('postgresql')
        config.set('postgresql', 'database', 'sshkey')
        config.set('postgresql', 'user', os.getenv('USER'))
        config.set('postgresql', 'password', 'EDITTHIS')
        config.set('postgresql', 'host', 'localhost')
        config.set('postgresql', 'port', '5432')
        with open(os.path.expanduser('~/.sshkeydb.conf'), 'wb') as configfile:
            config.write(configfile)
        sys.exit("Edit your configfile now")

def parseConfig():
        config.read([os.path.expanduser('~/.sshkeydb.conf')])
        databasename=config.get('postgresql','database')
        dbuser=config.get('postgresql','user')
        dbhost=config.get('postgresql','host')
        dbpass=config.get('postgresql','password')
        dbport=config.get('postgresql','port')
        if dbpass == 'EDITTHIS':
            sys.exit('Please edit your configfile')
        connectingString = "dbname=%s user=%s password=%s host=%s" % (databasename, dbuser, dbpass, dbhost)
        return connectingString

def connectDB(connectingString):
        try:
                conn = psycopg2.connect(connectingString);
                return conn 
        except psycopg2.OperationalError:
                print("Could not connect to the server"),
                sys.exit("ConnectionError")

def createSHA256(n):
    try:
        keyssh = open(n, 'r')
        readFile=keyssh.read()
        keychecksum = hashlib.sha256(readFile).hexdigest()
        print keychecksum
        return keychecksum, readFile
    except IOError:
        print("File not found in %s") % n 
        sys.exit("File not found")
        
def iQuery(conn, users):
# Database stuff if key not exists insert, else close the db-connection and make a clean exit
    cursor = conn.cursor()
    try:
        myQuery = "insert into users values ('%(key)s', '%(role)s', '%(keySum)s', '%(path)s', '%(realname)s')" % users
        cursor.execute(myQuery)
        conn.commit()
        print("Commited key successful in the database"),
    except psycopg2.IntegrityError:
        print("SSH-key exists in the database"),
        conn.close()
    sys.exit()


def fQuery(conn, getRole):
    cursor = conn.cursor()
    cursor.execute(getRole)
    myresults = cursor.fetchall()
    return myresults

def hashCheck(readFile):
    hashMe = keychecksum = hashlib.sha256(readFile).hexdigest()
    return hashMe

