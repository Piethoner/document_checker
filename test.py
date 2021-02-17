import json
import requests

from utils import ExcelOperator

with ExcelOperator('file_name') as eop:
    print(eop)
