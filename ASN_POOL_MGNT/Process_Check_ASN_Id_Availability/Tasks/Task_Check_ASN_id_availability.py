from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
dev_var.add('searchedAsnId', var_type='String')
dev_var.add('asnRangeList.0.poolStart', var_type='String')
dev_var.add('asnRangeList.0.poolEnd', var_type='String')
dev_var.add('asnRangeList.0.isSelected',var_type='Boolean')

context = Variables.task_call(dev_var)

if "asnRangeList" not in context:
	MSA_API.task_error('No ASN Pool found',context, True)

if len(context['asnRangeList']) != len(context['asnRangeList_backup']):
	context['asnRangeList']=context['asnRangeList_backup']
	MSA_API.task_error('ASN Pool update cannot be done from this process',context, True)

if not context['device_id'] or not context['name']:
	MSA_API.task_error('Mandatory parameters required, please edit the ASN pool',context, True)

if not context.get('asnRangeList'):
  context['asnRangeList'] = []
  
if not context.get('asnsInUse'):
  context['asnsInUse'] = []

if not context.get('searchedAsnId'):
	MSA_API.task_error('Please enter an ASN Id to search', context, True)
	
searchedAsnId=context['searchedAsnId']

# Check if given ASN Id is not starting with 0 (eg : 01)
if searchedAsnId.startswith('0'):
	MSA_API.task_error('ASN Id '+searchedAsnId+" not valid, please retry", context, True)
	
SelectedAsnRangeStart=""
SelectedAsnRangeEnd=""

nbSelected=0

if context.get('asnRangeList'):
	for asnRange in context['asnRangeList']:
		if asnRange.get('isSelected'):
			if not asnRange['isSelected']=='false':
				SelectedAsnRangeStart= asnRange['poolStart']
				SelectedAsnRangeEnd= asnRange['poolEnd']
				nbSelected+=1

if nbSelected == 0:
	MSA_API.task_error( 'You need to select one of the avaiable pool range ', context, True)
if nbSelected > 1:
	MSA_API.task_error( 'You need to select only one pool range ', context, True)

context['SelectedAsnRangeStart']=SelectedAsnRangeStart
context['SelectedAsnRangeEnd']=SelectedAsnRangeEnd


# Check if given ASN Id is include on the range
if int(context['SelectedAsnRangeStart']) > int(searchedAsnId) or int(searchedAsnId) > int(context['SelectedAsnRangeEnd']):
	MSA_API.task_error('ASN Id '+searchedAsnId+" not on the available range ("+context['SelectedAsnRangeStart']+" - "+context['SelectedAsnRangeEnd']+")", context, True)
		
#Check if the given ASN Id is already allocated
freeAsnId=True
for asnIdInUse in context['asnsInUse']:
	if (searchedAsnId == asnIdInUse['asnId']) and (str(asnIdInUse['assignment_information']) == 'From ASN Pool '+context['SelectedAsnRangeStart']+' - '+context['SelectedAsnRangeEnd']+''):
		freeAsnId=False
		break
if not freeAsnId:
  MSA_API.task_error('ASN Id '+searchedAsnId+' is already in use in Pool range '+context['SelectedAsnRangeStart']+' - '+context['SelectedAsnRangeEnd']+'', context, True)

		
ret = MSA_API.process_content('ENDED', 'The ASN Id '+searchedAsnId+' is available in Pool range '+context['SelectedAsnRangeStart']+' - '+context['SelectedAsnRangeEnd']+'', context, True)
print(ret)
