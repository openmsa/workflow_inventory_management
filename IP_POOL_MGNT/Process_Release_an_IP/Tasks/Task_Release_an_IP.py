import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.order import Order
from msa_sdk.util import address_is_in_network
from msa_sdk.util import get_ip_range
from msa_sdk.util import cidr_to_range
from ipaddress import ip_network
from statistics import mean

# List all the parameters required by the task
dev_var = Variables()
dev_var.add('ipToRelease', var_type='String')
dev_var.add('totalIpUsage', var_type='String')
dev_var.add('cidrList.0.cidr')
dev_var.add('cidrList.0.totalIps', var_type='String')
dev_var.add('cidrList.0.ipUsedNb', var_type='String')
dev_var.add('cidrList.0.ipUsage', var_type='String')
dev_var.add('cidrList.0.isSelected')
context = Variables.task_call(dev_var)

if "cidrList" not in context:
	MSA_API.task_error('No IP Pool found', context)

if len(context['cidrList']) != len(context['cidrList_backup']):
  context['cidrList']=context['cidrList_backup']
  MSA_API.task_error('IP Pool update cannot be done from this process', context)

if not context.get('IPsInUse'):
  context['IPsInUse'] = []

if not context.get('cidrList'):
  context['cidrList'] = []
  
if not context['device_id'] or not context['name']:
  MSA_API.task_error('Mandatory parameters required, please edit the IP pool', context)
  

if not context.get('ipToRelease'):
  MSA_API.task_error('Please enter the IP to be released', context)
  
ipToRelease=context['ipToRelease']

SelectedCidr=""
nbSelected=0

if context.get('cidrList'):
  for cidr in context['cidrList']:
    if cidr.get('isSelected'):
      if not cidr['isSelected']=='false':
        SelectedCidr= cidr['cidr']
        nbSelected+=1

if nbSelected == 0:
  MSA_API.task_error( 'You need to select one of the avaiable pool range ', context)
if nbSelected > 1:
  MSA_API.task_error( 'You need to select only one pool range ', context)

context['SelectedCidr']=SelectedCidr
iptoRelease=[]

#check if the entered IP address is part of the selectec network (cidr)
if not address_is_in_network(ipToRelease,SelectedCidr):
	MSA_API.task_error('Given address '+ipToRelease+' is not in network '+SelectedCidr, context)
	
ipReleased=False
for ipInUse in context['IPsInUse']:
  if (ipToRelease == ipInUse['address']) and (str(ipInUse['assignment_information']) == 'From IP Pool '+context['SelectedCidr']+''):
    ipReleased=True
    iptoRelease.append(dict(address=ipInUse['address'],assignment_information=ipInUse['assignment_information'],usage_information=ipInUse['usage_information']))
    break
  
context['iptoRelease']=iptoRelease

if not ipReleased:
  MSA_API.task_error('IP '+ipToRelease+' not found as used in Cidr '+context['SelectedCidr']+'', context)

IPsInUseTemp=[]
for ipInUse in context['IPsInUse']:
  if ipInUse not in context['iptoRelease']:   
    IPsInUseTemp.append(dict(address=ipInUse['address'],assignment_information=ipInUse['assignment_information'],usage_information=ipInUse['usage_information']))

context['IPsInUse']=IPsInUseTemp

cidrList=[]
avgPercentList=[]

for ip in context['pool']:
	if (str(''+ip['address']+'/'+ip['prefix']+'') == str(SelectedCidr)):
		ipUsedNb=int(ip['ipUsedNb'])
		ipUsedNb-=1
		ip['ipUsedNb']=str(ipUsedNb)
		percent = "{:.10%}".format((int(ip['totalIps'])-int(ip['ipUsedNb']))/int(ip['totalIps']))
		percent=(float(100)-float(percent.strip('%')))
		percent="{:.10f}".format(round(percent, 10))+"%"
		ip['ipUsage']=str(percent)
	my_dict = dict(cidr=ip['address']+'/'+ip['prefix'],totalIps=ip['totalIps'],ipUsage=ip['ipUsage'],ipUsedNb=ip['ipUsedNb'],isSelected='false')
	cidrList.append(my_dict)
	avgPercentList.append(float(ip['ipUsage'].strip('%')))
		
context['cidrList'] = cidrList
context['totalIpUsage']=str("{:.10f}".format(mean(avgPercentList)))+'%'
#context['totalIpUsage']="-11%"
context['pool_backup']=context['pool']
context['IPsInUse_backup']=context['IPsInUse']

context['newReleasedIP']=ipToRelease

MSA_API.task_success('IP '+ipToRelease+' has been released from Cidr '+context['SelectedCidr']+'', context)
