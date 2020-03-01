# -*- coding: utf-8 -*-
import logging
import sys

logging.basicConfig()

log = logging.getLogger(__name__)

try:
    from .base import *
except ImportError:
    log.warning('base settings NOT imported')

try:
    from .dev import *
except ImportError:
    if DEBUG:
        log.warning('dev settings NOT imported')
    pass
else:
    if DEBUG:
        log.warning('-=* DEV *=-')
