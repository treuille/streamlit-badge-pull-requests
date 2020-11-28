"""A script which lets you batch-add badges to the READMEs of
Streamlit sharing apps."""

import streamlit as st
import streamlit_github
import numpy as np
import pandas as pd
from github import MainClass as GithubMainClass
from github import ContentFile
from github.GithubException import UnknownObjectException
from github import GithubException
from typing import Iterator

# This is where we will store all the forked repositories
FORK_BASE_PATH = 'forks'

# This is the commit message when we add a new badge.
COMMIT_MESSAGE = "Added Streamlit app badge for discoverability"

# This is the title we give the pull request.
BADGE_PULL_REQUEST_TITLE = "Add a Stremlit app badge to readme"

# This is the body of the pull request.
BADGE_PULL_REQUEST_BODY = """
Hi 👋!

Thank for for making this awesome Streamlit app!

I noticed that your project's readme doesn't have a Streamlit badge.
Adding one would let people directly click into your app when
browsing your Github repo. Cool, right?!

This pull request automatically adds a beautiful Streamlit badge to your
reamde. Just go head and click `Merge pull request` below to get it!

Happy app creating 🎈 and (for those in the US) happy Thanksgiving too! 🥧

~ StreamlitBadgeBot 🤖
___
For more information about how pull requests work, please [click here](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/merging-a-pull-request).
"""


class ForkAppError(Exception):
    """Represents a mistake that could happen when trying to fork an app."""

    def __init__(self, reason):
        """Constructor."""
        Exception.__init__(self, reason)
        self.reason = reason

class ConfigOptions:
    """Returns all the config information to run the app."""

    def __init__(self) -> None:
        """Adds UI elements which give us some config information."""
        self.access_token = st.sidebar.text_input("Github access token", type="password")
        self.use_debug_repos = st.sidebar.checkbox('Use a debug repo list')
        self.auto_expand = st.sidebar.checkbox('Auto-expand app display')
        self.auto_process_apps = st.sidebar.checkbox("Auto-process apps")
        self.show_readmes = st.sidebar.checkbox("Show readme contents")
        self.do_pull_requests = st.sidebar.checkbox("Send pull reuqests")
    
def coords_iter(apps: pd.DataFrame) -> Iterator[streamlit_github.GithubCoords]:
    """Takes a list of apps and iterate over that list, yielding GithubCoord objects."""

    for app in apps.itertuples():
        if hasattr(app, "app_url"):
            coords = streamlit_github.GithubCoords.from_app_url(app.app_url)
            app_url = app.app_url
        else:
            coords = streamlit_github.GithubCoords.from_github_url(app.github_url)
            app_url = app.github_url
        yield coords, app_url

@st.cache
def get_s4a_apps() -> pd.DataFrame:
    apps = pd.read_csv('sharing_apps_2.csv')
    apps.drop('Unnamed: 0', axis=1, inplace=True)
    return apps

def filter_apps(apps: pd.DataFrame) -> pd.DataFrame:
    """Give the user a selection interface with which to select a set
    of apps to process. Displays and returns the selected apps."""

    # Let the user filter app URLs
    filter_text = st.text_input('Filter URLs')
    if filter_text:
        apps = apps[apps.app_url.str.contains(filter_text)]

    # Let the user select a numerical range of apps to work on
    first_app_index, last_app_index = \
       st.slider("Select apps", 0, len(apps), (0, 1))
    if first_app_index >= last_app_index:
        raise RuntimeError('Must select at least one app.')
    selected_apps = apps[first_app_index:last_app_index].copy()
    st.write(f"Selected `{len(selected_apps)} / {len(apps)}` apps.")
    st.write(selected_apps)

    return selected_apps

@st.cache(hash_funcs=streamlit_github.GITHUB_HASH_FUNCS, persist=True,
            suppress_st_warning=True, ttl=(60 * 60 * 6)) 
def compute_app_status(apps: pd.DataFrame, config: ConfigOptions, github: GithubMainClass.Github):
    """Adds a "status" column to the app DataFrame which indicates that
    whether the app has a badge or not and / or whether there was an
    error processing the app for some reason."""

    st.write("## Computing app status")

    # These are the additional columns which we're going to add
    status_column = []

    for app in apps.itertuples():
        with st.beta_expander(app.app_url, expanded=config.auto_expand):
            try:
                st.write(app)
                
                if app.app_url is None or app.app_url == "None":
                    raise ForkAppError("No URL")

                # Parse out the coordinates for this repo.
                coords = streamlit_github.GithubCoords.from_app_url(app.app_url)
                if coords == None:
                    raise ForkAppError("Unable to parse URL")
                st.write({attr:getattr(coords, attr)
                    for attr in ['owner', 'repo', 'branch', 'path']})

                # Get the repo.
                repo = coords.get_repo(github)
                st.write("repo", repo)
                # Show the readme if possible.
                if repo is None:
                    raise ForkAppError("Repo does not exist")

                readme = streamlit_github.get_readme(github, repo)
                if readme is None:
                    raise ForkAppError("Readme does not exist")

                if config.show_readmes:
                    readme_contents = readme.decoded_content.decode('utf-8')
                    st.beta_columns((1, 20))[1].text(readme_contents)
    
                # st.write(dir(repo))
                if repo.fork:
                    raise ForkAppError("Repo forks another.")

                if streamlit_github.has_streamlit_badge(github, repo):
                    app_status = "Has badge"
                else:
                    app_status = "No badge"
            except ForkAppError as e:
                app_status = f"ForkAppError: {e.reason}"
            # except Exception as e:
            #     app_status = str(type(e))

            st.write(f"app_status: '{app_status}'")

            # Fill in the status column
            status_column.append(app_status)
        
    # Assign these new columns to the app DataFrame.
    apps = apps.assign(status=status_column)
    return apps

