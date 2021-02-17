from utils import *
from config import config


POLICY_PASS = 1001   # 仅在文档checkpoint中出现， 跳过当前文档
POLICY_STOP = 1002   # 仅在全局checkpoint中出现， 结束当前checker


@add_log('读取 Consignee 文件')
def get_consignee_data():

    def isalnum(word):
        if (ord('A') <= ord(word) <= ord('Z')) or (ord('0') <= ord(word) <= ord('9')):
            return True

    with ExcelOperator(config.CONSIGNEE_FILE_PATH) as eop:
        consignee_map = {}
        for row in eop.read_data():
            key = row.get("Code", "")
            value = clean_punctuation(f'{row.get("Name", "")}{row.get("Address", "")}').upper().replace(' ', '')
            value = ''.join(([(w if isalnum(w) else '.') for w in value]))
            consignee_map[key] = value
        return consignee_map


CONSIGNEE_MAP = get_consignee_data()


def belong_consignee(address, consignee):
    clean_consignee = CONSIGNEE_MAP.get(consignee, "report_consignee")
    clean_address = clean_punctuation(address).upper().replace(' ', '')
    consignee_regex = re.compile(rf'^{clean_consignee[:min(len(clean_consignee), len(clean_address))]}$')
    return bool(consignee_regex.search(clean_address))


def check_page_num(page_num_list):
    page_regex = re.compile(r'PAGE(?P<current_page>\d+)OF(?P<total_page>\d+)')
    current_page_list = []
    total_page_list = []
    for each in page_num_list:
        page_regex_result = page_regex.search(clean_punctuation(each).replace(' ', '').upper())
        current_page_list.append(int(page_regex_result.group('current_page')))
        total_page_list.append(int(page_regex_result.group('total_page')))

    if len(set(total_page_list)) != 1:
        return False

    total_page = total_page_list[0]
    if not ((len(set(current_page_list)) == total_page) and
            (max(current_page_list) == total_page) and
            (min(current_page_list) == 1)):
        return False

    return True
