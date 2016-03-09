# Ganeti Fact Modules and Inventory for Ansible

## Installation
  - clone repo
```sh
$ git clone ...
```
  - run install script, which copies files at the right locations. This might not work in every environment.
```sh
$ chmod 755 install.sh ; ./install.sh
```
  - create Ganeti RAPI configuration file (see below)
  - have fun
```sh
GNT_RAPI_CONF=./rapi_conf.yml ansible-playbook -i /etc/ansible/ganeti-inventory.py someplaybook.yml
```

## Instance groups and owners
Instances may be grouped using ganeti tags prefixed by with "group:".
```sh
$ gnt-instance add-tag "group:foo" someinstance
```
After issuing this command a group "foo" is created containing the instance "someinstance".

Owners work the same way ("owner:someowner") yet its group name is prefixed with "owner.".

## RAPI configuration file
The RAPI configuration file may be specified using the GNT_RAPI_CONF environment variable or creating this file to the same path where the inventory script is located.

The same configuration may also be used as variable file for your Ansible playbooks.

### Example RAPI config file:
```yaml
ganeti:
  rapi: { host: "127.0.0.1", port: 5080, user: "username", pass: "passw0rd"}
```

## Modules
All modules require a "rapi" argument containing the same data as the rapi var in the rapi config file above. None of these modules indicates any state change.

### gnt_net_info module
Gathers facts about networks associated to an ganeti instance.

This module requires a "instance" argument.

Example call:
```yaml
- name: "populate list of interfaces"
  local_action: 
    module: gnt_net_info
    rapi: "{{ganeti.rapi}}"
    instance: "{{inventory_hostname}}"
```

Example output:
```json
"ganeti_net": [
    {
        "gw": "192.168.23.1", 
        "gw6": "fd00:dead:beef::1337", 
        "if": 0, 
        "ipv4": "192.168.23.42", 
        "mac": "ca:ff:ee:23:42:00", 
        "nw": "192.168.123.0/24", 
        "nw6": "fd00:dead:beef::/64", 
        "nw_uuid": "11122233-3444-5550-0666-aaabbbcccddd"
    }]
```

### gnt_tag_info module
This module may have an "type" argument being "instance" (default) or "network" and must have a "name" argument containing the name of the instance or network.

Example call:
```yaml
- name: "populate list of tags"
  local_action: 
    module: gnt_tag_info
    rapi: "{{ganeti.rapi}}"
    type: "instance"
    name: "{{inventory_hostname}}"
```

Example output:
```json
"ganeti_tags": {
    "attrib": {
        "group": [
            "foo"
        ]
    }, 
    "raw": [
        "group:foo"
    ], 
    "simple": []
}
```