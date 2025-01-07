#!/usr/bin/env python3
import os
import random
import subprocess
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


def read_number():
    if not os.path.exists('number.txt'):
        write_number(0)  # Initialize if file doesn't exist
    with open('number.txt', 'r') as f:
        return int(f.read().strip())


def write_number(num):
    with open('number.txt', 'w') as f:
        f.write(str(num))


def git_commit():
    try:
        subprocess.run(['git', 'add', 'number.txt'], check=True)
        date = datetime.now().strftime('%Y-%m-%d')
        commit_message = f"Update number: {date}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during git commit: {e}")
        exit(1)


def git_push():
    try:
        result = subprocess.run(['git', 'push'], capture_output=True, text=True, check=True)
        print("Changes pushed to GitHub successfully.")
    except subprocess.CalledProcessError as e:
        print("Error pushing to GitHub:")
        print(e.stderr)
        exit(1)


def update_cron_with_random_time():
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    new_cron_command = f"{random_minute} {random_hour} * * * cd {script_dir} && python3 {os.path.join(script_dir, 'update_number.py')}\n"

    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout
    except subprocess.CalledProcessError:
        current_cron = ""  # No existing cron jobs

    updated_cron = ""
    for line in current_cron.splitlines():
        if "update_number.py" not in line:
            updated_cron += line + "\n"
    updated_cron += new_cron_command

    with open('/tmp/new_cron', 'w') as cron_file:
        cron_file.write(updated_cron)

    subprocess.run(['crontab', '/tmp/new_cron'])
    os.remove('/tmp/new_cron')

    print(f"Cron job updated to run at {random_hour:02}:{random_minute:02}.")


def main():
    try:
        current_number = read_number()
        new_number = current_number + 1
        write_number(new_number)

        git_commit()
        git_push()

        update_cron_with_random_time()

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()