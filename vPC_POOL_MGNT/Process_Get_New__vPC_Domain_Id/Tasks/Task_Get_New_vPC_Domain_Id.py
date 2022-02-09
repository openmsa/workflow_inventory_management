from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()
context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name']:
  MSA_API.task_error('Mandatory parameters required, please edit the vPC pool',context, True)

if not context.get('pool'):
  MSA_API.task_error('You need to enter at least one vPC pool range',context, True)
  
if not context.get('vpcsInUse'):
  context['vpcsInUse']=[]
  
if not context.get('newVpcId'):
  context['newVpcId']=''
  
if not context.get('newAssignmentDescription'):
  context['newAssignmentDescription']=''
  
newVpcId=context['newVpcId']
newAssignmentDescription=context['newAssignmentDescription']

SelectedVpcRangeStart=""
SelectedVpcRangeEnd=""

usedList=""
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
        
if not newVpcId:
  #get new vPC Id from the given range
  for i in range(int(SelectedVpcRangeStart),int(SelectedVpcRangeEnd)+1):
    if not context['vpcsInUse']:
      newVpcId=str(i)
      break
    else:
      freevPC=True
      for vpcInUse in context['vpcsInUse']:
        if (str(i) == vpcInUse['vpcId']) and (str(vpcInUse['assignment_information']) == 'From vPC Pool '+context['SelectedVpcRangeStart']+' - '+context['SelectedVpcRangeEnd']+''):
          freevPC=False
          break
      if freevPC:
        newVpcId=str(i)
        break

  if not newVpcId:
    MSA_API.task_error('All vPC Ids from the range '+SelectedVpcRangeStart+' - '+SelectedVpcRangeEnd+' have been allocated', context, True)
else:
  # Check if given vPC Id is include on the range
  if int(SelectedVpcRangeStart) > int(newVpcId) or int(newVpcId) > int(SelectedVpcRangeEnd):
    MSA_API.task_error('vPC Id '+newAsnId+" not on the available range ("+SelectedVpcRangeStart+" - "+SelectedVpcRangeEnd+")", context, True) 
  # Check if given vPC Id is not starting with 0 (eg : 01)
  if newVpcId.startswith('0'):
    MSA_API.task_error('vPC Id '+newVpcId+" not valid, please retry", context, True)
  #Check if the given vPC Id is already allocated
  for usedVpc in context['vpcsInUse']:
    if (newVpcId == usedVpc['vpcId']) and (str(usedVpc['assignment_information']) == 'From vPC Pool '+context['SelectedVpcRangeStart']+' - '+context['SelectedVpcRangeEnd']+''):
      MSA_API.task_error('vPC Id '+newVpcId+" is already in use", context, True)

newAssignmentDescription='From vPC Pool '+SelectedVpcRangeStart+' - '+SelectedVpcRangeEnd+''
context['vpcsInUse'].append(dict(vpcId=newVpcId,assignment_information=newAssignmentDescription))

if context.get('usedVpcIds'):
  usedList=context['usedVpcIds']
usedList=usedList+"\n"+newVpcId
context['usedVpcIds']=usedList

for vpcRange in context['pool']:
	if (vpcRange['poolStart'] == SelectedVpcRangeStart) and (vpcRange['poolEnd'] == SelectedVpcRangeEnd):
		vpcRange['poolInUse']+=1
		break

ret = MSA_API.process_content('ENDED', 'New vPC Id '+newVpcId+" has been allocated", context, True)
print(ret)
