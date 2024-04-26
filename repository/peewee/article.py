from random import random
from uuid import UUID


def publish(uuid: UUID) -> bool:
    return random() > 0.5
