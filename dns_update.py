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
    ipv6 = get_ipv6()
    req_data = get_config()

    if req_data is None:
        print(f"[ {datetime.now()} ] Failed to retrieve configuration")
        return

    print(f"[ {datetime.now()} ] DNS Updates:")

    try:
        dns_list = os.getenv("CF_DNS").split(",")
    except KeyError:
        print(f"[ {datetime.now()} ] Wrong configuration CF_DNS")
        return

    update_list = [dns for dns in req_data if dns["name"] in dns_list]

    for dns in update_list:
        if dns["content"] != ipv6:
            update_config(dns["name"], ipv6, dns["id"])
            print(f"[ {datetime.now()} ] Updated: {dns['name']}")
        else:
            print(f"[ {datetime.now()} ] No change: {dns['name']}")


def get_config():
    """Get DNS Config from Cloudflare."""
    try:
        cf_key = os.getenv("CF_KEY")
        cf_zone = os.getenv("CF_ZONE")
    except KeyError:
        print(f"[ {datetime.now()} ] Wrong configuration")
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cf_key}",
    }

    api_url = f"{CF_URL}{cf_zone}/dns_records"

    try:
        response = requests.get(
            api_url,
            timeout=60,
            headers=headers,
        )
    except requests.exceptions.Timeout:
        print(f"[ {datetime.now()} ] Connection timeout while getting zone")

        return None

    return json.loads(sanitize_get(response.content))["result"]


def update_config(dns_name, dns_ip, dns_id):
    """Update DNS on Cloudflare servers."""
    try:
        cf_proxy = os.getenv("CF_PROXY")
        cf_key = os.getenv("CF_KEY")
        cf_zone = os.getenv("CF_ZONE")
    except KeyError:
        print(f"[ {datetime.now()} ] Wrong configuration")
        return

    if cf_proxy == "True":
        cf_proxy = True
    else:
        cf_proxy = False

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cf_key}",
    }

    json_data = {
        "comment": "Domain verification record",
        "content": dns_ip,
        "name": dns_name,
        "proxied": cf_proxy,
        "ttl": 1,
        "type": "AAAA",
    }

    api_url = f"{CF_URL}{cf_zone}/dns_records/{dns_id}"

    requests.patch(
        api_url,
        timeout=10,
        headers=headers,
        json=json_data,
    )


def get_ipv6():
    """Get ipv6 from externel server."""
    ipv6 = None

    try:
        ipv6 = requests.get("https://ipv6.icanhazip.com", timeout=60).text
        print(f"[ {datetime.now()} ] IPv6: {ipv6}")
    except requests.exceptions.Timeout:
        print(f"[ {datetime.now()} ] Connection timeout while getting IPv6")

    return ipv6


def sanitize_get(get_data):
    """Remove unneded characters from get requests."""
    return str(get_data).replace("b'", "").replace("'", "")


if __name__ == "__main__":
    main()
