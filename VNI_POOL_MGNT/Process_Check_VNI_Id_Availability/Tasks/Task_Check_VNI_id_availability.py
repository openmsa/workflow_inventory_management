from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
dev_var.add('searchedVniId', var_type='String')
dev_var.add('vniRangeList.0.poolStart', var_type='String')
dev_var.add('vniRangeList.0.poolEnd', var_type='String')
dev_var.add('vniRangeList.0.isSelected',var_type='Boolean')

context = Variables.task_call(dev_var)

if "vniRangeList" not in context:
	MSA_API.task_error('No VNI Pool found', context)

if len(context['vniRangeList']) != len(context['vniRangeList_backup']):
	context['vniRangeList']=context['vniRangeList_backup']
	MSA_API.task_error('VNI Pool update cannot be done from this process', context)
	
if not context['device_id'] or not context['name']:
	MSA_API.task_error('Mandatory parameters required, please edit the VNI pool', context)

if not context.get('vniRangeList'):
  context['vniRangeList'] = []
  
if not context.get('vnisInUse'):
  context['vnisInUse'] = []

if not context.get('searchedVniId'):
	MSA_API.task_error('Please enter an VNI Id to search', context)
	
searchedVniId=context['searchedVniId']

# Check if given VNI Id is not starting with 0 (eg : 01)
if searchedVniId.startswith('0'):
	MSA_API.task_error('VNI Id '+searchedVniId+" not valid, please retry", context)

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
	MSA_API.task_error( 'You need to select one of the avaiable pool range ', context)
if nbSelected > 1:
	MSA_API.task_error( 'You need to select only one pool range ', context)

context['SelectedVniRangeStart']=SelectedVniRangeStart
context['SelectedVniRangeEnd']=SelectedVniRangeEnd

# Check if given VNI Id is include on the range
if int(context['SelectedVniRangeStart']) > int(searchedVniId) or int(searchedVniId) > int(context['SelectedVniRangeEnd']):
	MSA_API.task_error('VNI Id '+searchedVniId+" not on the available range ("+context['SelectedVniRangeStart']+" - "+context['SelectedVniRangeEnd']+")", context)
		
#Check if the given VNI Id is already allocated
freeVniId=True
for vniIdInUse in context['vnisInUse']:
	if (searchedVniId == vniIdInUse['vniId']) and (str(vniIdInUse['assignment_information']) == 'From VNI Pool '+context['SelectedVniRangeStart']+' - '+context['SelectedVniRangeEnd']+''):
		freeVniId=False
		break
if not freeVniId:
	MSA_API.task_error('VNI Id '+searchedVniId+' is already in use in Pool range '+context['SelectedVniRangeStart']+' - '+context['SelectedVniRangeEnd']+'', context)

		
MSA_API.task_success('The VNI Id '+searchedVniId+' is available in Pool range '+context['SelectedVniRangeStart']+' - '+context['SelectedVniRangeEnd']+'', context)
