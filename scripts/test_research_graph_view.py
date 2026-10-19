"""Check safe rendering and the read-only transport boundary."""
import unittest
from unittest.mock import Mock, patch
from research_graph_view import render_graph
from research_graph_server import Handler, Snapshot


class GraphTests(unittest.TestCase):
    def test_render_keeps_list_and_escapes_records(self):
        page=render_graph({'jobs':[], 'graphCompanion':True, 'error':'</script><img onerror=alert(1)>'})
        for value in ('id="rows"','id="completed"','id="graph-panel"','id="graph-layout"','const TOKEN=""'):
            self.assertIn(value,page)
        self.assertNotIn('</script><img',page)
        self.assertNotIn('<script src=',page)

    def handler(self,headers=None):
        handler=object.__new__(Handler)
        handler.headers=headers or {'Host':'127.0.0.1:8766'}
        handler.reply=Mock()
        handler.server=Mock()
        return handler

    def test_read_only(self):
        h=self.handler();h.do_POST()
        self.assertEqual(h.reply.call_args.args[0],405)
        h.server.snapshot.read.assert_not_called()

    def test_origin_and_host(self):
        for headers in ({'Host':'evil:8766'},{'Host':'127.0.0.1:8766','Origin':'https://evil.example'}):
            h=self.handler(headers);h.path='/api/state';h.do_GET()
            self.assertEqual(h.reply.call_args.args[0],403)
            h.server.snapshot.read.assert_not_called()

    def test_paths_and_failures(self):
        h=self.handler();h.path='/../control.json';h.do_GET()
        self.assertEqual(h.reply.call_args.args[0],404)
        h.path='/api/state';h.server.snapshot.read.side_effect=ValueError('private secret');h.do_GET()
        self.assertEqual(h.reply.call_args.args[0],503)
        self.assertNotIn('private secret',str(h.reply.call_args))

    def test_snapshot_cache_and_origin_guard(self):
        response=Mock()
        response.__enter__=Mock(return_value=response)
        response.__exit__=Mock(return_value=False)
        response.read.return_value=b'{"jobs":[],"current":null}'
        with patch('pathlib.Path.read_text',return_value='{"origin":"http://127.0.0.1:8765","token":"test-only"}'), patch('urllib.request.urlopen',return_value=response) as request:
            cache=Snapshot()
            self.assertTrue(cache.read()['graphCompanion'])
            cache.read()
            self.assertEqual(request.call_count,1)
        with patch('pathlib.Path.read_text',return_value='{"origin":"https://example.com","token":"test-only"}'), patch('urllib.request.urlopen') as request:
            with self.assertRaises(ValueError):Snapshot().read()
            request.assert_not_called()


if __name__=='__main__':
    unittest.main()
