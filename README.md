# Примитивная база данных (project-2_lukyanchikov)

Учебный проект — консольная "примитивная" СУБД, реализующая управление таблицами и CRUD-операции, с сохранением метаданных в JSON и данными таблиц в отдельных файлах.

## Установка

```bash
python3 -m pip install --upgrade --user pip
sudo apt install python3-poetry   # если poetry не установлен
poetry config virtualenvs.in-project true
make install
