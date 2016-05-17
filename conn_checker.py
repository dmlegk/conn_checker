#!/usr/bin/python

import os
import sys
import subprocess
import time
import re


client_script = '''
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.settimeout(5)
    client_socket.connect(('%s', %s))
except socket.timeout as msg:
    print "[BAD]", msg
else:
    print "[OK] socket connected"

client_socket.close()
'''


server_script = '''
import socket, sys

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    server_socket.bind(('0.0.0.0', %s))
    server_socket.listen(10)
except socket.error as msg:
    print msg.strerror
    sys.exit()

sys.stdout.write("Server started. ")

try:
    server_socket.settimeout(5)
    conn, addr = server_socket.accept()
except socket.timeout as msg:
    print msg
else:
    print "Client connected:", addr

server_socket.close()
'''




def check_single(src, dst, port):

    src = re.sub(r'.*\((.*)\).*', r'\1', src)   # use IP instead of hostname if defined in brackets
    dst = re.sub(r'.*\((.*)\).*', r'\1', dst)


    pid = os.fork()
    if pid == 0:

        # Child process
        p_server = subprocess.Popen(['ssh', '-o ConnectTimeout=5', dst, 'python -'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out_server, err_server = p_server.communicate(server_script % (port))

        print '\tserver out:', out_server.rstrip()
        if err_server:
            print '\tserver err:', err_server.rstrip()

        os._exit(0)


    # Parent process
    time.sleep(1)   # allow server some time to start listening
    p_client = subprocess.Popen(['ssh', '-o ConnectTimeout=5', src, 'python -'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out_client, err_client = p_client.communicate(client_script % (dst, port))

    os.wait()   # wait for child process to finish

    print '\tclient out:', out_client.rstrip()
    if err_client:
        print '\tclient err:', err_client.rstrip()


    return out_client.split()[0]




#
# Main
#

summary = []

fh = open(sys.argv[1], 'r')
for line in fh:


    if line[0] == '#' or line[:2] == '||':          # skip comments and jira table headers
        continue

    try:
        if line[0] == '|':                          # input file in JIRA firewall format

            line = re.sub('[\s+]', '', line)        # strip all spaces
            (src, dst, port) = line.split('|')[2:5]

        else:                                       # input file in simple format (src dst port)
            (src, dst, port) = line.split()

    except:
        continue
    
    print "Trying connection from %s to %s:%s..." % (src, dst, port)
    result = check_single(src, dst, port)
    summary.append((result, src, dst, port))


print '\nSummary:'
for line in summary:
    print "%s - from %s to %s:%s" % line


