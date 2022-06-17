import requests
import smtplib  # to send email
import os
import paramiko
import boto3
import time
import schedule


EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv("APP_PASSWORD")


def restart_server():
    # rebot EC2 server
    ec2_client = boto3.client('ec2', region_name="eu-west-3")
    my_ec2_instance_id = ['i-08a4d80135bdd0dd6']
    response = ec2_client.reboot_instances(
        InstanceIds=my_ec2_instance_id
    )


def send_notification(email_msg):
    # Configure your email provider and it's port
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()  # encrypt the communicatin between python and our email server
        smtp.ehlo()  # Identifies our python with the email server
        smtp.login(EMAIL, PASSWORD)
        msg_email = f"Subject: SITE DOWN\n{email_msg}."
        smtp.sendmail(EMAIL, EMAIL, msg_email)  # send email to ourself


def restart_container():
    print('Restarting the application...')
    """ restart the application:
                1- connect to the server
                2- run docker start
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='13.37.250.12', username='ec2-user',
                key_filename='/home/ragheb/.ssh/aws-ec2-key.pem')
    stdin, stdout, stderr = ssh.exec_command('docker restart 7153d10b699a')
    """
    stdin is what we type in our terminal
    stdout is what we get from the terminal 
    stderr if we get an error 
    """
    print(stdout.readlines())
    ssh.close()
    print("Application restarted successfully")


# handle connection errors with try execpt and send email in case of Timeout ...
def monitor_applicaton():
    try:
        response = requests.get(
            'http://ec2-13-37-250-12.eu-west-3.compute.amazonaws.com:8080/')

        if response.status_code == 200:
            print("Applicatio is runnig successfully!")
        else:
            msg = f"Application returned {response.status_code}"
            send_notification(msg)
            restart_container()

    except Exception as ex:    # Exception is a Python objects that represents an error
        print(f"Connection error happened {ex}")
        msg = f"Application not accessible."
        send_notification(msg)
        restart_server()


schedule.every(5).minutes.do(monitor_applicaton)

while True:
    schedule.run_pending()
