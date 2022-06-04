from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()

context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name'] :
	MSA_API.task_error('Mandatory parameters required, please edit the VLAN pool',context, True)

if not context.get('pool'):
	MSA_API.task_error('You need to enter at least one VLAN pool range',context, True)

if not context.get('vlansInUse'):
	context['vlansInUse']=[]
	
if not context.get('newVlanId'):
	context['newVlanId']=''
	
if not context.get('newAssignmentDescription'):
	context['newAssignmentDescription']=''
	
newVlanId=context['newVlanId']
newAssignmentDescription=context['newAssignmentDescription']
newUsageInformation=context['newUsageInformation']

SelectedVlanRangeStart=""
SelectedVlanRangeEnd=""

usedList=""
nbSelected=0

if context.get('vlanRangeList'):
	for vlanRange in context['vlanRangeList']:
		if vlanRange.get('isSelected'):
			if not vlanRange['isSelected']=='false':
				SelectedVlanRangeStart= vlanRange['poolStart']
				SelectedVlanRangeEnd= vlanRange['poolEnd']
				nbSelected+=1

if nbSelected == 0:
	MSA_API.task_error( 'You need to select one of the avaiable pool range ', context, True)
if nbSelected > 1:
	MSA_API.task_error( 'You need to select only one pool range ', context, True)

context['SelectedVlanRangeStart']=SelectedVlanRangeStart
context['SelectedVlanRangeEnd']=SelectedVlanRangeEnd	
		

if not newVlanId:
	#get new VLAN Id from the selected vlan pool range
	for i in range(int(SelectedVlanRangeStart),int(SelectedVlanRangeEnd)+1):
		if not context['vlansInUse']:
			newVlanId=str(i)
			break
		else:
			freeVLAN=True
			for vlanInUse in context['vlansInUse']:
				if (str(i) == vlanInUse['vlanId']) and (str(vlanInUse['assignment_information']) == 'From VLAN Pool '+context['SelectedVlanRangeStart']+' - '+context['SelectedVlanRangeEnd']+''):
					freeVLAN=False
					break
			if freeVLAN:
				newVlanId=str(i)
				break

	if not newVlanId:
		context['newVlanId']=''
		MSA_API.task_error('All Vlan Ids from the range '+SelectedVlanRangeStart+' - '+SelectedVlanRangeEnd+' have been allocated', context, True)
else:
	# Check if given Vlan Id is include on the range
	if int(SelectedVlanRangeStart) > int(newVlanId) or int(newVlanId) > int(SelectedVlanRangeEnd):
		context['newVlanId']=''
		MSA_API.task_error('Vlan Id '+newVlanId+" not on the available range ("+SelectedVlanRangeStart+" - "+SelectedVlanRangeEnd+")", context, True)	
			# Check if given VLAN Id is not starting with 0 (eg : 01)
	if newVlanId.startswith('0'):
		context['newVlanId']=''
		MSA_API.task_error('VLAN Id '+newVlanId+" not valid, please retry", context, True)
		#Check if the given Vlan Id is already allocated
	for usedVlan in context['vlansInUse']:
		if (newVlanId == usedVlan['vlanId']) and (str(usedVlan['assignment_information']) == 'From VLAN Pool '+context['SelectedVlanRangeStart']+' - '+context['SelectedVlanRangeEnd']+''):
			context['newVlanId']=''
			MSA_API.task_error('Vlan Id '+newVlanId+" is already in use", context, True)

newAssignmentDescription='From VLAN Pool '+SelectedVlanRangeStart+' - '+SelectedVlanRangeEnd+''					
context['vlansInUse'].append(dict(vlanId=newVlanId,assignment_information=newAssignmentDescription,usage_information=newUsageInformation))
if context.get('usedVlanIds'):
	usedList=context['usedVlanIds']
usedList=usedList+"\n"+newVlanId
context['usedVlanIds']=usedList

for vlanRange in context['pool']:
	if (vlanRange['poolStart'] == SelectedVlanRangeStart) and (vlanRange['poolEnd'] == SelectedVlanRangeEnd):
		vlanRange['poolInUse']+=1
		break

context['pool_backup']=context['pool']
context['newAssignedVlan']=newVlanId

ret = MSA_API.process_content('ENDED', 'New Vlan Id '+newVlanId+" has been allocated", context, True)
print(ret)
