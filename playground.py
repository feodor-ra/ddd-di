from functools import wraps
from typing import Any, Callable, ClassVar, Container, Generic, Literal, ParamSpec, Self, TypeVar, Protocol, Concatenate
from uuid import UUID, uuid4


# Это уровень бибилиоки

P = ParamSpec('P')
T = TypeVar('T')
M = TypeVar('M')
_ = TypeVar('_')


class Bind:
    def __init__(self, injected: Container[M]) -> None:
        self.injected = injected

    def __getattr__(self, name: str) -> Any:
        if name in self.injected:
            return getattr(self, f'get_{name}')()
        raise AttributeError('Module not included', name)

    def __enter__(self):
        return

    def __exit__(self, exc_type, exc_value, traceback) -> Literal[False]:
        ...


class Module(Generic[M, _]):
    binder: ClassVar[type[Bind]]

    def __init__(self, module: M, /, *other: M) -> None:
        self.injecting = (module, ) + other

    def __call__(self, fn: Callable[Concatenate[Any, P], T]) -> Callable[P, T]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            binder = self.binder(self.injecting)
            # А вот тут можно например сделать atomic, что бы все вызовы сервисной функции всегда проходил в транзакции
            with binder:
                return fn(binder, *args, **kwargs)
        return wrapper

    def __class_getitem__(cls, params: tuple[Any, type[Bind]]) -> Self:
        _, binder = params
        cls.binder = binder
        return super().__class_getitem__(params)


# Это уровень типов с протоколами (на уровне репозитория)

RepositoryModules = Literal['author', 'article']


class AuthorProtocol(Protocol):
    @staticmethod
    def get_name(external_id: int) -> str: ...


class AricleProtocol(Protocol):
    @staticmethod
    def publish(uuid: UUID) -> bool: ...


class BindProtocol(Protocol):
    author: AuthorProtocol
    article: AricleProtocol


# Это конкретная реазиция DI (тоже на уровне репозитория)
import author
import article

class BindRepository(Bind):
    def get_author(self) -> AuthorProtocol:
        # Тут можно при каждом вызове bind в runtime решать какой репозиторий нужно отдать
        # Например если это будет переключатся по фиче-флагу, который будет внешний (или тоже runtime переключаемый)

        # Кстати типизация по протоколу проверяет что бы все методы были в нужном модуле с нужной сигнатурой
        return author

    def get_article(self) -> AricleProtocol:
        return article


repository = Module[RepositoryModules, BindRepository]


# Это уже сервисный уровень
# Нужно импортировать только repository и BindProtocol

@repository('article', 'author')
def publish_article_if_exists_or_random(bind: BindProtocol, uuid: UUID | None = None) -> bool:
    if not uuid:
        uuid = uuid4()
    print(bind.author.get_name(42))
    return bind.article.publish(uuid)


@repository('author')
def smth(bind: BindProtocol, a: int, b: str) -> float:
    bind.article.publish(uuid4()) # Тут будет ошибка потому что модуль в репозитории не был указан явно


# При вызове bind удаляется и видна чистая сигнатура без этого аргумента
print(publish_article_if_exists_or_random(None))
