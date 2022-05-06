import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.order import Order

# List all the parameters required by the task
dev_var = Variables()
dev_var.add('object_id', var_type='AutoIncrement')
dev_var.add('newip', var_type='String')
dev_var.add('totalIpUsage', var_type='String')
dev_var.add('newAssignmentDescription', var_type='String')
dev_var.add('newUsageInformation', var_type='String')
dev_var.add('cidrList.0.cidr')
dev_var.add('cidrList.0.totalIps', var_type='String')
dev_var.add('cidrList.0.ipUsedNb', var_type='String')
dev_var.add('cidrList.0.ipUsage', var_type='String')
dev_var.add('cidrList.0.isSelected')
context = Variables.task_call(dev_var)


if not context.get('IPsInUse'):
  context['IPsInUse'] = []

if not context.get('cidrList'):
  context['cidrList'] = []

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
object_parameters['IP_POOL'] = 0


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

