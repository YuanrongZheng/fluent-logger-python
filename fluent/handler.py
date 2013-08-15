import logging
import os
import sys
import msgpack
import socket
import traceback
from datetime import datetime

try:
    import json
except ImportError:
    import simplejson as json

from fluent import sender

class FluentHandler(logging.Handler):
    '''
    Logging Handler for fluent.
    '''
    def __init__(self,
           tag,
           host='localhost',
           port=24224,
           timeout=3.0,
           verbose=False,
           encoding='utf-8'):
        logging.Handler.__init__(self)
        self.tag = tag
        self.sender = sender.FluentSender(tag,
                                          host=host, port=port,
                                          timeout=timeout, verbose=verbose)
        self.hostname = socket.gethostname()
        self.fsencoding = sys.getfilesystemencoding()
        self.encoding = encoding

    def emit(self, record):
        self.sender.emit_with_time(None, record.created, self._build_structure(record))

    def _close(self):
        self.sender._close()

    def _build_structure(self, record):
        data = {
            u'time': datetime.fromtimestamp(record.created).isoformat(),
            u'sys_msecs': record.msecs,
            u'sys_host' : self._decode(self.hostname),
            u'sys_name' : self._asciidecode(record.name),
            u'sys_exc_info' : self._format_exception(record.exc_info),
            u'sys_levelno' : record.levelno,
            u'sys_levelname' : self._decode(record.levelname),
            u'sys_lineno' : record.lineno,
            u'sys_module' : self._decode(record.module),
            u'sys_filename' : self._fsdecode(record.filename),
            u'sys_funcname' : self._decode(record.funcName),
            u'sys_process': record.process,
            u'sys_processname': self._decode(record.processName),
            u'sys_thread': record.thread,
            u'sys_threadname': self._decode(record.threadName),
            u'message': self._decode(self.format(record))
            }
        return data

    def _decode(self, value):
        if value is None:
            return None
        elif isinstance(value, unicode):
            return value
        elif isinstance(value, basestring):
            return unicode(value, self.encoding, errors='replace')
        else:
            try:
                return getattr(value, '__unicode__', None)()
            except:
                pass
            try:
                return self._decode(unicode(value))
            except (TypeError, UnicodeDecodeError):
                return self._decode(str(value).encode('string_escape'))

    def _fsdecode(self, value):
        if value is None:
            return None
        elif isinstance(value, str):
            return unicode(value, self.fsencoding)
        elif isinstance(value, unicode):
            return value
        else:
            return '-'

    def _asciidecode(self, value):
        if value is None:
            return None
        elif isinstance(value, str):
            return unicode(value)
        elif isinstance(value, unicode):
            return value
        else:
            return self._asciidecode(str(value))

    def _format_exception(self, exc_info):
        if exc_info is not None and exc_info[0] is not None:
            return {
                'type': exc_info[0].__name__,
                'value': [self._decode(arg) for arg in exc_info[1].args],
                'traceback': traceback.extract_tb(exc_info[2])
                }
        else:
            return None


