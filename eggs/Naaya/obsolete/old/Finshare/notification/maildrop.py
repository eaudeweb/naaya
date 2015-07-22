#!/usr/bin/env python2.1
#
# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Original Code is ChangeNotification version 1.0.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by CMG and Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor(s):
# Cornel Nitu, Finsiel Romania

#This product includes software developed by Jens Vagelpohl
#for use in the Z Object Publishing Environment
#(http://www.zope.org/).
#
# maildrop  A daemon to handle mail delivery for the ChangeNotification
usage = """
Maildrop service startup file

Usage: maildrop.py [options]

Options:

  - d

    Debug mode: All output will be written to the terminal

  - h

    Zope home (Must be specified!)
    
  -s

    SMTP host to be used (Must be specified!)

  - i

    Polling interval in seconds
"""

import getopt, smtplib, os, sys, time, signal
import string

DEBUG = 0
MAILDROP_INTERVAL = 120
# User id to run maildrop as. Note that this only works under Unix, and if
# maildrop is started by root.
UID='nobody'
MaildropError = 'Maildrop Error'

def make_daemon():
    if os.getppid() != 1:  # we're already a daemon (started from init)
        if hasattr(signal, 'SIGTTOU'):
            signal.signal(signal.SIGTTOU, signal.SIG_IGN)
        if hasattr(signal, 'SIGTTIN'):
            signal.signal(signal.SIGTTIN, signal.SIG_IGN)
        if hasattr(signal, 'SIGTSTP'):
            signal.signal(signal.SIGTSTP, signal.SIG_IGN)
        pid = os.fork()
        if pid:
            sys.exit(0)
        os.setpgrp()
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
    sys.stdin.close()
    sys.stdout.close()
    sys.stderr.close()
    os.chdir(os.sep)
    os.umask(0)
    signal.signal(signal.SIGCLD, signal.SIG_IGN)


try:
    if sys.version.split()[0] < '2.1':
        raise  MaildropError, 'Invalid python version %s' % sys.version.split[0]

    if len( sys.argv ) < 3:
        print usage

    opts, args = getopt.getopt( sys.argv[1:], 'h:i:s:u:d' )

    for o_key, o_val in opts:
        if o_key == '-h':
            ZOPE_HOME = o_val
            #print ZOPE_HOME
            MAILDROP_HOME = os.path.join(ZOPE_HOME,'var','maildrop')
            if not os.path.isdir( MAILDROP_HOME ):
                raise MaildropError, 'Invalid maildrop home "%s"' % o_val

            MAILDROP_SPOOL = os.path.join( MAILDROP_HOME, 'spool' )
            if not os.path.isdir( MAILDROP_SPOOL ):
                os.mkdir( MAILDROP_SPOOL )

            log_home = os.path.join( MAILDROP_HOME, 'var' )
            if not os.path.isdir( log_home ):
                os.mkdir( log_home )
            LOG_FILE = os.path.join( log_home, 'maildrop.log' )

        if o_key == '-s':
            SMTP_HOST = o_val
            try:
                mail_server = smtplib.SMTP( SMTP_HOST )
                mail_server.quit()
            except:
                raise MaildropError, 'Invalid maildrop SMTP server "%s"' % o_val

        if o_key == '-i':
            try:
                MAILDROP_INTERVAL = int( o_val )
            except:
                raise MaildropError, 'Invalid Maildrop interval "%s"' % str( o_val )

        if o_key == '-d': DEBUG = 1

        if o_key == '-u': UID = o_val

except SystemExit: sys.exit( 0 )
except:
    print usage
    print
    print "%s: %s" % ( sys.exc_type, sys.exc_value )
    print
    sys.exit( 1 )

# Try to set uid to "-u" -provided uid.
# Try to set gid to  "-u" user's primary group.
# This will only work if this script is run by root.
try:
    import pwd
    try:
        try:    UID = string.atoi(UID)
        except: pass
        gid = None
        if type(UID) == type(""):
            uid = pwd.getpwnam(UID)[2]
            gid = pwd.getpwnam(UID)[3]
        elif type(UID) == type(1):
            uid = pwd.getpwuid(UID)[2]
            gid = pwd.getpwuid(UID)[3]
        else:
            raise KeyError
        try:
            if gid is not None:
                try:
                    os.setgid(gid)
                except OSError:
                    pass
            os.setuid(uid)
        except OSError:
            pass
    except KeyError:
        raise MaildropError, "can't find UID %s" % UID
