"""This class provides a set of utility functions to run large map operations
against the GitHub API. It provides three major pieces of functionality:

1. A map API which lets you run operations against GitHub (wrapping PyGithub)
2. Automatic caching and rate limiting to prevent too many GitHub API calls.
3. Graphical output to the Streamlit app.
"""

import streamlit as st
import github
from typing import Any

def _dont_hash(x: Any) -> None:
    """Streamit hash function which completely ingnores whateve x is."""
    st.write(f"Calling _dont_hash on an object of type {type(x)}")
    return None

# These are the hash functions which enable us to hash these types properly
_HASH_FUNCS = {
    "github_bot.GitHubBot": _dont_hash,
}

class GitHubBot:
    @staticmethod
    def from_user_defined_token() -> "GitHubBot":
        """Creates a text input for the user to type in an access token."""
        access_token = st.sidebar.text_input("Github access token", type="password")
        if not access_token:
            raise RuntimeError("Must supply an access token.")
        return GitHubBot.from_access_token(access_token)

    @staticmethod
    @st.cache(hash_funcs=_HASH_FUNCS)
    def from_access_token(access_token: str) -> "GitHubBot":
        """Returns a ghitub object from an access token."""
        return GitHubBot(access_token)

    def __init__(self, access_token: str) -> None:
        """The construtor takes an access token."""
        self.github = github.Github(access_token) 
        
        # Outputting the type so that I can figure out the right type for _HASH_FUNCS:
        st.write(f"self.github has type `{type(self.github)}`")

# These are the name that are exposed when someone imports * from this module.
__all__ = ["GitHubBot"]
