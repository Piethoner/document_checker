from functools import partial

from utils import *


class BaseRule:
    def __init__(self, compare_function, **kwargs):
        self.compare_function = partial(compare_function, **kwargs)
        self.compare_function.__name__ = compare_function.__name__
        self.compare_function = print_function_args(self.compare_function)

    def apply(self, *args, **kwargs):
        raise NotImplementedError


# 文档与report的比对规则
class Rule(BaseRule):
    def __init__(self, field1, compare_function, field2=None, **kwargs):
        super().__init__(compare_function, **kwargs)
        self.field1 = field1
        self.field2 = field2

    def apply(self, doc1, doc2):
        return self.compare_function(doc1.get(self.field1, ''), doc2.get(self.field2, '')) \
                if (doc2 and self.field2) else \
                self.compare_function(doc1.get(self.field1, ''))


# 文档之间的比对规则
class DocCompareRule(BaseRule):
    def __init__(self, doc1, doc2, compare_function, **kwargs):
        super().__init__(compare_function, **kwargs)
        self.doc1 = doc1
        self.doc2 = doc2

    def apply(self, docs, _):
        return self.compare_function(docs.get(self.doc1, []),
                                     docs.get(self.doc2, []))


# 自定义的比对规则
class CustomCompareRule(BaseRule):
    def apply(self, docs, report):
        return self.compare_function(docs, report)
