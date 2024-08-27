#! /usr/bin/python

from prensio import main
import logging_config

if __name__ == "__main__":
    import logging
    logger = logging.getLogger("main")
    main.main()
