from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.util import address_is_in_network
from msa_sdk.util import get_ip_range
from msa_sdk.util import cidr_to_range
from ipaddress import ip_network

dev_var = Variables()
dev_var.add('searchedip', var_type='String')

context = Variables.task_call(dev_var)

if "cidrList" not in context:
	MSA_API.task_error('No IP Pool found',context, True)

if len(context['cidrList']) != len(context['cidrList_backup']):
	context['cidrList']=context['cidrList_backup']
	MSA_API.task_error('IP Pool update cannot be done from this process',context, True)
	
if not context['device_id'] or not context['name'] :
	MSA_API.task_error('Mandatory parameters required',context, True)

if not context.get('IPsInUse'):
  context['IPsInUse'] = []
  
if not context.get('cidrList'):
  context['cidrList'] = []

if not context.get('searchedip'):
	MSA_API.task_error('Please enter an IP to search', context, True)
	
searchedip=context['searchedip']

#check if the entered IP address is part of the IP pool networks (cidrs)
context['loop']=''
partOfCidrs="no"
cidrFounded=""
for cidr in context['pool']:
	context['loop']=context['loop']+':'+cidr['address']
	if address_is_in_network(searchedip,cidr['address']+"/"+cidr['prefix']):
		partOfCidrs="yes"
		cidrFounded=cidr['address']+"/"+cidr['prefix']
		
if 	partOfCidrs == "no":
	MSA_API.task_error('Given address '+searchedip+' is not in any IP pool networks', context, True)

		
#Check if the entered IP address is already allocated
freeIP=True
for ipInUse in context['IPsInUse']:
	if (searchedip == ipInUse['address']) and ('From IP Pool '+cidrFounded+'' == ipInUse['assignment_information']):
		freeIP=False
		break
if not freeIP:
  MSA_API.task_error('IP address '+searchedip+' is already in use in Cidr '+cidrFounded+'', context, True)

		
ret = MSA_API.process_content('ENDED', 'The ip '+searchedip+" is available", context, True)
print(ret)


