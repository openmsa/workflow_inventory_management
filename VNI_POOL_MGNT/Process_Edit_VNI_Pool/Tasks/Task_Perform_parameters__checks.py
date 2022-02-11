from msa_sdk.msa_api import MSA_API
from msa_sdk.variables import Variables

context = Variables.task_call()

#check that at least there is one VNI range pool  defined
if not context.get('pool'):
	MSA_API.task_error('You need to enter at least one VNI range pool',context, True)
	
duplicateRangeCheck=[]

#check the range order
for vniRange in context.get('pool'):
	poolStart=int(vniRange['poolStart'])
	poolEnd=int(vniRange['poolEnd'])
	duplicateRangeCheck.append(''+str(poolStart)+'-'+str(poolEnd)+'')

	if poolStart > poolEnd:
		MSA_API.task_error('VNI ID start range value cannot be higher than end range value',context, True)

	elif poolStart < 4096 or poolEnd < 4096:
		MSA_API.task_error('VNI ID range should have values starting from 4096',context, True)

	elif poolStart > 16777215 or poolEnd > 16777215:
		MSA_API.task_error('VNI ID range cannot exceed the value of 16777215',context, True)

if len(duplicateRangeCheck) != len(set(duplicateRangeCheck)):
	MSA_API.task_error('Duplicate of VNI range detected, please edit your VNI Pool',context, True)
	
ret=MSA_API.process_content('ENDED','',context, True)
print(ret)