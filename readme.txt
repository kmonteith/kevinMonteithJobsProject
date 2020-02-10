Name: Kevin Monteith

Requirements to install:
    pytest
    requests
    python-dateutil

Description of Project:
    Sprint Two:
        Added a function that converts string to timestamp so that future sprints will be easier

        create_jobs_table will create a table inside of the jobs.sqlite file with the proper structure for our data

        insert_data_to_db will insert one piece of data at a time to the database that was created in create_jobs_table

        jobs_to_db will use to the function get_jobs to retrieve the data then it will loop through each entry and call insert_data_to_db to insert them into our db


    Sprint One:
        The production file has two functions. The function get_jobs() retrieves the json data from github jobs by looping through the pages till there is no jobs on the json request.
        After it appends each request to the list it returns this list of dictionaries.
        The second function takes calls get_jobs() and writes the response to a file called jobs.txt

        The test_production file has two test functions. The function test_number_entries calls get_jobs then runs assert on the response to check if the length of the list is greater than 100.
        The second function calls jobs_to_file then opens the file and loads the data to a variable. Then it converts it to a list of dictionaries and I run assert and check if the list contains a
        list item with an item that I copied from the githubs website to ensure the data is correct.

Missing:
    As far as I know, nothing is missing.