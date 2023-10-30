import logging
import datetime

def setup_logger(log_file):

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # 创建一个文件handler，用于写入日志文件
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 创建一个控制台handler，用于输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    # console_handler.setLevel(logging.DEBUG)

    # 定义日志输出格式
    f_formatter = logging.Formatter('%(asctime)s |%(levelname)-5s| %(message)s', 
                                  datefmt='%Y-%m-%d %H:%M:%S')
    c_formatter = logging.Formatter('%(asctime)s |%(levelname)-5s| %(message)s', 
                                  datefmt='%H:%M:%S')
    file_handler.setFormatter(f_formatter)
    console_handler.setFormatter(c_formatter)

    logger.addHandler(file_handler)

    divider = '-' * 40
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    logger.info(divider)
    logger.info(f'Program started at: {current_date}')
    logger.info(divider)

    logger.addHandler(console_handler)

    return logger

log = setup_logger('app.log')

if __name__ == '__main__':
    log.debug('Debug Message')
    log.info('Info Message')
    # logger.warning('Warning Message') # 不易对齐，不建议使用
    log.error('Error Message')