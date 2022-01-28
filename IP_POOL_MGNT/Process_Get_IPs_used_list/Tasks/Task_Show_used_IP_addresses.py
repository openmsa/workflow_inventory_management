
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()
context = Variables.task_call(dev_var)

usedList=''

if context.get('IPsInUse'):
	for ip in context['IPsInUse']:
		usedList=usedList+"\n"+ip['address']
context['usedIPs']=usedList
ret = MSA_API.process_content('ENDED', 'Used IP addresses:'+usedList, context, True)
print(ret)

