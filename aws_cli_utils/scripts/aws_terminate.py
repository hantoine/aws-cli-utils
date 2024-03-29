#!/usr/bin/env python3
from argparse import ArgumentParser

import boto3

# Only support Spot instances


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("instance_id", metavar="InstanceId", type=str)
    return parser.parse_args()


def check_persistent_request(client, instance_id):
    resp = client.describe_instances(InstanceIds=[instance_id])
    request_id = resp["Reservations"][0]["Instances"][0]["SpotInstanceRequestId"]
    resp = client.describe_spot_instance_requests(SpotInstanceRequestIds=[request_id])
    is_persistent_request = resp["SpotInstanceRequests"][0]["Type"] == "persistent"
    is_active_request = resp["SpotInstanceRequests"][0]["State"] in (
        "active",
        "disabled",
        "open",
    )
    return is_persistent_request and is_active_request, request_id


def cancel_spot_request(client, request_id):
    resp = client.cancel_spot_instance_requests(SpotInstanceRequestIds=[request_id])
    assert resp["CancelledSpotInstanceRequests"][0]["State"] == "cancelled"
    print(f"Spot request {request_id} cancelled.")


def terminate_instance(client, instance_id):
    resp = client.terminate_instances(InstanceIds=[instance_id])
    instance_state = resp["TerminatingInstances"][0]["CurrentState"]["Name"]
    assert (
        instance_state == "shutting-down"
    ), f"Instance is not shutting down, instance state is: {instance_state}"
    print(f"Instance {instance_id} shutting down.")


def check_part_of_fleet_request(client, request_id):
    resp = client.describe_spot_fleet_requests()
    if "NextToken" in resp:
        raise NotImplementedError("Too many fleet requests (limit is 1000)")
    resp["SpotFleetRequestConfigs"]
    active_spot_fleet_request_ids = [
        x["SpotFleetRequestId"]
        for x in resp["SpotFleetRequestConfigs"]
        if x["SpotFleetRequestState"] == "active"
    ]
    if len(active_spot_fleet_request_ids) == 0:
        return False, None, None
    for spot_fleet_request_id in active_spot_fleet_request_ids:
        resp = client.describe_spot_fleet_instances(
            SpotFleetRequestId=spot_fleet_request_id
        )
        if request_id in [x["SpotInstanceRequestId"] for x in resp["ActiveInstances"]]:
            return True, len(resp["ActiveInstances"]), spot_fleet_request_id
    return False, None, None


def cancel_spot_fleet_request(client, spot_fleet_request_id):
    resp = client.cancel_spot_fleet_requests(
        SpotFleetRequestIds=[spot_fleet_request_id], TerminateInstances=False
    )
    assert (
        resp["SuccessfulFleetRequests"][0]["CurrentSpotFleetRequestState"]
        == "cancelled_running"
    )


def main():
    args = parse_args()
    client = boto3.client("ec2")
    is_persistent_request, request_id = check_persistent_request(
        client, args.instance_id
    )
    if is_persistent_request:
        (
            is_part_of_fleet_request,
            nb_instance_in_spot_fleet,
            fleet_request_id,
        ) = check_part_of_fleet_request(client, request_id)
        if is_part_of_fleet_request:
            print(
                "This instance is linked to an active Spot Fleet request, if it is terminated without cancelling the Spot Fleet request, a new instance will be requested"
            )
            print(
                "Should the Spot Fleet Request be cancelled too? Other instances from the fleet will not be terminated, but the fleet will no longer be able to launch new instances."
            )
            if input("(Y/n): ") in ("y", "Y", ""):
                cancel_spot_fleet_request(client, fleet_request_id)
        else:
            if (
                input(
                    "This instance is linked to a persistent Spot instance request, should the request be cancelled too (Y/n): "
                )
                in ("Y", "y", "")
            ):
                cancel_spot_request(client, request_id)
    terminate_instance(client, args.instance_id)
