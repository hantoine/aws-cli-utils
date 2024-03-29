#!/usr/bin/env python3
import os
import subprocess
import time
from argparse import ArgumentParser
from pathlib import Path

import boto3


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "instance_type", metavar="InstanceType", default="c5.4xlarge", nargs="?"
    )
    parser.add_argument(
        "--ami", "-a", default=os.environ.get("AWS_CLI_UTILS_DEFAULT_AMI")
    )
    parser.add_argument(
        "--key", "-k", default=os.environ.get("AWS_CLI_UTILS_DEFAULT_KEY_NAME")
    )
    args = parser.parse_args()
    assert args.key != None
    assert args.ami != None
    return args


def request_spot_instance(client, args):
    resp = client.request_spot_instances(
        LaunchSpecification={
            "ImageId": args.ami,
            "KeyName": args.key,
            "InstanceType": args.instance_type,
        },
        Type="persistent",
        InstanceInterruptionBehavior="stop",
    )
    request_id = resp["SpotInstanceRequests"][0]["SpotInstanceRequestId"]
    price = resp["SpotInstanceRequests"][0]["SpotPrice"]
    print(f"Instance requested ({request_id=}, {price=})")
    return request_id


def wait_request_fulfilled(client, request_id):
    waiter = client.get_waiter("spot_instance_request_fulfilled")
    waiter.wait(SpotInstanceRequestIds=[request_id], WaiterConfig={"Delay": 3})


def get_instance_id_for_request(client, request_id):
    resp = client.describe_spot_instance_requests(SpotInstanceRequestIds=[request_id])
    instance_id = resp["SpotInstanceRequests"][0]["InstanceId"]
    return instance_id


def wait_instance_running(client, instance_id):
    waiter = client.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id], WaiterConfig={"Delay": 5})


def wait_instance_ready(client, request_id):
    wait_request_fulfilled(client, request_id)
    instance_id = get_instance_id_for_request(client, request_id)
    print(f"Instance request fulfilled ({instance_id=})")
    wait_instance_running(client, instance_id)
    return instance_id


def get_instance_ip(client, instance_id):
    resp = client.describe_instances(InstanceIds=[instance_id])
    instance_ip = resp["Reservations"][0]["Instances"][0]["PublicIpAddress"]
    return instance_ip


def add_ssh_host_key_to_known_keys(instance_ip):
    for _ in range(40):
        try:
            proc = subprocess.run(
                f"ssh-keyscan -t ed25519 -H {instance_ip}",
                check=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            host_key = proc.stdout.decode()
            with (Path.home() / ".ssh/known_hosts").open("a") as known_host_file:
                known_host_file.write(host_key)
            return
        except subprocess.CalledProcessError:
            time.sleep(3)


def wait_instance_reachable(ip_address):
    subprocess.run(f"aws-wait-up {ip_address}", shell=True, check=True)


def main():
    args = parse_args()
    client = boto3.client("ec2")
    request_id = request_spot_instance(client, args)
    instance_id = wait_instance_ready(client, request_id)
    instance_ip = get_instance_ip(client, instance_id)
    print(f"Instance starting... ({instance_ip=})")
    wait_instance_reachable(instance_ip)

    print("Connecting...")
    subprocess.run(
        f"aws-ssh {instance_ip} {args.ami}",
        shell=True,
        env={
            **os.environ,
            "AWS_CLI_UTILS_DEFAULT_KEY_NAME": args.key,
            "AWS_CLI_UTILS_ACCEPT_NEW_HOST_KEY": "",
        },
    )
