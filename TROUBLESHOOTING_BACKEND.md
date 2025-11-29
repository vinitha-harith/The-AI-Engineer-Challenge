# Troubleshooting Backend Connection Issues

## Problem: Backend not reachable at http://51.154.17.25:8000

### Quick Checks

1. **Is the server running?**
   ```bash
   lsof -i :8000
   ```
   Should show a process listening on port 8000.

2. **Is it accessible locally?**
   ```bash
   curl http://localhost:8000/
   ```
   Should return: `{"status": "ok"}`

3. **Is it accessible from your local network IP?**
   ```bash
   # Find your local IP
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Test from another device on same network
   curl http://YOUR_LOCAL_IP:8000/
   ```

### Common Issues & Solutions

#### Issue 1: Firewall Blocking Port 8000

**On Mac:**
1. System Settings → Network → Firewall → Options
2. Click "+" to add an application
3. Find Python or Terminal
4. Set to "Allow incoming connections"
5. Or temporarily disable firewall to test

**On Linux:**
```bash
# Check firewall status
sudo ufw status

# Allow port 8000
sudo ufw allow 8000

# Or for specific IP
sudo ufw allow from 51.154.17.25 to any port 8000
```

**On Windows:**
1. Windows Defender Firewall → Advanced Settings
2. Inbound Rules → New Rule
3. Port → TCP → 8000 → Allow

#### Issue 2: Router Port Forwarding Not Configured

If `51.154.17.25` is your router's public IP:

1. **Find your local machine's IP:**
   ```bash
   # Mac/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Windows
   ipconfig
   ```
   Look for something like `192.168.1.100` or `10.0.0.5`

2. **Configure Router Port Forwarding:**
   - Access router admin panel (usually `192.168.1.1` or `192.168.0.1`)
   - Find "Port Forwarding" or "Virtual Server" settings
   - Add rule:
     - **External Port**: 8000
     - **Internal IP**: Your local machine IP (e.g., `192.168.1.100`)
     - **Internal Port**: 8000
     - **Protocol**: TCP
   - Save and restart router if needed

3. **Verify the public IP:**
   ```bash
   curl ifconfig.me
   # Should show 51.154.17.25 (or your actual public IP)
   ```

#### Issue 3: Server Not Binding to 0.0.0.0

Make sure you're using:
```bash
uv run uvicorn api.index:app --host 0.0.0.0 --port 8000 --reload
```

**NOT:**
```bash
# ❌ This only binds to localhost
uv run uvicorn api.index:app --reload
```

#### Issue 4: ISP Blocking Incoming Connections

Some ISPs block incoming connections on residential connections. You may need to:
- Use a VPN
- Use a cloud service (Vercel, AWS, etc.)
- Contact your ISP about port forwarding

### Testing Steps

1. **Test locally:**
   ```bash
   curl http://localhost:8000/
   ```

2. **Test from local network:**
   ```bash
   # On another device on same WiFi
   curl http://YOUR_LOCAL_IP:8000/
   ```

3. **Test from internet:**
   ```bash
   # From a different network (or use online tool)
   curl http://51.154.17.25:8000/
   ```

4. **Check if port is open:**
   ```bash
   # From external network
   telnet 51.154.17.25 8000
   # Or use online port checker: https://www.yougetsignal.com/tools/open-ports/
   ```

### Alternative: Use ngrok for Testing

If port forwarding is complex, use ngrok for quick testing:

```bash
# Install ngrok
brew install ngrok  # Mac
# or download from https://ngrok.com

# Start your backend
uv run uvicorn api.index:app --host 0.0.0.0 --port 8000 --reload

# In another terminal, create tunnel
ngrok http 8000

# Use the ngrok URL (e.g., https://abc123.ngrok.io)
```

### Security Considerations

⚠️ **Warning**: Exposing your backend to the internet has security risks:

1. **Add authentication** - Don't expose OpenAI API without rate limiting/auth
2. **Use HTTPS** - Set up SSL certificate (Let's Encrypt)
3. **Rate limiting** - Prevent abuse
4. **Firewall rules** - Only allow necessary IPs if possible

### Recommended: Use Vercel Instead

For production, consider deploying to Vercel:
- Automatic HTTPS
- No port forwarding needed
- Better security
- See `BACKEND_DEPLOYMENT.md` for instructions

