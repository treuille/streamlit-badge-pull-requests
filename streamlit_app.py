"""A script which lets you batch-add badges to the READMEs of
Streamlit sharing apps."""

import streamlit as st
import streamlit_github
import pandas as pd
from github import MainClass as GithubMainClass
from github.GithubException import UnknownObjectException

# This is where we will store all the forked repositories
FORK_BASE_PATH = 'forks'

def get_config():
    """Returns all the config information to run the app."""

    # Parse and return the information
    access_token = st.sidebar.text_input("Github access token", type="password")
    github = streamlit_github.from_access_token(access_token)
    return github

@st.cache
def get_s4a_apps() -> pd.DataFrame:
    apps = pd.read_csv('sharing_apps_2.csv')
    apps.drop('Unnamed: 0', axis=1, inplace=True)
    return apps

def parse_s4a_apps(github: GithubMainClass.Github):
    apps = get_s4a_apps()
    st.write('## Apps')
    st.write(apps) 
    st.write(apps.columns)
    apps = apps[:10]
    st.write('n_apps', len(apps))
    has_streamlit_badge = []
    for i, app in enumerate(apps.itertuples()):
        st.write(app)
        st.text(app.app_url)
        try:
            coords = streamlit_github.GithubCoords.from_app_url(app.app_url)
            st.write('coords', i, coords)
            repo = coords.get_repo(github)
            readme = repo.get_contents("README.md") 
            readme_contents = readme.decoded_content.decode('utf-8')
            f"**readme**", readme
            st.code(readme_contents)
            has_badge = streamlit_github.has_streamlit_badge(repo) 
        # except (UnknownObjectException, RuntimeError):
        except UnknownObjectException:
            has_badge = False
        except RuntimeError:
            has_badge = False
        st.write('has_streamlit_badge', has_badge)
        has_streamlit_badge.append(has_badge)
    apps['has_badge'] = has_streamlit_badge
    apps.to_csv('out.csv')
    st.success('out.csv')

def main():
    """Execution starts here."""

    # Get a github object from the user's authentication token
    github = get_config()
 
    st.write('Hello, world! Again!!')
    parse_s4a_apps(github)

#     # Test out content_file_from_app_url()
#     app_url = "https://share.streamlit.io/shivampurbia/tweety-sentiment-analyis-streamlit-app/main/Tweety.py"
#     f"**app_url:** `{app_url}`"
#     coords = streamlit_github.GithubCoords.from_app_url(app_url)
#     f"**coords:**", coords
#     content_file = streamlit_github.get_contents(github, coords)
#     st.write(dir(content_file))
#     f"**content_file:**", content_file
#     repo = content_file.repository
#     f"**repo**", repo, repo.git_url
#     st.write(dir(repo))
#     st.code(readme_contents)
#     'has_badge', streamlit_github.BADGE_URL in readme_contents
#     # st.code(content_file.

#     # Test out content_file_from_app_url()
#     github_url = r"https://github.com/tester-burner/test1/blob/main/README.md"
#     f'**github_url** `{github_url}`'
#     coords = streamlit_github.GithubCoords.from_github_url(github_url)
#     content_file = coords.get_contents(github)
#     st.code(content_file.decoded_content.decode('utf-8'), language='markdown')
#     
#     if st.button('Fork the repo'):
#         repo = coords.get_repo(github)
#         'repo', repo
#         streamlit_github.fork_and_clone_repo(repo, FORK_BASE_PATH)


# Start execution at the main() function 
if __name__ == '__main__':
   main()
