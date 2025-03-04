import os
import requests
import json

from dotenv import load_dotenv

load_dotenv()


def main()

    request_data = get_config()

    print(request_data)


def get_config():
    headers = {
        'X-Auth-Email': os.environ.get('CF_EMAIL'),
        'X-Auth-Key': os.environ.get('CF_KEY'),
    }

    response = requests.get(
        'https://api.cloudflare.com/client/v4/zones/' + os.environ.get('CF_ZONE') + '/dns_records',
        headers=headers,
    )

    print("Data response:\n", response)
    return response


def update_config():

    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Email': os.getenv.get('CF_EMAIL', ''),
        'X-Auth-Key': os.getenv.get('CF_KEY', ''),
    }

    json_data = {
        'comment': 'Domain verification record',
        'content': '198.51.100.4',
        'name': 'example.com',
        'proxied': True,
        'settings': {
            'ipv4_only': True,
            'ipv6_only': True,
        },
        'tags': [
            'owner:dns-team',
        ],
        'ttl': 3600,
        'type': 'A',
    }

    response = requests.patch(
        'https://api.cloudflare.com/client/v4/zones/' + os.getenv.get('CF_ZONE') + '/dns_records/' + os.getenv('DNS_RECORD_ID', ''),
        headers=headers,
        json=json_data,
    )



if __name__ == "__main__":
    main()