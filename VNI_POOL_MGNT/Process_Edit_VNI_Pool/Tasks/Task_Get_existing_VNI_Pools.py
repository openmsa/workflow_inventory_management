import json
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.order import Order

# List all the parameters required by the task
dev_var = Variables()
dev_var.add('device_id', var_type='Device')
dev_var.add('object_id', var_type='AutoIncrement')
dev_var.add('name', var_type='String')
dev_var.add('pool.0.poolStart', var_type='Integer')
dev_var.add('pool.0.poolEnd', var_type='Integer')
dev_var.add('description', var_type='String')
context = Variables.task_call(dev_var)

#check that at least there is one VNI range pool  defined
if not context.get('pool'):
	MSA_API.task_error('You need to enter at least one VNI range pool',context, True)
	
if not context.get('vnisInUse'):
  context['vnisInUse'] = []

if not context.get('vniRangeList'):
  context['vniRangeList'] = []

if not context.get('pool'):
  context['pool'] = []

if not context.get('pool_backup'):
  context['pool_backup'] = []
  
vniPoolToBeDeleted=[]
context['vniPoolToBeDeleted']=[]
context['vniPoolToBeDeletedSum']=0

for vniPool in context['pool_backup']:
	if (vniPool not in context['pool']) and ( (len(context['pool_backup'])>len(context['pool'])) or (len(context['pool_backup']) == len(context['pool'])) ):
		if "poolInUse" not in vniPool:
			vniPool['poolInUse']=0
		vniPoolToBeDeleted.append(vniPool['poolInUse'])
	else:
		vniPoolToBeDeleted.append(0)

context['vniPoolToBeDeleted']=vniPoolToBeDeleted
context['vniPoolToBeDeletedSum']=sum(context['vniPoolToBeDeleted'])


if context['vniPoolToBeDeletedSum'] == 0:
	context['pool_backup']=context['pool']
else:
	context['pool']=context['pool_backup']
	MSA_API.task_error('Some range pool cannot be updated or deleted, ressource still in use, please release them',context, True)


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
object_parameters['VNI_POOL'] ={}


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