except:
    pass

# Also check if we're running on UNIX/LINUX
if DEBUG == 0 and sys.platform != 'win32':
    make_daemon()

try:
    pid = os.getpid()
except:
    pass # getpid not supported
else:
    pid_home = os.path.join( MAILDROP_HOME, 'var' )
    if not os.path.isdir( pid_home ):
        os.mkdir( pid_home )

    pidfile_path = os.path.join( pid_home, 'maildrop.pid' )
    pid_file = open( pidfile_path, 'w' )
    pid_file.write( '%s\n' %  pid )
    pid_file.close()

if DEBUG:
    print 'Maildrop started with PID %s' % str( pid )

while 1:
    # Are there any files in the spool directory?
    to_be_sent = []
    all_files = os.listdir( MAILDROP_SPOOL )

    if len( all_files ) > 0:
        for file_name in all_files:
            f_name, f_ext = os.path.splitext( file_name )

            # Exclude lock files
            if f_ext == '.lck':
                continue

            # Exclude files that have locked files
            if f_name + '.lck' in all_files:
                continue

            # Exclude directories
            file_path = os.path.join( MAILDROP_SPOOL, file_name )
            if os.path.isdir( file_path ):
                continue

            # Read in file
            file_handle = open( file_path, 'r' )
            file_contents = string.strip(file_handle.read())
            file_handle.close()

            # Is this a real mail turd?
            if not file_contents.startswith( '##To:' ):
                continue

            # Parse and handle content (mail it out)
            mail_dict = {}
            mail_dict['file_path'] = file_path
            file_lines = file_contents.split( '\n' )

            for i in range( len( file_lines ) ):
                if file_lines[i].startswith( '##' ):
                    header_line = file_lines[i][2:]
                    header_key, header_val = header_line.split( ':', 1 )
                    mail_dict[header_key] = header_val
                else:
                    mail_dict['body'] = '\n'.join( file_lines[i:] )
                    break

            to_be_sent.append( mail_dict )


        if len( to_be_sent ) > 0:
            # Open the log file
            time_stamp = time.strftime( '%Y/%m/%d %H:%M:%S' )
            log_file = open( LOG_FILE, 'a' )
            msg = '\n### Started at %s...' % time_stamp
            log_file.write( msg )
            if DEBUG: print msg

            # Send mail
            try:
                smtp_server = smtplib.SMTP( SMTP_HOST )
            except smtplib.SMTPConnectError:
                # SMTP server did not respond. Log it and stop processing.
                time_stamp = time.strftime( '%Y/%m/%d %H:%M:%S' )
                err_msg = '!!!!! Connection error at %s' % time_stamp
                finish_msg = '### Finished at %s' % time_stamp
                log_file.write( err_msg )
                if DEBUG: print err_msg
                log_file.write( finish_msg )
                if DEBUG: print finish_msg
                log_file.close()
                continue

            for mail_dict in to_be_sent:
                # Create mail and send it off
                h_from = mail_dict.get( 'From' )
                h_to = mail_dict.get( 'To' )
                h_to_list = h_to.split( ',' )
                h_body = mail_dict.get( 'body' )

                try:
                    smtp_server.sendmail( h_from, h_to_list, h_body )
                    stat = 'OK'
                    os.remove( mail_dict.get( 'file_path' ) )
                except smtplib.SMTPException, e:
                    stat = 'BAD: ', str(e)

                mail_msg = '\n%s\t %s' % ( stat, h_to )
                log_file.write( mail_msg )
                if DEBUG: print mail_msg
                log_file.flush()


            smtp_server.quit()

            time_stamp = time.strftime( '%Y/%m/%d %H:%M:%S' )
            finish_msg = '\n### Finished at %s\n' % time_stamp
            log_file.write( finish_msg )
            if DEBUG: print finish_msg
            log_file.close()

    time.sleep( MAILDROP_INTERVAL )
