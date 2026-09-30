"""Module 15 - reference solutions (a miniature pytest)."""

from __future__ import annotations

import inspect

# ------------------------------------------------------------------ tier: B


def approx(a, b, rel: float = 1e-9, abs_tol: float = 1e-12) -> bool:
    return abs(a - b) <= max(abs_tol, rel * max(abs(a), abs(b)))


class SkipTest(Exception):
    pass


class raises:
    def __init__(self, exc_type):
        self.exc_type = exc_type
        self.value = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            raise AssertionError(
                f"DID NOT RAISE {self.exc_type.__name__}")
        if not issubclass(exc_type, self.exc_type):
            return False
        self.value = exc
        return True


def collect(module) -> list:
    return [obj for name, obj in vars(module).items()
            if name.startswith("test_") and callable(obj)]


# -------------------------------------------------------------- tier: I
class ExhaustedSideEffect(Exception):
    pass


class Spy:
    def __init__(self, result=None, side_effect=None):
        if result is not None and side_effect is not None:
            raise ValueError("use result or side_effect, not both")
        self.result = result
        self.side_effect = list(side_effect) if side_effect else None
        self.calls: list = []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        if self.side_effect is not None:
            if not self.side_effect:
                raise ExhaustedSideEffect("side_effect list exhausted")
            item = self.side_effect.pop(0)
            if isinstance(item, BaseException):
                raise item
            return item
        return self.result

    @property
    def call_count(self) -> int:
        return len(self.calls)

    def called_with(self, *args, **kwargs) -> bool:
        return (args, kwargs) in self.calls


def run(module) -> dict:
    report = {"passed": [], "failed": {}, "skipped": []}
    for test in collect(module):
        try:
            test()
        except SkipTest:
            report["skipped"].append(test.__name__)
        except Exception as exc:        # noqa: BLE001 - recorded, not raised
            report["failed"][test.__name__] = exc
        else:
            report["passed"].append(test.__name__)
    return report


# -------------------------------------------------------------- tier: Ind
class FixtureError(Exception):
    pass


FIXTURES: dict = {}


def fixture(fn):
    FIXTURES[fn.__name__] = fn
    return fn


def parametrize(argnames: str, cases):
    def decorator(fn):
        fn.parametrize = (argnames, list(cases))
        return fn
    return decorator


def _resolve_fixture(name, cache, teardowns):
    if name in cache:
        return cache[name]
    fn = FIXTURES.get(name)
    if fn is None:
        raise FixtureError(f"unknown fixture: {name!r}")
    kwargs = {p: _resolve_fixture(p, cache, teardowns)
              for p in inspect.signature(fn).parameters}
    produced = fn(**kwargs)
    if inspect.isgenerator(produced):
        value = next(produced)
        teardowns.append(produced)
    else:
        value = produced
    cache[name] = value
    return value


def _teardown_all(teardowns):
    for gen in reversed(teardowns):
        try:
            next(gen)
        except StopIteration:
            pass
        except Exception:               # teardown errors must not mask
            pass


def run_full(module) -> dict:
    report = {"passed": [], "failed": {}, "skipped": [], "errors": {}}
    for test in collect(module):
        spec = getattr(test, "parametrize", None)
        if spec is None:
            expansions = [(test.__name__, ())]
        else:
            expansions = [(f"{test.__name__}[case{i}]", case)
                          for i, case in enumerate(spec[1])]
        for name, case in expansions:
            cache: dict = {}
            teardowns: list = []
            try:
                kwargs = {}
                if spec is not None:
                    argnames = [a.strip() for a in spec[0].split(",")]
                    values = case if isinstance(case, tuple) else (case,)
                    kwargs = dict(zip(argnames, values))
                for param in inspect.signature(test).parameters:
                    if param in kwargs:
                        continue
                    kwargs[param] = _resolve_fixture(param, cache, teardowns)
                test(**kwargs)
            except FixtureError as exc:
                report["errors"][name] = exc
            except SkipTest:
                report["skipped"].append(name)
            except Exception as exc:    # noqa: BLE001 - recorded per case
                report["failed"][name] = exc
            else:
                report["passed"].append(name)
            finally:
                _teardown_all(teardowns)
    return report
