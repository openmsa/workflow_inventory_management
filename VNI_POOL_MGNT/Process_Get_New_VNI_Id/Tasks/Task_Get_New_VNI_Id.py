from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()
context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name']:
	MSA_API.task_error('Mandatory parameters required, please edit the VNI pool',context, True)

if not context.get('pool'):
	MSA_API.task_error('You need to enter at least one VNI pool range',context, True)
	
if not context.get('vnisInUse'):
	context['vnisInUse']=[]
	
if not context.get('newVniId'):
	context['newVniId']=''
	
if not context.get('newAssignmentDescription'):
	context['newAssignmentDescription']=''
	
newVniId=context['newVniId']
newAssignmentDescription=context['newAssignmentDescription']

SelectedVniRangeStart=""
SelectedVniRangeEnd=""

usedList=""
nbSelected=0

if context.get('vniRangeList'):
	for vniRange in context['vniRangeList']:
		if vniRange.get('isSelected'):
			if not vniRange['isSelected']=='false':
				SelectedVniRangeStart= vniRange['poolStart']
				SelectedVniRangeEnd= vniRange['poolEnd']
				nbSelected+=1

if nbSelected == 0:
	MSA_API.task_error( 'You need to select one of the avaiable pool range ', context, True)
if nbSelected > 1:
	MSA_API.task_error( 'You need to select only one pool range ', context, True)

context['SelectedVniRangeStart']=SelectedVniRangeStart
context['SelectedVniRangeEnd']=SelectedVniRangeEnd	
				
if not newVniId:
	#get new VNI Id from the given range
	for i in range(int(SelectedVniRangeStart),int(SelectedVniRangeEnd)+1):
		if not context['vnisInUse']:
			newVniId=str(i)
			break
		else:
			freeVNI=True
			for vniInUse in context['vnisInUse']:
				if (str(i) == vniInUse['vniId']) and (str(vniInUse['assignment_information']) == 'From VNI Pool '+context['SelectedVniRangeStart']+' - '+context['SelectedVniRangeEnd']+''):
					freeVNI=False
					break
			if freeVNI:
				newVniId=str(i)
				break

	if not newVniId:
		MSA_API.task_error('All VNI Ids from the range '+SelectedVniRangeStart+' - '+SelectedVniRangeEnd+' have been allocated', context, True)
else:
	# Check if given VNI Id is include on the range
	if int(SelectedVniRangeStart) > int(newVniId) or int(newVniId) > int(SelectedVniRangeEnd):
		MSA_API.task_error('VNI Id '+newAsnId+" not on the available range ("+SelectedVniRangeStart+" - "+SelectedVniRangeEnd+")", context, True)	
	# Check if given VNI Id is not starting with 0 (eg : 01)
	if newVniId.startswith('0'):
		MSA_API.task_error('VNI Id '+newVniId+" not valid, please retry", context, True)
	#Check if the given VNI Id is already allocated
	for usedVni in context['vnisInUse']:
		if (newVniId == usedVni['vniId']) and (str(usedVni['assignment_information']) == 'From VNI Pool '+context['SelectedVniRangeStart']+' - '+context['SelectedVniRangeEnd']+''):
			MSA_API.task_error('VNI Id '+newVniId+" is already in use", context, True)

newAssignmentDescription='From VNI Pool '+SelectedVniRangeStart+' - '+SelectedVniRangeEnd+''
context['vnisInUse'].append(dict(vniId=newVniId,assignment_information=newAssignmentDescription))

if context.get('usedVniIds'):
	usedList=context['usedVniIds']
usedList=usedList+"\n"+newVniId
context['usedVniIds']=usedList

ret = MSA_API.process_content('ENDED', 'New VNI Id '+newVniId+" has been allocated", context, True)
print(ret)


