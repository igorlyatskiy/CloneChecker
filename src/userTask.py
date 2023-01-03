import os
import re

import git

from config import DOWNLOAD_DATA, GITHUB_TOKEN


class UserTask:
    def __init__(self, user_name, task_repo, task_name, local_path, check_path):
        self.user_name = user_name
        self.task_name = task_name
        self.task_repo = task_repo
        self.check_path = check_path
        self.local_path = local_path
        self.cash = None

        self.success = self._clone_project()

    def _clone_project(self):
        self.download_path = os.path.join(self.local_path, self.user_name, self.task_name)
        self.path_to_file = os.path.join(self.download_path, self.check_path)

        self.url_to_file = f'{self.task_repo["repo"]}/blob/{self.task_repo["branch"]}/{self.check_path}'

        if not DOWNLOAD_DATA:
            return self.is_success()

        try:
            os.makedirs(self.download_path)
        except OSError:
            print("Creation of the directory %s failed" % self.download_path)

        if not os.listdir(self.download_path):
            try:
                if len(GITHUB_TOKEN) > 1:
                    self.task_repo['repo'] = self.task_repo['repo'].replace('github.com',
                                                                            GITHUB_TOKEN + ':x-oauth-basic@github.com')
                git.Repo.clone_from(self.task_repo['repo'], self.download_path, branch=self.task_repo['branch'])
            except git.exc.GitError:
                print("Cloning from git failed")
                return False

        return self.is_success()

    def is_success(self):
        # path_to_file
        return os.path.exists(self.download_path)

    def get_text(self):
        if self.cash:
            return self.cash

        with open(self.path_to_file, "r", encoding='utf-8', errors='ignore') as f:
            self.cash = f.read()
            return self.cash

    def check(self, value):
        text = self.get_text()

        regexp = re.compile(value)
        return regexp.search(text)
