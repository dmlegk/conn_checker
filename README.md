# conn_checker

A simple script to check connectivity in bulk.

Usage:
conn_checker.py <inputfile>

The script accepts a file name as a parameter.
That file should have source and destination hosts and port in each line.

Currently it accepts 2 forms:

1) simple: 3 space separated values: src dst port

2) jira table as it is usually specified in firewall change requests, for example:
```
||Zone name||Source||Destination||Port||Status||
|zone|host1|host2|8220|
```
