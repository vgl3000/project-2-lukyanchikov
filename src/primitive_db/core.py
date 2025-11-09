from .constants import VALID_TYPES
from .decorators import handle_db_errors, confirm_action, log_time, create_cacher
from .utils import save_metadata, load_table_data, save_table_data
import copy

cacher = create_cacher()

@handle_db_errors
def create_table(metadata, table_name, columns):
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')
    cols = [("ID", "int")] + columns
    for _, typ in cols:
        if typ not in VALID_TYPES:
            raise ValueError(f"Некорректный тип: {typ}")
    metadata[table_name] = { "columns": cols }
    save_metadata(metadata)
    return metadata

@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in metadata:
        raise KeyError(table_name)
    del metadata[table_name]
    save_metadata(metadata)
    # also remove data file
    save_table_data(table_name, [])
    return metadata

@handle_db_errors
def list_tables(metadata):
    return list(metadata.keys())

@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    if table_name not in metadata:
        raise KeyError(table_name)
    cols = metadata[table_name]["columns"]
    if len(values) != len(cols) - 1:
        raise ValueError("Количество значений не соответствует числу столбцов (без ID).")
    table = load_table_data(table_name)
    # determine new ID
    max_id = 0
    for r in table:
        try:
            if int(r.get("ID", 0)) > max_id:
                max_id = int(r.get("ID", 0))
        except Exception:
            pass
    new_id = max_id + 1
    record = {"ID": new_id}
    for (col_name, col_type), val in zip(cols[1:], values):
        # cast/check
        pytype = VALID_TYPES[col_type]
        if not isinstance(val, pytype):
            # allow int from float if no fraction
            if pytype is int and isinstance(val, float) and val.is_integer():
                val = int(val)
            else:
                raise ValueError(f"Неверный тип для {col_name}: ожидалось {col_type}")
        record[col_name] = val
    table.append(record)
    save_table_data(table_name, table)
    return table

@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    if where_clause is None or not where_clause:
        return table_data
    key, val = next(iter(where_clause.items()))
    res = [r for r in table_data if str(r.get(key)) == str(val)]
    return res

@handle_db_errors
def update(table_data, set_clause, where_clause):
    if not where_clause:
        raise ValueError("Условие where обязательно")
    key_w, val_w = next(iter(where_clause.items()))
    updated = 0
    for r in table_data:
        if str(r.get(key_w)) == str(val_w):
            for k, v in set_clause.items():
                r[k] = v
            updated += 1
    return table_data, updated

@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    if not where_clause:
        raise ValueError("Условие where обязательно")
    key_w, val_w = next(iter(where_clause.items()))
    new = [r for r in table_data if not (str(r.get(key_w)) == str(val_w))]
    deleted = len(table_data) - len(new)
    return new, deleted