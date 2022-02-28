from msa_sdk.msa_api import MSA_API
from msa_sdk.variables import Variables
import ipaddress

context = Variables.task_call()

#check that at least there is one cidr/network defined
if not context.get('pool'):
	MSA_API.task_error('You need to enter at least one network',context, True)

for ipRange in context['pool']:
	if not ipRange['ipUsage'] or ipRange['ipUsage'] == 'null':
		ipRange['ipUsedNb']="0"
		ipRange['ipUsage']='0%'

duplicateCidrCheck=[]	

#check if the prefix is coherent regarding the IP version
for cidr in context.get('pool'):

    if not cidr['address'] or not cidr['prefix']:
        MSA_API.task_error('Invalid input in your pool list, please check',context, True)

	duplicateCidrCheck.append(''+cidr['address']+'/'+cidr['prefix']+'')
	if context['version'] == "ipv4" and ((int(cidr['prefix']) > 32) or (int(cidr['prefix']) <= 0)):
		MSA_API.task_error('Invalid prefix for CIDR '+cidr['address']+'/'+cidr['prefix']+'',context, True)
	elif context['version'] == "ipv6" and int(cidr['prefix']) > 128:
		MSA_API.task_error('Prefix for ipv46 network '+cidr['address']+'/'+cidr['prefix']+' should not exceed 128',context, True)

if len(duplicateCidrCheck) != len(set(duplicateCidrCheck)):
	MSA_API.task_error('Duplicate of CIDR detected, please edit your IP Pool',context, True)


for cidr in context.get('pool'):
	try:
		network = ipaddress.IPv4Network(cidr['address']+'/'+cidr['prefix'])
	except ValueError:
		MSA_API.task_error('address/netmask is invalid for IPv4:'+cidr['address']+'/'+cidr['prefix']+'',context, True)

	for cidr2 in context.get('pool'):
		try:
			network = ipaddress.IPv4Network(cidr2['address']+'/'+cidr2['prefix'])
		except ValueError:
			MSA_API.task_error('address/netmask is invalid for IPv4:'+cidr2['address']+'/'+cidr2['prefix']+'',context, True)
		
		if (ipaddress.IPv4Network(cidr['address']+'/'+cidr['prefix']).overlaps(ipaddress.IPv4Network(cidr2['address']+'/'+cidr2['prefix'])) == True):
			if (cidr['address']+'/'+cidr['prefix'] != cidr2['address']+'/'+cidr2['prefix'] ):
				MSA_API.task_error('Overlaps detected between cidr '+cidr['address']+'/'+cidr['prefix']+' and cidr '+cidr2['address']+'/'+cidr2['prefix']+'',context, True)

### Global Uniqueness check ###
context['all_ip_pools']=[]
context['nbGlobaluniq']=0

# only if globaluniq is checked on this current pool
if context['globaluniq'] == True :
	all_ip_pools=[]
	extract_ip_pool=[]
	nbGlobaluniq=0
	
	#Get all Pool Ids
	for pools in context['import_result_ip_pool']:
		extract_ip_pool.append(pools)	
	context['extract_ip_pool']=extract_ip_pool
	
	#Go on each external pool and add into table only if globaluniq is checked  
	for index in extract_ip_pool:
		if (context['import_result_ip_pool'][index]['globaluniq'] == '1') and (context['import_result_ip_pool'][index]['object_id'] != context['object_id']):
			nbGlobaluniq+=1
			all_ip_pools.append(dict(name=context['import_result_ip_pool'][index]['name'],object_id=context['import_result_ip_pool'][index]['object_id'],pool=context['import_result_ip_pool'][index]['pool']))
	context['all_ip_pools']=all_ip_pools
	context['nbGlobaluniq']=nbGlobaluniq

# Loop to check the current pools against external pools
for cidr in context.get('pool'):
	for all_ip_pools in context['all_ip_pools']:
		object_id=all_ip_pools['object_id']
		name=all_ip_pools['name']
		i=0
		for pool in all_ip_pools['pool']:
			if (ipaddress.IPv4Network(cidr['address']+'/'+cidr['prefix']).overlaps(ipaddress.IPv4Network(all_ip_pools['pool'][str(i)]['address']+'/'+all_ip_pools['pool'][str(i)]['prefix'])) == True):
				MSA_API.task_error('Overlaps detected from this current Pool Id: '+context['object_id']+' Name: '+context['name']+' and external Pool Id: '+object_id+' Name: '+name+ ', between cidr '+cidr['address']+'/'+cidr['prefix']+' and cidr '+all_ip_pools['pool'][str(i)]['address']+'/'+all_ip_pools['pool'][str(i)]['prefix']+'',context, True)
			i+=1
	
ret=MSA_API.process_content('ENDED','',context, True)
print(ret)