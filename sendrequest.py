import boto3
import requests

# Initialize AWS SDK clients
autoscaling_client = boto3.client('autoscaling', region_name='us-west-2')
ec2_client = boto3.client('ec2', region_name='us-west-2')

# Specify the Auto Scaling group name
auto_scaling_group_name = 'Raft'

# Retrieve the private IP addresses of the instances in the Auto Scaling group
response = autoscaling_client.describe_auto_scaling_groups(AutoScalingGroupNames=[auto_scaling_group_name])
instances = response['AutoScalingGroups'][0]['Instances']
private_ips = [instance['PrivateIpAddress'] for instance in instances]

# Retrieve the status of each Raft node
statuses = []
for private_ip in private_ips:
    url = f"http://{private_ip}:5000/status/raft"
    response = requests.get(url)
    status = response.json()
    statuses.append(status)

# Find the leader node
leader_node = None
for status in statuses:
    if status["is_current_node_leader"]:
        leader_node = status["self"]
        break

if leader_node:
    # Send a POST request to the leader node
    url = f"http://{leader_node}:5000/tasks"
    response = requests.post(url, json={"token": 2})
    if response.status_code == 200:
        print("Task sent successfully to the leader node.")
    else:
        print("Failed to send the task to the leader node.")
else:
    print("No leader node found.")

