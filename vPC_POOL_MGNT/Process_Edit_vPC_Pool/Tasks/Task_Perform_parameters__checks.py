from msa_sdk.msa_api import MSA_API
from msa_sdk.variables import Variables

context = Variables.task_call()

#check that at least there is one vPC range pool  defined
if not context.get('pool'):
	MSA_API.task_error('You need to enter at least one vPC range pool',context, True)

duplicateRangeCheck=[]

#check the range order
for vpcRange in context.get('pool'):
	poolStart=int(vpcRange['poolStart'])
	poolEnd=int(vpcRange['poolEnd'])
	duplicateRangeCheck.append(''+str(poolStart)+'-'+str(poolEnd)+'')

	if poolStart > poolEnd:
		MSA_API.task_error('vPC ID start range value cannot be higher than end range value',context, True)

	elif poolStart <= 0 or poolEnd <= 0:
		MSA_API.task_error('vPC ID range cannot have null or negative value',context, True)

	elif poolStart > 1000 or poolEnd > 1000:
		MSA_API.task_error('vPC ID range cannot exceed the value of 1000',context, True)

if len(duplicateRangeCheck) != len(set(duplicateRangeCheck)):
	MSA_API.task_error('Duplicate of vPC range detected, please edit your vPC Pool',context, True)
	
ret=MSA_API.process_content('ENDED','',context, True)
print(ret)