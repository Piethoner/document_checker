from config import config
from doc_compare import *
from rpa_process import download_files, update_to_mods

import time
from copy import deepcopy


def main():
    with OCROperator() as ocr_op:
        # 读取PO information
        poinfo_file = find_latest_modified_file_with_keyword(dir_path=config.POINFO_DIR, keyword='PO information')
        with PoInfomationOperator(poinfo_file) as piop:
            poinfo_data = piop.read_data()

        # 读取Walcen Doc
        walcendoc_file = find_latest_modified_file_with_keyword(dir_path=config.WALCENDOC_DIR, keyword='Walcen')
        with WalcenDocOperator(walcendoc_file) as wdop:
            walcendoc_data = wdop.read_data()

        # 读取PO List
        polist_file = find_latest_modified_file_with_keyword(dir_path=config.POLIST_DIR, keyword='-CAM')
        polist_data = []
        with POListOperator(polist_file) as plop:
            for i in range(1, plop.workbook.Sheets.Count+1):
                sheet = plop.workbook.Sheets.Item(i).Name
                polist_data.extend(plop.read_data(sheet=sheet))

        checker_list = []
        for po_num in polist_data:
            if po_num not in poinfo_data:
                rpa_logger.error(f'在PO INFO 文件中找不到 PO号 {po_num}')
                continue

            if po_num not in walcendoc_data:
                rpa_logger.error(f'在Walcen Doc 文件中找不到 PO号 {po_num}')
                continue

            report = Report(po_num, poinfo_data[po_num], walcendoc_data[po_num])
            mchecker = Checker(po_num=po_num, report=report)

            try:
                rpa_logger.info(f'开始执行 PO {po_num} 的相关操作')
                download_result = download_files(po_num)
                if not download_result.get('success'):
                    rpa_logger.error(f'PO号 {po_num} 下载文件失败， 错误信息: f{download_result.get("msg", "")}')
                    continue
                else:
                    download_result = download_result.get('files', {})

                for doc_type, docs in deepcopy(download_result).items():
                    _doc_class = DOC_CLASSES.get(doc_type)
                    if doc_type not in DOC_CLASSES:
                        rpa_logger.error(f"文档类型 {doc_type} 不属于任何已知类别")
                        download_result.pop(doc_type, [])
                        continue
                    download_result[doc_type] = [ocr_op.ocr(doc, doc_type) for doc in docs]

                for doc_type, request_id_list in download_result.items():
                    _doc_class = DOC_CLASSES.get(doc_type)
                    for req_id in request_id_list:
                        ocr_result = ocr_op.get_ocr_result(req_id, doc_type)
                        mchecker.add_doc(_doc_class(data=ocr_result))

                mchecker.check()

                rpa_logger.info(f'PO号 {mchecker.po_num} 检查结果 {mchecker.conclusion}')
                if mchecker.conclusion == '无差异':
                    ci_data = mchecker.docs['CI'][0]
                    update_result = update_to_mods(
                        mchecker.po_num, ci_data.get('INVOICE_NO'), ci_data.get('INVOICE_DATE'),
                        doc_codes=[config.DOC_CODE_MAP.get(key)
                                   for key in mchecker.docs.keys() if config.DOC_CODE_MAP.get(key)])
                    mchecker.update_result = update_result.get('success', False)

                checker_list.append(mchecker)

            except:
                error_msg = traceback.format_exc()
                rpa_logger.error(f'PO {po_num} 处理过程出错， 错误信息:\n {error_msg}')
                mchecker.conclusion = CONCLUSION_ERROR
                mchecker.error = error_msg

        result_path = os.path.join(config.OUTPUT_DIR, f'result{int(time.time())}.xlsx')
        with ResultTemplateOperator(config.RESULT_TEMPLATE_PATH) as rtop:
            [rtop.update(each) for each in checker_list]
            rtop.save(result_path)


if __name__ == '__main__':
    add_filehandler(rpa_logger, os.path.join(config.LOG_DIR, 'rpa.log'))
    main()
