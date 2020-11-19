"""A module that lets you run subprocesses in and
display them interactively in Streamlit."""

import streamlit as st
import subprocess

def run(args):
    """Runs a commmand on the command line and outputs the result to Streamlit."""
    # This is how many characters we read at a time from stdout.
    READ_BUFFER_LEN = 10

    # Print out the command line
    st.write(f"**`{' '.join(args)}`**")
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, encoding='utf-8')
    output = ''
    output_block = st.empty()
    while chunk := proc.stdout.read(READ_BUFFER_LEN):
        output += chunk
        output_block.code(output, language='sh')
    
