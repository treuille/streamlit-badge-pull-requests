"""A script which lets you batch-add badges to the READMEs of
Streamlit sharing apps."""

import streamlit as st
import streamlit_github

# This is where we will store all the forked repositories
FORK_BASE_PATH = 'forks'

def get_config():
    """Returns all the config information to run the app."""

    # Parse and return the information
    access_token = st.sidebar.text_input("Github access token", type="password")
    github = streamlit_github.from_access_token(access_token)
    return github

def main():
    """Execution starts here."""

    # Get a github object from the user's authentication token
    github = get_config()
 
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
#     readme = repo.get_contents("README.md")
#     readme_contents = readme.decoded_content.decode('utf-8')
#     f"**readme**", readme
#     st.code(readme_contents)
#     'has_badge', streamlit_github.BADGE_URL in readme_contents
#     # st.code(content_file.

    # Test out content_file_from_app_url()
    github_url = r"https://github.com/tester-burner/test1/blob/main/README.md"
    f'**github_url** `{github_url}`'
    coords = streamlit_github.GithubCoords.from_github_url(github_url)
    content_file = coords.get_contents(github)
    st.code(content_file.decoded_content.decode('utf-8'), language='markdown')
    
    if st.button('Fork the repo'):
        repo = coords.get_repo(github)
        'repo', repo
        streamlit_github.fork_and_clone_repo(repo, FORK_BASE_PATH)


# Start execution at the main() function 
if __name__ == '__main__':
   main()
