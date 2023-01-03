import csv
from concurrent import futures

import networkx as nx
from matplotlib import pyplot as plt

from config import UPPER_LIMIT, THRESHOLD
from src.handlers.pullTaskRepoHandler import PullTaskRepoHandler
from src.helpers.helpers import get_jaccard_sim, detect_components
from src.userTask import UserTask


class UserList:
    def __init__(self, repos, task_name, local_path, check_path):
        self.local_path = local_path
        self.check_path = check_path
        self.task_name = task_name
        self.users_tasks = {}
        self.set_cash = dict()

        self._create_user_tasks(repos)

    def update_user_list(self, repos):
        for user in list(self.users_tasks):
            if user not in repos:
                del self.users_tasks[user]

    def _create_user_tasks(self, repos):
        tasks_handler = PullTaskRepoHandler(len(repos))
        with futures.ProcessPoolExecutor() as pool:
            for user in repos:
                future_result = pool.submit(UserTask, user, repos[user], self.task_name, self.local_path,
                                            self.check_path)
                future_result.add_done_callback(tasks_handler)
        self.users_tasks = tasks_handler.users_tasks

    def compare(self, user_name_a, user_name_b):
        user_a = self.users_tasks[user_name_a]
        user_b = self.users_tasks[user_name_b]

        if user_name_a + self.check_path not in self.set_cash:
            text_a = user_a.get_text()
            if not text_a:
                return False
            self.set_cash[user_name_a + self.check_path] = set(text_a.split())

        if user_name_b + self.check_path not in self.set_cash:
            text_b = user_b.get_text()
            if not text_b:
                return False
            self.set_cash[user_name_b + self.check_path] = set(text_b.split())

        return get_jaccard_sim(self.set_cash[user_name_a + self.check_path],
                               self.set_cash[user_name_b + self.check_path])

    def clone_check(self, user_a, user_b, threshold_value):
        res = self.compare(user_a, user_b)

        if res is None:
            return False

        return res

    def create_result_row(self, user_a, user_b, clone_check_result):
        return f'Path: {self.check_path}\tUser: {user_a} <-> {user_b}\tSimilarity: {clone_check_result * 100}%'

    def check_by_value(self, value):
        res = []

        with open('new-Function.txt', 'w') as f:
            for user in self.users_tasks:
                if self.users_tasks[user].check(value):
                    res.append(user)
                    f.writelines([f'User: {user}\n\n', self.users_tasks[user].get_text()])
                    f.write('\n\n\n------------------------------------------------------\n\n\n')

        return res

    def cross_check(self):
        values = []
        file = open('crosscheck.txt', 'w')

        graph = nx.Graph()
        graph_csv = dict()

        i = 1

        print("Processing cross-check...")
        for user_a in self.users_tasks:
            print(f'{i / len(self.users_tasks) * 100}%')
            self.check_user(user_a, values, graph, graph_csv, file)
            i += 1
            file.flush()

        file.close()

        plt.hist(values, bins=1000)
        plt.show()

        nx.write_graphml(graph, 'graph.graphml')

        with open('results.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(['Number', 'User', 'Url', 'Data'])

            i = 1

            order = self.get_components(graph_csv)

            for component in order:
                for node in component:
                    line = [i, node, self.users_tasks[node].url_to_file]

                    data = ''
                    for user in graph_csv[node]:
                        data += f'{user}: {graph_csv[node][user]}; '
                    i += 1
                    line.append(data)
                    writer.writerow(line)
                writer.writerow('')

    def get_components(self, graph):
        all_components = set()
        res = []

        for i in list(graph):
            if i not in all_components:
                local_components = set()
                detect_components(graph, i, local_components)
                all_components = all_components.union(local_components)
                res.append(local_components)
        return res

    def check_user(self, user, values, graph=None, graph_csv=None, file=None):
        nodes = set()
        hist = [0] * 101

        for user_b in self.users_tasks:
            if user != user_b:
                res = self.clone_check(user, user_b, UPPER_LIMIT)

                if res:
                    values.append(res * 100)
                if THRESHOLD <= res <= UPPER_LIMIT:
                    line = self.create_result_row(user, user_b, res)

                    if graph != None:
                        if user not in graph.nodes:
                            graph.add_node(user, label=user)
                            graph.nodes[user]['xlink:href'] = self.users_tasks[user].url_to_file
                            graph_csv[user] = dict()

                        if user_b not in graph.nodes:
                            graph.add_node(user_b, label=user_b)
                            graph.nodes[user_b]['xlink:href'] = self.users_tasks[user_b].url_to_file
                            graph_csv[user_b] = dict()

                        graph.add_edge(user, user_b)
                        label = f'{round(res * 100)}%'
                        graph.add_edge(user_b, user, label=label)

                        graph_csv[user][user_b] = label
                        graph_csv[user_b][user] = label

                    if file:
                        file.write(line + '\n')

        return hist
