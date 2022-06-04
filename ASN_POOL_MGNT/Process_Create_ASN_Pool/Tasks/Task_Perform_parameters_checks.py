from msa_sdk.msa_api import MSA_API
from msa_sdk.variables import Variables
import pandas as pd

context = Variables.task_call()

#check that at least there is one ASN range pool  defined
if not context.get('pool'):
	MSA_API.task_error('You need to enter at least one ASN range pool',context, True)
	
#Get all Pool Ids
extract_asn_pool=[]
for pools in context['import_result_asn_pool']:
	extract_asn_pool.append(pools)	
context['extract_asn_pool']=extract_asn_pool

for index in extract_asn_pool:
	if context['import_result_asn_pool'][index]['name'] == context['name']:
		MSA_API.task_error(''+context['name']+' already exist, please edit your Pool Name',context, True)
	
duplicateRangeCheck=[]

#check the range order
for asnRange in context.get('pool'):
	if not asnRange['poolStart'] or not asnRange['poolEnd']:
		MSA_API.task_error('Invalid input in your pool list, please check',context, True)
	poolStart=int(asnRange['poolStart'])
	poolEnd=int(asnRange['poolEnd'])
	duplicateRangeCheck.append(''+str(poolStart)+'-'+str(poolEnd)+'')
	
	if poolStart >= poolEnd:
		MSA_API.task_error('ASN ID start range value cannot be higher or equals to end range value',context, True)
	elif poolStart <= 0 or poolEnd <= 0:
		MSA_API.task_error('ASN ID range cannot have null or negative value',context, True)
	elif poolStart > 65535 or poolEnd > 65535:
		MSA_API.task_error('ASN ID range cannot exceed the value of 65535',context, True)

if len(duplicateRangeCheck) != len(set(duplicateRangeCheck)):
	MSA_API.task_error('Duplicate of ASN range detected, please edit your ASN Pool',context, True)

for asnRange in context.get('pool'):
	poolStart=int(asnRange['poolStart'])
	poolEnd=int(asnRange['poolEnd'])
	
	for asnRange2 in context.get('pool'):
		poolStart2=int(asnRange2['poolStart'])
		poolEnd2=int(asnRange2['poolEnd'])
		i1 = pd.Interval(poolStart,poolEnd,closed='both')
		i2 = pd.Interval(poolStart2,poolEnd2,closed='both')
		#context['overlaps_check']=i1.overlaps(i2)
		if (i1.overlaps(i2) == True):
			if (poolStart != poolStart2) or (poolEnd != poolEnd2):
				MSA_API.task_error('Overlaps detected between range '+str(poolStart)+'-'+str(poolEnd)+' and range '+str(poolStart2)+'-'+str(poolEnd2)+'',context, True)
				
ret=MSA_API.process_content('ENDED','',context, True)
print(ret)