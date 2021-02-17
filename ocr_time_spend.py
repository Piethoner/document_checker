from doc_compare.ocr_operator import OCROperator
from datetime import datetime
import threading
import random
import logging
import time
from utils import *
from config import config


ocr_op = OCROperator()
add_filehandler(test_logger, os.path.join(config.LOG_DIR, 'ocr_time_spend.log'))


def run_ocr():
    time.sleep(random.randint(1, 180))
    while True:
        doc_files = {
                    'type1': ['file'],
                    'type2': ['file'],
                    'type3': ['file'],
                    'type4': ['file'],
                    'type5': ['file'],
                }
        download_result = {}

        start = datetime.now()
        for doc_type, docs in doc_files.items():
            download_result[doc_type] = [ocr_op.ocr(doc, doc_type) for doc in docs]

        for doc_type, request_id_list in download_result.items():
            for req_id in request_id_list:
                ocr_op.get_ocr_result(req_id, doc_type)
        end = datetime.now()
        test_logger.info(f'开始时间 {start}， 结束时间 {end}, 耗时 {(end - start).seconds}s')
        time.sleep(30)


record = []
for _ in range(3):
    p = threading.Thread(target=run_ocr)
    p.start()
    record.append(p)

for each in record:
    each.join()

