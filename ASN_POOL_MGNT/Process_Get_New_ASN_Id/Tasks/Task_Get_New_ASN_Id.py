from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()

context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name']:
	MSA_API.task_error('Mandatory parameters required, please edit the ASN pool',context, True)
	
if not context.get('pool'):
	MSA_API.task_error('You need to enter at least one ASN pool range',context, True)

if not context.get('asnsInUse'):
	context['asnsInUse']=[]
	
if not context.get('newAsnId'):
	context['newAsnId']=''
	
if not context.get('newAssignmentDescription'):
	context['newAssignmentDescription']=''
	
newAsnId=context['newAsnId']
newAssignmentDescription=context['newAssignmentDescription']
newUsageInformation=context['newUsageInformation']

SelectedAsnRangeStart=""
SelectedAsnRangeEnd=""

usedList=""
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
	
if not newAsnId:
	#get new ASN Id from the given range
	for i in range(int(SelectedAsnRangeStart),int(SelectedAsnRangeEnd)+1):
		if not context['asnsInUse']:
			newAsnId=str(i)
			break
		else:
			freeASN=True
			for asnInUse in context['asnsInUse']:
				if (str(i) == asnInUse['asnId']) and (str(asnInUse['assignment_information']) == 'From ASN Pool '+context['SelectedAsnRangeStart']+' - '+context['SelectedAsnRangeEnd']+''):
					freeASN=False
					break
			if freeASN:
				newAsnId=str(i)
				break

	if not newAsnId:
		context['newAsnId']=''
		MSA_API.task_error('All ASN Ids from the range '+SelectedAsnRangeStart+' - '+SelectedAsnRangeEnd+' have been allocated', context, True)
else:
	# Check if given ASN Id is included in the range
	if int(SelectedAsnRangeStart) > int(newAsnId) or int(newAsnId) > int(SelectedAsnRangeEnd):
		context['newAsnId']=''
		MSA_API.task_error('ASN Id '+newAsnId+" not on the available range ("+SelectedAsnRangeStart+" - "+SelectedAsnRangeEnd+")", context, True)	
	
	# Check if given ASN Id is not starting with 0 (eg : 01)
	if newAsnId.startswith('0'):
		context['newAsnId']=''
		MSA_API.task_error('ASN Id '+newAsnId+" not valid, please retry", context, True)	
	
	#Check if the given ASN Id is already allocated
	for usedAsn in context['asnsInUse']:
		if (newAsnId == usedAsn['asnId']) and (str(usedAsn['assignment_information']) == 'From ASN Pool '+context['SelectedAsnRangeStart']+' - '+context['SelectedAsnRangeEnd']+''):
			context['newAsnId']=''
			MSA_API.task_error('ASN Id '+newAsnId+" is already in use", context, True)

newAssignmentDescription='From ASN Pool '+SelectedAsnRangeStart+' - '+SelectedAsnRangeEnd+''	
context['asnsInUse'].append(dict(asnId=newAsnId,assignment_information=newAssignmentDescription,usage_information=newUsageInformation))

if context.get('usedAsnIds'):
	usedList=context['usedAsnIds']
usedList=usedList+"\n"+newAsnId
context['usedAsnIds']=usedList

for asnRange in context['pool']:
	if (asnRange['poolStart'] == SelectedAsnRangeStart) and (asnRange['poolEnd'] == SelectedAsnRangeEnd):
		asnRange['poolInUse']+=1
		break

context['pool_backup']=context['pool']
context['newAssignedASNId']=newAsnId

ret = MSA_API.process_content('ENDED', 'New ASN Id '+newAsnId+" has been allocated", context, True)
print(ret)


