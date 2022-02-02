from msa_sdk.msa_api import MSA_API
from msa_sdk.variables import Variables

context = Variables.task_call()

if not context.get('poolStart'):
	context['poolStart']=0
	
if not context.get('poolEnd'):
	context['poolEnd']=0
	
poolStart=int(context['poolStart'])
poolEnd=int(context['poolEnd'])

#check that if there is one ASN Pool range defined
if not context['poolStart'] or not context['poolEnd']:
	MSA_API.task_error('You need to enter the ASN pool range',context, True)

#check the range order
if poolStart > poolEnd:
	MSA_API.task_error('ASN ID start range value cannot be higher than end range value',context, True)

elif poolStart <= 0 or poolEnd <= 0:
		MSA_API.task_error('ASN ID range cannot have null or negative value',context, True)

elif poolStart > 64511 or poolEnd > 64511:
		MSA_API.task_error('ASN ID range cannot exceed the value of 64511',context, True)

ret=MSA_API.process_content('ENDED','',context, True)
print(ret)