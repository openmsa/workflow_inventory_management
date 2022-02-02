from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
dev_var.add('searchedAsnId', var_type='String')


context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name'] or not context['poolStart'] or not context['poolEnd']:
	MSA_API.task_error('Mandatory parameters required, please edit the ASN pool',context, True)
	
if not context.get('asnsInUse'):
  context['asnsInUse'] = []

if not context.get('searchedAsnId'):
	MSA_API.task_error('Please enter an ASN Id to search', context, True)
	
searchedAsnId=context['searchedAsnId']

# Check if given ASN Id is not starting with 0 (eg : 01)
if searchedAsnId.startswith('0'):
	MSA_API.task_error('ASN Id '+searchedAsnId+" not valid, please retry", context, True)

# Check if given ASN Id is include on the range
if int(context['poolStart']) > int(searchedAsnId) or int(searchedAsnId) > int(context['poolEnd']):
	MSA_API.task_error('ASN Id '+searchedAsnId+" not on the available range ("+context['poolStart']+" - "+context['poolEnd']+")", context, True)
		
#Check if the given ASN Id is already allocated
freeAsnId=True
for asnIdInUse in context['asnsInUse']:
	if searchedAsnId == asnIdInUse['asnId']:
		freeAsnId=False
		break
if not freeAsnId:
  MSA_API.task_error('ASN Id '+searchedAsnId+" is already in use", context, True)

		
ret = MSA_API.process_content('ENDED', 'The ASN Id '+searchedAsnId+" is available", context, True)
print(ret)
