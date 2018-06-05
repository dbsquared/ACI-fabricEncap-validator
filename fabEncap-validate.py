import json,re,argparse,commands


parser=argparse.ArgumentParser(description='To analyze the fabricEncap deployment of your ACI fabric')
parser.add_argument('--option',dest='option',action='store',default=None,help='available options: overlapVlanPool')
parser.add_argument('--file',dest='file',action='store',default=None,help='offline file')

args=parser.parse_args()
option  = args.option
file = args.file
if file:
    f = open(file, 'r')
    vlanCktEpLines = []
    for line in f:
        vlanCktEpLines.append(line)

else:
    vlanCktEpLines = commands.getstatusoutput('moquery -c vlanCktEp')[1].split('\n')

"""
Example of the moquery output:

Total Objects shown: 35

# vlan.CktEp
encap                    : vlan-2050    <<<<<<<
adminSt                  : active
allowUsegUnsupported     : 0
childAction              :
classPrefOperSt          : encap
createTs                 : 2018-04-24T07:45:25.000+00:00
ctrl                     : policy-enforced
dn                       : topology/pod-1/node-101/sys/ctx-[vxlan-3047425]/bd-[vxlan-16744306]/vlan-[vlan-2050]  <<<<
enfPref                  : hw
epUpSeqNum               : 0
epgDn                    : uni/tn-test-tenant/ap-test-AP/epg-test-EPG <<<<
excessiveTcnFlushCnt     : 0
fabEncap                 : vxlan-9092      <<<<<<<<<
floodInEncapUnsupported  : 0
fwdCtrl                  : mdst-flood
hwId                     : 13
id                       : 12
lcOwn                    : local
modTs                    : 2018-04-24T07:41:46.929+00:00
mode                     : CE
monPolDn                 : uni/tn-common/monepg-default
name                     : panjaisi-tenant:test-AP:test-EPG
operSt                   : up
operStQual               : unspecified
operState                : 0
pcTag                    : 16386
proxyArpUnsupported      : 0
qosPrio                  : unspecified
qosmCfgFailedBmp         :
qosmCfgFailedTs          : 00:00:00:00.000
qosmCfgState             : 0
rn                       : vlan-[vlan-2050]
status                   :
type                     : ckt-vlan
vlanmgrCfgFailedBmp      :
vlanmgrCfgFailedTs       : 00:00:00:00.000
vlanmgrCfgState          : 0
vlanmgrCustFaultBmp      :
"""

parsed1stLvl = []
vlanCktEpTmpDict = {}


"""
First level parsing: from lines to list of vlanCktEp with each field as key and value
for example:

[
    {
        "encap": "vlan-2622",
        "adminSt": "active",
        "allowUsegUnsupported": "0",
        "childAction": ""
        ....
    }

]
"""
for idx, line in enumerate(vlanCktEpLines):
    if "# vlan.CktEp" in line:
        if vlanCktEpTmpDict:
            parsed1stLvl.append(vlanCktEpTmpDict)
            vlanCktEpTmpDict = {}  # reinitialize the temp dictionary
    elif "Total Objects shown:" in line:
        continue
    elif line.strip() is "":
        if idx == len(vlanCktEpLines)-1:
            parsed1stLvl.append(vlanCktEpTmpDict)
        else:
            continue
    else:
        key = line.split(":")[0].strip()
        value = line.split(":")[1].strip()
        vlanCktEpTmpDict[key] = value
        if idx == len(vlanCktEpLines)-1:  # if this is the last line
            parsed1stLvl.append(vlanCktEpTmpDict)
#print(parsed1stLvl)
#print(len(parsed1stLvl))

epgEncapDict = {}
"""
epgEncapDict:
{
	'uni/tn-abc/ap-def/epg-ghi':{
		'vlan-100':[
			{
				'node': '101',
				'fabEncap': '12345'
			},
			{
				'node': '102',
				'fabEncap': '12346'
			}			
		],
		'vlan-101':[
			{
				'node': '101',
				'fabEncap': '12342'
			},
			{
				'node': '102',
				'fabEncap': '12069'
			}			
		]		
	}
}
"""


for vlanCktEp in parsed1stLvl:
    epgDn = vlanCktEp["epgDn"]
    accessEncap = vlanCktEp["encap"]
    fabEncap = vlanCktEp["fabEncap"]
    node = re.search('node-([0-9]+)/', vlanCktEp["dn"]).group(1)
    if epgDn not in epgEncapDict:
        epgEncapDict[epgDn] = {}

    if accessEncap not in epgEncapDict[epgDn]:
        epgEncapDict[epgDn][accessEncap] = []

    encapDictTmp = {}
    encapDictTmp['node'] = node
    encapDictTmp['fabEncap'] = fabEncap
    epgEncapDict[epgDn][accessEncap].append(encapDictTmp)



#print(epgEncapDict)


if option == "overlapVlanPool":
    result = []
    for key, epg in epgEncapDict.iteritems():
        for vlanKey, vlan in epg.iteritems():
            fabEncapTemp=""
            for deployment in vlan:
                if fabEncapTemp == "" or deployment["fabEncap"] == fabEncapTemp:
                    fabEncapTemp = deployment["fabEncap"]
                else: # something is wrong
                    tmpDict = {}
                    tmpDict["epgDn"] = key
                    tmpDict["epgDeployment"] = epg
                    if tmpDict not in result:    # some epg has more than one access encap.
                        result.append(tmpDict)
                    break
    if len(result) == 0:
        print("No issue found")
    else:
        #print result
        for item in result:
            print("epgDn:    " + item["epgDn"])
            for key, nodeFabEncaps in item["epgDeployment"].iteritems():
                print("++ " + key )
                for nodeFabEncap in nodeFabEncaps:
                    print("---- " + 'node ' +  nodeFabEncap['node'] + " : " + nodeFabEncap['fabEncap'])

else:
    print("Invalid option")
