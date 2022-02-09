from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
context = Variables.task_call(dev_var)

usedList=''

if context.get('vpcsInUse'):
	for vpcId in context['vpcsInUse']:
		usedList=usedList+"\n"+vpcId['vpcId']
context['usedVpcIds']=usedList
ret = MSA_API.process_content('ENDED', 'Used vPC Domain Ids :'+usedList, context, True)
print(ret)