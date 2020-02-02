import production
import pytest


def test_number_entries():
    json_list = production.get_jobs()
    json_length = len(json_list)
    assert json_length > 100