def display_badge_statistics(apps: pd.DataFrame) -> None:
    """Displays a bunch of statistics about apps with and without badges."""
    with st.beta_expander("Badge statistics"):
        no_badges = apps["status"] == "No badge"
        yes_badges = apps["status"] == "Has badge"
        error_apps = ~(no_badges | yes_badges)
        st.bar_chart(apps.status.value_counts())
    
def parse_app_from_file(config: ConfigOptions, github: GithubMainClass.Github):
    # Get the app dataframe
    apps = get_s4a_apps()
    apps = filter_apps(apps)

    # Don't do anything until the use clicks this button.
    if not (config.auto_process_apps or st.button('Process apps')):
        return
    apps = compute_app_status(apps, config, github)

    # Write out the results
    st.write("### Processed apps")
    st.write(apps)

    # Display some summary statistics on what the badges are doing
    display_badge_statistics(apps)
            
    # Filter down to just those apps which have no badges
    no_badges = apps["status"] == "No badge"
    apps = apps[no_badges]

    # Let the user futher filter down the apps to fork
    first_app_index, last_app_index = \
        st.slider("Range of remaining apps to fork", 0, len(apps), (0, 1))
    if first_app_index >= last_app_index:
        raise RuntimeError('Must select at least one app.')
    return apps[first_app_index:last_app_index].copy()

def create_debug_app_list():
    """Creates a list of apps which we can use to test the fork, branch and commit algorithms."""

    app_git_urls = [
        "https://github.com/tester-burner/test1/blob/main/README.md",
    ]
    apps = pd.DataFrame()
    apps['github_url'] = app_git_urls
    st.write(apps)
    st.write(f"Len apps {len(apps)}")
    apps.loc[:,'status'] = "No badge"
    return apps

def add_badge_to_readme(readme: ContentFile.ContentFile, app_url: str) -> str:
    """Adds a Streamlit badge to the URL."""

    # Get the contents from the readme.
    readme_contents = readme.decoded_content.decode('utf-8')
    st.text(readme_contents)

    # Don't add the badge twice
    badge_image = "https://static.streamlit.io/badges/streamlit_badge_black_white.svg"
    if badge_image in readme_contents:
        st.warning("Readme already has badge, skipping...")
        return None

    # Compute the badge location.
    st.write(f"app_url: `{app_url}`")
    badge_markdown = f"[![Open in Streamlit]({badge_image})]({app_url})"
    st.write(f"badge markdown:")
    st.text(badge_markdown)

    # Plan A is to add the badge to the end of the title readme,
    # but if that doesn't work, then we just prepend the badge to the
    # begining of the readme.
    prepend_badge = False
    if '\r' in readme_contents:
        # If we see weird line endings, then don't do anything fancy.
        prepend_badge = True
    else:
        lines = readme_contents.split('\n')
        if len(lines) < 1:
            prepend_badge = True
        else:
            first_line = lines[0]
            if first_line.startswith('#') and '[' not in first_line:
                lines[0] = f"{first_line} {badge_markdown}"
                new_contents = '\n'.join(lines)
                st.write("New first line:")
                st.text(lines[0])
            else:
                prepend_badge = True
    st.write(f"Prepend badge: `{prepend_badge}`")
    if prepend_badge:
        new_contents = f"{badge_markdown}\n\n{readme_contents}"
    st.write("New readme contents")
    st.text(new_contents)
    return new_contents


def batch_fork_repos(
        apps: pd.DataFrame,
        config: ConfigOptions,
        github: GithubMainClass.Github):
    """Goes through a list of apps and forks them all and then
    add badges to them an issues pull requests."""
    for coords, app_url in coords_iter(apps):
        with st.beta_expander(app_url, expanded=config.auto_expand):
            # Fork the repo.
            st.write("App to fork")
            st.write({attr:getattr(coords, attr)
                for attr in ['owner', 'repo', 'branch', 'path']})
            repo = coords.get_repo(github)
            forked_repo = streamlit_github.fork_repo(repo)

            # Add a badge to the readme.
            st.write(forked_repo, forked_repo._streamlit_hash)
            readme = streamlit_github.get_readme(github, forked_repo)
            new_contents = add_badge_to_readme(readme, app_url)
            if new_contents is None:
                st.warning("No extra commit since badge already exists.")
            else:
                forked_repo.update_file(readme.path, COMMIT_MESSAGE,
                        new_contents, readme.sha)
                st.success("Just added a badge to the readme.")

            # If we haven't allowed pull requesting, then nothing more to do.
            if not config.do_pull_requests:
                st.warning("Skipping this pull request.")
                continue

            # Create a pull request
            pull_request_args = {
                'title': BADGE_PULL_REQUEST_TITLE,
                'head': f"{forked_repo.owner.login}:{repo.default_branch}",
                'base': repo.default_branch,
                'body': BADGE_PULL_REQUEST_BODY,
            }
            st.write("Creating pull request", pull_request_args)
            try:
                pull_request = repo.create_pull(**pull_request_args)
                st.write("Created pull request", pull_request)
            except GithubException as e:
                st.error("Error creating the pull request.")
                st.json(e.data)


def main():
    """Execution starts here."""

    # Display the app title
    st.write("## Apps")

    # These are all the options the user can set
    config = ConfigOptions()
    github = streamlit_github.from_access_token(config.access_token)

    if config.use_debug_repos:
        apps = create_debug_app_list()
    else:
        apps = parse_app_from_file(config, github)
    st.write("## Remaining apps to fork", apps)
        
    # When clicked for the given repos.
    if st.button('Fork repos'):
        batch_fork_repos(apps, config, github)

# Start execution at the main() function 
if __name__ == '__main__':
    main()
