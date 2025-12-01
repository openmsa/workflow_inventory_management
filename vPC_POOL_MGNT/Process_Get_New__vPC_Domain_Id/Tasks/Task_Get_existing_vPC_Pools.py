import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.order import Order

# List all the parameters required by the task
dev_var = Variables()
dev_var.add('object_id', var_type='AutoIncrement')
dev_var.add('newVpcId', var_type='String')
dev_var.add('newAssignmentDescription', var_type='String')
dev_var.add('newUsageInformation', var_type='String')
dev_var.add('vpcRangeList.0.poolStart', var_type='String')
dev_var.add('vpcRangeList.0.poolEnd', var_type='String')
dev_var.add('vpcRangeList.0.isSelected',var_type='Boolean')
context = Variables.task_call(dev_var)

#check that at least there is one vPC range pool  defined
if not context.get('pool'):
	MSA_API.task_error('You need to enter at least one vPC range pool', context)

#if len(context['vpcRangeList']) != len(context['vpcRangeList_backup']):
#  context['vpcRangeList']=context['vpcRangeList_backup']
#  MSA_API.task_error('vPC Pool update cannot be done from this process', context)

if not context.get('vpcsInUse'):
  context['vpcsInUse'] = []

if not context.get('vpcRangeList'):
  context['vpcRangeList'] = []

if not context['device_id'] or not context['name'] :
  MSA_API.task_error('Mandatory parameters required', context)

# read the ID of the selected managed entity
device_id = context['device_id']

# extract the database ID
devicelongid = device_id[3:]

# build the Microservice JSON params
#{"Gateway":"0"}
#micro_service_vars_array = {"object_id":object_id}
object_parameters = {}
object_parameters['vPC_POOL'] = 0


# call the CREATE for the specified MS for each device
order = Order(devicelongid)
order.command_execute('IMPORT', object_parameters)

# convert dict object into json
content = json.loads(order.content)

context['import_result']=content

# check if the response is OK
if order.response.ok:
    MSA_API.task_success(f'STATUS: {content["status"]}, MESSAGE: successful', context)
else:
    MSA_API.task_error(f'Import failed - {order.content}', context)
