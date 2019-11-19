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
           encoding='utf-8',
           jsonifier=None,
           extra_attrs=[]):
        logging.Handler.__init__(self)
        self.tag = tag
        self.sender = sender.FluentSender(tag,
                                          host=host, port=port,
                                          timeout=timeout, verbose=verbose)
        self.hostname = socket.gethostname()
        self.fsencoding = sys.getfilesystemencoding()
        self.encoding = encoding
        self.jsonifier = jsonifier
        self.extra_attrs = extra_attrs

    def emit(self, record):
        self.sender.emit_with_time(None, record.created, self._build_structure(record))

    def _close(self):
        self.sender._close()

    def _build_structure(self, record):
        data = {
            'time': datetime.fromtimestamp(record.created).isoformat(),
            'sys_msecs': record.msecs,
            'sys_host' : self._decode(self.hostname),
            'sys_name' : self._asciidecode(record.name),
            'sys_exc_info' : self._format_exception(record.exc_info),
            'sys_levelno' : record.levelno,
            'sys_levelname' : self._decode(record.levelname),
            'sys_lineno' : record.lineno,
            'sys_module' : self._decode(record.module),
            'sys_filename' : self._fsdecode(record.filename),
            'sys_funcname' : self._decode(record.funcName),
            'sys_process': record.process,
            'sys_processname': self._decode(record.processName),
            'sys_thread': record.thread,
            'sys_threadname': self._decode(record.threadName),
            'message': self._decode(self.format(record))
            }
        for k in self.extra_attrs:
            try:
                data[k] = self._decode_tree(getattr(record, k))
            except AttributeError:
                pass
        if self.jsonifier is not None:
            data.update(self.jsonifier(record.msg))
        return data

    def _decode_tree(self, value):
        if isinstance(value, dict):
            return dict(
                (k, self._decode_tree(v))
                for k, v in list(value.items())
                )
        elif isinstance(value, (list, tuple)):
            return [
                self._decode_tree(v)
                for v in value
                ]
        else:
            return self._decode(value)

    def _decode(self, value):
        if value is None:
            return None
        elif isinstance(value, str):
            return value
        elif isinstance(value, str):
            return str(value, self.encoding, errors='replace')
        else:
            try:
                return getattr(value, '__unicode__', None)()
            except:
                pass
            try:
                return self._decode(str(value))
            except (TypeError, UnicodeEncodeError, UnicodeDecodeError):
                try:
                    return self._decode(str(value).encode('string_escape'))
                except:
                    # last resort
                    return self._decode(str(type(value)))

    def _fsdecode(self, value):
        if value is None:
            return None
        #elif isinstance(value, str):
            #return str(value, self.fsencoding)
        elif isinstance(value, str):
            return value
        else:
            return '-'

    def _asciidecode(self, value):
        if value is None:
            return None
        elif isinstance(value, str):
            return str(value)
        elif isinstance(value, str):
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


