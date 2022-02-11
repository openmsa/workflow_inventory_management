from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
dev_var.add('asnIdToRelease', var_type='String')
dev_var.add('asnRangeList.0.poolStart', var_type='String')
dev_var.add('asnRangeList.0.poolEnd', var_type='String')
dev_var.add('asnRangeList.0.isSelected',var_type='Boolean')

context = Variables.task_call(dev_var)

if len(context['asnRangeList']) != len(context['asnRangeList_backup']):
	context['asnRangeList']=context['asnRangeList_backup']
	MSA_API.task_error('ASN Pool update cannot be done from this process',context, True)

if not context.get('asnsInUse'):
  context['asnsInUse'] = []

if not context.get('asnRangeList'):
  context['asnRangeList'] = []
  
if not context['device_id'] or not context['name']:
	MSA_API.task_error('Mandatory parameters required, please edit the ASN pool',context, True)
	
if not context.get('asnsInUse'):
  context['asnsInUse'] = []

if not context.get('asnIdToRelease'):
	MSA_API.task_error('Please enter an ASN Id to be released', context, True)
	
asnIdToRelease=context['asnIdToRelease']

# Check if given ASN Id is not starting with 0 (eg : 01)
if asnIdToRelease.startswith('0'):
	MSA_API.task_error('ASN Id '+asnIdToRelease+" not valid, please retry", context, True)


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
asntoRelease=[]

# Check if given ASN Id is include on the range
if int(SelectedAsnRangeStart) > int(asnIdToRelease) or int(asnIdToRelease) > int(SelectedAsnRangeEnd):
	MSA_API.task_error('ASN Id '+asnIdToRelease+" not on the available range ("+SelectedAsnRangeStart+" - "+SelectedAsnRangeEnd+")", context, True)	
# Check if given ASN Id is not starting with 0 (eg : 01)
if asnIdToRelease.startswith('0'):
	MSA_API.task_error('ASN Id '+asnIdToRelease+" not valid, please retry", context, True)

asnReleased=False
for asnIdInUse in context['asnsInUse']:
	if (asnIdToRelease == asnIdInUse['asnId']) and (str(asnIdInUse['assignment_information']) == 'From ASN Pool '+context['SelectedAsnRangeStart']+' - '+context['SelectedAsnRangeEnd']+''):
		asnReleased=True
		asntoRelease.append(dict(asnId=asnIdInUse['asnId'],assignment_information=asnIdInUse['assignment_information']))
		break
	
context['asntoRelease']=asntoRelease

if not asnReleased:
	MSA_API.task_error('ASN Id '+asnIdToRelease+' not found as used in Pool '+context['SelectedAsnRangeStart']+' - '+context['SelectedAsnRangeEnd']+'', context, True)

asnsInUseTemp=[]
for asnIdInUse in context['asnsInUse']:
	if asnIdInUse not in context['asntoRelease']:		
		asnsInUseTemp.append(dict(asnId=asnIdInUse['asnId'],assignment_information=asnIdInUse['assignment_information']))

context['asnsInUse']=asnsInUseTemp

for asnRange in context['pool']:
	if (asnRange['poolStart'] == SelectedAsnRangeStart) and (asnRange['poolEnd'] == SelectedAsnRangeEnd):
		asnRange['poolInUse']-=1
		break

context['pool_backup']=context['pool']

ret = MSA_API.process_content('ENDED', 'The ASN Id '+asnIdToRelease+' has been released from Pool range '+context['SelectedAsnRangeStart']+' - '+context['SelectedAsnRangeEnd']+'', context, True)
print(ret)
