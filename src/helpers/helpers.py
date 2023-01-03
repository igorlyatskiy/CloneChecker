import os
import shutil
from pathlib import Path

from config import BUNDLE_FILENAME


def get_jaccard_sim(a, b):
    c = a.intersection(b)

    if len(a) + len(b) - len(c) == 0:
        return 0

    return float(len(c)) / (len(a) + len(b) - len(c))


def concat_files(dir_path, file_pattern):
    res = ''

    for path in Path(dir_path).rglob(file_pattern):
        with open(path, "r", encoding='utf-8', errors='ignore') as infile:
            res += infile.read()
    return res


def concatenate_all(path, repos, task_name, pattern):
    user_list = []
    for user in repos:
        current_path = os.path.join(path, user, task_name)
        node_modules = os.path.join(current_path, 'node_modules')
        doc_dir = os.path.join(current_path, 'doc')
        test_dir = os.path.join(current_path, 'test')
        extensions_dir = os.path.join(current_path, 'extensions')

        if os.path.exists(node_modules):
            shutil.rmtree(node_modules)

        if os.path.exists(doc_dir):
            shutil.rmtree(doc_dir)

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        if os.path.exists(extensions_dir):
            shutil.rmtree(extensions_dir)

        if os.path.exists(current_path):
            text = concat_files(current_path, pattern)
            if len(text) > 0:
                user_list.append(user)
                with open(os.path.join(current_path, BUNDLE_FILENAME), 'w', encoding='utf-8') as f:
                    f.write(text)
    return user_list


def detect_components(graph, key, detected):
    for v in graph[key]:
        if v not in detected:
            detected.add(v)
            detect_components(graph, v, detected)
