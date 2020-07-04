# AWS CLI utils
Bash scripts to quickly request and manage EC2 spot instances from the command line.
  - `aws-list`: List EC2 instances currently running.
  - `aws-request`:  Request an EC2 Spot instance and SSH to it. Use the cheapest availability zone and instance type from configuration.
  - `aws-ssh`: SSH to an EC2 instance. By default connect to the first instance returned by `aws-list`.
  - `aws-price`: Display the current Spot price of an instance type in an availability zone. Support glob patterns. 
  - `aws-list-requests`: List Spot Fleet requests.
  - `aws-cancel-requests`: Cancel Spot Fleet requests.
  - `aws-terminate`: Terminate EC2 instances.
  

## Installation:
  0. If you don't already have it, install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html "Installing the AWS CLI version 2 on Linux") and [configure it](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html "Configuration basics").
  1. Clone this repository
  2. Execute `sudo ./install.sh` from the root of the repos.


## Configuration
  The configuration files are located in `/etc/aws-cli-utils/`:
  - `default-aws-request.json`: [Spot Fleet configurations](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-fleet-examples.html) used by `aws-request` by default.
  - `*-aws-request.json`: Additional Spot Fleet configurations to use with `aws-request`. Can be exported from the [AWS Management console](https://console.aws.amazon.com/ec2sp/v2/home?#/spot/launch "EC2 Spot instances request creation").
