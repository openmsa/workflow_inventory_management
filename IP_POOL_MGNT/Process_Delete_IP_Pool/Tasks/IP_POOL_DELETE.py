import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.order import Order

# List all the parameters required by the task
dev_var = Variables()
dev_var.add('Confirmation', var_type='String')
context = Variables.task_call(dev_var)

if not context['Confirmation'] == "Delete me":
	ret=MSA_API.process_content('ERROR','You need to enter "Delete me" as a confirmation keyword',context, True)
	print(ret)




# read the ID of the selected managed entity
device_id = context['device_id']

# extract the database ID
devicelongid = device_id[3:]

# build the Microservice JSON params
#{"Gateway":"0"}
#micro_service_vars_array = {"object_id":object_id}
object_id=context['object_id']

object_parameters = {}
object_parameters['IP_POOL'] = {}
object_parameters['IP_POOL'] [object_id]={}
object_parameters['IP_POOL'] [object_id]['object_id']= object_id


# call the CREATE for the specified MS for each device
order = Order(devicelongid)
order.command_execute('DELETE', object_parameters)

# convert dict object into json
content = json.loads(order.content)

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

