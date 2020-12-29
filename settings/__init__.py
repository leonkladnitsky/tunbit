# -*- coding: utf-8 -*-
from logging import getLogger

logger = getLogger(__name__)

try:
    from .base import *
except ImportError:
    logger.error('base settings NOT imported !!!')
    pass

try:
    from .dev import *
except ImportError:
    logger.warning('dev settings NOT imported')
    pass
else:
    logger.info('-=* DEV *=-')
    pass
