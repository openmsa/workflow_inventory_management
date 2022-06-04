
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.util import address_is_in_network
from msa_sdk.util import get_ip_range
from msa_sdk.util import cidr_to_range
from ipaddress import ip_network

dev_var = Variables()

context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name'] :
	MSA_API.task_error('Mandatory parameters required',context, True)

if not context.get('IPsInUse'):
	context['IPsInUse']=[]
	
if not context.get('newip'):
	context['newip']=''
	
if not context.get('newAssignmentDescription'):
	context['newAssignmentDescription']=''

if not context.get('newUsageInformation'):
	context['newUsageInformation']=''
	
newip=context['newip']
newAssignmentDescription=context['newAssignmentDescription']
newUsageInformation=context['newUsageInformation']

SelectedCidr=""
usedList=""
nbSelected=0

if context.get('cidrList'):
	for cidr in context['cidrList']:
		if cidr.get('isSelected'):
			if  not cidr['isSelected']=='false':
				SelectedCidr=cidr['cidr']
				nbSelected+=1

if nbSelected == 0:
	MSA_API.task_error( 'You need to select one of the avaiable cidr pool', context, True)
if nbSelected > 1:
	MSA_API.task_error( 'You need to select only one cidr pool ', context, True)
	
context['SelectedCidr']=SelectedCidr

if not newip:
	#get new IP from the selected network (cidr)
	for ip in list(ip_network(SelectedCidr).hosts()):
		if not context['IPsInUse']:
			newip=str(ip)
			break
		else:
			freeIP=True
			for ipInUse in context['IPsInUse']:
				if str(ip) == ipInUse['address']:
					freeIP=False
					break
			if freeIP:
				newip=str(ip)
				break

	if not newip:
		context['newip']=''
		MSA_API.task_error('All IPs from '+SelectedCidr+' have been allocated', context, True)
else:
	#check if the entered IP address is part of the selectec network (cidr)
	if not address_is_in_network(newip,SelectedCidr):
		context['newip']=''
		MSA_API.task_error('Entered address '+newip+' is not in network '+SelectedCidr, context, True)

	#Check if the ntered IP address is already allocated
	for usedIP in context['IPsInUse']:
		if newip == usedIP['address']:
			context['newip']=''
			MSA_API.task_error('IP address '+newip+" is already in use", context, True)

newAssignmentDescription='From IP Pool '+SelectedCidr+''	
context['IPsInUse'].append(dict(address=newip,assignment_information=newAssignmentDescription,usage_information=newUsageInformation))
if context.get('usedIPs'):
	usedList=context['usedIPs']
usedList=usedList+"\n"+newip
context['usedIPs']=usedList

context['newAssignedIP']=newip

ret = MSA_API.process_content('ENDED', 'New ip '+newip+" has been allocated", context, True)
print(ret)


