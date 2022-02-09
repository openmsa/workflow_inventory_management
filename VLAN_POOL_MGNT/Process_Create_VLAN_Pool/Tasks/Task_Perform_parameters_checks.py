from msa_sdk.msa_api import MSA_API
from msa_sdk.variables import Variables

context = Variables.task_call()

#check that at least there is one VLAN range pool  defined
if not context.get('pool'):
	MSA_API.task_error('You need to enter at least one VLAN range pool',context, True)

duplicateRangeCheck=[]	

#check the range order
for vlanRange in context.get('pool'):
	poolStart=int(vlanRange['poolStart'])
	poolEnd=int(vlanRange['poolEnd'])
	duplicateRangeCheck.append(''+str(poolStart)+'-'+str(poolEnd)+'')	
	if poolStart > poolEnd:
		MSA_API.task_error('VLAN ID start range value cannot be higher than end range value',context, True)
	elif poolStart <= 0 or poolEnd <= 0:
		MSA_API.task_error('Vlan ID range cannot have null or negative value',context, True)
	elif poolStart > 4095 or poolEnd > 4095:
		MSA_API.task_error('Vlan ID range cannot exceed the value of 4095',context, True)

if len(duplicateRangeCheck) != len(set(duplicateRangeCheck)):
	MSA_API.task_error('Duplicate of VLAN range detected, please edit your VLAN Pool',context, True)
	
ret=MSA_API.process_content('ENDED','',context, True)
print(ret)