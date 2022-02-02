from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()
dev_var.add('newVpcId', var_type='String')
dev_var.add('newAssignmentDescription', var_type='String')

context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name'] or not context['poolStart'] or not context['poolEnd']:
	MSA_API.task_error('Mandatory parameters required, please edit the vPC pool',context, True)

if not context.get('vpcsInUse'):
	context['vpcsInUse']=[]
	
if not context.get('newVpcId'):
	context['newVpcId']=''
	
if not context.get('newAssignmentDescription'):
	context['newAssignmentDescription']=''
	
newVpcId=context['newVpcId']
newAssignmentDescription=context['newAssignmentDescription']
usedList=""

if not newVpcId:
	#get new vPC Id from the given range
	for i in range(int(context['poolStart']),int(context['poolEnd'])+1):
		if not context['vpcsInUse']:
			newVpcId=str(i)
			break
		else:
			freeVPC=True
			for vpcInUse in context['vpcsInUse']:
				if str(i) == vpcInUse['vpcDomainId']:
					freeVPC=False
					break
			if freeVPC:
				newVpcId=str(i)
				break

	if not newVpcId:
		MSA_API.task_error('All vPC Ids from the range '+context['poolStart']+' - '+context['poolEnd']+' have been allocated', context, True)
else:
	# Check if given vPC Id is include on the range
	if int(context['poolStart']) > int(newVpcId) or int(newVpcId) > int(context['poolEnd']):
		MSA_API.task_error('vPC Id '+newVpcId+" not on the available range ("+context['poolStart']+" - "+context['poolEnd']+")", context, True)	
	# Check if given vPC Id is not starting with 0 (eg : 01)
	if newVpcId.startswith('0'):
		MSA_API.task_error('vPC Id '+newVpcId+" not valid, please retry", context, True)
	#Check if the given vPC Id is already allocated
	for usedVpc in context['vpcsInUse']:
		if newVpcId == usedVpc['vpcDomainId']:
			MSA_API.task_error('vPC Id '+newVpcId+" is already in use", context, True)

context['vpcsInUse'].append(dict(vpcDomainId=newVpcId,assignment_information=newAssignmentDescription))


if context.get('usedVpcIds'):
	usedList=context['usedVpcIds']
usedList=usedList+"\n"+newVpcId
context['usedVpcIds']=usedList

ret = MSA_API.process_content('ENDED', 'New vPC Id '+newVpcId+" has been allocated", context, True)
print(ret)


