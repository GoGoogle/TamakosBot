import logging
import logging.config

import yaml


def setup_logging(path="common/logconfig.yaml"):
    with open(path, "r") as f:
        config = yaml.load(f)
        logging.config.dictConfig(config)
