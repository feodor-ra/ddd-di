from functools import wraps
from typing import Any, Callable, ClassVar, Container, Generic, Literal, ParamSpec, Self, TypeVar, Protocol
from asyncio import iscoroutine

P = ParamSpec('P')
T = TypeVar('T')
M = TypeVar('M')
B = TypeVar('B', bound='Bind')

class Bind:
    def __init__(self, injected: Container[M]) -> None:
        self.injected = injected

    def __getattr__(self, name: str) -> Any:
        if name in self.injected:
            return getattr(self, f'get_{name}_module')()
        raise AttributeError('Module not included', name)

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, traceback) -> Literal[False]:
        ...

    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc_value, traceback) -> Literal[False]:
        ...


class Function(Protocol[B, P, T]):
    def __call__(self, bind: B, *args: P.args, **kwds: P.kwargs) -> T:
        ...


class Module(Generic[M, B]):
    binder: ClassVar[type[B]]

    def __init__(self, module: M, /, *other: M) -> None:
        self.injecting = (module, ) + other

    def __call__(self, fn: Function[B, P, T]) -> Callable[P, T]:
        if getattr(fn, '__bind__', False):
            raise RuntimeError(f'{fn.__name__} already has injected')

        @wraps(fn)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            binder = self.binder(self.injecting)
            # А вот тут можно например сделать atomic, что бы все вызовы сервисной функции всегда проходил в транзакции
            with binder:
                return fn(binder, *args, **kwargs)

        @wraps(fn)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            binder = self.binder(self.injecting)
            async with binder:
                return await fn(binder, *args, **kwargs)

        wrapper = async_wrapper if iscoroutine(fn) else sync_wrapper
        wrapper.__bind__ = True
        return wrapper

    def __class_getitem__(cls, params: tuple[Any, type[Bind]]) -> Self:
        _, binder = params
        cls.binder = binder
        return super().__class_getitem__(params)
