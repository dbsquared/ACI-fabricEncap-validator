# ACI Fabric Encap Validator

This project is to validate the fabric encap deployment within the ACI fabric.
In most use cases, it will be used to detect overlapping vlan pool issues.

```
python fabEncap-validate.py --help
usage: fabEncap-validate.py [-h] [--option OPTION] [--file FILE]

To analyze the fabricEncap deployment of your ACI fabric

optional arguments:
  -h, --help       show this help message and exit
  --option OPTION  available options: overlapVlanPool
  --file FILE      offline file
```


## Getting Started

### Online mode
* Copy the script to any of your APICs
* Run it with python:

```
apic1# python fabEncap-validate.py --option overlapVlanPool
epgDn:    uni/tn-diqiu/ap-overlapping-test/epg-test-epg
++ vlan-100
---- node 103 : vxlan-12491
---- node 104 : vxlan-12542
++ vlan-99
---- node 103 : vxlan-12490
---- node 104 : vxlan-12541
```
* If using option overlapVlanPool, it will detect any EPG that has fabric encap discrepancy.
* If using option raw, it will print out all the fabric encap per EPG per access encap. [under construction]
* Other ideas about fabric encap validation will be welcomed.

### Offline mode
* Collect the output of 'moquery -c vlanCktEp' in a text file
* For example: 'moquery -c vlanCktEp > vlanCktEp.txt'
* Copy the script fabEncap-validate.py and the text file to any machine that runs Python 2.7
* Run it with python:

```
# python fabEncap-validate.py --option overlapVlanPool --file vlanCktEp.txt
epgDn:    uni/tn-diqiu/ap-overlapping-test/epg-test-epg
++ vlan-100
---- node 104 : vxlan-12542
---- node 103 : vxlan-12491
++ vlan-99
---- node 104 : vxlan-12541
---- node 103 : vxlan-12490
```
* Options should be the same as Online mode.