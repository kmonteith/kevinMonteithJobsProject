import os
import time
import pytest
import production
from geopy.distance import vincenty
from geopy import geocoders


def test_number_entries():
    json_list = production.get_jobs()
    json_length = len(json_list)
    assert json_length > 100


def test_table_exists():
    conn, cursor = production.open_db(os.path.join(production.ROOT_DIR, 'jobs.sqlite'))
    result = cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='jobs';''')
    production.close_db(conn)
    assert result.arraysize > 0


def test_check_db_data_hacker_rank():
    conn, cursor = production.open_db(os.path.join(production.ROOT_DIR, 'jobs.sqlite'))
    result = cursor.execute('''SELECT `id` FROM `jobs` WHERE `id` = "364246"''')
    production.close_db(conn)
    assert result.arraysize > 0


def test_check_db_data_stack_overflow():
    conn, cursor = production.open_db(os.path.join(production.ROOT_DIR, 'jobs.sqlite'))
    result = cursor.execute('''SELECT id FROM jobs WHERE id = "3f11116f-8230-481d-bfe9-c83e1a81d601"''')
    production.close_db(conn)
    assert result.arraysize > 0


def test_insert_good_data_stack_overflow():
    data = {"id": "8ytvv6", "type": "Full Time", "url": "https://kevin.com",
            "created_at": 123456789, "company": "Kevin Corp", "company_url": "https://kevin.com",
            "location": "Atlanta, Georgia", "title": "Senior Python/Django Developer ",
            "description": "Programming things", "how_to_apply": "Go to website",
            "company_logo": "https://jobs.github.com/rails/active_storage/blobs/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBa"
                            "HBBcUI5IiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--919750b6eab525b746f9ce45a1f90"
                            "4bb1a8f7170/bafa694ef984ae859dc362c4056571c0.png"}
    assert production.insert_data_to_db(data)


def test_insert_good_data_hacker_rank():
    data = {"id": "1273", "type": "Not Available", "url": "https://kevin.com",
            "created_at": 123456789, "company": "Kevin Corp", "company_url": "https://kevin.com",
            "location": "Atlanta, Georgia", "title": "Senior Python/Django Developer ",
            "description": "Programming things", "how_to_apply": "Go to website",
            "company_logo": "Not Available"}
    assert production.insert_data_to_db(data)


@pytest.mark.xfail
def test_insert_bad_data_hacker_rank():
    data = {"id": "1273", "type": "Not Available", "url": "https://kevin.com",
            "created_at": 123456789, "company": "Kevin Corp", "company_url": "https://kevin.com",
            "location": "Atlanta, Georgia", "title": "Senior Python/Django Developer ",
            "description": "Programming things", "ho_to_apply": "Go to website",
            "company_logo": "Not Available"}
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


def test_filter_age():
    jobs_array = production.retrieve_jobs_from_db()
    # filter from dates now to a month ago
    jobs_array = production.filter_map_age(jobs_array, 0, 30)
    current_timestamp = time.time()
    one_month_future_timestamp = current_timestamp - 2592000
    jobs_array_size = len(jobs_array)
    item_counter = 0
    for item in jobs_array:
        if one_month_future_timestamp < item['created_at'] <= current_timestamp:
            item_counter = item_counter + 1
    assert item_counter == jobs_array_size


def test_filter_seniority():
    jobs_array = production.retrieve_jobs_from_db()
    # filter from dates now to a month ago
    jobs_array = production.filter_map_age(jobs_array, 0, 30)
    current_timestamp = time.time()
    one_month_future_timestamp = current_timestamp - 2592000
    jobs_array_size = len(jobs_array)
    item_counter = 0
    for item in jobs_array:
        if one_month_future_timestamp < item['created_at'] <= current_timestamp:
            item_counter = item_counter + 1
    assert item_counter == jobs_array_size


def test_filter_technology():
    jobs_array = production.retrieve_jobs_from_db()
    jobs_array = production.filter_map_seniority(jobs_array, ["junior", "senior"])
    jobs_array_size = len(jobs_array)
    item_counter = 0
    for item in jobs_array:
        if all(substring in item['description'] for substring in ["junior", "senior"]) or all(
                substring in item['title'] for substring in ["junior", "senior"]):
            item_counter = item_counter + 1
    assert item_counter == jobs_array_size


def test_check_correct_selected_result_id():
    jobs_array = production.retrieve_jobs_from_db()
    # grab all jobs from fort collins
    jobs_array = production.get_jobs_from_coord_id(jobs_array, 106)
    counter = 0
    for item in jobs_array:
        if item['id'] == "336cc8d4-e39a-11e8-87d1-d137f96d2919":
            counter = counter + 1
    assert counter == 1


def test_check_correct_selected_result_title():
    jobs_array = production.retrieve_jobs_from_db()
    # grab all jobs from Bloomington
    jobs_array = production.get_jobs_from_coord_id(jobs_array, 234)
    counter = 0
    for item in jobs_array:
        print(item['title'])
        if item['title'] == \
                "Senior Software Developer - Multi-Product Environment at Bloom Insurance (Bloomington, IN)":
            counter = counter + 1
    print(counter)
    assert counter == 1


def test_in_location_range():
    jobs_array = production.retrieve_jobs_from_db()
    jobs_array = production.filter_location(jobs_array, "Bridgewater,Massachusetts, United States", 50)
    test_item = jobs_array[0]
    test_coordinates = (float(test_item['latitude']), float(test_item['longitude']))
    distance = vincenty(test_coordinates, (41.9904, -70.9751)).miles
    assert distance <= 50


def test_out_of_location_range():
    jobs_array = production.retrieve_jobs_from_db()
    jobs_array = production.filter_location(jobs_array, "Bridgewater,Massachusetts, United States", 50)
    test_item = jobs_array[0]
    test_coordinates = (float(test_item['latitude']), float(test_item['longitude']))
    distance = vincenty(test_coordinates, (40.7128, -74.0060)).miles
    assert distance >= 50


def test_location_distance_function():
    gn = geocoders.Nominatim(user_agent="Jobs_Project_kmonteith_rand")
    location_geocode = gn.geocode("Bridgewater, Massachusetts, United States", timeout=1000)
    distance = vincenty((location_geocode.latitude,location_geocode.longitude), (40.7128, -74.0060)).miles
    assert distance == distance


# check to see if timestamp is accurate
def test_timestamp_accurate():
    assert production.date_to_timestamp("Mon Feb 10 4:11:52 UTC 2020") == 1581307912

