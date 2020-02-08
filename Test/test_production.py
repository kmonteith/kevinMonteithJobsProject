import production
import os
import json


def test_number_entries():
    json_list = production.get_jobs()
    json_length = len(json_list)
    assert json_length > 100


def test_table_exists():
    conn, cursor = production.open_db(os.path.join(production.ROOT_DIR, 'jobs.sqlite'))
    result = cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='jobs';''')
    assert result.arraysize > 0


def test_check_db_data():
    conn, cursor = production.open_db(os.path.join(production.ROOT_DIR, 'jobs.sqlite'))
    result = cursor.execute('''SELECT id FROM jobs WHERE id = "3f11116f-8230-481d-bfe9-c83e1a81d601"''')
    assert result.arraysize > 0
