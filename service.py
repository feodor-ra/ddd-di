from uuid import UUID, uuid4
from repository import repository, Repo


@repository('article', 'author')
def publish_article_if_exists_or_random(bind: Repo, uuid: UUID | None = None) -> bool:
    if not uuid:
        uuid = uuid4()
    print(bind.author.get_name(42))
    return bind.article.publish(uuid)


@repository('author')
async def bar(bind: Repo, a: int, b: str) -> float:
    # Тут будет ошибка потому что модуль в репозитории не был указан явно
    bind.article.publish(uuid4())

