import logging
import logging.handlers
from functools import wraps

# 创建日志记录器
logging.basicConfig(level=logging.INFO)
rpa_logger = logging.getLogger('rpa')
test_logger = logging.getLogger('test')


def add_filehandler(logger, log_path):
    fh = logging.handlers.TimedRotatingFileHandler(log_path,
                                                   when='midnight',
                                                   interval=3,
                                                   backupCount=10)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s %(name)s %(levelname)s] %(filename)s:%(lineno)d:%(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


# 日志装饰器
def add_log(func_name=''):
    def decorator(func):
        @wraps(func)
        def inner_decorator(*args, **kwargs):
            rpa_logger.info(f'{func_name} 开始执行')
            result = func(*args, **kwargs)
            rpa_logger.info(f'{func_name} 执行完成')
            return result

        return inner_decorator

    return decorator


# 输出函数参数
def print_function_args(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        rpa_logger.info(f'方法名称 {func.__name__}\n'
                        f'请求参数 {args}, {kwargs}')
        result = func(*args, **kwargs)
        rpa_logger.info(f'结果是 {result}')
        return result

    return decorator
