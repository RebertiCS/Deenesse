# Deenesse v1.0
Update DNS name using cloudflare API

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

#### Running
```bash
chmod +x deenesse
./deenesse [configuration]
```
