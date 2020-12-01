"""This class provides a set of utility functions to run large map operations
against the GitHub API. It provides three major pieces of functionality:

1. A map API which lets you run operations against GitHub (wrapping PyGithub)
2. Automatic caching and rate limiting to prevent too many GitHub API calls.
3. Graphical output to the Streamlit app.
"""

import streamlit as st
import github

class GitHubBot:
    @staticmethod
    def from_user_defined_token() -> "GitHubBot":
        """Creates a text input for the user to type in an access token."""
        access_token = st.sidebar.text_input("Github access token", type="password")
        return GitHubBot.from_access_token(access_token)

    @st.cache
    @staticmethod
    def from_access_token(access_token: str) -> GitHubBot:
        """Returns a ghitub object from an access token."""
        return GitHubBot(access_token)

    def __init__(self, access_token: str) -> None:
        """The construtor takes an access token."""
        self.github = github.Github(access_token) 


