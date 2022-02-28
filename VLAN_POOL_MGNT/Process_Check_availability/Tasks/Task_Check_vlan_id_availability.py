from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
dev_var.add('searchedVlanId', var_type='String')
dev_var.add('vlanRangeList.0.poolStart', var_type='String')
dev_var.add('vlanRangeList.0.poolEnd', var_type='String')
dev_var.add('vlanRangeList.0.isSelected',var_type='Boolean')

context = Variables.task_call(dev_var)

if "vlanRangeList" not in context:
	MSA_API.task_error('No IP Pool exist',context, True)

if len(context['vlanRangeList']) != len(context['vlanRangeList_backup']):
	context['vlanRangeList']=context['vlanRangeList_backup']
	MSA_API.task_error('Vlan Pool update cannot be done from this process',context, True)

if not context.get('vlansInUse'):
  context['vlansInUse'] = []

if not context.get('vlanRangeList'):
  context['vlanRangeList'] = []
  
if not context['device_id'] or not context['name']:
	MSA_API.task_error('Mandatory parameters required, please edit the VLAN pool',context, True)
	
if not context.get('searchedVlanId'):
	MSA_API.task_error('Please enter an VLAN Id to search', context, True)
	
searchedVlanId=context['searchedVlanId']

# Check if given VLAN Id is not starting with 0 (eg : 01)
if searchedVlanId.startswith('0'):
	MSA_API.task_error('VLAN Id '+searchedVlanId+" not valid, please retry", context, True)


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


# Check if given Vlan Id is include on the range
if int(context['SelectedVlanRangeStart']) > int(searchedVlanId) or int(searchedVlanId) > int(context['SelectedVlanRangeEnd']):
	MSA_API.task_error('Vlan Id '+searchedVlanId+" not on the available range ("+context['SelectedVlanRangeStart']+" - "+context['SelectedVlanRangeEnd']+")", context, True)
		
#Check if the given Vlan Id is already allocated
freeVlanId=True
for vlanIdInUse in context['vlansInUse']:
	if (searchedVlanId == vlanIdInUse['vlanId']) and (str(vlanIdInUse['assignment_information']) == 'From Vlan Pool '+context['SelectedVlanRangeStart']+' - '+context['SelectedVlanRangeEnd']+''):
		freeVlanId=False
		break
if not freeVlanId:
  MSA_API.task_error('VLAN Id '+searchedVlanId+' is already in use in Pool range '+context['SelectedVlanRangeStart']+' - '+context['SelectedVlanRangeEnd']+'', context, True)

		
ret = MSA_API.process_content('ENDED', 'The ASN Id '+searchedVlanId+' is available in Pool range '+context['SelectedVlanRangeStart']+' - '+context['SelectedVlanRangeEnd']+'', context, True)
print(ret)
