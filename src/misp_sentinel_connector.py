import os
import requests
import urllib3
from datetime import datetime, timezone

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TENANT_ID = os.environ.get("TENANT_ID")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
WORKSPACE_ID = os.environ.get("WORKSPACE_ID")
MISP_URL = os.environ.get("MISP_URL", "https://<CTI_NODE_IP>")
MISP_KEY = os.environ.get("MISP_KEY")


def get_entra_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://management.azure.com/.default",
        "grant_type": "client_credentials",
    }
    response = requests.post(url, data=payload, timeout=30)
    response.raise_for_status()
    return response.json().get("access_token")


def fetch_misp_ip_indicators(limit=100):
    url = f"{MISP_URL.rstrip('/')}/attributes/restSearch"
    headers = {
        "Authorization": MISP_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    body = {
        "returnFormat": "json",
        "type": ["ip-dst", "ip-src"],
        "to_ids": 1,
        "limit": limit,
    }
    response = requests.post(url, headers=headers, json=body, verify=False, timeout=60)
    response.raise_for_status()
    attributes = response.json().get("response", {}).get("Attribute", [])
    return attributes


def build_stix_indicators(attributes):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    indicators = []
    for attr in attributes:
        ip_val = attr.get("value")
        uuid = attr.get("uuid")
        if not ip_val or not uuid:
            continue
        indicators.append(
            {
                "type": "indicator",
                "spec_version": "2.1",
                "id": f"indicator--{uuid}",
                "created": now,
                "modified": now,
                "name": f"MISP IOC: {ip_val}",
                "pattern": f"[ipv4-addr:value = '{ip_val}']",
                "pattern_type": "stix",
                "valid_from": now,
                "confidence": 100,
                "labels": ["misp-osint", "malicious-ip"],
            }
        )
    return indicators


def push_to_sentinel(token, stix_objects):
    url = (
        f"https://sentinelus.azure-api.net/workspaces/{WORKSPACE_ID}"
        f"/threatintelligenceindicators:upload?api-version=2022-07-01"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "sourcesystem": "MISP-Homelab-CTI",
        "value": stix_objects,
    }
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.status_code


if __name__ == "__main__":
    raw_attrs = fetch_misp_ip_indicators()
    stix_batch = build_stix_indicators(raw_attrs)
    print(f"[+] Fetched {len(stix_batch)} STIX indicators from MISP ({MISP_URL}).")
    if all([TENANT_ID, CLIENT_ID, CLIENT_SECRET, WORKSPACE_ID]):
        access_token = get_entra_token()
        status = push_to_sentinel(access_token, stix_batch)
        print(f"[+] Uploaded indicators to Microsoft Sentinel (HTTP {status}).")
    else:
        print("[!] Cloud credentials not set yet. Dry-run completed locally.")
