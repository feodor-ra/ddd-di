from . import peewee

from typing import Literal, Protocol
from uuid import UUID
from di import Module, Bind


RepositoryModules = Literal['author', 'article']


class AuthorProtocol(Protocol):
    @staticmethod
    def get_name(external_id: int) -> str: ...


class ArticleProtocol(Protocol):
    @staticmethod
    def publish(uuid: UUID) -> bool: ...


class RepositoryProtocol(Protocol):
    author: AuthorProtocol
    article: ArticleProtocol



class Repository(Bind):
    def get_author_module(self) -> AuthorProtocol:
        # Тут можно при каждом вызове bind в runtime решать какой репозиторий нужно отдать
        # Например если это будет переключатся по фиче-флагу, который будет внешний (или тоже runtime переключаемый)

        # Кстати типизация по протоколу проверяет что бы все методы были в нужном модуле с нужной сигнатурой
        return peewee.author

    def get_article_module(self) -> ArticleProtocol:
        return peewee.article

    def __enter__(self):
        print('service running')
        return super().__enter__()


repository = Module[RepositoryModules, Repository]
