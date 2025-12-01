from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
dev_var.add('vpcIdToRelease', var_type='String')
dev_var.add('vpcRangeList.0.poolStart', var_type='String')
dev_var.add('vpcRangeList.0.poolEnd', var_type='String')
dev_var.add('vpcRangeList.0.isSelected',var_type='Boolean')

context = Variables.task_call(dev_var)

if "vpcRangeList" not in context:
	MSA_API.task_error('No vPC Pool found', context)

#if len(context['vpcRangeList']) != len(context['vpcRangeList_backup']):
#  context['vpcRangeList']=context['vpcRangeList_backup']
#  MSA_API.task_error('vPC Pool update cannot be done from this process', context)

if not context.get('vpcsInUse'):
  context['vpcsInUse'] = []

if not context.get('vpcRangeList'):
  context['vpcRangeList'] = []
  
if not context['device_id'] or not context['name']:
  MSA_API.task_error('Mandatory parameters required, please edit the vPC pool', context)
  
if not context.get('vpcsInUse'):
  context['vpcsInUse'] = []

if not context.get('vpcIdToRelease'):
  MSA_API.task_error('Please enter an vPC Id to be released', context)
  
vpcIdToRelease=context['vpcIdToRelease']

# Check if given vPC Id is not starting with 0 (eg : 01)
if vpcIdToRelease.startswith('0'):
  MSA_API.task_error('vPC Id '+vpcIdToRelease+" not valid, please retry", context)


SelectedVpcRangeStart=""
SelectedVpcRangeEnd=""

nbSelected=0

if context.get('vpcRangeList'):
  for vpcRange in context['vpcRangeList']:
    if vpcRange.get('isSelected'):
      if not vpcRange['isSelected']=='false':
        SelectedVpcRangeStart= vpcRange['poolStart']
        SelectedVpcRangeEnd= vpcRange['poolEnd']
        nbSelected+=1

if nbSelected == 0:
  MSA_API.task_error( 'You need to select one of the avaiable pool range ', context)
if nbSelected > 1:
  MSA_API.task_error( 'You need to select only one pool range ', context)

context['SelectedVpcRangeStart']=SelectedVpcRangeStart
context['SelectedVpcRangeEnd']=SelectedVpcRangeEnd
vpctoRelease=[]

# Check if given vPC Id is include on the range
if int(SelectedVpcRangeStart) > int(vpcIdToRelease) or int(vpcIdToRelease) > int(SelectedVpcRangeEnd):
  MSA_API.task_error('vPC Id '+vpcIdToRelease+" not on the available range ("+SelectedVpcRangeStart+" - "+SelectedVpcRangeEnd+")", context) 
# Check if given vPC Id is not starting with 0 (eg : 01)
if vpcIdToRelease.startswith('0'):
  MSA_API.task_error('vPC Id '+vpcIdToRelease+" not valid, please retry", context)

vpcReleased=False
for vpcIdInUse in context['vpcsInUse']:
  if (vpcIdToRelease == vpcIdInUse['vpcId']) and (str(vpcIdInUse['assignment_information']) == 'From vPC Pool '+context['SelectedVpcRangeStart']+' - '+context['SelectedVpcRangeEnd']+''):
    vpcReleased=True
    vpctoRelease.append(dict(vpcId=vpcIdInUse['vpcId'],assignment_information=vpcIdInUse['assignment_information'],usage_information=vpcIdInUse['usage_information']))
    break
  
context['vpctoRelease']=vpctoRelease

if not vpcReleased:
  MSA_API.task_error('vPC Id '+vpcIdToRelease+' not found as used in Pool '+context['SelectedVpcRangeStart']+' - '+context['SelectedVpcRangeEnd']+'', context)

vpcsInUseTemp=[]
for vpcIdInUse in context['vpcsInUse']:
  if vpcIdInUse not in context['vpctoRelease']:   
    vpcsInUseTemp.append(dict(vpcId=vpcIdInUse['vpcId'],assignment_information=vpcIdInUse['assignment_information'],usage_information=vpcIdInUse['usage_information']))

context['vpcsInUse']=vpcsInUseTemp

for vpcRange in context['pool']:
	if (vpcRange['poolStart'] == SelectedVpcRangeStart) and (vpcRange['poolEnd'] == SelectedVpcRangeEnd):
		vpcRange['poolInUse']-=1
		break

context['pool_backup']=context['pool']
context['newReleasedVpc']=vpcIdToRelease

MSA_API.task_success('The vPC Id '+vpcIdToRelease+' has been released from Pool range '+context['SelectedVpcRangeStart']+' - '+context['SelectedVpcRangeEnd']+'', context)
