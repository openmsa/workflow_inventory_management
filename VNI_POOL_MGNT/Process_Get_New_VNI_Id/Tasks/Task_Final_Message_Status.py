from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()

context = Variables.task_call(dev_var)

MSA_API.task_success('New VNI '+context['newAssignedVni']+ ' has been allocated from VNI Pool '+ context['name']+'', context)
