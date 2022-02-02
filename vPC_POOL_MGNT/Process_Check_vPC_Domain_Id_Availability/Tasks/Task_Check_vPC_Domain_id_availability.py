from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
dev_var.add('searchedVpcId', var_type='String')


context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name'] or not context['poolStart'] or not context['poolEnd']:
	MSA_API.task_error('Mandatory parameters required, please edit the vPC pool',context, True)
	
if not context.get('vpcsInUse'):
  context['vpcsInUse'] = []

if not context.get('searchedVpcId'):
	MSA_API.task_error('Please enter an vPC Domain Id to search', context, True)
	
searchedVpcId=context['searchedVpcId']

# Check if given vPC Id is include on the range
if int(context['poolStart']) > int(searchedVpcId) or int(searchedVpcId) > int(context['poolEnd']):
	MSA_API.task_error('vPC Id '+searchedVpcId+" not on the available range ("+context['poolStart']+" - "+context['poolEnd']+")", context, True)
		
#Check if the given vPC Domain Id is already allocated
freeVpcId=True
for vpcIdInUse in context['vpcsInUse']:
	if searchedVpcId == vpcIdInUse['vpcDomainId']:
		freeVpcId=False
		break
if not freeVpcId:
  MSA_API.task_error('vPC Domain Id '+searchedVpcId+" is already in use", context, True)

		
ret = MSA_API.process_content('ENDED', 'The vPC Domain Id '+searchedVpcId+" is available", context, True)
print(ret)


