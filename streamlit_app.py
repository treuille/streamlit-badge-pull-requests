import streamlit as st

# Libraries from this project
import cached_github

# External libraries
import re
import collections

def get_config():
    """Returns all the config information to run the app."""
    
#     # Get input
#     zip_file = get_zip_file()
# 
#     # Check for input
#     if not zip_file:
#         err('Please upload a user file. Ask TC for the file.')
#     if not access_token:
#         err('Please enter a github access token.')
#     if not token_name:
#         err('Please name this token.')

    # Parse and return the information
    # user_table = extract_csv_from_zip_file(zip_file)
    access_token = st.sidebar.text_input("Github access token", type="password")
    f"**access_token:** `{access_token}`"
    # token_name = st.sidebar.text_input("Token name")
    
    github = cached_github.from_access_token(access_token)
    return github

GithubPath = collections.namedtuple('GithubPath', ('user', 'repo', 'branch', 'file'))

def get_github_path(url):
    """Returns the Github path given a Streamlit url."""
    streamlit_app_url = re.compile(
        r"https://share.streamlit.io/" +
        r"(?P<user>[\w-]+)/" +
        r"(?P<repo>[\w-]+)/" +
        r"(?P<branch>[\w-]+)/" +
        r"(?P<file>[\w-]+\.py)"
    )
    matched_url = streamlit_app_url.match(url)
    return GithubPath(
        matched_url.group('user'),
        matched_url.group('repo'),
        matched_url.group('branch'),
        matched_url.group('file')
    )

def main():
    """Execution starts here."""
    github = get_config()
    st.write('Hello world')
    'github', github, id(github)

    repo_streamlit_url = "https://share.streamlit.io/shivampurbia/tweety-sentiment-analyis-streamlit-app/main/Tweety.py"
    f"**repo_streamlit_url:** `{repo_streamlit_url}`"
    github_path = get_github_path(repo_streamlit_url)
    'github_path', github_path
    'about to get content file'
    content_file = cached_github.get_content_file(github,
            github_path.user, github_path.repo, github_path.branch, 'README.md')
    '**content_file:**', content_file
    st.text(content_file.decoded_content.decode('utf-8'))

    st.write(dir(content_file))
#     f"**user:** `{github_path.group('user')}`"
#     f"**repo:** `{github_path.group('repo')}`"
#     f"**branch:** `{github_path.group('branch')}`"
#     f"**file:** `{github_path.group('file')}`"

# Start execution at the main() function 
if __name__ == '__main__':
    main()

