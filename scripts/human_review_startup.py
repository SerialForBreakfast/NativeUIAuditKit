"""Isolated, bounded Qt startup check used by every supported editor CLI launch."""
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parent.parent
VERSION = 'human-review-qt-startup-v1'
PREFIX = 'NUIAK_QT_PROBE='


def diagnose(message):
    if 'unsupported_explicit_qt_platform:' in message:
        return 'platform_configuration', 'Remove the unexpected QT_QPA_PLATFORM override for a native macOS launch; do not silently fall back to offscreen.'
    if 'Library not loaded:' in message:
        return 'framework_lookup', 'Inspect the named framework and the verified cache lib link; do not reinstall Qt or change global DYLD settings.'
    if 'changed_qt_' in message or 'qt_framework_link_collision' in message:
        return 'cache_integrity', 'Preserve the reported cache and inspect its exact changed bytes/link; do not delete the wheel or retry unchanged.'
    if 'unsupported_editor_version' in message or 'distribution was not found' in message or 'No module named' in message:
        return 'environment', 'Use the existing project .venv-review interpreter; inspect the pinned dependency before considering any installation.'
    return 'qt_initialization', 'Use this receipt and child stderr to identify the failing layer; do not restart the current annotator or retry blindly.'


def child(runtime):
    result = dict(version=VERSION, passed=False, stage='configure', interpreter=sys.executable)
    try:
        import human_review_editor as editor
        editor.configure(runtime)
        from qtpy import QtCore, QtWidgets
        result['versions'] = {p:importlib.metadata.version(p) for p in ('labelme','PyQt5','PyQt5-Qt5','QtPy')}
        result['pluginPaths'] = QtCore.QCoreApplication.libraryPaths()
        platform = os.environ.get('QT_QPA_PLATFORM','cocoa' if sys.platform=='darwin' else 'xcb')
        result['platform'] = platform
        if platform not in ('cocoa','offscreen','minimal','xcb'):
            raise ValueError('unsupported_explicit_qt_platform:'+platform)
        suffix = '.dylib' if sys.platform=='darwin' else '.so'
        plugins = [Path(p)/'platforms'/('libq'+platform+suffix) for p in result['pluginPaths']]
        plugin = next((p for p in plugins if p.is_file()),None)
        result['stage'] = 'platform-library'
        if plugin is None: raise ValueError('missing_platform_plugin:'+platform)
        result['plugin'] = str(plugin)
        loader = QtCore.QPluginLoader(str(plugin))
        if not loader.load(): raise ValueError(loader.errorString())
        result['stage'] = 'application'
        app = QtWidgets.QApplication(['nuiak-qt-probe'])
        if app.platformName() != platform: raise ValueError('unexpected_effective_platform:'+app.platformName())
        # Exercise widget allocation, but show no window and open no annotation.
        widget = QtWidgets.QWidget(); app.processEvents(); widget.close()
        result.update(passed=True,stage='ready')
        app.quit()
    except Exception as error:
        message = str(error)
        category,action = diagnose(message)
        result.update(error=message,category=category,nextAction=action)
    print(PREFIX+json.dumps(result,sort_keys=True),flush=True)
    return 0 if result['passed'] else 2


def preflight(runtime, *, timeout=20):
    """No Qt imports in this parent; native crashes/timeouts cannot abort it."""
    from human_annotation_review import local, require, write
    runtime = local(runtime)
    require(runtime.is_relative_to(ROOT/'.build') or runtime.is_relative_to(ROOT/'reports/work'), 'invalid_editor_runtime')
    root = runtime/'startup'/uuid.uuid4().hex
    require(not any(p.is_symlink() for p in (root,*root.parents)), 'symlink_startup_output')
    root.mkdir(parents=True)
    tmp = runtime/'tmp'; tmp.mkdir(parents=True,exist_ok=True)
    env = {**os.environ,'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':str(tmp)}
    command = [sys.executable,str(Path(__file__).resolve()),'--probe',str(runtime)]
    started = time.monotonic(); result = None; code = None
    with (root/'stdout.log').open('x') as out, (root/'stderr.log').open('x') as err:
        try:
            completed = subprocess.run(command,cwd=ROOT,env=env,stdout=out,stderr=err,timeout=timeout,check=False)
            code = completed.returncode
        except subprocess.TimeoutExpired:
            result = dict(passed=False,category='timeout',error='qt_probe_timeout',nextAction='Inspect the child logs and dependency residency. Do not repeat the unchanged launch.')
        except OSError as error:
            result = dict(passed=False,category='spawn',error=str(error),nextAction='Check the recorded interpreter and process execution context.')
    if result is None:
        with (root/'stdout.log').open('rb') as stream:
            stream.seek(max(0,os.fstat(stream.fileno()).st_size-65536)); tail=stream.read().decode('utf-8',errors='replace')
        try:
            records=[line[len(PREFIX):] for line in tail.splitlines() if line.startswith(PREFIX)]
            require(len(records)==1,'missing_or_duplicate_probe_receipt')
            result=json.loads(records[0])
            require(isinstance(result,dict),'invalid_probe_receipt')
            require(result.get('version')==VERSION and type(result.get('passed')) is bool,'invalid_probe_receipt')
            require((code==0) == result['passed'],'inconsistent_probe_exit')
        except (ValueError,TypeError):
            result=dict(passed=False,category='native_exit' if code else 'invalid_receipt',
                        error='probe_did_not_complete',nextAction='Inspect child stderr and exit code; plugin discovery alone is not readiness.')
    result.update(version=VERSION,exitCode=code,elapsedSeconds=time.monotonic()-started,
                  interpreter=sys.executable,timeoutSeconds=timeout,receipt=str(root/'receipt.json'),
                  stdout=str(root/'stdout.log'),stderr=str(root/'stderr.log'))
    write(root/'receipt.json',result)
    return result


if __name__=='__main__':
    if len(sys.argv)!=3 or sys.argv[1]!='--probe': raise SystemExit('Internal probe: use human_review_editor.py --doctor')
    raise SystemExit(child(sys.argv[2]))
