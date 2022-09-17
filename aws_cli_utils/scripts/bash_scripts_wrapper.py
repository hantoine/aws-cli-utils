#!/usr/bin/env python3
import subprocess
from pathlib import Path
import sys
import os

def launch_script(script_file_name):
    subprocess.run([Path(__file__).parent / "bash" / script_file_name] + sys.argv[1:])

def aws_list():
    launch_script('aws-list')

def aws_cancel_requests():
    launch_script('aws-cancel-requests')

def aws_list_requests():
    launch_script('aws-list-requests')

def aws_price():
    launch_script('aws-price')

def aws_scp():
    launch_script('aws-scp')

def aws_ssh():
    launch_script('aws-ssh')

def aws_wait_request():
    launch_script('aws-wait-request')

def aws_wait_up():
    launch_script('aws-wait-up')
