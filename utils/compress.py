import os
import zipfile

from config import config


# 生成zip文件
def compress(filepath):
    if filepath.lower().endswith('.zip'):
        return filepath
    filename = os.path.basename(filepath)
    zip_path = os.path.join(config.TMP_DIR, 'rpa_' + os.path.splitext(filename)[0] + '.zip')
    f = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    f.write(filepath, filename)
    f.close()
    return zip_path
