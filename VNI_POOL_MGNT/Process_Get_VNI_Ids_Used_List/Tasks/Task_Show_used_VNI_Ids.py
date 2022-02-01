from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()
context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name'] or not context['poolStart'] or not context['poolEnd']:
	MSA_API.task_error('Mandatory parameters required, please edit the VLAN pool',context, True)

usedList=''

if context.get('vnisInUse'):
	for vlanId in context['vnisInUse']:
		usedList=usedList+"\n"+vlanId['vniId']
context['usedVniIds']=usedList
ret = MSA_API.process_content('ENDED', 'Used VNI Ids :'+usedList, context, True)
print(ret)