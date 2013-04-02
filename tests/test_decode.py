# -*- coding:utf-8 -*-

import unittest

class TestHandler(unittest.TestCase):

    def _getTarget(self):
        from fluent.handler import FluentHandler
        return FluentHandler


    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def test_decode_none(self):
        h = self._makeOne('app.follow')
        result = h._decode(None)
        self.assertIsNone(result)

    def test_decode_str(self):
        h = self._makeOne('app.follow')
        result = h._decode("あいうえお")
        self.assertTrue(isinstance(result, unicode), type(result).__name__)
        self.assertEqual(result, u"あいうえお")

    def test_decode_str2(self):
        h = self._makeOne('app.follow')
        result = h._decode(u"あいうえお".encode('Shift_JIS'))
        self.assertTrue(isinstance(result, unicode), type(result).__name__)
        self.assertEqual(result, u"\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd")  # replaced

    def test_decode_unicode(self):
        h = self._makeOne('app.follow')
        result = h._decode(u"あいうえお")
        self.assertTrue(isinstance(result, unicode), type(result).__name__)
        self.assertEqual(result, u"あいうえお")

    def test_decode_obj(self):
        h = self._makeOne('app.follow')
        marker = object()
        result = h._decode(marker)
        self.assertTrue(isinstance(result, unicode), type(result).__name__)
        
        self.assertEqual(result, str(marker))
