from doc_compare.rule import *
from doc_compare.doc_checkpoints import *


pl_checkpoints = [
    {
        'description': '标题是否为 xxx',
        'rule': Rule('标题', lambda x: 'xxx' in x.strip().upper().replace(' ', ''))
    },
]
