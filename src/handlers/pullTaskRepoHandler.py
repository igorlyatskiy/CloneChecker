# Counts amount of pulled students repositories.
class PullTaskRepoHandler:
    def __init__(self, length):
        self.users_tasks = {}
        self.iterator = 0
        self.length = length

    def __call__(self, r):
        self.iterator += 1
        print(f'Downloaded: {self.iterator}/{self.length}')
        if r.result().success:
            self.users_tasks[r.result().user_name] = r.result()
            print(f'Success for {r.result().user_name}')
