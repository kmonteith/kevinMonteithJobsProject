import requests
import json


def get_jobs():
    counter = 0
    jobs_json = []
    while True:
        get_url = "https://jobs.github.com/positions.json?page="+str(counter)
        request = requests.get(get_url)
        if len(request.json()) == 0:
            break
        jobs_json.extend(request.json())
        counter = counter+1
    return jobs_json


def jobs_to_file():
    f = open("jobs.txt", "a")
    f.write(json.dumps(get_jobs()))
    f.close()

