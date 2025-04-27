#!/usr/bin/python3
"""Deenesse DNS Updater."""
import json
import os

from datetime import datetime
from dotenv import load_dotenv

import requests

load_dotenv()

CF_URL = "https://api.cloudflare.com/client/v4/zones/"


def main():
    """DNS updater."""
    ipv6_req = requests.get("https://ipv6.icanhazip.com", timeout=10).content
    ipv6 = str(sanitize_get(ipv6_req)).replace("\\n", "")

    ipv4_req = requests.get("https://icanhazip.com", timeout=10).content
    ipv4 = str(sanitize_get(ipv4_req)).replace("\\n", "")

    dns_list = os.getenv("CF_DNS").split(",")

    print("\n# Deenesse v1.0", datetime.now().strftime("%d/%m/%Y - %H:%M"),
          "\n## IPV6: ", ipv6)

    if ipv4 != ipv6:
        print("## IPV4: ", ipv4)

    req_data = get_config()

    print("# DNS Updates\n")
    for dns in req_data["result"]:
        for dns_name in dns_list:
            if dns_name == dns["name"]:

                if dns["type"] == "AAAA":
                    # Update IPv6 if it has changed
                    if dns["content"] != ipv6:
                        update_config(dns["name"], ipv6, dns["id"], dns["type"])

                        print("Name:", dns_name,
                              "\nType:", dns["type"],
                              "\n - Old:",  dns["content"],
                              "\n - New:", ipv6)

                    # Logs when the IPv6 dind't change
                    else:
                        print("Name:", dns_name,
                              "\nType:", dns["type"],
                              "\n - IP", ipv6,
                              "\n - Same IPv6, won't update")

                else:
                    # Update IPv4 if it has changed
                    if dns["content"] != ipv4:
                        update_config(dns["name"], ipv4, dns["id"], dns["type"])

                        print("Name:", dns_name,
                              "\nType:", dns["type"],
                              "\n - Old:",  dns["content"],
                              "\n - New:", ipv4)

                    # Logs when the IPv4 dind't change
                    else:
                        print("Name:", dns_name,
                              "\nType:", dns["type"],
                              "\n - IP", ipv4,
                              "\n - Same IPv4, won't update")


def get_config():
    """Get DNS Config from Cloudflare."""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + os.getenv('CF_KEY'),
    }

    api_url = CF_URL + os.getenv("CF_ZONE") + '/dns_records'

    response = requests.get(
        api_url,
        timeout=10,
        headers=headers,
    )

    request_data = json.loads(sanitize_get(response.content))

    print("\n# DNS Configuration\n")

    # Show information about DNS Server
    for data in request_data["result"]:
        print(" - Name: ", data["name"],
              "\n\t+ Id:\t", data["id"],
              "\n\t+ Type:\t", data["type"],
              "\n\t+ IP:\t", data["content"],
              "\n")

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

    api_url = CF_URL + os.getenv('CF_ZONE') + '/dns_records/' + dns_id

    requests.patch(
        api_url,
        timeout=10,
        headers=headers,
        json=json_data,
    )


def sanitize_get(get_data):
    """Remove unneded characters from get requests."""

    return str(get_data).replace("b\'", "").replace("\'", "")


if __name__ == "__main__":
    main()
