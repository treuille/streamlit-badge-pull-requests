"""A script which lets you batch-add badges to the READMEs of
Streamlit sharing apps."""

import streamlit as st
import cached_github
import github
import re
import collections

def get_config():
    """Returns all the config information to run the app."""

    # Parse and return the information
    access_token = st.sidebar.text_input("Github access token", type="password")
    github = cached_github.from_access_token(access_token)
    f"**access_token:** `{access_token}`"
    
    return github

def content_file_from_streamlit_url(github, url):
    """Returns the Github path given a Streamlit url."""

    # Parse the Stremalit URL into component parts
    streamlit_app_url = re.compile(
        r"https://share.streamlit.io/"
        r"(?P<owner>[\w-]+)/"
        r"(?P<repo>[\w-]+)/"
        r"(?P<branch>[\w-]+)/"
        r"(?P<path>[\w-]+\.py)"
    )
    matched_url = streamlit_app_url.match(url)
    owner = matched_url.group('owner')
    repo = matched_url.group('repo')
    branch = matched_url.group('branch')
    path = matched_url.group('path')

    # Convert that into a PyGithub ContentFile
    github_repo = github.get_repo(f"{owner}/{repo}")
    return github_repo.get_contents(path, ref=branch)

def content_file_from_github_url(github, url):
    """Returns the Github path given a Github url."""

    # Parse the Github URL into component parts
    github_url = re.compile(
           r"https://github.com/"
           r"(?P<owner>[\w-]+)/"
           r"(?P<repo>[\w-]+)/blob/" 
           r"(?P<branch>[\w-]+)/"
           r"(?P<path>[\w-]+\.md)"
           )
    matched_url = github_url.match(url)
    owner = matched_url.group('owner')
    repo = matched_url.group('repo')
    branch = matched_url.group('branch')
    path = matched_url.group('path')

    # Convert that into a PyGithub ContentFile
    github_repo = github.get_repo(f"{owner}/{repo}")
    return github_repo.get_contents(path, ref=branch)

def main():
    """Execution starts here."""

    # Get a github object from the user's authentication token
    github = get_config()

    # Test out content_file_from_streamlit_url()
    streamlit_url = "https://share.streamlit.io/shivampurbia/tweety-sentiment-analyis-streamlit-app/main/Tweety.py"
    f"**streamlit_url:** `{streamlit_url}`"
    content_file = content_file_from_streamlit_url(github, streamlit_url)
    f"**content_file:**", content_file
    st.write(dir(content_file))
    st.code(content_file.decoded_content.decode('utf-8'))

    # Test out content_file_from_streamlit_url()
    github_url = r"https://github.com/tester-burner/test1/blob/main/README.md"
    content_file = content_file_from_github_url(github, github_url)
    f"**content_file:**", content_file
    st.write(dir(content_file))
    st.code(content_file.decoded_content.decode('utf-8'), language='markdown')

#       if st.button('Fork the repo'):
#           repo = github.get_repo(f'{github_path.org}/{github_path.repo}')
#           'repo', repo
#           forked_repo = repo.create_fork()
#           'forked_repo', forked_repo
#       

# Start execution at the main() function 
if __name__ == '__main__':
   main()
