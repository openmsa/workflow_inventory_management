from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()
dev_var.add('newAsnId', var_type='String')
dev_var.add('newAssignmentDescription', var_type='String')

context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name'] or not context['poolStart'] or not context['poolEnd']:
	MSA_API.task_error('Mandatory parameters required, please edit the ASN pool',context, True)

if not context.get('asnsInUse'):
	context['asnsInUse']=[]
	
if not context.get('newAsnId'):
	context['newAsnId']=''
	
if not context.get('newAssignmentDescription'):
	context['newAssignmentDescription']=''
	
newAsnId=context['newAsnId']
newAssignmentDescription=context['newAssignmentDescription']
usedList=""

if not newAsnId:
	#get new ASN Id from the given range
	for i in range(int(context['poolStart']),int(context['poolEnd'])+1):
		if not context['asnsInUse']:
			newAsnId=str(i)
			break
		else:
			freeASN=True
			for asnInUse in context['asnsInUse']:
				if str(i) == asnInUse['asnId']:
					freeASN=False
					break
			if freeASN:
				newAsnId=str(i)
				break

	if not newAsnId:
		MSA_API.task_error('All ASN Ids from the range '+context['poolStart']+' - '+context['poolEnd']+' have been allocated', context, True)
else:
	# Check if given ASN Id is included in the range
	if int(context['poolStart']) > int(newAsnId) or int(newAsnId) > int(context['poolEnd']):
		MSA_API.task_error('ASN Id '+newAsnId+" not on the available range ("+context['poolStart']+" - "+context['poolEnd']+")", context, True)	
	
	# Check if given ASN Id is not starting with 0 (eg : 01)
	if newAsnId.startswith('0'):
		MSA_API.task_error('ASN Id '+newAsnId+" not valid, please retry", context, True)	
	
	#Check if the given ASN Id is already allocated
	for usedAsn in context['asnsInUse']:
		if newAsnId == usedAsn['asnId']:
			MSA_API.task_error('ASN Id '+newAsnId+" is already in use", context, True)

context['asnsInUse'].append(dict(asnId=newAsnId,assignment_information=newAssignmentDescription))


if context.get('usedAsnIds'):
	usedList=context['usedAsnIds']
usedList=usedList+"\n"+newAsnId
context['usedAsnIds']=usedList

ret = MSA_API.process_content('ENDED', 'New ASN Id '+newAsnId+" has been allocated", context, True)
print(ret)


