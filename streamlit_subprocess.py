"""A module that lets you run subprocesses in and
display them interactively in Streamlit."""

import streamlit as st
import subprocess

def run(args):
    """Runs a commmand on the command line and outputs the result to Streamlit."""
    # Print out the command.
    st.write(f"**`{' '.join(args)}`**")
    
    # Start the subprocess.
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, encoding='utf-8')
    
    # Run the subprocess and write the output to Streamlit.
    output = ''
    output_block = st.empty()
    while chunk := proc.stdout.readline():
        output += chunk
        output_block.code(output, language='sh')
    
