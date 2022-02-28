from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
dev_var.add('searchedVpcId', var_type='String')
dev_var.add('vpcRangeList.0.poolStart', var_type='String')
dev_var.add('vpcRangeList.0.poolEnd', var_type='String')
dev_var.add('vpcRangeList.0.isSelected',var_type='Boolean')

context = Variables.task_call(dev_var)

if "vpcRangeList" not in context:
	MSA_API.task_error('No vPC Pool found',context, True)

if len(context['vpcRangeList']) != len(context['vpcRangeList_backup']):
  context['vpcRangeList']=context['vpcRangeList_backup']
  MSA_API.task_error('vPC Pool update cannot be done from this process',context, True)
  
if not context['device_id'] or not context['name']:
  MSA_API.task_error('Mandatory parameters required, please edit the vPC pool',context, True)

if not context.get('vpcRangeList'):
  context['vpcRangeList'] = []
  
if not context.get('vpcsInUse'):
  context['vpcsInUse'] = []

if not context.get('searchedVpcId'):
  MSA_API.task_error('Please enter an vPC Id to search', context, True)
  
searchedVpcId=context['searchedVpcId']

# Check if given vPC Id is not starting with 0 (eg : 01)
if searchedVpcId.startswith('0'):
  MSA_API.task_error('vPC Id '+searchedVpcId+" not valid, please retry", context, True)

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
  MSA_API.task_error( 'You need to select one of the avaiable pool range ', context, True)
if nbSelected > 1:
  MSA_API.task_error( 'You need to select only one pool range ', context, True)

context['SelectedVpcRangeStart']=SelectedVpcRangeStart
context['SelectedVpcRangeEnd']=SelectedVpcRangeEnd

# Check if given vPC Id is include on the range
if int(context['SelectedVpcRangeStart']) > int(searchedVpcId) or int(searchedVpcId) > int(context['SelectedVpcRangeEnd']):
  MSA_API.task_error('vPC Id '+searchedVpcId+" not on the available range ("+context['SelectedVpcRangeStart']+" - "+context['SelectedVpcRangeEnd']+")", context, True)
    
#Check if the given vPC Id is already allocated
freeVpcId=True
for vpcIdInUse in context['vpcsInUse']:
  if (searchedVpcId == vpcIdInUse['vpcId']) and (str(vpcIdInUse['assignment_information']) == 'From vPC Pool '+context['SelectedVpcRangeStart']+' - '+context['SelectedVpcRangeEnd']+''):
    freeVpcId=False
    break
if not freeVpcId:
  MSA_API.task_error('vPC Id '+searchedVpcId+' is already in use in Pool range '+context['SelectedVpcRangeStart']+' - '+context['SelectedVpcRangeEnd']+'', context, True)

    
ret = MSA_API.process_content('ENDED', 'The vPC Id '+searchedVpcId+' is available in Pool range '+context['SelectedVpcRangeStart']+' - '+context['SelectedVpcRangeEnd']+'', context, True)
print(ret)


