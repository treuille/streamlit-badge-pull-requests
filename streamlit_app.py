import streamlit as st
import cached_github


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
    token_name = st.sidebar.text_input("Token name")
    
    github = cached_github.from_access_token(access_token)
    return github

def main():
    """Execution starts here."""
    github = get_config()
    st.write('Hello world')
    'github', github, id(github)

# Start execution at the main() function 
if __name__ == '__main__':
    main()

