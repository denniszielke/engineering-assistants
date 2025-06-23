import asyncio
from github import Github
from github import Auth

class GithubWrapper:
    github: Github
    repo_owner: str
    repo_name: str
    access_token: str

    def __init__(self, repo_owner, repo_name, access_token):
        auth = Auth.Token(access_token)
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.access_token = access_token
        self.github = Github(auth=auth)
        self.github.get_user().login
    

    async def get_issue(self, issue_number: int):
        repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
        issue = repo.get_issue(number=issue_number)
        return issue
    
    async def get_file(self, file_path: str):
        repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
        file_path = "/sample/data/Location.java"
        contents = repo.get_contents(file_path, ref="main")
        return contents.decoded_content.decode("utf-8")

    async def add_comment(self, issue_number: int, comment: str):
        repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
        issue = repo.get_issue(number=issue_number)
        issue.create_comment(comment)

    async def add_comment(self, issue_number: int, comment: str):
        repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
        issue = repo.get_issue(number=issue_number)
        issue.create_comment(comment)   
