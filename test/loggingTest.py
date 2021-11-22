import logging

'''
https://velog.io/@devmin/first-python-logging

'''


class MyLoggingHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        self.l = []

    def emit(self, record: logging.LogRecord) -> None:
        formed = self.formatter.format(record)
        print(record.levelno)
        self.l.append(formed)


def test1():
    loggerName = "myLogger"
    logger1 = logging.getLogger(loggerName)
    logger1.setLevel(logging.DEBUG)
    logger2 = logging.getLogger(loggerName)

    print(logger1)
    print(logger2)


def test2():
    loggerName = "myLogger"
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s ##%(levelname)s## : %(message)s \n\t >> File "%(filename)s", line %(lineno)s, in %(module)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler('my.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    my_handler = MyLoggingHandler()
    my_handler.setFormatter(formatter)
    logger.addHandler(my_handler)


    logger.warning("메렁1")
    logger.info("메렁2")
    logger.info("메렁3")


if __name__ == '__main__':
    test2()
