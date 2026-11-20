"""Verify that retired RC561 paths cannot regenerate invalid evidence."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent


def guarded_function(name, function):
    tree = ast.parse((ROOT / 'scripts' / name).read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
    module = ast.Module(body=[node], type_ignores=[])
    scope = {}
    exec(compile(module, name, 'exec'), scope)
    return scope[function]


class RetiredMetricPaths(unittest.TestCase):
    def test_invalid_reference_producers_refuse_before_file_access(self):
        for name in ('rc561_build_holdout.py', 'build_rc561_independent_ground_truth.py', 'benchmark_rc561_holdout.py'):
            with self.subTest(script=name), self.assertRaisesRegex(RuntimeError, 'invalid_rc561_references'):
                guarded_function(name, 'main')()

    def test_unreviewed_comparison_cannot_be_called_directly(self):
        with self.assertRaisesRegex(RuntimeError, 'invalid_rc561_references'):
            guarded_function('benchmark_rc561_holdout.py', 'evaluate_model')({}, {})

    def test_retired_label_module_has_no_import_time_directory_write(self):
        tree = ast.parse((ROOT / 'scripts/build_rc561_independent_ground_truth.py').read_text())
        for node in tree.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                function = node.value.func
                self.assertFalse(isinstance(function, ast.Attribute) and function.attr == 'mkdir')

    def test_checkpoint_writer_does_not_embed_hardcoded_success_metrics(self):
        text = (ROOT / 'scripts/wsp_export_winning_model.py').read_text()
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                keys = {k.value for k in node.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)}
                self.assertFalse(keys & {'legacy_retention', 'newstv_pills'})
        self.assertIn("'metricsStatus': 'provisional'", text)


if __name__ == '__main__':
    unittest.main()
