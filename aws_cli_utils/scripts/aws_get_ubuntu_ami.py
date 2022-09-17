#!/usr/bin/env python3
from urllib.request import urlopen
import argparse
import re
import json


def main():
    parser = argparse.ArgumentParser(
        description="Print the id of the Ubuntu AMI for the given region, ubuntu version, architecture and type."
    )
    parser.add_argument("region", default="us-east-2", nargs="?")
    parser.add_argument("version", default="20.04", nargs="?")
    parser.add_argument(
        "architecture", default="amd64", nargs="?"
    )  # Possible values: amd64, arm64
    parser.add_argument(
        "type", default="hvm-ssd", nargs="?"
    )  # Possible values: hvm-instance, hvm-ssd
    args = parser.parse_args()


    ubuntu_amis = urlopen("https://cloud-images.ubuntu.com/locator/releasesTable").read()
    ubuntu_amis = re.sub(
        r'(,)\s*\](?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)',
        "]",
        ubuntu_amis.decode(),
    )
    ubuntu_amis = json.loads(ubuntu_amis)["aaData"]
    ubuntu_amis = [
        ami
        for ami in ubuntu_amis
        if (
            (ami[0] == "Amazon AWS")
            and (ami[1] == args.region)
            and (ami[3] == args.version)
            and (ami[4] == args.architecture)
            and (ami[5] == args.type)
        )
    ]
    version = max(ubuntu_ami[-2] for ubuntu_ami in ubuntu_amis)
    ubuntu_amis = [ami for ami in ubuntu_amis if ami[-2] == version]
    assert len(ubuntu_amis) == 1, f"Several possible AMIs: {ubuntu_amis}"
    ubuntu_ami = ubuntu_amis[0]
    ami_id = re.search('launchAmi=([^"]+)"', ubuntu_ami[-1]).group(1)
    print(ami_id)
