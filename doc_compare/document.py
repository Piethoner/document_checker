import string
from copy import deepcopy
from itertools import groupby
from datetime import datetime
from operator import itemgetter

from utils import *
from doc_compare.checker import *
from doc_compare.doc_checkpoints.common import *
from doc_compare.doc_checkpoints import CHECKPOINTS_MAP


class _GetDataType:
    def get(self, key, default=None):
        if isinstance(key, (list, tuple, set)):
            result = {each: self.data.get(each, default) for each in key}
        else:
            result = self.data.get(key, default)

        return result


class _ParseDataType:
    DATE_TITLES = []
    NUM_TITLES = []
    KEY_MAP = {}

    def parse_data(self, data: dict):
        result = {}
        for k, v in data.items():
            new_key = self.__class__.KEY_MAP.get(k, k)
            if k in self.__class__.DATE_TITLES:
                result[new_key] = parse_datetime(v)
            elif k in self.__class__.NUM_TITLES:
                result[new_key] = parse_num(v)
            else:
                result[new_key] = v
        return result


# =======================================================


class ReportOperator(ExcelOperator, _ParseDataType):
    GROUP_KEY = None     # 将excel数据分组的列名
    ITEM_KEY = None      # 在item中作为key的列名
    ITEM_TITLES = []     # 放入item中的列名
    NUM_TITLES = []

    def parse_data(self, data: dict):
        data = super().parse_data(data)
        data[self.__class__.GROUP_KEY] = str(int(float(data[self.__class__.GROUP_KEY]))).zfill(10)
        return data

    def read_data(self, sheet='Sheet1', **kwargs):
        result = {}

        data = super().read_data(sheet=sheet)
        data = [self.parse_data(row) for row in data if row.get(self.__class__.GROUP_KEY)]

        data = sorted(data, key=itemgetter(self.__class__.GROUP_KEY))
        data_groupby_po_num = groupby(data, itemgetter(self.__class__.GROUP_KEY))
        data_groupby_po_num = {str(po_num): list(row_data) for po_num, row_data in data_groupby_po_num}

        item_titles = self.__class__.ITEM_TITLES

        for po_num, po_data in data_groupby_po_num.items():

            # 存储非item数据
            result[po_num] = {key: value for key, value in po_data[0].items() if key not in item_titles}

            # 存储item数据
            result[po_num]['items'] = \
                {str(each.get(self.__class__.ITEM_KEY, 'N/N')): {k: v for k, v in each.items() if k in item_titles}
                 for each in po_data}

        return result


class PoInfomationOperator(ReportOperator):

    GROUP_KEY = ''
    ITEM_KEY = ''
    ITEM_TITLES = ['']
    NUM_TITLES = ['']

    def read_data(self, sheet='Sheet1', **kwargs):
        rpa_logger.info(f'读取 PO Information 文件 {self.file_name}')
        return super().read_data(sheet)


class WalcenDocOperator(ReportOperator):

    GROUP_KEY = ''
    ITEM_KEY = ''
    ITEM_TITLES = ['']
    NUM_TITLES = ['']

    def read_data(self, sheet=None, **kwargs):
        rpa_logger.info(f'读取 Walcen Doc 文件 {self.file_name}')
        if not sheet:
            sheet = self.workbook.Sheets.Item(1).Name
        return super().read_data(sheet)


class POListOperator(ExcelOperator):
    def read_data(self, sheet='Sheet1', **kwargs):
        rpa_logger.info(f'读取PO List文件 {self.file_name}  Sheet页 {sheet} 的信息')
        excel_data = super().read_data(sheet=sheet, header_row=6)
        return set(parse_num(row.get('PO#')).zfill(10) for row in excel_data if row.get("PO#"))


class ResultTemplateOperator(ExcelOperator):

    DOC_COLUMN = ('CI', 'CO', 'PL', 'CM', 'FCR')

    def __init__(self, template_path):
        self.current_row_num = 2
        super().__init__(template_path)

    def update(self, checker):
        """
        将checker结果写入result文件
        """
        end_row = start_row = self.current_row_num

        row_data = [
            ('完成日期', f"'{datetime.now().strftime('%Y-%m-%d')}"),
            ('完成情况', checker.conclusion),
            ('CY/CFS', ''),
            ('是否哥斯达黎加', 'Y'),
            ('PO', f"'{checker.po_num}"),
            ('全局规则', ';'.join(checker.result.get('GLOBAL', []))),
            ('文件间比对规则', ';'.join(checker.result.get('DOC_COMPARE', []))),
            ('是否成功更新到mods', 'Y' if checker.update_result else 'N'),
            ('是否报错', checker.error if checker.error else '无报错')
        ]
        self.insert_data(irange=f'A{start_row}:{self.column_num_to_alpha(len(row_data))}{start_row}',
                         data=[each[1] for each in row_data])

        for col, doc_type in enumerate(self.__class__.DOC_COLUMN, len(row_data)+1):
            now_row = start_row
            col = self.column_num_to_alpha(col)
            for n, doc in enumerate(checker.docs.get(doc_type, []), 1):
                self.insert_data(irange=f'{col}{now_row}', data=f'{doc_type}文件{n}')
                self.set_hyperlink(irange=f'{col}{now_row}', link=doc.ocr_link)
                doc_conclusion = ';'.join(doc.result) if doc.result else ('无差异' if doc.checked else '未检查')
                self.insert_data(irange=f'{col}{now_row+1}', data=doc_conclusion)
                now_row += 2
                end_row = max(end_row, now_row)

        for n in range(1, len(row_data)+1):
            self.merge_cells(f'{self.column_num_to_alpha(n)}{start_row}:'
                             f'{self.column_num_to_alpha(n)}{end_row-1}')

        self.auto_fit()
        self.current_row_num = end_row

        return True

    @staticmethod
    def gen_ocr_link_desc(checker):
        link_desc = []
        for doc_type, doc_list in checker.docs.items():
            link_desc.extend([f'{doc_type} link'] + [each.ocr_link for each in doc_list])
        return '\n'.join(link_desc)


