from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
dev_var.add('searchedVlanId', var_type='String')


context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name'] or not context['poolStart'] or not context['poolEnd']:
	MSA_API.task_error('Mandatory parameters required, please edit the VLAN pool',context, True)
	
if not context.get('VLANsInUse'):
  context['VLANsInUse'] = []

if not context.get('searchedVlanId'):
	MSA_API.task_error('Please enter an VLAN Id to search', context, True)
	
searchedVlanId=context['searchedVlanId']

# Check if given Vlan Id is include on the range
if int(context['poolStart']) > int(searchedVlanId) or int(searchedVlanId) > int(context['poolEnd']):
	MSA_API.task_error('Vlan Id '+searchedVlanId+" not on the available range ("+context['poolStart']+" - "+context['poolEnd']+")", context, True)
		
#Check if the given Vlan Id is already allocated
freeVlanId=True
for vlanIdInUse in context['VLANsInUse']:
	if searchedVlanId == vlanIdInUse['vlanId']:
		freeVlanId=False
		break
if not freeVlanId:
  MSA_API.task_error('VLAN Id '+searchedVlanId+" is already in use", context, True)

		
ret = MSA_API.process_content('ENDED', 'The Vlan Id '+searchedVlanId+" is available", context, True)
print(ret)


