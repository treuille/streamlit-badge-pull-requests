"""This is a second script which I'm creating to clean up every PR
which had a misspelled title.

Todo:

- Create a list of all of the repos which we forked.
- Create a template which performs actions and then captures errors
  which can be displayed layer

Overview of pieces:

- GithubBot
    - map(input, func): map a function over a set and store the errors
    - fromIdToken():

- Repository
    - a repository from the bot that helps you do stuff
"""

import streamlit as st
from GitHubBot import GitHubBot

st.title("Fix the typos in the PRs")

gh_bot = GitHubBot.from_user_defined_token()
