from msa_sdk.msa_api import MSA_API
from msa_sdk.variables import Variables
import pandas as pd

context = Variables.task_call()

#check that at least there is one vlan range pool  defined
if not context.get('pool'):
	context['pool']=context['pool_backup']
	MSA_API.task_error('You need to enter at least one vlan range pool',context, True)

duplicateRangeCheck=[]	

#check the range order
for vlanRange in context.get('pool'):

    if not vlanRange['poolStart'] or not vlanRange['poolEnd']:
        MSA_API.task_error('Invalid input in your pool list, please check',context, True)

	poolStart=int(vlanRange['poolStart'])
	poolEnd=int(vlanRange['poolEnd'])
	duplicateRangeCheck.append(''+str(poolStart)+'-'+str(poolEnd)+'')	
	if poolStart >= poolEnd:
		MSA_API.task_error('VLAN ID start range value cannot be higher or equals to end range value',context, True)
	elif poolStart <= 0 or poolEnd <= 0:
		MSA_API.task_error('Vlan ID range cannot have null or negative value',context, True)
	elif poolStart > 4095 or poolEnd > 4095:
		MSA_API.task_error('Vlan ID range cannot exceed the value of 4095',context, True)

if len(duplicateRangeCheck) != len(set(duplicateRangeCheck)):
	MSA_API.task_error('Duplicate of Vlan range detected, please edit your VLAN Pool',context, True)

for vlanRange in context.get('pool'):
	poolStart=int(vlanRange['poolStart'])
	poolEnd=int(vlanRange['poolEnd'])
	
	for vlanRange2 in context.get('pool'):
		poolStart2=int(vlanRange2['poolStart'])
		poolEnd2=int(vlanRange2['poolEnd'])
		i1 = pd.Interval(poolStart,poolEnd,closed='both')
		i2 = pd.Interval(poolStart2,poolEnd2,closed='both')
		#context['overlaps_check']=i1.overlaps(i2)
		if (i1.overlaps(i2) == True):
			if (poolStart != poolStart2) or (poolEnd != poolEnd2):
				MSA_API.task_error('Overlaps detected between range '+str(poolStart)+'-'+str(poolEnd)+' and range '+str(poolStart2)+'-'+str(poolEnd2)+'',context, True)
				
ret=MSA_API.process_content('ENDED','',context, True)
print(ret)