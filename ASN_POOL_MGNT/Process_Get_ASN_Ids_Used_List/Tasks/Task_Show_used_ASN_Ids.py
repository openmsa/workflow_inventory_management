from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()
context = Variables.task_call(dev_var)

usedList=''

if context.get('asnsInUse'):
	for asnId in context['asnsInUse']:
		usedList=usedList+"\n"+asnId['asnId']+' >> '+asnId['assignment_information']+''
context['usedAsnIds']=usedList
MSA_API.task_success('Used ASN Ids :'+usedList, context)
