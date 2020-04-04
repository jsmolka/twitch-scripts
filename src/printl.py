import logging

_logger = None


def printl_init(filename = None):
    global _logger
    _logger = logging.getLogger("printl")
    _logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    _logger.addHandler(stream_handler)

    if filename:
        file_handler = logging.FileHandler(filename)
        file_handler.setFormatter(formatter)
        _logger.addHandler(file_handler)


def printl(*args, level="info", sep=" "):
    global _logger
    if not _logger:
        printl_init()
    message = sep.join(map(str, args))
    getattr(_logger, level)(message)
