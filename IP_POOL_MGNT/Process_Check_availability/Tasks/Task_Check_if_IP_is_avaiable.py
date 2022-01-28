from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.util import address_is_in_network
from msa_sdk.util import get_ip_range
from msa_sdk.util import cidr_to_range
from ipaddress import ip_network

dev_var = Variables()
dev_var.add('searchedip', var_type='String')


context = Variables.task_call(dev_var)

if not context.get('IPsInUse'):
  context['IPsInUse'] = []

if not context.get('searchedip'):
	MSA_API.task_error('Please enter an IP to search', context, True)
	
searchedip=context['searchedip']

#check if the entered IP address is part of the IP pool networks (cidrs)
context['loop']=''
partOfCidrs="no"
for cidr in context['pool']:
	context['loop']=context['loop']+':'+cidr['address']
	if address_is_in_network(searchedip,cidr['address']+"/"+cidr['prefix']):
		partOfCidrs="yes"
		
if 	partOfCidrs == "no":
	MSA_API.task_error('Entered address '+searchedip+' is not in any IP pool networks', context, True)

		
#Check if the entered IP address is already allocated
freeIP=True
for ipInUse in context['IPsInUse']:
	if searchedip == ipInUse['address']:
		freeIP=False
		break
if not freeIP:
  MSA_API.task_error('IP address '+searchedip+" is already in use", context, True)

		
ret = MSA_API.process_content('ENDED', 'The ip '+searchedip+" is available", context, True)
print(ret)


