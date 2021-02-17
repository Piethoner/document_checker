from .common import *
from .ci_checkpoints import ci_checkpoints
from .co_checkpoints import co_checkpoints
from .cm_checkpoints import cm_checkpoints
from .pl_checkpoints import pl_checkpoints
from .fcr_checkpoints import fcr_checkpoints
from .global_checkpoints import global_checkpoints, doc_compare_checkpoints


CHECKPOINTS_MAP = {
    'GLOBAL': global_checkpoints,
    'DOC_COMPARE': doc_compare_checkpoints,
    'CI': ci_checkpoints,
    'CO': co_checkpoints,
    'CM': cm_checkpoints,
    'PL': pl_checkpoints,
    'FCR': fcr_checkpoints
}
