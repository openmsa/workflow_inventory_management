from msa_sdk.msa_api import MSA_API
from msa_sdk.variables import Variables
import pandas as pd

context = Variables.task_call()

#check that at least there is one vPC range pool  defined
if not context.get('pool'):
	MSA_API.task_error('You need to enter at least one vPC range pool',context, True)

duplicateRangeCheck=[]

#check the range order
for vpcRange in context.get('pool'):
	if not vpcRange['poolStart'] or not vpcRange['poolEnd']:
		MSA_API.task_error('Invalid input in your pool list, please check',context, True)
	poolStart=int(vpcRange['poolStart'])
	poolEnd=int(vpcRange['poolEnd'])
	duplicateRangeCheck.append(''+str(poolStart)+'-'+str(poolEnd)+'')
	
	if poolStart >= poolEnd:
		context['pool']=context['pool_backup']
		MSA_API.task_error('vPC ID start range value cannot be higher or equals to end range value',context, True)

	elif poolStart <= 0 or poolEnd <= 0:
		context['pool']=context['pool_backup']
		MSA_API.task_error('vPC ID range cannot have null or negative value',context, True)

	elif poolStart > 1000 or poolEnd > 1000:
		context['pool']=context['pool_backup']
		MSA_API.task_error('vPC ID range cannot exceed the value of 1000',context, True)

if len(duplicateRangeCheck) != len(set(duplicateRangeCheck)):
	MSA_API.task_error('Duplicate of vPC range detected, please edit your vPC Pool',context, True)

for vpcRange in context.get('pool'):
	poolStart=int(vpcRange['poolStart'])
	poolEnd=int(vpcRange['poolEnd'])
	
	for vpcRange2 in context.get('pool'):
		poolStart2=int(vpcRange2['poolStart'])
		poolEnd2=int(vpcRange2['poolEnd'])
		i1 = pd.Interval(poolStart,poolEnd,closed='both')
		i2 = pd.Interval(poolStart2,poolEnd2,closed='both')
		context['overlaps_check']=i1.overlaps(i2)
		#if (poolStart != poolStart2) and (poolEnd != poolEnd2):
		if (i1.overlaps(i2) == True):
			if (poolStart != poolStart2) or (poolEnd != poolEnd2):
				context['pool']=context['pool_backup']
				MSA_API.task_error('Overlaps detected between range '+str(poolStart)+'-'+str(poolEnd)+' and range '+str(poolStart2)+'-'+str(poolEnd2)+'',context, True)

## Check Range update and vpcsInUse

if context.get('vpcsInUse'):
	if len(context['pool_backup']) == len(context['pool']):
		i=0
		for vpcPoolUpdate in context['pool']:
			for vpcsInUse in context['vpcsInUse']:
				if vpcsInUse['assignment_information'] == 'From vPC Pool '+context['pool_backup'][i]['poolStart']+' - '+context['pool_backup'][i]['poolEnd']+'':
					if (int(vpcPoolUpdate['poolStart']) <= int(vpcsInUse['vpcId']) ) and (int(vpcsInUse['vpcId']) <= int(vpcPoolUpdate['poolEnd'])):
						vpcsInUse['assignment_information']='From vPC Pool '+vpcPoolUpdate['poolStart']+' - '+vpcPoolUpdate['poolEnd']+''
					else:
						context['pool']=context['pool_backup']
						context['vpcsInUse']=context['vpcsInUse_backup']
						MSA_API.task_error('vPC Id ' +vpcsInUse['vpcId']+ ' in use is out of the new range ' +vpcPoolUpdate['poolStart']+'-'+ vpcPoolUpdate['poolEnd']+'',context, True)
			i+=1			
	
ret=MSA_API.process_content('ENDED','',context, True)
print(ret)