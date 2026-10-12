"""Report py2 str attributes in a Python 2 Data.fs, per class and attribute.

Usage: parts/<instance>/bin/interpreter py3migration/analyze_py2.py Data.fs out.json
"""
import io
import json
import pickle
import sys
from collections import defaultdict

from ZODB.FileStorage import FileStorage
from ZODB.utils import p64


class Stub:
    def __init__(self, *args, **kw):
        pass

    def __setstate__(self, state):
        self.__dict__['_state'] = state


def newobj(cls, *args):
    """copy_reg.__newobj__ replacement that also accepts stub classes."""
    if isinstance(cls, type) and issubclass(cls, Stub):
        obj = object.__new__(cls)
        obj.__dict__['_args'] = args
        return obj
    return cls.__new__(cls, *args)


def reconstructor(cls, base, state):
    """copy_reg._reconstructor replacement that also accepts stub classes."""
    if isinstance(cls, type) and issubclass(cls, Stub):
        return newobj(cls, state)
    return base.__new__(cls, state) if state is not None else object.__new__(cls)


class Py2Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == '__newobj__':
            return newobj
        if name == '_reconstructor':
            return reconstructor
        if module in ('__builtin__', 'copy_reg', 'builtins', 'copyreg'):
            try:
                return super().find_class(module, name)
            except Exception:
                pass
        return type(name, (Stub,), {'_module': module})

    def persistent_load(self, pid):
        return None


def classify(value):
    """Return ascii, utf8, binary or text8 (non-utf8 text) for py2 bytes."""
    try:
        value.decode('ascii')
        return 'ascii'
    except UnicodeDecodeError:
        pass
    try:
        value.decode('utf-8')
        return 'utf8'
    except UnicodeDecodeError:
        pass
    sample = value[:512]
    controls = sum(1 for b in sample if b < 9 or 13 < b < 32)
    return 'binary' if controls > 2 else 'text8'


def class_name(meta):
    if isinstance(meta, tuple):
        meta = meta[0]
    if isinstance(meta, tuple) and len(meta) == 2:
        return ' '.join(
            part.decode() if isinstance(part, bytes) else part for part in meta)
    if isinstance(meta, type):
        return '%s %s' % (getattr(meta, '_module', meta.__module__),
                          meta.__name__)
    return str(meta)[:80]


def walk(value, path, record, depth=0):
    if depth > 8:
        return
    if isinstance(value, bytes):
        record(path, classify(value), value)
    elif isinstance(value, dict):
        for k, v in value.items():
            if isinstance(k, bytes) and classify(k) not in ('ascii',):
                record(path + '{key}', classify(k), k)
            walk(v, path + '{}', record, depth + 1)
    elif isinstance(value, (list, tuple)):
        for v in value:
            walk(v, path + '[]', record, depth + 1)
    elif isinstance(value, Stub):
        walk(value.__dict__.get('_state'), path + '.', record, depth + 1)
        walk(value.__dict__.get('_args'), path + '()', record, depth + 1)


def main(path, out):
    storage = FileStorage(path, read_only=True)
    stats = defaultdict(lambda: defaultdict(int))
    samples = {}
    oid = p64(0)
    count = errors = 0
    while True:
        try:
            oid, tid, data, next_oid = storage.record_iternext(oid)
        except Exception:
            break
        count += 1
        try:
            unpickler = Py2Unpickler(io.BytesIO(data), encoding='bytes')
            cls = class_name(unpickler.load())
            state = unpickler.load()
        except Exception:
            errors += 1
        else:
            def record(attr_path, kind, value, cls=cls):
                key = '%s %s' % (cls, attr_path)
                stats[key][kind] += 1
                if kind != 'ascii':
                    samples.setdefault((key, kind), repr(value[:60]))

            if isinstance(state, dict):
                for attr, value in state.items():
                    if isinstance(attr, bytes):
                        attr = attr.decode('latin-1')
                    walk(value, attr, record)
            else:
                walk(state, '<state>', record)
        if count % 200000 == 0:
            print('scanned', count, file=sys.stderr)
        if next_oid is None:
            break
        oid = next_oid

    result = {
        'records': count,
        'unreadable': errors,
        'attributes': {
            key: dict(kinds, samples={
                kind: samples[(key, kind)]
                for kind in kinds if (key, kind) in samples})
            for key, kinds in stats.items()
            if set(kinds) - {'ascii'}
        },
    }
    with open(out, 'w') as f:
        json.dump(result, f, indent=1, sort_keys=True)
    print('records', count, 'unreadable', errors,
          'attributes with non-ascii', len(result['attributes']))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
