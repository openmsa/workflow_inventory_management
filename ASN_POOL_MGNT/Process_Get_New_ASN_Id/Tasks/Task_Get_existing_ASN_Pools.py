import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.order import Order

# List all the parameters required by the task
dev_var = Variables()
dev_var.add('object_id', var_type='AutoIncrement')
dev_var.add('newAsnId', var_type='String')
dev_var.add('newAssignmentDescription', var_type='String')
dev_var.add('asnRangeList.0.poolStart', var_type='String')
dev_var.add('asnRangeList.0.poolEnd', var_type='String')
dev_var.add('asnRangeList.0.isSelected',var_type='Boolean')
context = Variables.task_call(dev_var)

if len(context['asnRangeList']) != len(context['asnRangeList_backup']):
	context['asnRangeList']=context['asnRangeList_backup']
	MSA_API.task_error('ASN Pool update cannot be done from this process',context, True)

if not context.get('asnsInUse'):
  context['asnsInUse'] = []

if not context.get('asnRangeList'):
  context['asnRangeList'] = []

if not context['device_id'] or not context['name'] :
	MSA_API.task_error('Mandatory parameters required',context, True)

# read the ID of the selected managed entity
device_id = context['device_id']

# extract the database ID
devicelongid = device_id[3:]

# build the Microservice JSON params
#{"Gateway":"0"}
#micro_service_vars_array = {"object_id":object_id}
object_parameters = {}
object_parameters['ASN_POOL'] ={}


# call the CREATE for the specified MS for each device
order = Order(devicelongid)
order.command_execute('IMPORT', object_parameters)

# convert dict object into json
content = json.loads(order.content)

context['import_result']=content

# check if the response is OK
if order.response.ok:
    ret = MSA_API.process_content('ENDED',
                                  f'STATUS: {content["status"]}, \
                                    MESSAGE: successfull',
                                  context, True)
else:
    ret = MSA_API.process_content('FAILED',
                                  f'Import failed \
                                  - {order.content}',
                                  context, True)
                                  
print(ret)