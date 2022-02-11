from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()
context = Variables.task_call(dev_var)

usedList=''

if context.get('vnisInUse'):
	for vniId in context['vnisInUse']:
		usedList=usedList+"\n"+vniId['vniId']+' >> '+vniId['assignment_information']+''
context['usedVniIds']=usedList
ret = MSA_API.process_content('ENDED', 'Used VNI Ids :'+usedList, context, True)
print(ret)