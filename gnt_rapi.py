#!/usr/bin/python
from httplib import HTTPSConnection, HTTPException
import socket
import ssl
import base64
import json

class GntRapi:
  def __init__(self,host,port,ru,rp):
    self.hc=HTTPSConnection(host,port, timeout=20,
      context=ssl._create_unverified_context())
    authstr=base64.encodestring('%s:%s'%(ru,rp)).replace('\n', '')
    self.authhead={"Authorization": "Basic %s"%authstr}

  def get(self,path):
    self.hc.request('GET',path,headers=self.authhead)
    resp=self.hc.getresponse()
    if resp.status==200:
      return json.load(resp)
    elif resp.status==404:
      raise Exception("instance not found.")
    elif resp.status==401:
      raise Exception("login failed.")
    else:
      raise Exception("HTTP status error: %s." % resp.status)

  def _merge_dicts(self,x,y):
    z=x.copy()
    z.update(y)
    return z

  def query(self,qfields,qfilter,qtype="instance"):
    self.hc.request('PUT',"/2/query/"+qtype,
      body=json.dumps({"fields":qfields,"filter":qfilter,
        "qfilter":qfilter}),
      headers=self._merge_dicts(self.authhead,
        {"Content-type":"application/json"}))
    resp=self.hc.getresponse()
    if resp.status==200:
      return json.load(resp)
    elif resp.status==500:
      raise Exception(qtype+" not found.")
    elif resp.status==401:
      raise Exception("login failed.")
    else:
      raise Exception("HTTP status error: %s." % resp.status)

class GntTagMap:
  def __init__(self,tags):
    """Parse tags and group them into simple and key-value tags"""
    self.raw=tags
    self.attrib={}
    self.simple=[]
    self.additional={}
    self.nolist=False

    for i in tags:
      k,s,v=i.partition(":")
      if s != ":": # tag has not key-value type
        # noansible tag marks host as not to be handled by ansible
        if i=="noansible":
          self.nolist=True # True indicates to not include instance in inventory
          return
        self.simple+=[i]
      else: # key-value type
        if k not in self.attrib:
          self.attrib[k]=list()
        self.attrib[k]+=[v]

  def add_to_group_map(self,group_map,instance_name):
    """Generate groups from tags"""
    # group:...
    if "group" in self.attrib:
      for j in self.attrib["group"]:
        if j not in group_map: # if group not listed before create key
          group_map[j]=[]
        group_map[j]+=[instance_name]
    # owner:...
    if "owner" in self.attrib:
      for j in self.attrib["owner"]:
        g="owner."+j
        if g not in group_map: # if group not listed before create key
          group_map[g]=[]
        group_map[g]+=[instance_name]
    # default group to include hosts without group
    if "all" not in group_map:
      group_map["all"]=[]
    group_map["all"]+=[instance_name]


  def add_fact(self,key,value):
    """adds hostvar to dump"""
    self.additional[key]=value

  def dump(self):
    """dumps tags and hostvars"""
    if self.nolist:
      return False
    ret=dict()
    ret["ganeti_info"]=self.additional
    ret["ganeti_tags"]=dict()
    ret["ganeti_tags"]["attrib"]=self.attrib
    ret["ganeti_tags"]["simple"]=self.simple
    ret["ganeti_tags"]["raw"]=self.raw
    return ret

# vim:ff=unix ts=2 sw=2 ai expandtab
