import logging


def create_logger():
    """
    Create and configure a logger named 'cowrie' that logs to both
    a file and the console with timestamps.
    """
    logger = logging.getLogger("cowrie")
    logger.setLevel(logging.INFO)

    #  "<timestamp> <message>"
    formatter = logging.Formatter(
        "%(asctime)s %(message)s"
    )

    # where we log
    file_handler = logging.FileHandler("/app/logs/honeypot.log")

    file_handler.setFormatter(formatter)


    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Attach both handlers so every log goes to file + console
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
