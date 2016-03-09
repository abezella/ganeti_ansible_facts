#!/usr/bin/python

from __future__ import print_function
import sys
import json
from httplib import HTTPException
import socket
from pprint import pprint, pformat
import os
from gnt_rapi import GntRapi, GntTagMap
import yaml

def gnt_inst_list(rapi):
  """Get list of all instances (including host-vars)"""
  group_map=dict()
  meta_list=dict()
  instance_data=rapi.query(["name","tags","os","status"],None,
    "instance")["data"]
  for i in instance_data:
    instance_name=i[0][1]
    tags=GntTagMap(i[1][1])
    if not tags.nolist:
      tags.add_fact("os",i[2][1])
      tags.add_fact("status",i[3][1])
      tags.add_to_group_map(group_map,instance_name)
      meta_list[instance_name]={"ganeti":tags.dump()}
  group_map["_meta"]=meta_list
  return group_map

def gnt_inst_get(rapi,name):
  """Get host-vars for host //name//"""
  vars_raw=rapi.query(["tags","os","status"],["=","name",name],
    "instance")["data"][0]
  tags=GntTagMap(vars_raw[0][1])
  if tags.nolist:
    return False
  tags.add_fact("os",vars_raw[1][1])
  tags.add_fact("status",vars_raw[2][1])
  return {"ganeti":tags.dump()}


def err(msg,rc=1):
  pprint(msg,stream=sys.stderr)
  sys.exit(rc)


def main():
  """Main procedure"""
  # read configuration
  try:
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
      'rapi.yml'),'r') as stream:
        conf_data=yaml.load(stream)
  except yaml.YAMLError as e:
    err("Configuration file syntax error: %s " % e)
  except IOError as e:
    err("Configuration file error: %s " % e)

  if "ganeti" in conf_data and "rapi" in conf_data["ganeti"]:
    # parse command line arguments
    name=sys.argv[2] if len(sys.argv)>2 and sys.argv[1]=="--host" else False
    try:
      # RAPI initialization
      rapi=GntRapi(conf_data["ganeti"]["rapi"]["host"],
        conf_data["ganeti"]["rapi"]["port"],conf_data["ganeti"]["rapi"]["user"],
        conf_data["ganeti"]["rapi"]["pass"])
      if name: # --host
        tag_info=gnt_inst_get(rapi,name)
        if not tag_info:
          err("No data for host")
      else: # --list
        tag_info=gnt_inst_list(rapi)
    except HTTPException as e:
      err("HTTP error: %s " % e)
    except socket.error as e:
      err("HTTP Socket error: %s" %e)
    except Exception as e:
      err("Error: %s " % e)
    else:
      # return data if no error occured
      print(json.dumps(tag_info,indent=4))

if __name__ == '__main__':
  main()

# vim:ff=unix ts=2 sw=2 ai expandtab
