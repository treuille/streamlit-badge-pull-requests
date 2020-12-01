"""This is a second script which I'm creating to clean up every PR
which had a misspelled title.

Todo:

- Create a list of all of the repos which we forked.
- Create a template which performs actions and then captures errors
  which can be displayed layer

Overview of pieces:

- GithubCache
    - map(input, func): map a function over a set and store the errors
    - 
"""

import streamlit as st

st.write("Clean up PRs.")

def double(x: int) -> int:
    return x * 2

st.write("double", double(10))
