import os


class CreateDir(type):
    def __new__(mcs, class_name, parents, class_attr):
        for key, value in class_attr.items():
            if key.endswith('DIR'):
                if not os.path.exists(value):
                    os.makedirs(value)
        return type.__new__(mcs, class_name, parents, class_attr)


class Config(metaclass=CreateDir):
    OCR_HOST = 'http://host:80'
    OCR_USERNAME = 'user'
    OCR_PASSWORD = 'pass'

    MYMAERSK_USERNAME = '1111'
    MYMAERSK_PASSWORD = '2222'

    MODS_USERNAME = 'xxxx'
    MODS_PASSWORD = 'ggggg'
    MODS_PATH = r"x"
    MARCO_NAME = 'dddd'
    MARCO_PATH = f'dddd'

    WORK_DIR = os.path.dirname(__file__)
    TMP_DIR = os.path.join(WORK_DIR, 'tmp')
    LOG_DIR = os.path.join(WORK_DIR, 'log')
    REFERENCE_DIR = os.path.join(WORK_DIR, 'reference')
    OUTPUT_DIR = os.path.join(WORK_DIR, 'output')
    TEMPLATE_DIR = os.path.join(WORK_DIR, 'template')
    DOWNLOAD_DIR = os.path.join(WORK_DIR, 'download')
    RESULT_TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, 'result_template.xlsx')
    CONSIGNEE_FILE_PATH = os.path.join(REFERENCE_DIR, 'tttt')
    POINFO_DIR = 'gggg'
    WALCENDOC_DIR = 'gggg'
    POLIST_DIR = 'gggg'

    # 文档类型对应的code, 用于传递给mods
    DOC_CODE_MAP = {
        'CI': 'INV',
        'PL': 'P/L',
        'CM': 'COM',
        'CO': 'C/O'
    }


config = Config()
