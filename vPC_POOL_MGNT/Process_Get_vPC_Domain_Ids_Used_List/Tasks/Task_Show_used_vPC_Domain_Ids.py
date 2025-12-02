from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
context = Variables.task_call(dev_var)

usedList=''

if context.get('vpcsInUse'):
	for vpcId in context['vpcsInUse']:
		usedList=usedList+"\n"+vpcId['vpcId']+' >> '+vpcId['assignment_information']+''
context['usedVpcIds']=usedList
MSA_API.task_success('Used vPC Ids :'+usedList, context)
