from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()
context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name'] or not context['poolStart'] or not context['poolEnd']:
	MSA_API.task_error('Mandatory parameters required, please edit the vPC pool',context, True)

usedList=''

if context.get('vpcsInUse'):
	for vpcId in context['vpcsInUse']:
		usedList=usedList+"\n"+vpcId['vpcDomainId']
context['usedVpcIds']=usedList
ret = MSA_API.process_content('ENDED', 'Used vPC Domain Ids :'+usedList, context, True)
print(ret)