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
    print(
        "# Deenesse v1.1",
        datetime.now().strftime("%d/%m/%Y - %H:%M"),
    )

    try:
        ipv6 = requests.get("https://ipv6.icanhazip.com", timeout=60).text
        print(f"[ {datetime.now()} ] IPV6: {ipv6}")
    except requests.exceptions.Timeout:
        print(f"[ {datetime.now()} ] Connection timeout while getting IPv6")

    try:
        ipv4 = requests.get("https://icanhazip.com", timeout=60).text
        if len(ipv4) > 15:
            print(f"[ {datetime.now()} ] Coudn't get IPv4")
            ipv4 = None

        else:
            print(f"[ {datetime.now()} ] IPv4: {ipv4}")

    except requests.exceptions.Timeout:
        print(f"[ {datetime.now()} ] Connection timeout while getting IPv4")

    try:
        dns_list = os.getenv("CF_DNS").split(",")
    except KeyError:
        print(f"[ {datetime.now()} ] Wrong configuration CF_DNS")
        return

    if ipv4:
        print("## IPV4: ", ipv4)

    req_data = get_config()

    if req_data is None:
        print(f"[ {datetime.now()} ] Failed to retrieve configuration")
        return

    print(f"[ {datetime.now()} ] DNS Updates:")

    for dns in req_data["result"]:
        for dns_name in dns_list:
            if dns_name == dns["name"]:
                if dns["type"] == "AAAA" and ipv6 is not None:
                    # Update IPv6 if it has changed
                    if dns["content"] != ipv6:
                        update_config(dns["name"], ipv6, dns["id"], dns["type"])

                        print(
                            f"Name:{dns_name} \n Type: {dns['type']}",
                            f"\n - Old: {dns['content']} \n - New: {ipv6}",
                        )

                    else:
                        print(
                            f"Name: {dns_name} \nType: {dns['type']}",
                            f"\n - IP {ipv6} \n - Same IPv6, won't update",
                        )
                elif ipv4 is not None:
                    # Update IPv4 if it has changed
                    if dns["content"] != ipv4:
                        update_config(dns["name"], ipv4, dns["id"], dns["type"])

                        print(
                            f"Name: {dns_name} \nType: {dns['type']} ",
                            f"\n - Old: {dns['content']} \n - New: {ipv4}",
                        )

                    else:
                        print(
                            f"Name: {dns_name} \nType: {dns['type']} ",
                            f"\n - IP {ipv4} \n - Same IPv4, won't update",
                        )


def get_config():
    """Get DNS Config from Cloudflare."""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.getenv("CF_KEY"),
        }
    except KeyError:
        print(f"[ {datetime.now()} ] Wrong configuration CF_KEY")
        return None

    try:
        api_url = CF_URL + os.getenv("CF_ZONE") + "/dns_records"
    except KeyError:
        print(f"[ {datetime.now()} ] Wrong configuration CF_ZONE")
        return None

    try:
        response = requests.get(
            api_url,
            timeout=60,
            headers=headers,
        )
    except requests.exceptions.Timeout:
        print(f"[ {datetime.now()} ] Connection timeout while getting zone")

        return None

    request_data = json.loads(sanitize_get(response.content))

    print(f"[ {datetime.now()} ] DNS Configuration")

    # Show information about DNS Server
    for data in request_data["result"]:
        print(
            f" - Name: {data['name']} \n\t+ Id:\t {data['id']}",
            f"\n\t+ Type:\t {data['type']} \n\t+ IP:\t {data['content']}",
        )

    return request_data


def update_config(dns_name, dns_ip, dns_id, dns_type):
    """Update DNS on Cloudflare servers."""
    try:
        cf_proxy = os.getenv("CF_PROXY")
    except KeyError:
        print(f"[ {datetime.now()} ] Wrong configuration CF_PROXY")
        return

    if cf_proxy == "True":
        cf_proxy = True
    else:
        cf_proxy = False

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.getenv("CF_KEY"),
        }
    except KeyError:
        print(f"[ {datetime.now()} ] Wrong configuration CF_KEY")

        return

    json_data = {
        "comment": "Domain verification record",
        "content": dns_ip,
        "name": dns_name,
        "proxied": cf_proxy,
        "ttl": 1,
        "type": dns_type,
    }

    try:
        api_url = CF_URL + os.getenv("CF_ZONE") + "/dns_records/" + dns_id
    except KeyError:
        print(f"[ {datetime.now()} ] Wrong configuration CF_ZONE")

        return

    requests.patch(
        api_url,
        timeout=10,
        headers=headers,
        json=json_data,
    )


def sanitize_get(get_data):
    """Remove unneded characters from get requests."""
    return str(get_data).replace("b'", "").replace("'", "")


if __name__ == "__main__":
    main()
