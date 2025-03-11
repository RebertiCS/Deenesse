"""Deenesse DNS Updater."""
import json
import os

from datetime import datetime
from dotenv import load_dotenv

import requests

load_dotenv()

def main():
    """DNS updater."""

    ipv6 = str(requests.get("https://ipv6.icanhazip.com", timeout=10).content).replace("b\'", '').replace("\\n\'", '')
    ipv4 = str(requests.get("https://icanhazip.com", timeout=10).content).replace("b\'", '').replace("\\n\'", '')
    dns_list = os.getenv("CF_DNS").split(",")

    print("\n# Deenesse v1.0", datetime.now().strftime("%d/%m/%Y - %H:%M"), "\n## Updated IPV6: ", ipv6)

    if ipv4 != ipv6:
        print("## Updated IPV4: ", ipv4)

    req_data = get_config()

    print("# DNS Updates\n")
    for dns in req_data["result"]:
        for dns_name in dns_list:
            if dns_name == dns["name"]:
                if dns["type"] == "AAAA" and dns["content"] != ipv6:
                    update_config(dns["name"], ipv6, dns["id"], dns["type"])
                    print("Name:", dns_name, "\nType:", dns["type"], "\n - Old:",  dns["content"], "\n - New:", ipv6)
                elif dns["type"] == "AAAA":
                    print("Name:", dns_name, "\nType:", dns["type"], '\n - IP', ipv6, "\n - Same IPV6, won't update")

                if dns["type"] == "A" and dns["content"] != ipv4:
                    update_config(dns["name"], ipv4, dns["id"], dns["type"])
                    print("Name:", dns_name, "\nType:", dns["type"], "\n - Old:",  dns["content"], "\n - New:", ipv4)
                elif dns["type"] == "A":
                    print("Name:", dns_name, "\nType:", dns["type"], '\n - IP', ipv4, "\n - Same IPV4, won't update")



def get_config():
    """Get DNS Config from Cloudflare."""

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + os.getenv('CF_KEY'),
    }

    response = requests.get(
        'https://api.cloudflare.com/client/v4/zones/' + os.getenv("CF_ZONE") + '/dns_records', 
        timeout=10,
        headers=headers,
    )

    request_data = json.loads(str(response.content).replace("b\'", "").replace("\'",""))

    print("\n# DNS Configuration\n")

    for data in request_data["result"]:
        print(" - Name: ", data["name"], "\n\t+ Id:\t", data["id"], "\n\t+ Type:\t", data["type"], "\n\t+ IP:\t", data["content"], "\n")

    return request_data


def update_config(dns_name, dns_ip, dns_id, dns_type):
    """Update DNS on Cloudflare servers."""

    cf_proxy = True

    if os.getenv('CF_PROXY') == "False":
        cf_proxy = False

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + os.getenv('CF_KEY'),
    }

    json_data = {
        'comment': 'Domain verification record',
        'content': dns_ip,
        'name': dns_name,
        'proxied': cf_proxy,
        'ttl': 1,
        'type': dns_type,
    }

    requests.patch(
        'https://api.cloudflare.com/client/v4/zones/' + os.getenv('CF_ZONE') + '/dns_records/' + dns_id,
        timeout=10,
        headers=headers,
        json=json_data,
    )


if __name__ == "__main__":
    main()
