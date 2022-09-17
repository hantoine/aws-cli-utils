#!/usr/bin/env python3
from argparse import ArgumentParser

import boto3


def stop_instance(client, instance_id):
    resp = client.stop_instances(InstanceIds=[instance_id])
    assert resp["StoppingInstances"][0]["CurrentState"]["Name"] == "stopping"


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("instance_id", metavar="InstanceId", type=str)
    return parser.parse_args()


def main():
    args = parse_args()
    client = boto3.client("ec2")
    stop_instance(client, args.instance_id)
