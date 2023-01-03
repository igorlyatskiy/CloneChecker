import json
from urllib.request import Request, urlopen

from config import GITHUB_TOKEN


# Parses repos and checks that they exist.
class ParseRepos:
    def __init__(self, user, repo):
        self.user_name = user
        self.repo = repo

        self.success = self._parse_repos()

    # Checks that repo exists and returns students githubs.
    def _parse_repos(self):
        if 'https://github.com/' not in self.repo['repo']:
            self.repo['repo'] = 'https://github.com/' + self.user_name + '/' + self.repo['repo']
        if self.repo['repo'].find('github.com') != -1:
            if '/pull/' in self.repo['repo']:
                api_link = self.repo['repo'].replace('github.com', 'api.github.com/repos')
                api_link = api_link.replace('/pull/', '/pulls/')
                commits_str = api_link.find('/commits/')

                if commits_str != -1:
                    api_link = api_link[:commits_str]

                try:
                    request = Request(api_link)
                    request.add_header('Authorization', 'token %s' % GITHUB_TOKEN)
                    with urlopen(request) as url:
                        data = json.loads(url.read().decode())

                        self.repo['repo'] = data['head']['repo']['html_url']
                        self.repo['branch'] = data['head']['ref']
                except:
                    print('Could not find ', self.user_name, '\'s repo')
                    return False
            return self.is_success()
        else:
            return False

    def is_success(self):
        return self.repo
