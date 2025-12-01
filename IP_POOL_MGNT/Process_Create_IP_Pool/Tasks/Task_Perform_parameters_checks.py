from msa_sdk.msa_api import MSA_API
from msa_sdk.variables import Variables
import ipaddress
from msa_sdk.util import address_is_in_network
from msa_sdk.util import get_ip_range
from msa_sdk.util import cidr_to_range
from ipaddress import ip_network
from statistics import mean
import uuid

context = Variables.task_call()

#check that at least there is one cidr/network defined
if not context.get('pool'):
	MSA_API.task_error('You need to enter at least one network', context)

if not context.get('object_id'):
	context['object_id']=str(uuid.uuid4())
	
for ipRange in context['pool']:
	if not ipRange['ipUsage'] or ipRange['ipUsage'] == 'null':
		ipRange['ipUsedNb']="0"
		ipRange['ipUsage']='0%'

duplicateCidrCheck=[]	

#check if the prefix is coherent regarding the IP version
for cidr in context.get('pool'):
	if not cidr['address'] or not cidr['prefix']:
		if context['create'] == "false":
			context['pool']=context['pool_backup']
		MSA_API.task_error('Invalid input in your pool list, please check', context)
	duplicateCidrCheck.append(''+cidr['address']+'/'+cidr['prefix']+'')
	if context['version'] == "ipv4" and ((int(cidr['prefix']) > 32) or (int(cidr['prefix']) <= 0)):
		if context['create'] == "false":
			context['pool']=context['pool_backup']
		MSA_API.task_error('Invalid prefix for CIDR '+cidr['address']+'/'+cidr['prefix']+'', context)
	elif context['version'] == "ipv6" and int(cidr['prefix']) > 128:
		if context['create'] == "false":
			context['pool']=context['pool_backup']
		MSA_API.task_error('Prefix for ipv46 network '+cidr['address']+'/'+cidr['prefix']+' should not exceed 128', context)

if len(duplicateCidrCheck) != len(set(duplicateCidrCheck)):
	MSA_API.task_error('Duplicate of CIDR detected, please edit your IP Pool', context)


for cidr in context.get('pool'):
	try:
		network = ipaddress.IPv4Network(cidr['address']+'/'+cidr['prefix'])
	except ValueError:
		MSA_API.task_error('address/netmask is invalid for IPv4:'+cidr['address']+'/'+cidr['prefix']+'', context)

	for cidr2 in context.get('pool'):
		try:
			network = ipaddress.IPv4Network(cidr2['address']+'/'+cidr2['prefix'])
		except ValueError:
			MSA_API.task_error('address/netmask is invalid for IPv4:'+cidr2['address']+'/'+cidr2['prefix']+'', context)
		
		if (ipaddress.IPv4Network(cidr['address']+'/'+cidr['prefix']).overlaps(ipaddress.IPv4Network(cidr2['address']+'/'+cidr2['prefix'])) == True):
			if (cidr['address']+'/'+cidr['prefix'] != cidr2['address']+'/'+cidr2['prefix'] ):
				if context['create'] == "false":
					context['pool']=context['pool_backup']
				MSA_API.task_error('Overlaps detected between cidr '+cidr['address']+'/'+cidr['prefix']+' and cidr '+cidr2['address']+'/'+cidr2['prefix']+'', context)

### Global Uniqueness check ###
context['all_ip_pools']=[]
context['nbGlobaluniq']=0

# only if globaluniq is checked on this current pool
#if context['globaluniq'] == True :
all_ip_pools=[]
extract_ip_pool=[]
nbGlobaluniq=0
	
#Get all Pool Ids
for pools in context['import_result_ip_pool']:
	extract_ip_pool.append(pools)	
context['extract_ip_pool']=extract_ip_pool


for index in extract_ip_pool:
	if context['create'] == "true":
		if context['import_result_ip_pool'][index]['name'] == context['name']:
			MSA_API.task_error(''+context['name']+' already exist, please edit your Pool Name', context)
	if context['create'] == "false":
		if context['import_result_ip_pool'][index]['name'] == context['name'] and context['import_result_ip_pool'][index]['object_id'] != context['object_id']:
			MSA_API.task_error(''+context['name']+' already exist, please edit your Pool Name', context)
	
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
				if context['create'] == "false":
					context['pool']=context['pool_backup']
				MSA_API.task_error('Overlaps detected from this current Pool Id: '+context['object_id']+' Name: '+context['name']+' and external Pool Id: '+object_id+' Name: '+name+ ', between cidr '+cidr['address']+'/'+cidr['prefix']+' and cidr '+all_ip_pools['pool'][str(i)]['address']+'/'+all_ip_pools['pool'][str(i)]['prefix']+'', context)
			i+=1
			
if context['create'] == "false":
	## Check Range update and IPsInUse
	if context.get('IPsInUse'):
		if len(context['pool_backup']) == len(context['pool']):
			i=0
			cidrList=[]
			avgPercentList=[]
			for ipPoolUpdate in context['pool']:
				for IPsInUse in context['IPsInUse']:
					if IPsInUse['assignment_information'] == 'From IP Pool '+context['pool_backup'][i]['address']+'/'+context['pool_backup'][i]['prefix']+'':
						if address_is_in_network(IPsInUse['address'],ipPoolUpdate['address']+'/'+ipPoolUpdate['prefix']):
							IPsInUse['assignment_information']='From IP Pool '+ipPoolUpdate['address']+'/'+ipPoolUpdate['prefix']+''
							
							ipPoolUpdate['totalIps']=str(len(cidr_to_range(ipPoolUpdate['address']+'/'+ipPoolUpdate['prefix'])))
							ipUsedNb=int(ipPoolUpdate['ipUsedNb'])
							ipPoolUpdate['ipUsedNb']=str(ipUsedNb)
							percent = "{:.10%}".format((int(ipPoolUpdate['totalIps'])-int(ipPoolUpdate['ipUsedNb']))/int(ipPoolUpdate['totalIps']))
							percent=(float(100)-float(percent.strip('%')))
							percent="{:.10f}".format(round(percent, 10))+"%"
							ipPoolUpdate['ipUsage']=str(percent)
						
						else:
							context['pool']=context['pool_backup']
							context['IPsInUse']=context['IPsInUse_backup']
							MSA_API.task_error('IP address ' +IPsInUse['address']+ ' in use is out of the new range of Cidr ' +ipPoolUpdate['address']+'/'+ ipPoolUpdate['prefix']+'', context)
				i+=1	
				
				my_dict = dict(cidr=ipPoolUpdate['address']+'/'+ipPoolUpdate['prefix'],totalIps=ipPoolUpdate['totalIps'],ipUsage=ipPoolUpdate['ipUsage'],ipUsedNb=ipPoolUpdate['ipUsedNb'],isSelected='false')
				cidrList.append(my_dict)
				avgPercentList.append(float(ipPoolUpdate['ipUsage'].strip('%')))
			
			context['cidrList'] = cidrList
			context['totalIpUsage']=str("{:.10f}".format(mean(avgPercentList)))+'%'

MSA_API.task_success('', context)
