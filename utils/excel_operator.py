import os
import time
import shutil
import string
import win32com.client as win32

from ._logging import *


class ExcelOperator:
    def __init__(self, excel_path):
        self.file_path = os.path.abspath(excel_path)

    @property
    def file_name(self):
        return os.path.basename(self.file_path)

    def __enter__(self):
        try:
            self.app = win32.gencache.EnsureDispatch('Excel.Application')
        except AttributeError:
            shutil.rmtree(os.path.join(os.environ.get("LOCALAPPDATA"), "Temp", "gen_py"))
            time.sleep(1)
            self.app = win32.gencache.EnsureDispatch('Excel.Application')

        self.app.Visible = False
        self.app.DisplayAlerts = False

        if not os.path.exists(self.file_path):
            self.workbook = self.app.Workbooks.Add()
        else:
            self.workbook = self.app.Workbooks.Open(self.file_path, IgnoreReadOnlyRecommended=True)

        return self

    def __exit__(self, *args):
        # self.workbook.SaveAs(self.file_path)
        self.app.Quit()

    def get_rows_count(self, sheet='Sheet1'):
        sht = self.workbook.Sheets.Item(sheet)
        return sht.UsedRange.Rows.Count

    def get_column_count(self, sheet='Sheet1'):
        sht = self.workbook.Sheets.Item(sheet)
        return sht.UsedRange.Columns.Count

    @staticmethod
    def column_num_to_alpha(num):
        """
        将数字列号转化为excel字母列号
        :param num:
        :return:
        """
        alphabets = list(string.ascii_uppercase)
        result = []

        def num_to_alpha(n):
            nonlocal alphabets
            nonlocal result
            n -= 1
            result.append(alphabets[n % 26])
            s = n // 26
            if s > 0:
                num_to_alpha(s)

        num_to_alpha(num)
        result.reverse()
        return ''.join(result)

    def read_data(self, sheet='Sheet1', header_row=1):
        sht = self.workbook.Sheets.Item(sheet)
        row_count = sht.UsedRange.Rows.Count
        column_count = sht.UsedRange.Columns.Count

        column_name = sht.Range(f'A{header_row}:{self.column_num_to_alpha(column_count)}{header_row}').Value[0]

        excel_data = []
        for n in range(header_row+1, row_count+1):
            row_data = sht.Range(f'A{n}:{self.column_num_to_alpha(column_count)}{n}').Value[0]
            excel_data.append(dict(zip(column_name, row_data)))

        return excel_data

    def auto_fit(self, start_row=None, end_row=None, sheet='Sheet1'):
        sht = self.workbook.Sheets.Item(sheet)
        start_row = 1 if not start_row else start_row
        end_row = sht.UsedRange.Rows.Count if not end_row else end_row
        sht.Range(f'A{start_row}:A{end_row}').Columns.AutoFit()
        sht.Range(f'A{start_row}:A{end_row}').Rows.AutoFit()

    def insert_data(self, irange, data, sheet='Sheet1'):
        sht = self.workbook.Sheets.Item(sheet)
        sht.Range(irange).Value = data

    def set_hyperlink(self, irange, link, sheet='Sheet1'):
        sht = self.workbook.Sheets.Item(sheet)
        sht.Hyperlinks.Add(sht.Range(irange), link)

    def merge_cells(self, irange, sheet='Sheet1'):
        sht = self.workbook.Sheets.Item(sheet)
        sht.Range(irange).Merge()

    def save(self, save_path):
        self.workbook.SaveAs(save_path)

    def save_sheet_as_pdf(self, save_path, sheet='Sheet1'):
        rpa_logger.info(f'将excel文件{self.file_path} 另存为pdf')
        sht = self.workbook.Sheets.Item(sheet)
        sht.SaveAs(save_path, FileFormat=57)


if __name__ == '__main__':
    import json
    with ExcelOperator('xxxxx') as eop:
        eop.save_sheet_as_pdf('ttttt', sheet='3 Packing List')