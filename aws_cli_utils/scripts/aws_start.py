#!/usr/bin/env python3
import subprocess
from argparse import ArgumentParser
import time
from pathlib import Path
import os

import boto3


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("instance_id", metavar="InstanceId", type=str)
    return parser.parse_args()


def start_instance(client, instance_id):
    resp = client.start_instances(InstanceIds=[instance_id])
    assert resp["StartingInstances"][0]["CurrentState"]["Name"] == "pending"


def wait_instance_running(client, instance_id):
    waiter = client.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id], WaiterConfig={"Delay": 5})


def get_instance_info(client, instance_id):
    resp = client.describe_instances(InstanceIds=[instance_id])
    instance_ip = resp["Reservations"][0]["Instances"][0]["PublicIpAddress"]
    instance_ami = resp["Reservations"][0]["Instances"][0]["ImageId"]
    instance_key = resp["Reservations"][0]["Instances"][0]["KeyName"]
    return instance_ip, instance_ami, instance_key


def add_ssh_host_key_to_known_keys(instance_ip):
    for _ in range(40):
        try:
            proc = subprocess.run(
                f"ssh-keyscan -t ecdsa -H {instance_ip}",
                check=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            break
        except subprocess.CalledProcessError:
            time.sleep(3)
    host_key = proc.stdout.decode()
    with (Path.home() / ".ssh/known_hosts").open("a") as known_host_file:
        known_host_file.write(host_key)


def main():
    args = parse_args()
    client = boto3.client("ec2")
    start_instance(client, args.instance_id)
    print(f"Started instance {args.instance_id}")
    wait_instance_running(client, args.instance_id)
    ip, ami, key = get_instance_info(client, args.instance_id)
    print(f"Instance is running, connecting... ({ip=})")
    add_ssh_host_key_to_known_keys(ip)

    subprocess.run(
        f"aws-ssh {ip} {ami}",
        shell=True,
        env={**os.environ, "AWS_CLI_UTILS_DEFAULT_KEY_NAME": key},
    )
