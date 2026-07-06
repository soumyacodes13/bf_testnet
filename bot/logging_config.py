import logging

def setup_logging(log_file="bot.log"):
    """
    Sets up logging to both a local log file (DEBUG) and the console (INFO).
    """
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)
    
    # Avoid adding duplicate handlers if setup is called multiple times
    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="%H:%M:%S")
        
        # File Logger (Full debug logs)
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        # Console Logger (Summary messages)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(ch)
        
    return logger
