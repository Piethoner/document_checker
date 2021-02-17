import os
import time
from config import config
from utils import ExcelOperator


def read_polist():
    po_list = set()
    for file in os.listdir(config.DOWNLOAD_DIR):
        if os.path.isdir(os.path.join(config.DOWNLOAD_DIR, file)):
            po_list.add(file)
    return po_list


def download_files(po_num):
    doc_sheet_map = {
        'CI': "xxxx",
        'PL': "asdadas",
        'CM': "Sheet1",

    }
    result_files = {}
    dir_path = os.path.join(config.DOWNLOAD_DIR, str(po_num))
    for file in os.listdir(dir_path):
        for keyword in ('CI', 'PL', 'CO', 'CM', 'FCR'):
            if keyword in file:
                file_path = os.path.join(dir_path, file)
                if file.upper().endswith('PDF'):
                    result_files.setdefault(keyword, []).append(file_path)
                else:
                    pdf_path = os.path.splitext(file_path)[0] + '.pdf'
                    with ExcelOperator(file_path) as eop:
                        eop.save_sheet_as_pdf(pdf_path, doc_sheet_map.get(keyword, 'Sheet1'))
                    result_files.setdefault(keyword, []).append(pdf_path)
                break

    return {'success': True, 'files': result_files}