# ===========================================================================================


# 文件OCR出来的结果与报告(class Report)进行比对, 报告是标准答案.
# 每个PO号对应一个Report
class Report(_GetDataType, _ParseDataType):
    DATE_TITLES = []
    NUM_TITLES = []

    def __init__(self, po_num, *data_dicts, **kw_info):
        self.po_num = po_num
        self.data = {}

        # 各个来源的report数据整合
        for data_dict in data_dicts:
            self.update_data(self.data, self.parse_data(data_dict))
        self.update_data(self.data, kw_info)

    def update_data(self, data1, data2):
        for k, v in data2.items():
            if isinstance(v, dict):
                self.update_data(data1.setdefault(k, {}), v)
            elif isinstance(v, list):
                data1.setdefault(k, []).extend(v)
            else:
                data1[k] = v


class Doc(_GetDataType, _ParseDataType):
    CHECK_POINTS = []

    def __new__(cls, *args, **kwargs):
        cls.CHECK_POINTS = [CheckPoint(**kwargs) for kwargs in CHECKPOINTS_MAP.get(cls.__name__, [])]
        return super().__new__(cls)

    def __init__(self, data):
        self.data = self.parse_data(data)
        self.ocr_link = data.get('ocr_link')
        self.result = set()
        self.checked = False

    def check(self, report):
        rpa_logger.info(f'####### 开始进行 {self.__class__.__name__} checkpoint 检查 #######')
        result = []
        for checkpoint in self.__class__.CHECK_POINTS:
            _res = checkpoint.check(self, report)
            if _res:
                result.extend(_res)
                if checkpoint.policy == POLICY_PASS:
                    break

        self.checked = True
        return result

    def merge(self, doc):
        for key, value in doc.data.items():
            if isinstance(value, list):
                self.data.setdefault(key, []).extend(doc.data.get(key, []))
            elif isinstance(value, dict):
                self.data.setdefault(key, {}).update(doc.data.get(key, {}))
            else:
                self.data[key] = value

    @property
    def doc_type(self):
        return self.__class__.__name__


class CI(Doc):

    DATE_TITLES = []
    KEY_MAP = {
        'PO_Number': 'PO Number',
    }

    def parse_data(self, data) -> {}:
        data = super().parse_data(data)

        result = {}
        items = result['items'] = {}
        pages = result['pages'] = []
        model_style = result['model_style'] = []
        serial_num = result['serial_num'] = []

        for row in data.get('xxx', []):
            items[row.get('xxx', 'N/N')] = {}

        result.update({k: v for k, v in data.items() if k != 'xxx'})

        return result


class CO(Doc):

    DATE_TITLES = ['']
    KEY_MAP = {
        'PO_Number': 'PO Number',
    }

    def parse_data(self, data):
        data[''] = clean_punctuation(data.get('', '')).replace(' ', '')
        data = super().parse_data(data)

        result = {}
        items = result['items'] = []
        ctns = result['ctns'] = []

        for row in data.get('Commodity', []):
            pass

        result.update({k: v for k, v in data.items() if k != 'Commodity'})

        return result


class CM(Doc):
    def parse_data(self, data):
        data = super().parse_data(data)
        data['PO Number'] = [each.get('') for each in data.pop('Commodity', [])]
        return data


class PL(Doc):
    DATE_TITLES = ['']
    NUM_TITLES = []
    KEY_MAP = {
        'PO_Number': 'PO Number',
    }

    def parse_data(self, data):
        data = super().parse_data(data)

        result = {}
        pages = result['pages'] = []

        for row in data.get('Commodity', []):
            if row.get('Commodity_页码'):
                pages.append(row.get('Commodity_页码'))

        result.update({k: v for k, v in data.items() if k != 'Commodity'})
        result['item_nums'] = []

        return data


class FCR(Doc):
    def parse_data(self, data):
        data = super().parse_data(data)
        po_num_set = data['PO Number'] = set()
        po_num_regex = re.compile(r'\d+')
        [po_num_set.update(po_num_regex.findall(each.get('Commodity_PO_Number')))
         for each in data.get('Commodity', [])
         if each.get('Commodity_PO_Number')]
        return data


if __name__ == '__main__':
    pass
