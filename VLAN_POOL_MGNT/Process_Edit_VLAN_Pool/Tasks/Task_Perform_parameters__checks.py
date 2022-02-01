from msa_sdk.msa_api import MSA_API
from msa_sdk.variables import Variables

context = Variables.task_call()

if not context.get('poolStart'):
	context['poolStart']=0
if not context.get('poolEnd'):
	context['poolEnd']=0
	
poolStart=int(context['poolStart'])
poolEnd=int(context['poolEnd'])

#check that at least there is one vlan range defined
if not context['poolStart'] or not context['poolEnd']:
	MSA_API.task_error('You need to enter the vlan range',context, True)

#check the range order
if poolStart > poolEnd:
	MSA_API.task_error('VLAN ID Range start cannot be higher range end',context, True)

elif poolStart <= 0 or poolEnd <= 0:
		MSA_API.task_error('Vlan ID range cannot have null or negative value',context, True)

elif poolStart > 4095 or poolEnd > 4095:
		MSA_API.task_error('Vlan ID range cannot exceed the value of 4095',context, True)

ret=MSA_API.process_content('ENDED','',context, True)
print(ret)