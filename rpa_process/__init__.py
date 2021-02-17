from utils import *
from .file_downloader import FileDownloader
from .mods_demo import *


# filedownloader = FileDownloader()


@add_log('下载PO号对应的文件')
def download_files(po_num, retry=3):
    return {
        'success': True,
        'files': {
        }}

    for _ in range(retry):
        result = filedownloader.download_files(po_num)
        if result.get('success'):
            break
    return result


@add_log('更新数据到mods')
def update_to_mods(po_num, invoice_no, courier, doc_codes):
    if open_mods():
        return get_data(po_num, invoice_no, courier, doc_codes)
    else:
        return {'success': False, 'msg': '打开mods失败'}


if __name__ == '__main__':
    update_to_mods()
