
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()
context = Variables.task_call(dev_var)

if not context['device_id'] or not context['name'] :
	MSA_API.task_error('Mandatory parameters required', context)

usedList=''

if context.get('IPsInUse'):
	for ip in context['IPsInUse']:
		usedList=usedList+"\n"+ip['address']+' >> '+ip['assignment_information']+''
context['usedIPs']=usedList
MSA_API.task_success('Used IP addresses:'+usedList, context)
