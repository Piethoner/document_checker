"""
不读excel 而是将excel 转化为pdf 后通过正常OCR 流程处理。
"""

from utils import *


def flat(iterable_obj):
    for item in iterable_obj:
        if isinstance(item, (list, tuple, set)):
            tmp = flat(item)
            for each in tmp:
                yield each
        else:
            yield item


class DocReader(ExcelOperator):
    DOC_TYPE = None
    TARGET_SHEET = None
    FIELD_MAP = {''}

    def parse_data(self, data):
        raise NotImplementedError

    def read_data(self, **kwargs):
        sht = self.workbook.Sheets.Item(self.__class__.TARGET_SHEET)

        format_args = {
            'row_count': sht.UsedRange.Rows.Count,
            'column_count': sht.UsedRange.Columns.Count
        }

        result = {}
        for field_name, field_range in self.__class__.FIELD_MAP.items():
            result[field_name] = flat(sht.Range(field_range.format(**format_args)).Value)

        return self.parse_data(result)


class CMReader(DocReader):
    DOC_TYPE = 'CM'
    TARGET_SHEET = 'Sheet1'
    FIELD_MAP = {
        '标题': 'A1',
        'PO Number': 'F12:F{column_count}'
    }

    def parse_data(self, data):
        data['标题'] = data.get('标题')[0] if data.get('标题') else ''
        data['PO Number'] = [parse_num(each).zfill(10) for each in data.get('PO Number', [])]


class PLReader(DocReader):
    DOC_TYPE = 'PL'
    FIELD_MAP = {

    }

    def parse_data(self, data):
        pass


if __name__ == '__main__':
    with DocReader('xxx') as dr:
        dr.read_data()
