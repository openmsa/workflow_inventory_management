from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API


dev_var = Variables()

context = Variables.task_call(dev_var)

ret = MSA_API.process_content('ENDED', ' '+context['newReleasedVpc']+ ' has been released from vPC Pool '+ context['name']+'', context, True)
print(ret)
