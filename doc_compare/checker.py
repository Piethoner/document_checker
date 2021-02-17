import traceback

from utils import *
from doc_compare.doc_checkpoints.common import *
from doc_compare.doc_checkpoints import CHECKPOINTS_MAP

CONCLUSION_DIFFERENCE = 2001  # 有差异
CONCLUSION_CORRECT = 2002  # 核对无误
CONCLUSION_GLOBAL_ERROR = 2003  # 全局检查未通过
CONCLUSION_ERROR = 2004  # 检查过程报错

CONCLUSION_MAP = {
    CONCLUSION_DIFFERENCE: '有差异',
    CONCLUSION_CORRECT: '核对无误',
    CONCLUSION_GLOBAL_ERROR: '全局检查未通过',
    CONCLUSION_ERROR: '检查过程报错'
}


# 每个PO号对应一个Checker
class Checker:

    GLOBAL_CHECKPOINTS = []
    DOC_COMPARE_CHECKPOINTS = []

    def __init__(self, po_num=None, report=None):
        self.po_num: str = po_num
        self.report = report
        self.docs = {}
        self.result = {}
        self.__class__.GLOBAL_CHECKPOINTS = \
            [CheckPoint(**kwargs) for kwargs in CHECKPOINTS_MAP.get('GLOBAL', [])]
        self.__class__.DOC_COMPARE_CHECKPOINTS = \
            [CheckPoint(**kwargs) for kwargs in CHECKPOINTS_MAP.get('DOC_COMPARE', [])]
        self._conclusion = CONCLUSION_CORRECT
        self.update_result = None
        self.error = None

    def check(self):
        # 全局检查
        rpa_logger.info('####### 开始进行全局 checkpoint 检查 ########')
        for checkpoint in self.__class__.GLOBAL_CHECKPOINTS:
            _result = checkpoint.check(self.docs, self.report)
            if _result:
                self.result.setdefault('GLOBAL', set()).update(_result)
                if checkpoint.policy == POLICY_STOP:
                    self._conclusion = CONCLUSION_GLOBAL_ERROR
                    return

        # 文件间比较
        for checkpoint in self.__class__.DOC_COMPARE_CHECKPOINTS:
            _result = checkpoint.check(self.docs, self.report)
            if _result:
                self.result.setdefault('DOC_COMPARE', set()).update(_result)
                self._conclusion = CONCLUSION_DIFFERENCE

        # 按文件类型分别检查
        for doc_type, doc_list in self.docs.items():
            for doc in doc_list:
                _result = doc.check(self.report)
                if _result:
                    self._conclusion = CONCLUSION_DIFFERENCE
                    doc.result.update(_result)
                    # self.result.setdefault(doc_type, set()).update(_result)

    def add_doc(self, doc):
        self.docs.setdefault(doc.doc_type, []).append(doc)

    @property
    def conclusion(self):
        return CONCLUSION_MAP.get(self._conclusion, 'Unknown key')

    @conclusion.setter
    def conclusion(self, value):
        if value not in CONCLUSION_MAP:
            raise ValueError(f'不被允许的结论值 {value}')
        self._conclusion = value

    def output_result(self):
        for k, v in self.result.items():
            print(f'======= {k} 的结果是 =========')
            for each in v:
                print(each)

    @conclusion.setter
    def conclusion(self, value):
        self._conclusion = value


class CheckPoint:
    def __init__(self, description=None, rule=None, policy=None):
        self.description = description
        self.rule = rule
        self.policy = policy

    def check(self, doc, report):
        rpa_logger.info(f'开始检查checkpoint [{self.description}]')

        try:
            result = self.rule.apply(doc, report)
            if isinstance(result, list):
                return result
            elif not result:
                return [f'{self.description} 不满足']
        except:
            error_msg = traceback.format_exc()
            rpa_logger.error(f'检查checkpoint [{self.description}] 过程出错, 错误信息如下: \n{error_msg}')
            return [f'checkpoint [{self.description}] 检查过程出错, 错误信息 {error_msg}']
