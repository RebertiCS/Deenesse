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

    req_data = get_config()

    print("# DNS Updates\n")
    for dns in req_data["result"]:
        if os.getenv("CF_DNS") == dns["name"]:
            if dns["type"] == "AAAA":
                print(" - IPv6:", os.getenv("CF_DNS"), "to", ipv6)
                update_config(dns["name"], ipv6, dns["id"])

            elif dns["type"] == "A":
                print(" - IPv4:", os.getenv("CF_DNS"), "to", ipv4)
                #update_config(dns["name"], ipv4)


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

    print("\n# DNS Configuration\n")

    for data in request_data["result"]:
        print(" - Name: ", data["name"], "\n\t+ Id:\t", data["id"], "\n\t+ Type:\t", data["type"], "\n\t+ IP:\t", data["content"], "\n")

    return request_data


def update_config(dns_name, dns_ip, dns_id):

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + os.getenv('CF_KEY'),
    }

    json_data = {
        'comment': 'Domain verification record',
        'content': dns_ip,
        'name': dns_name,
        'proxied': False,
        'ttl': 1,
        'type': 'AAAA',
    }

    response = requests.patch(
        'https://api.cloudflare.com/client/v4/zones/' + os.getenv('CF_ZONE') + '/dns_records/' + dns_id,
        headers=headers,
        json=json_data,
    )

    print(response.content)



if __name__ == "__main__":
    main()