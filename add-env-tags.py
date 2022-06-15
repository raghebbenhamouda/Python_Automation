import boto3

# Function that tags all the instances from the Region with a specific tag

def tag_ec2_servers(region, tag_key, tag_value):
    ec2_client = boto3.client('ec2',region_name=region)
    ec2_resource = boto3.resource('ec2',region_name=region)

    instance_ids = [] 

    reservations = ec2_client.describe_instances()['Reservations']

    for res in reservations:
        instances = res['Instances']
        for ins in instances:
            """
            Collect all Instances Ids into a list, then add tags for all instances at once.
            Because making one request to update 100 servers is more efficient than making
            One request for each server.
            """
            instance_ids.append(ins['InstanceId'])

    response = ec2_resource.create_tags(
        Resources= instance_ids,
        Tags=[
            {
                'Key': tag_key,
                'Value': tag_value
            },
        ]
    )


# Tag all the instances from the Paris Region with env="prod"

tag_ec2_servers("eu-west-3", "test", "function")

# Tag all the instances from the Frankfurt Region with env="dev"

tag_ec2_servers("eu-central-1", "test", "function")