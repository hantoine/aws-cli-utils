if [ -z ${AWS_CLI_UTILS_DEFAULT_LAUNCH_TEMPLATE_ID} ] ; then
	echo "Please enter the ID of the launch template that aws-request should use by default:"
	read AWS_CLI_UTILS_DEFAULT_LAUNCH_TEMPLATE_ID
fi
cp -v aws-* /usr/local/bin/
mkdir -p /etc/aws-cli-utils/
cp -v default-aws-request.json /etc/aws-cli-utils/
sed -i "s/<%= DEFAULT_LAUNCH_TEMPLATE_ID %>/${AWS_CLI_UTILS_DEFAULT_LAUNCH_TEMPLATE_ID}/" /etc/aws-cli-utils/default-aws-request.json
