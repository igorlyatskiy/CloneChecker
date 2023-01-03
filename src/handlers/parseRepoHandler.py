# Counts amount of parsed and checked students repositories.
class ParseRepoHandler:
    def __init__(self, length):
        self.user_task_repos = {}
        self.iterator = 0
        self.length = length

    def __call__(self, r):
        self.iterator += 1
        print(f'Parsed: {self.iterator}/{self.length}')
        if r.result().success:
            self.user_task_repos[r.result().user_name] = r.result().repo