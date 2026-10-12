"""Report bytes values and mojibake strings in a converted (Python 3) Data.fs.

Usage: parts/<instance>/bin/interpreter py3migration/scan_py3.py Data.fs
"""
import io
import pickle
import re
import sys
from collections import Counter

from ZODB.FileStorage import FileStorage
from ZODB.utils import p64

MOJIBAKE = re.compile('[Â-Å][\u0080-¿]')


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


class StubUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == '__newobj__':
            return newobj
        if name == '_reconstructor':
            return reconstructor
        if module in ('builtins', 'copyreg', 'datetime', 'collections'):
            try:
                return super().find_class(module, name)
            except Exception:
                pass
        return type(name, (Stub,), {'_module': module})

    def persistent_load(self, pid):
        return None


def class_name(meta):
    if isinstance(meta, tuple):
        meta = meta[0]
    if isinstance(meta, type):
        return '%s %s' % (getattr(meta, '_module', meta.__module__),
                          meta.__name__)
    return str(meta)[:80]


def main(path):
    storage = FileStorage(path, read_only=True)
    found = Counter()
    samples = {}

    def walk(value, key, depth=0):
        if depth > 8:
            return
        if isinstance(value, bytes):
            found[('bytes', key)] += 1
            samples.setdefault(('bytes', key), repr(value[:50]))
        elif isinstance(value, str):
            if MOJIBAKE.search(value):
                found[('mojibake', key)] += 1
                samples.setdefault(('mojibake', key), value[:80])
        elif isinstance(value, dict):
            for v in value.values():
                walk(v, key + '{}', depth + 1)
        elif isinstance(value, (list, tuple)):
            for v in value:
                walk(v, key + '[]', depth + 1)
        elif isinstance(value, Stub):
            walk(value.__dict__.get('_state'), key + '.', depth + 1)
            walk(value.__dict__.get('_args'), key + '()', depth + 1)

    oid = p64(0)
    count = errors = 0
    while True:
        try:
            oid, tid, data, next_oid = storage.record_iternext(oid)
        except Exception:
            break
        count += 1
        try:
            unpickler = StubUnpickler(io.BytesIO(data))
            cls = class_name(unpickler.load())
            state = unpickler.load()
        except Exception:
            errors += 1
        else:
            if isinstance(state, dict):
                for attr, value in state.items():
                    walk(value, '%s %s' % (cls, attr))
            else:
                walk(state, '%s <state>' % cls)
        if next_oid is None:
            break
        oid = next_oid

    print('records', count, 'unreadable', errors)
    for kind in ('mojibake', 'bytes'):
        print('--- %s' % kind)
        rows = [(n, key) for (k, key), n in found.items() if k == kind]
        for n, key in sorted(rows, reverse=True):
            print('%7d %s | %s' % (n, key, samples[(kind, key)]))


if __name__ == '__main__':
    main(sys.argv[1])
