from msa_sdk.msa_api import MSA_API
from msa_sdk.variables import Variables

context = Variables.task_call()

#check that at least there is one ASN range pool  defined
if not context.get('pool'):
	MSA_API.task_error('You need to enter at least one ASN range pool',context, True)
	
duplicateRangeCheck=[]

#check the range order
for asnRange in context.get('pool'):
	poolStart=int(asnRange['poolStart'])
	poolEnd=int(asnRange['poolEnd'])
	duplicateRangeCheck.append(''+str(poolStart)+'-'+str(poolEnd)+'')
	
	if poolStart > poolEnd:
		MSA_API.task_error('ASN ID start range value cannot be higher than end range value',context, True)
	elif poolStart <= 0 or poolEnd <= 0:
		MSA_API.task_error('ASN ID range cannot have null or negative value',context, True)
	elif poolStart > 64511 or poolEnd > 64511:
		MSA_API.task_error('ASN ID range cannot exceed the value of 64511',context, True)

if len(duplicateRangeCheck) != len(set(duplicateRangeCheck)):
	MSA_API.task_error('Duplicate of ASN range detected, please edit your ASN Pool',context, True)
	
ret=MSA_API.process_content('ENDED','',context, True)
print(ret)