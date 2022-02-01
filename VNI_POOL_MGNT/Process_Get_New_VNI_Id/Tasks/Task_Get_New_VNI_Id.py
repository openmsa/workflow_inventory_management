from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()
dev_var.add('newVniId', var_type='String')
dev_var.add('newDomainName', var_type='String')
dev_var.add('newAssignmentDescription', var_type='String')

context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name'] or not context['poolStart'] or not context['poolEnd']:
	MSA_API.task_error('Mandatory parameters required, please edit the VNI pool',context, True)

if not context.get('vnisInUse'):
	context['vnisInUse']=[]
if not context.get('newVniId'):
	context['newVniId']=''
if not context.get('newAssignmentDescription'):
	context['newAssignmentDescription']=''
	
if not context.get('newDomainName'):
	MSA_API.task_error('VNI Domain name required',context, True)
	
newVniId=context['newVniId']
newAssignmentDescription=context['newAssignmentDescription']
newDomainName=context['newDomainName']
usedList=""

if not newVniId:
	#get new VNI Id from the given range
	for i in range(int(context['poolStart']),int(context['poolEnd'])+1):
		if not context['vnisInUse']:
			newVniId=str(i)
			break
		else:
			freeIP=True
			for vniInUse in context['vnisInUse']:
				if str(i) == vniInUse['vniId']:
					freeIP=False
					break
			if freeIP:
				newVniId=str(i)
				break

	if not newVniId:
		MSA_API.task_error('All VNI Ids from the range '+context['poolStart']+' - '+context['poolEnd']+' have been allocated', context, True)
else:
	# Check if given VNI Id is include on the range
	if int(context['poolStart']) > int(newVniId) or int(newVniId) > int(context['poolEnd']):
		MSA_API.task_error('VNI Id '+newVniId+" not on the available range ("+context['poolStart']+" - "+context['poolEnd']+")", context, True)	
	#Check if the given VNI Id is already allocated
	for usedVni in context['vnisInUse']:
		if newVniId == usedVni['vniId']:
			MSA_API.task_error('Vlan Id '+newVlanId+" is already in use", context, True)

context['vnisInUse'].append(dict(vniId=newVniId,domainName=newDomainName,assignment_information=newAssignmentDescription))


if context.get('usedVniIds'):
	usedList=context['usedVniIds']
usedList=usedList+"\n"+newVniId
context['usedVniIds']=usedList

ret = MSA_API.process_content('ENDED', 'New VNI Id '+newVniId+" has been allocated", context, True)
print(ret)


