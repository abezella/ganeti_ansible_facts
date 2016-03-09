#!/bin/bash

cp gnt_rapi.py /usr/local/lib/python2.7/dist-packages/
chmod 755 /usr/local/lib/python2.7/dist-packages/gnt_rapi.py
cp gnt_index.py /etc/ansible/ganeti-inventory.py
chmod 755 /etc/ansible/ganeti-inventory.py
