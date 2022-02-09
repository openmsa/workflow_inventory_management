from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
dev_var.add('vlanIdToRelease', var_type='String')
dev_var.add('vlanRangeList.0.poolStart', var_type='String')
dev_var.add('vlanRangeList.0.poolEnd', var_type='String')
dev_var.add('vlanRangeList.0.isSelected',var_type='Boolean')

context = Variables.task_call(dev_var)

if len(context['vlanRangeList']) != len(context['vlanRangeList_backup']):
	context['vlanRangeList']=context['vlanRangeList_backup']
	MSA_API.task_error('Vlan Pool update cannot be done from this process',context, True)

if not context.get('vlansInUse'):
  context['vlansInUse'] = []

if not context.get('vlanRangeList'):
  context['vlanRangeList'] = []
  
if not context['device_id'] or not context['name']:
	MSA_API.task_error('Mandatory parameters required, please edit the VLAN pool',context, True)
	
if not context.get('vlansInUse'):
  context['vlansInUse'] = []

if not context.get('vlanIdToRelease'):
	MSA_API.task_error('Please enter an VLAN Id to be released', context, True)
	
vlanIdToRelease=context['vlanIdToRelease']

# Check if given VLAN Id is not starting with 0 (eg : 01)
if vlanIdToRelease.startswith('0'):
	MSA_API.task_error('VLAN Id '+vlanIdToRelease+" not valid, please retry", context, True)


SelectedVlanRangeStart=""
SelectedVlanRangeEnd=""

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
vlantoRelease=[]


# Check if given Vlan Id is include on the range
if int(SelectedVlanRangeStart) > int(vlanIdToRelease) or int(vlanIdToRelease) > int(SelectedVlanRangeEnd):
	MSA_API.task_error('VLAN Id '+vlanIdToRelease+" not on the available range ("+SelectedVlanRangeStart+" - "+SelectedVlanRangeEnd+")", context, True)	
# Check if given VLAN Id is not starting with 0 (eg : 01)
if vlanIdToRelease.startswith('0'):
	MSA_API.task_error('VLAN Id '+vlanIdToRelease+" not valid, please retry", context, True)

vlanReleased=False
for vlanIdInUse in context['vlansInUse']:
	if (vlanIdToRelease == vlanIdInUse['vlanId']) and (str(vlanIdInUse['assignment_information']) == 'From VLAN Pool '+context['SelectedVlanRangeStart']+' - '+context['SelectedVlanRangeEnd']+''):
		vlanReleased=True
		vlantoRelease.append(dict(vlanId=vlanIdInUse['vlanId'],assignment_information=vlanIdInUse['assignment_information']))
		break
	
context['vlantoRelease']=vlantoRelease

if not vlanReleased:
	MSA_API.task_error('VLAN Id '+vlanIdToRelease+' not found as used in Pool '+context['SelectedVlanRangeStart']+' - '+context['SelectedVlanRangeEnd']+'', context, True)

vlansInUseTemp=[]
for vlanIdInUse in context['vlansInUse']:
	#if ((context['vlantoRelease'][0]['vlanId'] != vlanIdInUse['vlanId']) and (str(vlanIdInUse['assignment_information']) != str(context['vlantoRelease'][0]['assignment_information']))):
	if vlanIdInUse not in context['vlantoRelease']:		
		vlansInUseTemp.append(dict(vlanId=vlanIdInUse['vlanId'],assignment_information=vlanIdInUse['assignment_information']))

context['vlansInUse']=vlansInUseTemp

for vlanRange in context['pool']:
	if (vlanRange['poolStart'] == SelectedVlanRangeStart) and (vlanRange['poolEnd'] == SelectedVlanRangeEnd):
		vlanRange['poolInUse']-=1
		break
	
ret = MSA_API.process_content('ENDED', 'The VLAN Id '+vlanIdToRelease+' has been released from Pool range '+context['SelectedVlanRangeStart']+' - '+context['SelectedVlanRangeEnd']+'', context, True)
print(ret)
