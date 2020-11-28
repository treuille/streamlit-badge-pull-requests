"""Special utility functions to use PyGithub with Streamlit."""

import streamlit as st
import streamlit_subprocess
import functools
import os
import tempfile
import math
import time
import datetime
import shutil
import re
import urllib.parse
from datetime import datetime
from github import Github
from github import NamedUser
from github import ContentFile
from github import Repository
from github import RateLimitExceededException
from github import UnknownObjectException
from github import BadCredentialsException
from github import GithubException
from github import MainClass as GithubMainClass

def _get_attr_func(attr):
    """Returns a function which gets this attribute from an object."""

    def get_attr_func(obj):
        return getattr(obj, attr)
    return get_attr_func

def hash_repo(repo):
    st.warning(f"`hash_repo` -> `{repo._streamlit_hash}`")
    return repo._streamlit_hash

# This dictionary of hash functions allows you to safely intermix PyGithub
# with Streamit caching.
GITHUB_HASH_FUNCS = {
    GithubMainClass.Github: lambda _: None,
    NamedUser.NamedUser: _get_attr_func('login'),
    ContentFile.ContentFile: _get_attr_func('download_url'),
    Repository.Repository: hash_repo,
}

def rate_limit(limit_type: str):
    """Function decorator to try to handle Github search rate limits.
    See: https://developer.github.com/v3/search/#rate-limit

    limit_type: 'core' for regular API calls | 'search' for search calls
    """

    # Willing to wait up to an hour to lift the limits.
    MAX_WAIT_SECONDS = 60.0 * 60.0

    def rate_limit_decorator(func):
        @functools.wraps(func)
        def wrapped_func(github, *args, **kwargs):
            try:
                return func(github, *args, **kwargs)
            except RateLimitExceededException:
                # We were rate limited by Github, Figure out how long to wait.
                # Round up, and wait that long.
                search_limit = getattr(github.get_rate_limit(), limit_type)
                remaining = search_limit.reset - datetime.utcnow()
                wait_seconds = math.ceil(remaining.total_seconds() + 1.0)
                wait_seconds = min(wait_seconds, MAX_WAIT_SECONDS)
                with st.spinner(f'Waiting {wait_seconds}s to avoid {limit_type} rate limit.'):
                    time.sleep(wait_seconds)
                return func(github, *args, **kwargs)
        return wrapped_func
    return rate_limit_decorator

# The URL of the app badge to include in the apps README.md
BADGE_URL = r"https://static.streamlit.io/badges/streamlit_badge_black_white.svg"

class GithubCoords:
    """The path of a Github file, consisting of owner, repo, branch, and path."""

    def __init__(self, owner: str, repo: str, branch: str, path: str) -> None:
        """Constructor."""

        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.path = path
        
    def __str__(self) -> str:
        return ("<GithubCoords "
            f"owner:{self.owner} "
            f"repo:{self.repo} "
            f"branch:{self.branch} "
            f"path:{self.path}>")

    @staticmethod
    def from_app_url(url: str) -> 'GithubCoords':
        """Returns the GithubCoords given a Streamlit url."""

        # Convert the url intp a more cannonical form
        url = urllib.parse.unquote(url)
        if not url.startswith("https://share.streamlit.io/"):
            return None
        if url.endswith("/"):
            url = url + "streamlit_app.py"
        elif not url.endswith(".py"):
            url = url + "/streamlit_app.py"

        # Parse the Stremalit URL into component parts
        streamlit_app_url = re.compile(
            r"https://share.streamlit.io/"
            r"(?P<owner>\w[\w\-]*)/"
            r"(?P<repo>\w[\w\-]*)/"
            r"((?P<branch>\w[\w\-\.]*)/)?"
            r"(?P<path>\w[\w\-/\.]*\w\.py)"
        )
        matched_url = streamlit_app_url.match(url)
        if matched_url is None:
            raise RuntimeError(f"Unable to parse {url} with {streamlit_app_url}")

        return GithubCoords(
            matched_url.group('owner'),
            matched_url.group('repo'),
            matched_url.group('branch'),
            matched_url.group('path')
        )

    @staticmethod
    def from_github_url(url: str) -> 'GithubCoords':
        """Returns the GithubCoords given a Github url."""

        # Parse the Github URL into component parts
        github_url = re.compile(
             r"https://github.com/"
             r"(?P<owner>[\w-]+)/"
             r"(?P<repo>[\w-]+)/blob/"
             r"(?P<branch>[\w-]+)/"
             r"(?P<path>[\w-]+\.md)"
             )
        matched_url = github_url.match(url)
        return GithubCoords(
            matched_url.group('owner'),
            matched_url.group('repo'),
            matched_url.group('branch'),
            matched_url.group('path')
        )

    # Hold repos in the cache for 6 hours.
    @st.cache(hash_funcs=GITHUB_HASH_FUNCS, persist=True, suppress_st_warning=True,
            ttl=(60 * 60 * 6)) 
    def get_repo(self, github: GithubMainClass.Github) -> Repository.Repository:
        """Returns a cached version of a PyGithub repository with additional
        metadata which can be used for caching."""
        # Insert some debug information here to see if we're in the cached function.
        st.warning(f"In cached get_repo for `{self.owner}/{self.repo}`.")

        # Get the underlying github repo, or None if it doesn't exist.
        try:
            repo = github.get_repo(f"{self.owner}/{self.repo}") 
        except (UnknownObjectException, BadCredentialsException):
            return None
        
        # Adds a string which lets us hash this repository quickly
        add_streamlit_hash(repo)
        return repo

