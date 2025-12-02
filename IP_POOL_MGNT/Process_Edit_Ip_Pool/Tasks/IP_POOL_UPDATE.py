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

# read the ID of the selected managed entity
device_id = context['device_id']

# extract the database ID
devicelongid = device_id[3:]

if not context.get('IPsInUse'):
  context['IPsInUse'] = []

if not context.get('cidrList'):
  context['cidrList'] = []

if not context.get('pool_backup'):
	context['pool_backup']=[]
#if len(context['cidrList']) != len(context['cidrList_backup']):
#	context['cidrList']=context['cidrList_backup']
#	MSA_API.task_error('IP Pool update cannot be done from this process', context)
	
for ipRange in context['pool']:
	if not ipRange['ipUsage'] or ipRange['ipUsage'] == 'null':
		ipRange['ipUsedNb']="0"
		ipRange['ipUsage']='0%'

ipPoolToBeDeleted=[]
context['ipPoolToBeDeleted']=[]
context['ipPoolToBeDeletedSum']=0

for ipPool in context['pool_backup']:
	if (ipPool not in context['pool']) and (len(context['pool_backup'])>len(context['pool'])):
		if "ipUsedNb" not in ipPool:
			ipPool['ipUsedNb']="0"
		ipPoolToBeDeleted.append(int(ipPool['ipUsedNb']))
	else:
		ipPoolToBeDeleted.append(0)

context['ipPoolToBeDeleted']=ipPoolToBeDeleted
context['ipPoolToBeDeletedSum']=sum(context['ipPoolToBeDeleted'])


if context['ipPoolToBeDeletedSum'] != 0:
	context['pool']=context['pool_backup']
	MSA_API.task_error('Some range pool cannot be deleted, ressource still in use, please release them', context)

cidrList=[]

for cidr in context['pool']:
	
	try:
		network = ipaddress.IPv4Network(cidr['address']+'/'+cidr['prefix'])
	except ValueError:
		MSA_API.task_error('address/netmask is invalid for IPv4:'+cidr['address']+'/'+cidr['prefix']+'', context)
	
	cidr['totalIps']=str(len(cidr_to_range(cidr['address']+'/'+cidr['prefix'])))
	my_dict = dict(cidr=cidr['address']+'/'+cidr['prefix'],totalIps=cidr['totalIps'],ipUsage=cidr['ipUsage'],ipUsedNb=cidr['ipUsedNb'],isSelected='false')
	cidrList.append(my_dict)
	
context['cidrList'] = cidrList
context['cidrList_backup'] = cidrList
context['pool_backup']=context['pool']
context['IPsInUse_backup']=context['IPsInUse']

if not context.get('globaluniq'):
	context['globaluniq']=''

if not context.get('description'):
	context['description']=''
	
if not context.get('object_id'):
	context['object_id']=str(uuid.uuid4())

object_id=context['object_id']

if not context.get('IPsInUse'):
	context['IPsInUse']=[]

if not context.get('totalIpUsage'):
	context['totalIpUsage']="0%"
	
	
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
object_parameters['IP_POOL'] [object_id]['IPsInUse']=context['IPsInUse']

# call the CREATE for the specified MS for each device
order = Order(devicelongid)
order.command_execute('UPDATE', object_parameters)

# convert dict object into json
content = json.loads(order.content)

# check if the response is OK
if order.response.ok:
    MSA_API.task_success(f'STATUS: {content["status"]}, MESSAGE: successful', context)
else:
    MSA_API.task_error(f'Import failed - {order.content}', context)
