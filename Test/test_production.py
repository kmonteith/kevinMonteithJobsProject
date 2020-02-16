import pytest
import production
import os


def test_number_entries():
    json_list = production.get_jobs()
    json_length = len(json_list)
    assert json_length > 100


def test_table_exists():
    conn, cursor = production.open_db(os.path.join(production.ROOT_DIR, 'jobs.sqlite'))
    production.create_jobs_table()
    result = cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='jobs';''')
    production.close_db(conn)
    assert result.arraysize > 0


def test_check_db_data_hacker_rank():
    production.jobs_to_db()
    conn, cursor = production.open_db(os.path.join(production.ROOT_DIR, 'jobs.sqlite'))
    result = cursor.execute('''SELECT `id` FROM `jobs` WHERE `id` = "364246"''')
    production.close_db(conn)
    assert result.arraysize > 0


def test_check_db_data_stack_overflow():
    production.jobs_to_db()
    conn, cursor = production.open_db(os.path.join(production.ROOT_DIR, 'jobs.sqlite'))
    result = cursor.execute('''SELECT id FROM jobs WHERE id = "3f11116f-8230-481d-bfe9-c83e1a81d601"''')
    production.close_db(conn)
    assert result.arraysize > 0


def test_insert_good_data():
    conn, cursor = production.open_db(os.path.join(production.ROOT_DIR, 'jobs.sqlite'))
    data = {"id": "8ytvv6", "type": "Full Time", "url": "https://kevin.com",
            "created_at": 123456789, "company": "Kevin Corp", "company_url": "https://kevin.com",
            "location": "Atlanta, Georgia", "title": "Senior Python/Django Developer ",
            "description": "Programming things", "how_to_apply": "Go to website",
            "company_logo": "https://jobs.github.com/rails/active_storage/blobs/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBa"
                            "HBBcUI5IiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--919750b6eab525b746f9ce45a1f90"
                            "4bb1a8f7170/bafa694ef984ae859dc362c4056571c0.png"}
    assert production.insert_data_to_db(data)


@pytest.mark.xfail
def test_insert_bad_data():
    data = {"type": "Full Time", "url": "https://kevin.com",
            "created_at": "111111111", "company": "Kevin Corp", "company_url": "https://kevin.com",
            "location": "Atlanta, Georgia", "title": "Senior Python/Django Developer ",
            "description": "Programming things", "how_to_apply": "Go to website",
            "company_logo": "https://jobs.github.com/rails/active_storage/blobs/eyJfcmFpbHMiOns"
                            "ibWVzc2FnZSI6IkJBaHBBcUI5IiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--919750b6eab525"
                            "b746f9ce45a1f904bb1a8f7170/bafa694ef984ae859dc362c4056571c0.png"}
    assert production.insert_data_to_db(data)


# check to see if timestamp is accurate
def test_timestamp_accurate():
    assert production.date_to_timestamp("Mon Feb 10 4:11:52 UTC 2020") == 1581307912
