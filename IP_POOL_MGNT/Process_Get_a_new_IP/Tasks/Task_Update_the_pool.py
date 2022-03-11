import json
import uuid
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.order import Order
from statistics import mean

# List all the parameters required by the task
dev_var = Variables()
context = Variables.task_call(dev_var)

# read the ID of the selected managed entity
device_id = context['device_id']

# extract the database ID
devicelongid = device_id[3:]

cidrList=[]
avgPercentList=[]

for cidr in context['pool']:
	if context['SelectedCidr'] == cidr['address']+'/'+cidr['prefix']:
		ipUsedNb=int(cidr['ipUsedNb'])
		ipUsedNb+=1
		cidr['ipUsedNb']=str(ipUsedNb)
		percent = "{:.10%}".format((int(cidr['totalIps'])-int(cidr['ipUsedNb']))/int(cidr['totalIps']))
		percent=(float(100)-float(percent.strip('%')))
		percent="{:.10f}".format(round(percent, 10))+"%"
		cidr['ipUsage']=str(percent)
	my_dict = dict(cidr=cidr['address']+'/'+cidr['prefix'],totalIps=cidr['totalIps'],ipUsage=cidr['ipUsage'],ipUsedNb=cidr['ipUsedNb'],isSelected='false')
	cidrList.append(my_dict)
	avgPercentList.append(float(cidr['ipUsage'].strip('%')))
	
context['cidrList'] = cidrList
context['totalIpUsage']=str("{:.10f}".format(mean(avgPercentList)))+'%'
context['pool_backup']=context['pool']
context['IPsInUse_backup']=context['IPsInUse']

if not context.get('globaluniq'):
	context['globaluniq']=''

if not context.get('description'):
	context['description']=''
	
if not context.get('totalIpUsage'):
	context['totalIpUsage']="0%"	

if not context.get('object_id'):
	context['object_id']=str(uuid.uuid4())
	
object_id=context['object_id']

# build the Microservice JSON params
#{"Gateway":"0"}
#micro_service_vars_array = {"object_id":object_id}

object_parameters = {}
object_parameters['IP_POOL']={}
object_parameters['IP_POOL'] [object_id]={}
object_parameters['IP_POOL'] [object_id]['object_id']=object_id
object_parameters['IP_POOL'] [object_id]['name']=context['name']
object_parameters['IP_POOL'] [object_id]['globaluniq']=context['globaluniq']
object_parameters['IP_POOL'] [object_id]['version']=context['version']
object_parameters['IP_POOL'] [object_id]['totalIpUsage']=context['totalIpUsage']
object_parameters['IP_POOL'] [object_id]['description']=context['description']
object_parameters['IP_POOL'] [object_id]['pool']=context['pool']
object_parameters['IP_POOL'] [object_id]['IPsInUse']=context['IPsInUse']

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

