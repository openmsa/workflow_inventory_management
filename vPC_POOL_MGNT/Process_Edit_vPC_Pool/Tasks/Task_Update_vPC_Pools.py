import json
import uuid
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.order import Order

# List all the parameters required by the task
dev_var = Variables()
dev_var.add('device_id', var_type='Device')
dev_var.add('object_id', var_type='AutoIncrement')
dev_var.add('name', var_type='String')
dev_var.add('poolStart', var_type='Integer')
dev_var.add('poolEnd', var_type='Integer')
dev_var.add('description', var_type='String')

context = Variables.task_call(dev_var)

# read the ID of the selected managed entity
device_id = context['device_id']

# extract the database ID
devicelongid = device_id[3:]

if not context.get('description'):
	context['description']=''

if not context.get('object_id'):
	context['object_id']=str(uuid.uuid4())

object_id=context['object_id']

# build the Microservice JSON params
#{"Gateway":"0"}
#micro_service_vars_array = {"object_id":object_id}
object_parameters = {}
object_parameters['vPC_POOL']={}
object_parameters['vPC_POOL'] [object_id]={}
object_parameters['vPC_POOL'] [object_id]['object_id']=object_id
object_parameters['vPC_POOL'] [object_id]['name']=context['name']
object_parameters['vPC_POOL'] [object_id]['description']=context['description']
object_parameters['vPC_POOL'] [object_id]['poolStart']=context['poolStart']
object_parameters['vPC_POOL'] [object_id]['poolEnd']=context['poolEnd']
object_parameters['vPC_POOL'] [object_id]['vpcsInUse']=context['vpcsInUse']


# call the CREATE for the specified MS for each device
order = Order(devicelongid)
order.command_execute('CREATE', object_parameters)

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

