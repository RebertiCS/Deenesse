import os
import requests
import json

from dotenv import load_dotenv

load_dotenv()

global ipv6
global ipv4


def main():

    ipv6 = str(requests.get("https://ipv6.icanhazip.com").content).replace("b\'", '')
    ipv6 = ipv6.replace("\\n\'", '')

    ipv4 = str(requests.get("https://icanhazip.com").content).replace("b\'", '')
    ipv4 = ipv4.replace("\\n\'", '')

    print("# MorpheusDNS v0.1")
    print("## Updated IPV6: ", ipv6)

    if ipv4 != ipv6:
        print("## Updated IPV4: ", ipv4)

    info = get_config()


def get_config():

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + os.getenv('CF_KEY'),
    }

    response = requests.get(
        'https://api.cloudflare.com/client/v4/zones/' + os.getenv("CF_ZONE") + '/dns_records',
        headers=headers,
    )

    request_data = json.loads(str(response.content).replace("b\'", "").replace("\'",""))

    print(request_data)

    dns_config = "{ "

    print("\n# DNS Configuration\n")
    for data in request_data["result"]:
        print(" - Name: ", data["name"], "\n\t+ Id:\t", data["id"], "\n\t+ Type:\t", data["type"], "\n\t+ IP:\t", data["content"], "\n")
        dns_config = dns_config + '{\'name\': \'' + data["name"] + '\',\'id\':\'' + data["id"] + '\' },'

    dns_config = dns_config + '}'

    print(dns_config)

    return request_data


def update_config(dns_name, ip):

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + os.getenv('CF_KEY'),
    }

    json_data = {
        'comment': 'Domain verification record',
        'content': ip,
        'name': dns_name,
        'proxied': False,
        'settings': {
            'ipv4_only': False,
            'ipv6_only': True,
        },
        'tags': [
            'owner:dns-team',
        ],
        'ttl': 3600,
        'type': 'AAAA',
    }

    response = requests.patch(
        'https://api.cloudflare.com/client/v4/zones/' + os.getenv.get('CF_ZONE') + '/dns_records/' + os.getenv('DNS_RECORD_ID', ''),
        headers=headers,
        json=json_data,
    )



if __name__ == "__main__":
    main()