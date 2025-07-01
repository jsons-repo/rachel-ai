# Local LAN Setup

[Installation](install.md)

[Configure LAN setup](lan_setup.md)

[Getting Started](getting_started.md)

[How It Works](how_it_works.md)

[config.yaml Reference](docs/config.md)

To actually use Rachel during a live podcast (or any real-time conversation) you need to make it accessible to people on your local network, so they can open their browsers and see it. After completing these steps, anyone on your network should be able to simply open a browser, visit the URL you've set up, and view Rachel’s transcription and analysis in real time.

## Linux Setup

### 1. Install `avahi`
```bash
sudo apt update
sudo apt install avahi-daemon
sudo systemctl enable --now avahi-daemon
```

Verify its running (optional)
```bash
systemctl status avahi-daemon
```
> You should see 'You should see: active (running)' towards the top of the response

### 2. Check your hostname
```bash
hostname
```

The URL that viewers use to view the Rachel app will be [hostname].local

To verify, try to ping this from another device on your network:
```bash
# If hostname was json-linux
ping jason-linux.local
```

### 3. Change your host name (optional)
If you want to have a more user-friendly URL for your viewers to use, these steps will allow you to create a custom named url. For sake of simplicity, these instructions will create a url `rachel` but you can easily change it to whatever you want.

1. **Create a service definition in avahi**
```bash
sudo vim /etc/avahi/services/rachel-http.service
```

2. **Paste/enter this**
```xml
<?xml version="1.0" standalone='no'?><!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name>rachel</name>
  <service>
    <type>_http._tcp</type>
    <port>6677</port>
  </service>
</service-group>
```
- The `<name>` becomes `rachel.local`
- Port should match whatever is in your `config.yaml` for `network.fe.port`
- Note: _this does not affect_ your actual hostnames or `/etc/hosts`

3. **Update Avahi main config**
```bash
sudo vim /etc/avahi/avahi-daemon.conf
# Add or edit the [server] section:
# [server]
# host-name=rachel
```
4. **Restart Avahi**
```bash
sudo systemctl restart avahi-daemon
```

5. **Verify (from another device on your network)**
```bash
ping rachel.local
```

Or try in browser:
```bash
http://rachel.local:6677
```

