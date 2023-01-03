import os

from config import COMPARE_FILENAME, SCRIPT_PATH, TASK_NAME, BUNDLE_FILENAME, CONCAT_PATTERN
from src.helpers.helpers import concatenate_all
from src.taskRepos import get_user_task_repos
from src.userList import UserList

if __name__ == "__main__":
    repos = {}
    # Repo item example:
    # {
    #     'username1': {
    #         'repo': 'https://github.com/username1/repoName',
    #         'branch': 'task_name',
    #     }
    # }

    tasks = []

    # Get user list from files
    if COMPARE_FILENAME.endswith(".csv"):
        repos = get_user_task_repos(os.path.join(SCRIPT_PATH, 'scores', COMPARE_FILENAME), 2)
    elif COMPARE_FILENAME.endswith(".json"):
        repos = get_user_task_repos(os.path.join(SCRIPT_PATH, 'scores', COMPARE_FILENAME), 0)

    # Get task list from files
    user_list = UserList(repos, TASK_NAME, os.path.join('data'), BUNDLE_FILENAME)

    tasks = concatenate_all('data', repos, TASK_NAME, CONCAT_PATTERN)
    user_list.update_user_list(repos)
    user_list.cross_check()
