"""A module that lets you run subprocesses in and
display them interactively in Streamlit."""

import streamlit as st
import subprocess

def run(args):
    """Runs a commmand on the command line and outputs the result to Streamlit."""
    # Print out the command.
    cmd = ' '.join(args) 
    st.write(f"**`{cmd}`**")
    
    # Start the subprocess.
    proc = subprocess.Popen(args,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        encoding='utf-8', universal_newlines=True, bufsize=1)
    
    # Run the subprocess and write the output to Streamlit.
    output = ''
    output_block = st.empty()
    while chunk := proc.stdout.readline():
        output += chunk
        output_block.code(output, language='sh')
    return_code = proc.wait(timeout=1.0)
    if return_code is None:
        raise RuntimeError(f'Cmd "{cmd}" taking too long to return.')
    return return_code 
