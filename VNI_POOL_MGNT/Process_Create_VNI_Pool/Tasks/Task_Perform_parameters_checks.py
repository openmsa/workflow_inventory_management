from msa_sdk.msa_api import MSA_API
from msa_sdk.variables import Variables

context = Variables.task_call()

if not context.get('poolStart'):
	context['poolStart']=0
if not context.get('poolEnd'):
	context['poolEnd']=0
	
poolStart=int(context['poolStart'])
poolEnd=int(context['poolEnd'])

#check that at least there is one VNI range defined
if not context['poolStart'] or not context['poolEnd']:
	MSA_API.task_error('You need to enter the VNI range',context, True)

#check the range order
if poolStart > poolEnd:
	MSA_API.task_error('VNI ID Range start cannot be higher range end',context, True)

elif poolStart < 4096 or poolEnd < 4096:
		MSA_API.task_error('VNI ID range should have values starting from 4096',context, True)

elif poolStart > 16777215 or poolEnd > 16777215:
		MSA_API.task_error('VNI ID range cannot exceed the value of 16777215',context, True)

ret=MSA_API.process_content('ENDED','',context, True)
print(ret)