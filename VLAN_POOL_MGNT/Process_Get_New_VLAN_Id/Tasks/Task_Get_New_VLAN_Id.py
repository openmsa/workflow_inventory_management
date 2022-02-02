from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()
dev_var.add('newVlanId', var_type='String')
dev_var.add('newAssignmentDescription', var_type='String')

context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name'] or not context['poolStart'] or not context['poolEnd']:
	MSA_API.task_error('Mandatory parameters required, please edit the VLAN pool',context, True)

if not context.get('vlansInUse'):
	context['vlansInUse']=[]
	
if not context.get('newVlanId'):
	context['newVlanId']=''
	
if not context.get('newAssignmentDescription'):
	context['newAssignmentDescription']=''
	
newVlanId=context['newVlanId']
newAssignmentDescription=context['newAssignmentDescription']
usedList=""

if not newVlanId:
	#get new VLAN Id from the given range
	for i in range(int(context['poolStart']),int(context['poolEnd'])+1):
		if not context['vlansInUse']:
			newVlanId=str(i)
			break
		else:
			freeVLAN=True
			for vlanInUse in context['vlansInUse']:
				if str(i) == vlanInUse['vlanId']:
					freeVLAN=False
					break
			if freeVLAN:
				newVlanId=str(i)
				break

	if not newVlanId:
		MSA_API.task_error('All Vlan Ids from the range '+context['poolStart']+' - '+context['poolEnd']+' have been allocated', context, True)
else:
	# Check if given Vlan Id is include on the range
	if int(context['poolStart']) > int(newVlanId) or int(newVlanId) > int(context['poolEnd']):
		MSA_API.task_error('Vlan Id '+newVlanId+" not on the available range ("+context['poolStart']+" - "+context['poolEnd']+")", context, True)	
	# Check if given VLAN Id is not starting with 0 (eg : 01)
	if newVlanId.startswith('0'):
		MSA_API.task_error('VLAN Id '+newVlanId+" not valid, please retry", context, True)
	#Check if the given Vlan Id is already allocated
	for usedVlan in context['vlansInUse']:
		if newVlanId == usedVlan['vlanId']:
			MSA_API.task_error('Vlan Id '+newVlanId+" is already in use", context, True)

context['vlansInUse'].append(dict(vlanId=newVlanId,assignment_information=newAssignmentDescription))


if context.get('usedVlanIds'):
	usedList=context['usedVlanIds']
usedList=usedList+"\n"+newVlanId
context['usedVlanIds']=usedList

ret = MSA_API.process_content('ENDED', 'New Vlan Id '+newVlanId+" has been allocated", context, True)
print(ret)


