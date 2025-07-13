# Deenesse v1.0
Update DNS name to ipv6 or ipv4 on domain name provider

### Usage
#### Configuration
Create `.env` file containing:

```bash
# Cloudflare API Token
CF_KEY="KEY"

# Cloudflare Zone
CF_ZONE="ZONE_ID"

# Enable Cloudflare Proxy
CF_PROXY="False"

# DNS Managed by the script
CF_DNS="video.example.com,example.com"
```

#### Building
```bash
# Creates Virtual Env
python3-venv .venv

source .venv/bin/YOURSHELL
pip install -r requirements.txt
```

#### Running
```bash
python dns-update.py
```

### Crontab Exemple:
Run `crontab -e` to edit crontab.
```bash
0 * * * * /usr/bin/python3 <Deenesse Folder>/dns_update.py
```
