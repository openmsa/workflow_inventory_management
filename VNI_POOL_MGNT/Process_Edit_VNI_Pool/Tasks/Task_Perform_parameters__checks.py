from msa_sdk.msa_api import MSA_API
from msa_sdk.variables import Variables
import pandas as pd

context = Variables.task_call()

#check that at least there is one VNI range pool  defined
if not context.get('pool'):
	MSA_API.task_error('You need to enter at least one VNI range pool',context, True)
	
#Get all Pool Ids
extract_vni_pool=[]
for pools in context['import_result_vni_pool']:
	extract_vni_pool.append(pools)	
context['extract_vni_pool']=extract_vni_pool

for index in extract_vni_pool:
	if context['import_result_vni_pool'][index]['name'] == context['name'] and context['import_result_vni_pool'][index]['object_id'] != context['object_id']:
		MSA_API.task_error(''+context['name']+' already exist, please edit your Pool Name',context, True)

duplicateRangeCheck=[]

#check the range order
for vniRange in context.get('pool'):
	if not vniRange['poolStart'] or not vniRange['poolEnd']:
		MSA_API.task_error('Invalid input in your pool list, please check',context, True)
	poolStart=int(vniRange['poolStart'])
	poolEnd=int(vniRange['poolEnd'])
	duplicateRangeCheck.append(''+str(poolStart)+'-'+str(poolEnd)+'')

	if poolStart >= poolEnd:
		context['pool']=context['pool_backup']
		MSA_API.task_error('VNI ID start range value cannot be higher or equals to end range value',context, True)

	elif poolStart < 4096 or poolEnd < 4096:
		context['pool']=context['pool_backup']
		MSA_API.task_error('VNI ID range should have values starting from 4096',context, True)

	elif poolStart > 16777215 or poolEnd > 16777215:
		context['pool']=context['pool_backup']
		MSA_API.task_error('VNI ID range cannot exceed the value of 16777215',context, True)

if len(duplicateRangeCheck) != len(set(duplicateRangeCheck)):
	MSA_API.task_error('Duplicate of VNI range detected, please edit your VNI Pool',context, True)

for vniRange in context.get('pool'):
	poolStart=int(vniRange['poolStart'])
	poolEnd=int(vniRange['poolEnd'])
	
	for vniRange2 in context.get('pool'):
		poolStart2=int(vniRange2['poolStart'])
		poolEnd2=int(vniRange2['poolEnd'])
		i1 = pd.Interval(poolStart,poolEnd,closed='both')
		i2 = pd.Interval(poolStart2,poolEnd2,closed='both')
		#context['overlaps_check']=i1.overlaps(i2)
		if (i1.overlaps(i2) == True):
			if (poolStart != poolStart2) or (poolEnd != poolEnd2):
				context['pool']=context['pool_backup']
				MSA_API.task_error('Overlaps detected between range '+str(poolStart)+'-'+str(poolEnd)+' and range '+str(poolStart2)+'-'+str(poolEnd2)+'',context, True)

## Check Range update and vnisInUse

if context.get('vnisInUse'):
	if len(context['pool_backup']) == len(context['pool']):
		i=0
		for vniPoolUpdate in context['pool']:
			for vnisInUse in context['vnisInUse']:
				if vnisInUse['assignment_information'] == 'From VNI Pool '+context['pool_backup'][i]['poolStart']+' - '+context['pool_backup'][i]['poolEnd']+'':
					if (int(vniPoolUpdate['poolStart']) <= int(vnisInUse['vniId']) ) and (int(vnisInUse['vniId']) <= int(vniPoolUpdate['poolEnd'])):
						vnisInUse['assignment_information']='From VNI Pool '+vniPoolUpdate['poolStart']+' - '+vniPoolUpdate['poolEnd']+''
					else:
						context['pool']=context['pool_backup']
						context['vnisInUse']=context['vnisInUse_backup']
						MSA_API.task_error('VNI Id ' +vnisInUse['vniId']+ ' in use is out of the new range ' +vniPoolUpdate['poolStart']+'-'+ vniPoolUpdate['poolEnd']+'',context, True)
			i+=1
			
ret=MSA_API.process_content('ENDED','',context, True)
print(ret)