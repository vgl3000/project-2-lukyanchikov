import shlex
from .utils import load_metadata, save_metadata, load_table_data, save_table_data
from .core import create_table, drop_table, list_tables, insert, select, update, delete
from .parser import parse_command, parse_where, parse_set, parse_values
from .decorators import create_cacher
from prettytable import PrettyTable

def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <table> values (<v1>, ...) - вставить запись")
    print("<command> select from <table> [where <col>=<value>] - выбрать")
    print("<command> update <table> set <col>=<value> where <col>=<value> - обновить")
    print("<command> delete from <table> where <col>=<value> - удалить")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def run():
    print("DB project is running!")
    while True:
        metadata = load_metadata()
        try:
            user_input = input(">>> Введите команду: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input.strip():
            continue
        tokens = parse_command(user_input)
        cmd = tokens[0].lower()
        if cmd == "exit":
            break
        if cmd == "help":
            print_help()
            continue
        if cmd == "create_table":
            if len(tokens) < 3:
                print("Некорректная команда. Использование: create_table <name> <col:typ> ...")
                continue
            table = tokens[1]
            cols = []
            for c in tokens[2:]:
                if ":" not in c:
                    print(f"Некорректное значение: {c}. Попробуйте снова.")
                    cols = None
                    break
                name, typ = c.split(":",1)
                cols.append((name, typ))
            if cols is None:
                continue
            try:
                create_table(metadata, table, cols)
                print(f'Таблица "{table}" успешно создана со столбцами: ' + ", ".join([f"{n}:{t}" for n,t in [("ID","int")] + cols]))
            except Exception as e:
                print(e)
            continue
        if cmd == "list_tables":
            mts = list_tables(metadata)
            if mts:
                for t in mts:
                    print("- " + t)
            else:
                print("Таблиц нет.")
            continue
        if cmd == "drop_table":
            if len(tokens) != 2:
                print("Использование: drop_table <name>")
                continue
            try:
                drop_table(metadata, tokens[1])
                print(f'Таблица "{tokens[1]}" успешно удалена.')
            except Exception as e:
                print(e)
            continue
        # insert
        if cmd == "insert":
            # expect: insert into table values (...)
            if len(tokens) < 4 or tokens[1].lower() != "into":
                print("Некорректная команда insert.")
                continue
            table = tokens[2]
            values = parse_values(tokens[3:])
            try:
                insert(metadata, table, values)
                print(f"Запись успешно добавлена в таблицу "{table}".")
            except Exception as e:
                print(e)
            continue
        # select
        if cmd == "select":
            # select from <table> [where ...]
            if len(tokens) < 3 or tokens[1].lower() != "from":
                print("Некорректная команда select.")
                continue
            table = tokens[2]
            where = None
            if "where" in [t.lower() for t in tokens]:
                idx = [t.lower() for t in tokens].index("where")
                where = parse_where(tokens[idx+1:])
            data = load_table_data(table)
            res = select(data, where)
            # print via prettytable
            if res:
                cols = res[0].keys()
                pt = PrettyTable()
                pt.field_names = list(cols)
                for r in res:
                    pt.add_row([r.get(c) for c in cols])
                print(pt)
            else:
                print("Ничего не найдено.")
            continue
        # update
        if cmd == "update":
            # update <table> set <col>=<val> where <col>=<val>
            if len(tokens) < 6:
                print("Некорректная команда update.")
                continue
            table = tokens[1]
            if "set" not in [t.lower() for t in tokens] or "where" not in [t.lower() for t in tokens]:
                print("Некорректная команда update.")
                continue
            set_idx = [t.lower() for t in tokens].index("set")
            where_idx = [t.lower() for t in tokens].index("where")
            set_clause = parse_set(tokens[set_idx+1:where_idx])
            where_clause = parse_where(tokens[where_idx+1:])
            data = load_table_data(table)
            new_data, updated = update(data, set_clause, where_clause)
            save_table_data(table, new_data)
            print(f"Обновлено записей: {updated}")
            continue
        # delete
        if cmd == "delete":
            # delete from <table> where <col>=<val>
            if len(tokens) < 5 or tokens[1].lower() != "from":
                print("Некорректная команда delete.")
                continue
            table = tokens[2]
            if "where" not in [t.lower() for t in tokens]:
                print("Некорректная команда delete.")
                continue
            where_idx = [t.lower() for t in tokens].index("where")
            where_clause = parse_where(tokens[where_idx+1:])
            data = load_table_data(table)
            new_data, deleted = delete(data, where_clause)
            save_table_data(table, new_data)
            print(f"Удалено записей: {deleted}")
            continue
        if cmd == "info":
            if len(tokens) != 2:
                print("Использование: info <table>")
                continue
            table = tokens[1]
            metadata = load_metadata()
            if table not in metadata:
                print("Таблица не найдена.")
                continue
            cols = metadata[table]["columns"]
            data = load_table_data(table)
            print(f"Таблица: {table}")
            print("Столбцы: " + ", ".join([f"{n}:{t}" for n,t in cols]))
            print("Количество записей: " + str(len(data)))
            continue
        print(f"Функции {cmd} нет. Попробуйте снова.")