
from service import publish_article_if_exists_or_random


# При вызове bind удаляется и видна чистая сигнатура без этого аргумента
print(publish_article_if_exists_or_random(None))
