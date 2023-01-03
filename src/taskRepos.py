import csv
import json
from concurrent import futures

from config import CSV_DELIMITER
from src.handlers.parseRepoHandler import ParseRepoHandler
from src.parseRepos import ParseRepos


# Gets user task repos from files.
def get_user_task_repos(path, file_type):
    # .json
    if file_type == 0:
        with open(path) as json_file:
            return json.load(json_file)

    # .csv
    elif file_type == 2:
        repos = {}
        with open(path) as csv_file:
            reader = csv.reader(csv_file, delimiter=CSV_DELIMITER)
            repos = {row[1]: {'repo': row[0], 'branch': 'main'} for row in reader}

        repo_handler = ParseRepoHandler(len(repos))
        with futures.ProcessPoolExecutor() as pool:
            for user in repos:
                future_result = pool.submit(ParseRepos, user, repos[user])
                future_result.add_done_callback(repo_handler)

        return repo_handler.user_task_repos

    else:
        return {}
