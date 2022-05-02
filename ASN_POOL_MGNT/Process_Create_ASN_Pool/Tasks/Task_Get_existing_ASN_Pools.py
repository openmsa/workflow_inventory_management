import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.order import Order

# List all the parameters required by the task
dev_var = Variables()
dev_var.add('device_id', var_type='Device')
dev_var.add('name', var_type='String')
dev_var.add('pool.0.poolStart', var_type='Integer')
dev_var.add('pool.0.poolEnd', var_type='Integer')
dev_var.add('pool.0.poolInUse', var_type='Integer')
dev_var.add('pool.0.description', var_type='String')
dev_var.add('asnsInUse.0.asnId', var_type='String')
dev_var.add('asnsInUse.0.assignment_information', var_type='String')
dev_var.add('description', var_type='String')
context = Variables.task_call(dev_var)

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

import_result_message=json.loads(context['import_result']['message'])
if "ASN_POOL" not in import_result_message:
	context['import_result_asn_pool']=[]
else:
	context['import_result_asn_pool']=import_result_message['ASN_POOL']

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