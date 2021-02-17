import time
import json
import requests
from copy import deepcopy

from utils import *
from config import config


class OCROperator:
    def __init__(self):
        self.host = config.OCR_HOST
        self.username = config.OCR_USERNAME
        self.password = config.OCR_PASSWORD
        self.token = None
        self.type_id_map = {}
        self.ajax_op = AjaxOperator()

        self._login()
        self._get_id_map()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.quit()

    def quit(self):
        self.ajax_op.quit()

    @add_log('请求OCR登录接口')
    def _login(self):
        return
        url = self.host + '/login'
        data = {
            'username': self.username,
            'password': self.password
        }
        for _ in range(3):
            resp = self.ajax_op.post(url, data=data)
            if resp.status_code == 200 and resp.json().get('access_token'):
                self.token = resp.json().get('access_token')
                return
            time.sleep(10)
        else:
            raise Exception(f'登录失败, 错误码 {resp.status_code}, 错误信息 {resp.text}')

    @add_log('请求获取 文档类型-ID映射 接口')
    def _get_id_map(self):
        if not self.token:
            self._login()
        url = self.host
        self.type_id_map = {
            'CI': 100,
        }

    @add_log('请求OCR识别发起接口')
    def ocr(self, file_path, file_type):
        rpa_logger.info(f'识别文件 {file_path}')
        if not self.token:
            self._login()

        url = self.host + "/upload"
        doc_type_id = self.type_id_map.get(file_type)
        assert doc_type_id, f'文档类型 {file_type} 找不到对应的ID号'
        data = {'template_type': doc_type_id}
        files = [('file', compress(file_path))]
        headers = {'Authorization': f'Bearer {self.token}'}
        for _ in range(3):
            resp = self.ajax_op.post(url, headers=headers, data=data, files=files)
            if resp.status_code == 200 and resp.json().get('record_id_list'):
                return resp.json().get('record_id_list')[0]
            time.sleep(10)
        else:
            self.token = None
            raise Exception(f'识别发起失败, 错误码 {resp.status_code}, 错误信息 {resp.text}')

    @add_log('请求OCR结果获取接口')
    def get_ocr_result(self, request_id, doc_type=None):
        rpa_logger.info(f'请求ID {request_id}, 文档类型 {doc_type}')
        if not self.token:
            self._login()

        url = self.host + '/record_item'
        headers = {'Authorization': f'Bearer {self.token}'}
        params = {'record_id': request_id}
        for _ in range(50):
            resp = self.ajax_op.get(url, headers=headers, params=params)
            if resp.status_code == 200 and 'res' in resp.json():
                result = self.parse_data(json.loads(resp.json().get('res', '')))
                result['ocr_link'] = f'{self.host}/{request_id}'
                return result
            rpa_logger.info(f'{resp.status_code} {resp.content}')
            time.sleep(10)
        else:
            self.token = None
            raise Exception(f'获取结果失败, 错误码 {resp.status_code}, 错误信息 {resp.text}')

    @staticmethod
    def parse_data(data):
        parsed_result = {}
        ocr_result = data.get('data', {}).get('NCList', [])
        repeat_key = set()

        for each_result in ocr_result:
            for key, value in each_result.items():
                if isinstance(value, dict):
                    parsed_result.setdefault(key, []).append(value.get("value"))
                    repeat_key.add(key)
                elif isinstance(value, list):
                    parsed_result.setdefault(key, []).extend(
                        [{k: v.get('value') for k, v in each.items()} for each in value])

        # 非item类的数据重复出现只取第一个
        for key, value in deepcopy(parsed_result).items():
            if key in repeat_key:
                parsed_result[key] = value[0]

        return parsed_result


if __name__ == '__main__':
    oop = OCROperator()
    print(oop.token)
    oop.quit()









