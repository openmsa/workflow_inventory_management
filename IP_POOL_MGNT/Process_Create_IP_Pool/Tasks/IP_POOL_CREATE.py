import json
import uuid
import ipaddress
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.order import Order
from msa_sdk.util import get_ip_range
from msa_sdk.util import cidr_to_range
# List all the parameters required by the task
dev_var = Variables()
context = Variables.task_call(dev_var)


context['totalIpUsage']="0%"

# read the ID of the selected managed entity
device_id = context['device_id']

# extract the database ID
devicelongid = device_id[3:]

cidrList=[]
for cidr in context['pool']:
	
	try:
		network = ipaddress.IPv4Network(cidr['address']+'/'+cidr['prefix'])
	except ValueError:
		MSA_API.task_error('address/netmask is invalid for IPv4:'+cidr['address']+'/'+cidr['prefix']+'',context, True)
		
	cidr['ipUsedNb']="0"	
	cidr['totalIps']=str(len(cidr_to_range(cidr['address']+'/'+cidr['prefix'])))
	cidr['ipUsage']='0%'
	my_dict = dict(cidr=cidr['address']+'/'+cidr['prefix'],totalIps=cidr['totalIps'],ipUsage=cidr['ipUsage'],ipUsedNb=cidr['ipUsedNb'],isSelected='false')
	cidrList.append(my_dict)

context['cidrList'] = cidrList
context['cidrList_backup']=cidrList
context['pool_backup']=context['pool']

if not context.get('globaluniq'):
	context['globaluniq']=''

if not context.get('description'):
	context['description']=''
	
if not context.get('object_id'):
	context['object_id']=str(uuid.uuid4())

object_id=context['object_id']
context['create']="true"
# build the Microservice JSON params
#{"Gateway":"0"}
#micro_service_vars_array = {"object_id":object_id}
object_parameters = {}
object_parameters['IP_POOL']={}
object_parameters['IP_POOL'] [object_id]={}
object_parameters['IP_POOL'] [object_id]['object_id']=object_id
object_parameters['IP_POOL'] [object_id]['name']=context['name']
object_parameters['IP_POOL'] [object_id]['SERVICEINSTANCEREFERENCE']=context['SERVICEINSTANCEREFERENCE']
object_parameters['IP_POOL'] [object_id]['SERVICEINSTANCEID']=context['SERVICEINSTANCEID']
object_parameters['IP_POOL'] [object_id]['globaluniq']=context['globaluniq']
object_parameters['IP_POOL'] [object_id]['version']=context['version']
object_parameters['IP_POOL'] [object_id]['totalIpUsage']=context['totalIpUsage']
object_parameters['IP_POOL'] [object_id]['description']=context['description']
object_parameters['IP_POOL'] [object_id]['pool']=context['pool']


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
