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
        self.assertTrue(isinstance(result, str), type(result).__name__)
        self.assertEqual(result, "あいうえお")

    def test_decode_str2(self):
        h = self._makeOne('app.follow')
        result = h._decode("あいうえお".encode('Shift_JIS'))
        self.assertTrue(isinstance(result, str), type(result).__name__)
        self.assertEqual(result, "\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd")  # replaced

    def test_decode_unicode(self):
        h = self._makeOne('app.follow')
        result = h._decode("あいうえお")
        self.assertTrue(isinstance(result, str), type(result).__name__)
        self.assertEqual(result, "あいうえお")

    def test_decode_obj(self):
        h = self._makeOne('app.follow')
        marker = object()
        result = h._decode(marker)
        self.assertTrue(isinstance(result, str), type(result).__name__)
        
        self.assertEqual(result, str(marker))

    def test_decode_more(self):
        handler = self._makeOne('app.follow', encoding='ascii')
        self.assertEqual(handler._decode('a'), 'a')
        self.assertEqual(handler._decode('\u2600'), '\u2600')
        self.assertEqual(handler._decode([1, 2, '3']), "[1, 2, '3']")
        self.assertEqual(handler._decode((1, 2, [3])), "(1, 2, [3])")
        self.assertEqual(handler._decode({'a': '\u2600', 'c': [1, 2, {'c': 'd'}]}), "{'a': u'\\u2600', 'c': [1, 2, {'c': 'd'}]}")

        class Something(object):
            def __unicode__(self):
                return '123'

        self.assertEqual(handler._decode(Something()), '123')

        class Something(object):
            def __str__(self):
                return '\xe3\x98\x80'

        self.assertEqual(handler._decode(Something()), '\\xe3\\x98\\x80')
