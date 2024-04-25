def get_name(external_id: int) -> str:
    if external_id == 42:
        return 'Имя'
    raise ValueError('Таких не знаю')
