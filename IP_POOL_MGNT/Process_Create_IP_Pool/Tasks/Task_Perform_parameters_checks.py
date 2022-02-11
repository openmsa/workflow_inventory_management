from msa_sdk.msa_api import MSA_API
from msa_sdk.variables import Variables

context = Variables.task_call()

#check that at least there is one cidr/network defined
if not context.get('pool'):
	MSA_API.task_error('You need to enter at least one network',context, True)
	
duplicateCidrCheck=[]	

#check if the prefix is coherent regarding the IP version
for cidr in context.get('pool'):
	duplicateCidrCheck.append(''+cidr['address']+'/'+cidr['prefix']+'')
	if context['version'] == "ipv4" and ((int(cidr['prefix']) > 32) or (int(cidr['prefix']) <= 0)):
		MSA_API.task_error('Invalid prefix for CIDR '+cidr['address']+'/'+cidr['prefix']+'',context, True)
	elif context['version'] == "ipv6" and int(cidr['prefix']) > 128:
		MSA_API.task_error('Prefix for ipv46 network '+cidr['address']+'/'+cidr['prefix']+' should not exceed 128',context, True)

if len(duplicateCidrCheck) != len(set(duplicateCidrCheck)):
	MSA_API.task_error('Duplicate of CIDR detected, please edit your IP Pool',context, True)
	
ret=MSA_API.process_content('ENDED','',context, True)
print(ret)