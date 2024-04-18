import logging
import datetime
import eel

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

logger = setup_logger('app.log')

class log:
    def info(msg):
        try:
            eel.addLog(datetime.datetime.now().strftime('%H:%M:%S') + ' |INFO | ' + msg)
        except:
            pass
        logger.info(msg)
    def error(msg):
        try:
            eel.addLog(datetime.datetime.now().strftime('%H:%M:%S') + ' |ERROR| ' + msg)
        except:
            pass
        logger.error(msg)
    def debug(msg):
        logger.debug(msg)
    def warning(msg):
        try:
            eel.addLog(datetime.datetime.now().strftime('%H:%M:%S') + ' |WARN | ' + msg)
        except:
            pass
        logger.warning(msg)

if __name__ == '__main__':
    logger.debug('Debug Message')
    logger.info('Info Message')
    # logger.warning('Warning Message') # 不易对齐，不建议使用
    logger.error('Error Message')