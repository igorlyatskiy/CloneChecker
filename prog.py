import git
import os
import matplotlib.pyplot as plt
import numpy as np
import glob

import networkx as nx

from bs4 import BeautifulSoup

import sys
sys.setrecursionlimit(10000)

DOWNLOAD_DATA = False
LIMIT = 0.5

from pathlib import Path


def concat_files(dir_path, file_pattern):
    res = ''

    for path in Path(dir_path).rglob(file_pattern):
      print(path)
      with open(path, "r") as infile:
          res += infile.read()
    return res

def concatenateAll(path, userList, taskName, pattenn):
  for user in userList:
    path = os.path.join(path, user, taskName)
    with open('clonecheckbundle.cc') as f:
      f.write(concat_files(path))


def detectComponents(graph, key, detected):
  for v in graph[key]:
    if not v in detected:
      detected.add(v)
      detectComponents(graph, v, detected)


def getPercent(value):
  return f'{value * 100}%'

def get_jaccard_sim(a, b):
    c = a.intersection(b)

    if len(a) + len(b) - len(c) == 0:
      return 0

    return float(len(c)) / (len(a) + len(b) - len(c))

def parseScores(path):
  pageText = open(path,'r').read()
  page = BeautifulSoup(pageText, 'html.parser')
  
  users = set()

  for user in page.find_all('tr'):
    if user.has_attr('data-row-key'):
      users.add(user.get('data-row-key'))

  return list(users)

class UserTask:
  def __init__(self, userName, taskName, localPath):
    self.userName = userName
    self.taskName = taskName
    self.localPath = localPath
    self.cash = dict()

    self.success = self._cloneProject()

  def _cloneProject(self):
    self.path = os.path.join(self.localPath, self.userName)
    self.fullPath = os.path.join(self.path, self.taskName)
    
    if not DOWNLOAD_DATA:
      return True

    try:
      os.makedirs(self.fullPath)
    except OSError:
      print ("Creation of the directory %s failed" % self.path)

    if not os.listdir(self.fullPath):
      try:
        git.Git(self.path).clone(f'https://github.com/{self.userName}/{self.taskName}.git')
      except git.exc.GitError:
        return False
    return True

  def getText(self, path):
    textPath = os.path.join(self.path, self.taskName, path)

    if not os.path.exists(textPath):
      return False
    
    if path in self.cash.keys():
      return self.cash[path]
    


    with open (textPath, "r", encoding='utf-8', errors='ignore') as f:
      self.cash[path] = f.read()
      return self.cash[path]

class UserList:
  def __init__(self, users, taskName, localPath, checkPaths, isPattern):
    self.taskName = taskName
    self.localPath = localPath
    self.checkPaths = checkPaths
    self.usersTasks = {}
    self.setCash = dict()
    self.isPattern = isPattern
    
    self._createUserTasks(users)

  def _createUserTasks(self, users):
    i = 0
    for user in users:
      task = UserTask(user, self.taskName, self.localPath)
      
      if task.success:
        self.usersTasks[user] = task
      
        print(f'Downloaded: {i + 1}/{len(users)}')
        i += 1
  
  def compare(self, userNameA, userNameB, path):
    userA = self.usersTasks[userNameA]
    userB = self.usersTasks[userNameB]

    if not userNameA + path in self.setCash:
      textA = userA.getText(path)
      if not textA:
        return False
      self.setCash[userNameA + path] = set(textA.split())
    
    if not userNameB + path in self.setCash:
      textB = userB.getText(path)
      if not textB:
        return False
      self.setCash[userNameB + path] = set(textB.split())

    return get_jaccard_sim(self.setCash[userNameA + path], self.setCash[userNameB + path])

  def cloneCheck(self, path, userA, userB, thresholdValue):
    res = self.compare(userA, userB, path)

    if not res:
      return False

    return res

  def createResultRow(self, path, userA, userB, cloneCheckResult):
    return f'Path: {path}\tUser: {userA} <-> {userB}\tSimilarity: {cloneCheckResult * 100}%'

  def crossCheck(self):
    values = []
    file = open('crosscheck.txt', 'w')

    graph = nx.Graph()

    i = 1
    
    for userA in self.usersTasks:
      print(f'{i/len(self.usersTasks)*100}%')
      self.checkUser(userA, values, graph, file)
      i += 1
      file.flush()

    file.close()

    plt.hist(values, bins=1000)
    plt.show()

    nx.write_graphml(graph, 'graph.graphml')

  
  def printComponents(self, graph):
    allComponents = set()


    for i in graph.keys():
      if not i in allComponents:
        localComponents = set()
        detectComponents(graph, i, localComponents)
        allComponents = allComponents.union(localComponents)
        print(localComponents)

  

  def checkUser(self, user, values, graph=None, file=None):
    nodes = set()

    hist = [0] * 101

    for taskPath in self.checkPaths:
      for userB in self.usersTasks:
        if user != userB:
          res = self.cloneCheck(taskPath, user, userB, LIMIT)

          if res != False:
            values.append(res * 100)
          if res >= LIMIT:
            line = self.createResultRow(taskPath, user, userB, res)

            if graph != None:
              if not user in graph.nodes:
                graph.add_node(user)
              
              if not userB in graph.nodes:
                graph.add_node(userB)

              graph.add_edge(user, userB)
              graph.add_edge(userB, user, label=f'{round(res * 100)}%')

            if file:
              file.write(line + '\n')

    return hist

if __name__ == "__main__":
  users = []

  for i in range(1, 23):
    users += parseScores(os.path.join('.', 'scores', f'{i}.html'))
  chechPaths = [
    os.path.join('src', 'index.js'),
  ]

  '''os.path.join('src', 'carbon-dating.js'),
    os.path.join('src', 'count-cats.js'),
    os.path.join('src', 'dream-team.js'),
    os.path.join('src', 'extended-repeater.js'),
    os.path.join('src', 'hanoi-tower.js'),
    os.path.join('src', 'recursive-depth.js'),
    os.path.join('src', 'transform-array.js'),
    os.path.join('src', 'vigenere-cipher.js'),
    os.path.join('src', 'what-season.js')'''

  #print(concat_files('data/sovaz1997/basic-js/src', '*.js'))