# Deenesse
Update DNS IPv6 using cloudflare API

## Usage
### Installing

#### Building from source
```bash
go build .
chmod +x deenesse
sudo install deenesse /usr/bin/
```

#### Installing Debian Package
```bash
dkpk -i --install deenesse-<VERSION>.deb
```

### Running
```bash
deenesse <CONFIG_FILE>
```

#### Configuration
Create config file in `/etc/deenesse/` (eg `dns-test.conf`) file containing:
```bash
# Network device to get ipv6
NETWORK_DEVICE="enp0s0" # Actual host device showed in ip addr

# Cloudflare API Token
CF_KEY="KEY"

# Cloudflare Zone
CF_ZONE="ZONE_ID"

# Enable Cloudflare Proxy
CF_PROXY="False"

# Target DNS
CF_DNS="video.example.com,example.com"
```

#### Systemctl
```bash
sudo systemctl enable --now deenesse@<CONFIG_FILE>.timer
sudo systemctl enable --now deenesse@<CONFIG_FILE>.service
```
