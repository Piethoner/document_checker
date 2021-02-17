import re
import os
import time
import json
import chardet
from jinja2 import Template
from requests.utils import guess_json_utf
from selenium.webdriver import Chrome, ChromeOptions

from config import config
from utils import rpa_logger


class Response:
    def __init__(self, headers, content, status):
        self.headers = headers
        self.content = content.encode()
        self.text = content
        self.status_code = int(status or 0)

    def json(self):
        encoding = guess_json_utf(self.content)
        if encoding is not None:
            try:
                return json.loads(self.content.decode(encoding))
            except UnicodeDecodeError:
                pass
        return json.loads(self.text)

    def __str__(self):
        return f'< Ajax Response {self.status_code} >'


class AjaxOperator:
    FILE_UPLOAD_TEMPLATE = os.path.join(config.TEMPLATE_DIR, 'fileupload_template.html')
    AJAX_TEMPLATE = os.path.join(config.TEMPLATE_DIR, 'ajax_template.js')

    def __init__(self):
        self._driver = self.driver
        self._fileupload_template = None
        self._ajax_template = None

        self._import_template()

    def quit(self):
        try:
            self._driver.quit()
        except Exception as e:
            rpa_logger.info(f'AjaxOperator 关闭 driver 出错, 原因 {str(e)}')

    @property
    def driver(self):
        try:
            _ = self._driver.current_window_handle
        except:
            rpa_logger.info('获取Driver...')
            options = ChromeOptions()
            options.headless = True
            self._driver = Chrome(options=options)
        return self._driver

    def _import_template(self):
        with open(self.__class__.FILE_UPLOAD_TEMPLATE, 'r') as f:
            self._fileupload_template = Template(f.read())
        with open(self.__class__.AJAX_TEMPLATE, 'r') as f:
            self._ajax_template = Template(f.read())

    def _gen_fileupload_html(self, fill_data):
        tmp_html = os.path.join(config.TMP_DIR, 'tmp.html')
        with open(tmp_html, 'w') as f:
            f.write(self._fileupload_template.render(**fill_data))
        return tmp_html

    def request(self, method, url, data=None, params=None, headers=None, files=None, timeout=120):
        method = method.upper()
        data = {} if data is None else data
        headers = {} if headers is None else headers
        files = [] if files is None else files
        params = {} if params is None else params

        params = [f'{k}={v}' for k, v in params.items()]
        url = f"{url}?{'&'.join(params)}" if params else url

        rpa_logger.info(f'Ajax {method.lower()} {url}')

        fill_data = {
            'method': method,
            'url': url,
            'data': data,
            'headers': headers,
            'files': files
        }

        fileupload_html = self._gen_fileupload_html(fill_data)
        self.driver.get(f'file:///{fileupload_html}')
        for n, (key, file) in enumerate(files, 1):
            ele = self.driver.find_element_by_id(f'{n}_file_upload')
            ele.send_keys(file)

        self.driver.execute_script(self._ajax_template.render(fill_data))

        for _ in range(timeout):
            response_content = self.driver.find_element_by_id('response_content').get_attribute('value')
            response_status = self.driver.find_element_by_id('response_status').get_attribute('value')
            response_headers = self.driver.find_element_by_id('response_headers').get_attribute('value')

            if response_content:
                # 得到结果后，需要将 response块置空， 防止下次请求错误返回
                self.driver.execute_script("document.getElementById('response_status').setAttribute('value', '')")
                self.driver.execute_script("document.getElementById('response_headers').setAttribute('value', '')")
                self.driver.execute_script("document.getElementById('response_content').setAttribute('value', '')")
                return Response(response_headers, response_content, response_status)

            time.sleep(1)
        else:
            return Response('', '{"success": false, "msg": "请求超时"}', 0)

    def get(self, url, params=None, headers=None, **kwargs):
        return self.request('GET', url=url, params=params, headers=headers, **kwargs)

    def post(self, url, params=None, data=None, headers=None, files=None, **kwargs):
        return self.request('POST', url=url, params=params, data=data, headers=headers, files=files, **kwargs)

    def head(self, url, headers=None, **kwargs):
        return self.request('HEAD', url=url, headers=headers, **kwargs)


if __name__ == '__main__':
    ajax = AjaxOperator()
    print(ajax.head('www.baidu.com', timeout=10))
    ajax.quit()
