# LiveKit Local Server Setup Guide

## Option 1: Docker Setup (Recommended)

### Prerequisites
- Docker Desktop installed
- Docker Compose installed

### Steps

1. **Create Docker Compose file:**
```yaml
version: '3.8'
services:
  livekit:
    image: livekit/livekit-server:latest
    container_name: livekit-server
    ports:
      - "7880:7880"
      - "7881:7881"
      - "7882:7882/udp"
    environment:
      - LIVEKIT_CONFIG=/etc/livekit.yaml
    volumes:
      - ./livekit.yaml:/etc/livekit.yaml
    command: --config /etc/livekit.yaml
```

2. **Create LiveKit configuration file (livekit.yaml):**
```yaml
port: 7880
bind_addresses:
  - ""

rtc:
  tcp_port: 7881
  port_range_start: 50000
  port_range_end: 60000
  use_external_ip: false

redis:
  address: localhost:6379

keys:
  devkey: secret

log_level: info

room:
  auto_create: true
  join_timeout: 45s
  empty_timeout: 5m
  max_participants: 100

audio:
  # audio settings
  update_interval: 100ms

development: true
```

3. **Start the server:**
```bash
docker-compose up -d
```

## Option 2: Direct Binary Installation

### Windows
1. Download LiveKit server binary from: https://github.com/livekit/livekit-server/releases
2. Extract to a folder (e.g., C:\livekit)
3. Create config file as above
4. Run: `livekit-server.exe --config livekit.yaml`

### Configuration for Development
- Server URL: ws://localhost:7880
- API Key: devkey
- API Secret: secret

## Option 3: npm/yarn Installation (Lightweight)

```bash
npm install -g @livekit/livekit-server
# or
yarn global add @livekit/livekit-server

# Start server
livekit-server --dev --bind 0.0.0.0 --port 7880
```

## Environment Variables
Add these to your .env file:

```
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

## Testing Connection
1. Start LiveKit server
2. Start your FastAPI backend: `python enhanced_backend.py`
3. Open: http://localhost:8002/live-local
4. Click "Connect to LiveKit" - should show "Connected"

## Troubleshooting

### Common Issues:
1. **Port conflicts**: Change ports in config if 7880 is in use
2. **Firewall**: Allow ports 7880-7882 through Windows Firewall
3. **Docker issues**: Ensure Docker Desktop is running
4. **Permission issues**: Run command prompt as Administrator

### Logs:
- Docker: `docker logs livekit-server`
- Direct binary: Check console output
- Browser: Open Developer Tools > Console

### Network Configuration:
If accessing from other devices on local network, update:
- Change `bind_addresses` to your local IP
- Update `LIVEKIT_URL` to use your IP instead of localhost
