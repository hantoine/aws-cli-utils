cp -v aws-* /usr/local/bin/
mkdir -p /etc/aws-cli-utils/
cp -iv default-aws-request.json.ejs /etc/aws-cli-utils/
cp -iv gpu-small-aws-request.json.ejs /etc/aws-cli-utils/
cp -iv ami-users /etc/aws-cli-utils/
ln -s /usr/local/bin/aws-request-v1 /usr/local/bin/aws-request
