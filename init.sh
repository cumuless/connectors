cd /home/ubuntu
mkdir connectors
cd connectors

sudo apt-get install python3 python3-venv python3-pip 

python3 -m venv venv
source venv/bin/activate

pip install python-dotenv asyncio boto3 pymilvus==2.4.3

