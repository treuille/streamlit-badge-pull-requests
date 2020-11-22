"""A script which lets you batch-add badges to the READMEs of
Streamlit sharing apps."""

import streamlit as st
import streamlit_github
import numpy as np
import pandas as pd
from github import MainClass as GithubMainClass
from github.GithubException import UnknownObjectException

# This is where we will store all the forked repositories
FORK_BASE_PATH = 'forks'

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
        self.auto_expand = st.sidebar.checkbox('Auto-expand app display')
        self.auto_process_apps = st.sidebar.checkbox("Auto-process apps")
        self.show_readmes = st.sidebar.checkbox("Show readme contents")

@st.cache
def get_s4a_apps() -> pd.DataFrame:
    apps = pd.read_csv('sharing_apps_2.csv')
    apps.drop('Unnamed: 0', axis=1, inplace=True)
    return apps

def filter_apps(apps: pd.DataFrame) -> pd.DataFrame:
    """Give the user a selection interface with which to select a set
    of apps to process. Displays and returns the selected apps."""

    # Display the selector
    st.write("## Apps")

    # Let the user select which apps to focus on.
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

                readme = streamlit_github.get_readme(repo)
                if readme is None:
                    raise ForkAppError("Readme does not exist")

                if config.show_readmes:
                    readme_contents = readme.decoded_content.decode('utf-8')
                    st.beta_columns((1, 20))[1].text(readme_contents)

                if streamlit_github.has_streamlit_badge(repo):
                    app_status = "Has badge"
                else:
                    app_status = "No badge"
            except ForkAppError as e:
                app_status = f"ForkAppError: {e.reason}"
            except Exception as e:
                app_status = str(type(e))

            st.write(f"app_status: '{app_status}'")

            # Fill in the status column
            status_column.append(app_status)
        
    # Assign these new columns to the app DataFrame.
    apps = apps.assign(status=status_column)
    return apps

# def display_badge_statistics(apps: pd.DataFrame) -> None:
#     """Displays a bunch of statistics about apps with and without badges."""
#     st.write("## Badge statistics")
#     no_badges = apps["status"] == "No badge"
#     yes_badges = apps["status"] == "Has badge"
#     error_apps = ~(no_badges | yes_badges)
#     st.write("no badges", np.sum(no_badges))
#     st.write("yes badges", np.sum(yes_badges))
#     st.write("error apps", np.sum(error_apps))
#     st.write('App sums', (np.sum(no_badges) + np.sum(yes_badges) + np.sum(error_apps)), 
#             len(apps))
#     statuses = set(apps.status)
#     st.write({status:int(np.sum(apps.status == status)) for status in statuses})
#     st.bar_chart(apps.status.value_counts())
#     st.write(apps.columns)
#     st.write(apps.daily_views.min(), apps.daily_views.max())
#     st.write(apps.weekly_views.min(), apps.weekly_views.max())
#     bins = np.arange(0, 51, 5)
#     st.write('bins', bins)
#     st.write('dtype', apps.daily_views.dtype)
#     histogram = pd.cut(apps.daily_views, bins=bins)
#     st.write(type(histogram), histogram.dtype, len(histogram))
#     st.text(histogram)
#     st.text(histogram.value_counts())
#     st.help(st.bar_chart)
    
#     # # Generating Data
#     # source = pd.DataFrame({
#     #     'Trial A': np.random.normal(0, 0.8, 1000),
#     #     'Trial B': np.random.normal(-2, 1, 1000),
#     #     'Trial C': np.random.normal(3, 2, 1000)
#     # })

#     # alt.Chart(source).transform_fold(
#     #     ['Trial A', 'Trial B', 'Trial C'],
#     #     as_=['Experiment', 'Measurement']
#     # ).mark_area(
#     #     opacity=0.3,
#     #     interpolate='step'
#     # ).encode(
#     #     alt.X('Measurement:Q', bin=alt.Bin(maxbins=100)),
#     #     alt.Y('count()', stack=None),
#     #     alt.Color('Experiment:N')
#     # )

def main():
    """Execution starts here."""
    # These are all the options the user can set
    config = ConfigOptions()

    # Get a github object from the user's authentication token
    github = streamlit_github.from_access_token(config.access_token)

    # Get the app dataframe
    apps = get_s4a_apps()
    apps = filter_apps(apps)
        
    # Don't do anything until the use clicks this button.
    if not (config.auto_process_apps or st.button('Process apps')):
        return

    apps = compute_app_status(apps, config, github)
    st.write("### Processed apps")
    st.write(apps)

    # Display some summary statistics on what the badges are doing
    # display_badge_statistics(apps)

#     if st.button('Fork the repo'):
#         repo = coords.get_repo(github)
#         'repo', repo
#         streamlit_github.fork_and_clone_repo(repo, FORK_BASE_PATH)

# Start execution at the main() function 
if __name__ == '__main__':
    main()
