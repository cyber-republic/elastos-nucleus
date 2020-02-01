import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s browser: %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S',
)