import logging

def setup_logging():
    logger = logging.getLogger('project_logger')
    logger.setLevel(logging.INFO)
    
    # Create file handler
    fh = logging.FileHandler('project.log')
    fh.setLevel(logging.INFO)
    
    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

def get_logger():
    return logging.getLogger('project_logger')
