import requests
import json


def get_jobs():
    get_url = "https://jobs.github.com/positions.json"
    request = requests.get(get_url)
    jobs_json = request.json()
    return jobs_json


def jobs_to_file():
    f = open("jobs.txt", "a")
    f.write(json.dumps(get_jobs()))
    f.close()


jobs_to_file()