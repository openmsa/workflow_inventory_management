import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.order import Order

# List all the parameters required by the task
dev_var = Variables()
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


vlanRangeList=[]

for vlanRange in context['pool']:
	my_dict = dict(poolStart=vlanRange['poolStart'],poolEnd=vlanRange['poolEnd'],isSelected='false')
	vlanRangeList.append(my_dict)
	
context['vlanRangeList'] = vlanRangeList


# build the Microservice JSON params
#{"Gateway":"0"}
#micro_service_vars_array = {"object_id":object_id}

object_parameters = {}
object_parameters['VLAN_POOL']={}
object_parameters['VLAN_POOL'] [object_id]={}
object_parameters['VLAN_POOL'] [object_id]['object_id']=object_id
object_parameters['VLAN_POOL'] [object_id]['name']=context['name']
object_parameters['VLAN_POOL'] [object_id]['description']=context['description']
object_parameters['VLAN_POOL'] [object_id]['pool']=context['pool']
object_parameters['VLAN_POOL'] [object_id]['vlansInUse']=context['vlansInUse']

# call the CREATE for the specified MS for each device
order = Order(devicelongid)
order.command_execute('UPDATE', object_parameters)

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