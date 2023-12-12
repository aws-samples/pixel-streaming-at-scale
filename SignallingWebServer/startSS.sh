cd /usr/customapps

echo 'shutdown configured !'

cd pixelstreaming

git pull https://git-codecommit.ap-south-1.amazonaws.com/v1/repos/pixelstreaming

TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
INSTANCE_ID=`curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/meta-data/instance-id`

cd /usr/customapps/pixelstreaming/SignallingWebServer/platform_scripts/bash
chmod +x Start_WithTURN_SignallingServer.sh
./Start_WithTURN_SignallingServer.sh --UseMatchmaker=true --MatchmakerAddress=$1 --AWSInstanceID=$INSTANCE_ID