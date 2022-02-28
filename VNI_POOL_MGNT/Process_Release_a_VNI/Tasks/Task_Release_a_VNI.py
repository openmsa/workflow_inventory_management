from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
dev_var.add('vniIdToRelease', var_type='String')
dev_var.add('vniRangeList.0.poolStart', var_type='String')
dev_var.add('vniRangeList.0.poolEnd', var_type='String')
dev_var.add('vniRangeList.0.isSelected',var_type='Boolean')

context = Variables.task_call(dev_var)

if "vniRangeList" not in context:
	MSA_API.task_error('No VNI Pool found',context, True)

if len(context['vniRangeList']) != len(context['vniRangeList_backup']):
  context['vniRangeList']=context['vniRangeList_backup']
  MSA_API.task_error('VNI Pool update cannot be done from this process',context, True)

if not context.get('vnisInUse'):
  context['vnisInUse'] = []

if not context.get('vniRangeList'):
  context['vniRangeList'] = []
  
if not context['device_id'] or not context['name']:
  MSA_API.task_error('Mandatory parameters required, please edit the VNI pool',context, True)
  
if not context.get('vnisInUse'):
  context['vnisInUse'] = []

if not context.get('vniIdToRelease'):
  MSA_API.task_error('Please enter an VNI Id to be released', context, True)
  
vniIdToRelease=context['vniIdToRelease']

# Check if given VNI Id is not starting with 0 (eg : 01)
if vniIdToRelease.startswith('0'):
  MSA_API.task_error('VNI Id '+vniIdToRelease+" not valid, please retry", context, True)


SelectedVniRangeStart=""
SelectedVniRangeEnd=""

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
vnitoRelease=[]

# Check if given VNI Id is include on the range
if int(SelectedVniRangeStart) > int(vniIdToRelease) or int(vniIdToRelease) > int(SelectedVniRangeEnd):
  MSA_API.task_error('VNI Id '+vniIdToRelease+" not on the available range ("+SelectedVniRangeStart+" - "+SelectedVniRangeEnd+")", context, True) 
# Check if given VNI Id is not starting with 0 (eg : 01)
if vniIdToRelease.startswith('0'):
  MSA_API.task_error('VNI Id '+vniIdToRelease+" not valid, please retry", context, True)

vniReleased=False
for vniIdInUse in context['vnisInUse']:
  if (vniIdToRelease == vniIdInUse['vniId']) and (str(vniIdInUse['assignment_information']) == 'From VNI Pool '+context['SelectedVniRangeStart']+' - '+context['SelectedVniRangeEnd']+''):
    vniReleased=True
    vnitoRelease.append(dict(vniId=vniIdInUse['vniId'],assignment_information=vniIdInUse['assignment_information'],usage_information=vniIdInUse['usage_information']))
    break
  
context['vnitoRelease']=vnitoRelease

if not vniReleased:
  MSA_API.task_error('VNI Id '+vniIdToRelease+' not found as used in Pool '+context['SelectedVniRangeStart']+' - '+context['SelectedVniRangeEnd']+'', context, True)

vnisInUseTemp=[]
for vniIdInUse in context['vnisInUse']:
  if vniIdInUse not in context['vnitoRelease']:   
    vnisInUseTemp.append(dict(vniId=vniIdInUse['vniId'],assignment_information=vniIdInUse['assignment_information'],usage_information=vniIdInUse['usage_information']))

context['vnisInUse']=vnisInUseTemp

for vniRange in context['pool']:
	if (vniRange['poolStart'] == SelectedVniRangeStart) and (vniRange['poolEnd'] == SelectedVniRangeEnd):
		vniRange['poolInUse']-=1
		break
	
context['pool_backup']=context['pool']

ret = MSA_API.process_content('ENDED', 'The VNI Id '+vniIdToRelease+' has been released from Pool range '+context['SelectedVniRangeStart']+' - '+context['SelectedVniRangeEnd']+'', context, True)
print(ret)
