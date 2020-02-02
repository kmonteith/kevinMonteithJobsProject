import production
import os
import json


def test_number_entries():
    json_list = production.get_jobs()
    json_length = len(json_list)
    assert json_length > 100


def test_check_file_data():
    production.jobs_to_file()
    with open(os.path.join(production.ROOT_DIR, 'jobs.txt'), 'r') as f:
        data = json.load(f)
    assert any(item['id'] == '3f11116f-8230-481d-bfe9-c83e1a81d601' for item in data)