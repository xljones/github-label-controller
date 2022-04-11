import logging
import github

class GithubAuthenticator:
    _authenticated = False
    _github_login = []
    _rate_limit = []
    _username = []

    def __init__(self, github_token):
        self._github_login = github.Github(github_token)
        try:
            self._username = self._github_login.get_user().login
        except Exception as e:
            self._authenticated = False
            logging.error("Unable to login: " + str(e))
        else:
            self._authenticated = True
            self._rate_limit = self._github_login.get_rate_limit()

    def get_auth(self):
        return self._github_login

    def get_username(self):
        if self.is_authenticated:
            return self._username
        else:
            return Exception("Can't get username. A user is not authenticated")

    def get_rate_limit(self):
        if self.is_authenticated:
            return self._rate_limit
        else:
            return Exception("Can't get rate limit. A user is not authenticated")

    def is_authenticated(self):
        return self._authenticated