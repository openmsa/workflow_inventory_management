from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
dev_var.add('searchedVniId', var_type='String')


context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name'] or not context['poolStart'] or not context['poolEnd']:
	MSA_API.task_error('Mandatory parameters required, please edit the VNI pool',context, True)
	
if not context.get('vnisInUse'):
  context['vnisInUse'] = []

if not context.get('searchedVniId'):
	MSA_API.task_error('Please enter an VNI Id to search', context, True)
	
searchedVniId=context['searchedVniId']

# Check if given VNI Id is not starting with 0 (eg : 01)
if searchedVniId.startswith('0'):
	MSA_API.task_error('VNI Id '+searchedVniId+" not valid, please retry", context, True)

# Check if given VNI Id is include on the range
if int(context['poolStart']) > int(searchedVniId) or int(searchedVniId) > int(context['poolEnd']):
	MSA_API.task_error('VNI Id '+searchedVniId+" not on the available range ("+context['poolStart']+" - "+context['poolEnd']+")", context, True)
		
#Check if the given VNI Id is already allocated
freeVniId=True
for vniIdInUse in context['vnisInUse']:
	if searchedVniId == vniIdInUse['vniId']:
		freeVniId=False
		break
if not freeVniId:
  MSA_API.task_error('VNI Id '+searchedVniId+" is already in use", context, True)

		
ret = MSA_API.process_content('ENDED', 'The VNI Id '+searchedVniId+" is available", context, True)
print(ret)