class RepoHasNoBranches(Exception):
    def __init__(self, repo_name):
        Exception.__init__(self, repo_name)

def add_streamlit_hash(repo: Repository.Repository) -> None:
    """Adds a string to the repo which reflects the most recent
    modification time for the repo.

    Raises RepoHasNoBranches if the repo doesn't have any branches
    then this raises RepoHasNoBranches, which would probably happen
    if they repo had been just created.
    """

    # A litle debug output
    st.write("Owner:", repo.owner.login)
    st.write("Name:", repo.name)

    # raise RuntimeError("Testing our abilitity to introspect repos.")
    # raise RuntimeError("Testing add_streamlit_hash.")
        
    # Figure out the most recent modification time
    repo_last_modified = datetime.min
    for branch in repo.get_branches():
        branch_last_modified = branch.commit.commit.committer.date
        if branch_last_modified > repo_last_modified:
            repo_last_modified = branch_last_modified  
    if repo_last_modified == datetime.min:
        raise RepoHasNoBranches(f"{repo.owner.login}/{repo.name}")

    # Give this repo a hash which represents the most recent modification time.
    repo._streamlit_hash = f"{repo.owner.login}/{repo.name} @ {repo_last_modified}"
    st.write(f'repo._streamlit_hash: `{repo._streamlit_hash}`')


@st.cache(hash_funcs=GITHUB_HASH_FUNCS)
def from_access_token(access_token):
    """Returns a ghitub object from an access token."""

    github = Github(access_token) 
    return github

@rate_limit("search")
@st.cache(hash_funcs=GITHUB_HASH_FUNCS, persist=True)
def get_user_from_email(github, email):
    """Returns a user for that email or None."""

    users = list(github.search_users(f'type:user {email} in:email'))
    if len(users) == 0:
        return None
    elif len(users) == 1:
        return users[0]
    else:
        raise RuntimeError(f'{email} associated with {len(users)} users.')

@rate_limit("search")
@st.cache(hash_funcs=GITHUB_HASH_FUNCS, persist=True)
def get_streamlit_files(github, github_login):
    """Returns every single file on github which imports streamlit."""

    try:
        SEARCH_QUERY = 'extension:py "import streamlit as st" user:'
        files = github.search_code(SEARCH_QUERY + github_login)
        return list(files)
    except RateLimitExceededException:
        raise
    except GithubException as e:
        if e.data['message'] == 'Validation Failed':
            # Then this user changed their permissions, I think.
            # In any case, we just pretend they have no files.
            return []
        else:
            # In this case, we have no idea what's going on, so just raise again. 
            raise

@rate_limit("core")
@st.cache(hash_funcs=GITHUB_HASH_FUNCS, suppress_st_warning=True)
def get_readme(
       github: GithubMainClass.Github,
       repo: Repository.Repository) -> ContentFile.ContentFile:
    """Gets the readme for this repo, or None if the repo has none."""
    try:
        contents = repo.get_contents("")
    except UnknownObjectException:
        return None

    st.write(f"`get_readme`: `{type(contents)}` for `{repo}`")
    for content_file in contents:
        st.write(f"`get_readme`: `{content_file.name}`")
        if content_file.name.lower() == "readme.md":
            return content_file
    return None

@rate_limit("core")
@st.cache(hash_funcs=GITHUB_HASH_FUNCS, suppress_st_warning=True)
def has_streamlit_badge(
        github: GithubMainClass.Github,
        repo: Repository.Repository) -> bool:
    readme = get_readme(github, repo)
    if readme:
        readme_contents = readme.decoded_content.decode('utf-8')
        return BADGE_URL in readme_contents
    else:
        return False

def fork_repo(repo: Repository.Repository) -> Repository.Repository:
    """Fork this repository and return a new version of it which 
    has a _streamlit_hash tag."""
    forked_repo = repo.create_fork()
    add_streamlit_hash(forked_repo)
    return forked_repo

# Shouldn't be st.cached because this has a side effect.
def fork_and_clone_repo(repo: Repository.Repository, base_path: str) -> str:
    """Clones the given repository into the path give by base_path.Returns
    the root path of the repository."""

    # Fork the original repo
    forked_repo = repo.create_fork()
    st.success(f"Forked repo `{repo.git_url}`")

    # Check to see whether we've already cloned this repo.
    clone_path = os.path.join(base_path, f'{repo.owner.login}__{forked_repo.name}')
    if os.path.exists(clone_path):
        st.warning(f"Repo path `{clone_path}` already exists. Skipping.")        
        return clone_path

    # Clone the repo.
    temp_path = tempfile.mkdtemp()
    st.write(clone_path, temp_path)
    clone_retval = streamlit_subprocess.run(['git', 'clone', forked_repo.git_url, temp_path])
    if clone_retval != 0:
        raise RuntimeError(f'Unable to clone {forked_repo.git_url}.')
    shutil.move(temp_path, clone_path)
    st.success(f"Cloned `{forked_repo.git_url}` to `{clone_path}`.")
    return clone_path


