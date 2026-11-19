"""The hard spend stop and the prompt subset in scripts/panel_run.py. Fake transport only, no network."""
import contextlib
import gc
import http.client
import http.server
import importlib.util
import io
import json
import os
import pathlib
import tempfile
import threading
import unittest
import warnings
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("panel_run", pathlib.Path(__file__).parents[1] / "scripts/panel_run.py")
panel = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(panel)

QUESTIONS = """| ID | Question | Page |
| --- | --- | --- |
| bq-001 | How much does handoff software cost? | /pricing |
| bq-002 | How long is setup? | /setup |
| bq-003 | Who integrates with Slack? | /integrations |
"""
GOOD = {"choices": [{"message": {"content": "Contoso costs $10. See https://contoso.example/pricing"}}]}
ENV = {"OPENAI_API_KEY": "fake", "PERPLEXITY_API_KEY": "fake"}


class SpendStopTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = pathlib.Path(self._tmp.name)
        self.qfile = self.tmp / "questions.md"
        self.qfile.write_text(QUESTIONS, encoding="utf-8")
        self.out = self.tmp / "brain" / "search" / "panel-runs" / "out"
        self.transport = panel._fake([GOOD])

    def tearDown(self):
        self._tmp.cleanup()

    def run_cli(self, *extra, env=ENV):
        argv = ["--questions", str(self.qfile), "--runs", "2", "--root", str(self.tmp), "--out", str(self.out),
                "--company", "Contoso", "--engines", "chatgpt,perplexity", "--date", "2026-11-18", *extra]
        args = panel.build_parser().parse_args(argv)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            code = panel.run_main(args, env, self.transport)
        return code, err.getvalue()

    def test_over_the_cap_makes_zero_calls_and_exits_non_zero(self):
        # 3 prompts x 2 engines x 2 runs x 2 (retry) = 24 worst-case calls
        code, err = self.run_cli("--max-calls", "23")
        self.assertEqual(code, panel.EXIT_OVER_CAP)
        self.assertEqual(self.transport.calls, [])
        self.assertIn("24", err)
        self.assertFalse(self.out.exists())

    def test_no_cap_given_makes_zero_calls(self):
        code, _ = self.run_cli()
        self.assertEqual(code, panel.EXIT_OVER_CAP)
        self.assertEqual(self.transport.calls, [])

    def test_at_the_cap_runs(self):
        code, _ = self.run_cli("--max-calls", "24")
        self.assertEqual(code, panel.EXIT_OK)
        self.assertEqual(len(self.transport.calls), 12)  # no retries needed with good answers

    def test_prompt_subset_runs_only_named_prompts(self):
        code, _ = self.run_cli("--prompts", "bq-002", "--max-calls", "8")
        self.assertEqual(code, panel.EXIT_OK)
        self.assertEqual(len(self.transport.calls), 4)
        self.assertTrue(all("setup" in str(body) and "cost" not in str(body) for _, _, body in self.transport.calls))

    def test_prompt_subset_rejects_unknown_id_with_no_call(self):
        code, err = self.run_cli("--prompts", "bq-002,bq-999", "--max-calls", "100")
        self.assertEqual(code, panel.EXIT_INPUT)
        self.assertIn("bq-999", err)
        self.assertEqual(self.transport.calls, [])

    def test_prompt_flag_with_no_ids_is_rejected_with_no_call(self):
        code, err = self.run_cli("--prompts", " , ", "--max-calls", "100")
        self.assertEqual(code, panel.EXIT_INPUT)
        self.assertEqual(self.transport.calls, [])

    def test_empty_prompt_selection_exits_2_even_with_no_keys(self):
        code, _ = self.run_cli("--prompts", " , ", "--max-calls", "100", env={})
        self.assertEqual(code, panel.EXIT_INPUT)
        self.assertEqual(self.transport.calls, [])


class _Redirecting(http.server.BaseHTTPRequestHandler):
    requests = []
    status, location = 307, "/next"

    def _answer(self):
        type(self).requests.append((self.command, self.path))
        if self.path == "/v1":
            self.send_response(self.status)
            self.send_header("Location", self.location)
            self.send_header("Content-Length", "0")
            self.end_headers()
        else:
            body = json.dumps(GOOD).encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    do_POST = do_GET = _answer

    def log_message(self, *args):
        pass


class RedirectTests(unittest.TestCase):
    def redirect_once(self, status, location):
        """One counted call against a local server that answers with a redirect; return (error, warnings)."""
        _Redirecting.requests, _Redirecting.status, _Redirecting.location = [], status, location
        server = http.server.HTTPServer(("127.0.0.1", 0), _Redirecting)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{server.server_port}/v1"
        category, closes, original_close = None, [], http.client.HTTPResponse.close

        def counting_close(response):
            closes.append(response.status)
            original_close(response)
        try:
            with warnings.catch_warnings(record=True) as seen, \
                    patch.dict(os.environ, {"no_proxy": "127.0.0.1", "NO_PROXY": "127.0.0.1"}), \
                    patch.object(http.client.HTTPResponse, "close", counting_close):
                warnings.simplefilter("always", ResourceWarning)
                gc.disable()  # a close done only by the garbage collector does not count
                try:
                    panel.call_with_retry(panel.http_post, url, {}, {})
                except panel.PanelError as err:  # anything else aborts the panel and fails the test
                    category = err.category
                closed_on_return = list(closes)
                gc.enable()
                gc.collect()
        finally:
            gc.enable()
            server.shutdown()
            server.server_close()
        return category, closed_on_return, [w for w in seen if issubclass(w.category, ResourceWarning)]

    def test_redirect_is_one_failed_request_not_retried(self):
        for status, location in ((307, "/next"), (302, "/next"), (302, "http://[")):
            with self.subTest(status=status, location=location):
                category, closed, leaked = self.redirect_once(status, location)
                self.assertEqual(category, "redirect")
                self.assertIn(status, closed, "the 3xx response was not closed before the call returned")
                self.assertEqual(_Redirecting.requests, [("POST", "/v1")])
                self.assertEqual(leaked, [], "the 3xx response was left open")


if __name__ == "__main__":
    unittest.main()
