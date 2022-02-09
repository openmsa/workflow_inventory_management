from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()
context = Variables.task_call(dev_var)

usedList=''

if context.get('vlansInUse'):
	for vlanId in context['vlansInUse']:
		usedList=usedList+"\n"+vlanId['vlanId']
context['usedVlanIds']=usedList
ret = MSA_API.process_content('ENDED', 'Used Vlan Ids :'+usedList, context, True)
print(ret)