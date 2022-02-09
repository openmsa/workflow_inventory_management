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

if not context.get('vlansInUse'):
  context['vlansInUse'] = []

if not context.get('vlanRangeList'):
  context['vlanRangeList'] = []
  
assignment_information_Check=[]

for vlanInUse in context['vlansInUse']:
	assignment_information_Check.append(vlanInUse['assignment_information'])

context['assignment_information_Check']=assignment_information_Check

#context['len_pool']=len(context['pool']	)
#context['len_assignmentCheck']=len(set(assignment_information_Check))

#context['str_check']='From VLAN Pool '+context['pool'][0]['poolStart']+' - '+context['pool'][0]['poolEnd']+''

if ( (len(context['pool']) < len(set(assignment_information_Check))) or ( (len(set(assignment_information_Check)) == 1) and ('From VLAN Pool '+context['pool'][0]['poolStart']+' - '+context['pool'][0]['poolEnd']+'' != context['assignment_information_Check'][0])) ):
	context['pool']=context['pool_backup']
	MSA_API.task_error('Range pool cannot be updated or deleted, ressource still in use, please release them',context, True)

context['pool_backup']=	context['pool']

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
object_parameters['VLAN_POOL'] ={}


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