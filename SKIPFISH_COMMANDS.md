# Skipfish Comprehensive Scanning Commands

## Single Command - Full Scan (Recommended)

```bash
skipfish -o results -S /usr/share/skipfish/dictionaries/complete.wl -W /usr/share/skipfish/dictionaries/extensions-only.wl -Y -O -U -G 256 -m 5 -t 20 -w 60 -i 60 -l 200 -g 25 -k 10 https://team-t1-wargames.vercel.app
```

## Authenticated Scan with Login Credentials

```bash
skipfish -o results_auth \
  -I ashishtest1@gmail.com:123456789 \
  -S /usr/share/skipfish/dictionaries/complete.wl \
  -Y -O -U -G 256 -m 5 -t 20 -w 60 \
  https://team-t1-wargames.vercel.app
```

## Scan with Custom Headers (JWT Token)

```bash
skipfish -o results_jwt \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -S /usr/share/skipfish/dictionaries/complete.wl \
  -Y -O -U -G 256 -m 5 \
  https://team-t1-wargames.vercel.app
```

## Aggressive Scan (Maximum Coverage)

```bash
skipfish -o results_aggressive \
  -S /usr/share/skipfish/dictionaries/complete.wl \
  -W /usr/share/skipfish/dictionaries/extensions-only.wl \
  -LVY -O -U -G 512 -m 10 -t 30 -w 120 -i 120 -l 500 -g 50 -k 20 \
  https://team-t1-wargames.vercel.app
```

## Fast Scan (Quick Assessment)

```bash
skipfish -o results_fast \
  -S /usr/share/skipfish/dictionaries/minimal.wl \
  -Y -O -m 2 -t 10 -w 30 \
  https://team-t1-wargames.vercel.app
```

## API-Focused Scan

```bash
skipfish -o results_api \
  -S /usr/share/skipfish/dictionaries/complete.wl \
  -Y -O -U -G 256 -m 5 \
  -X /logout -X /signout \
  https://team-t1-wargames.vercel.app/api/
```

## Scan with Cookie Authentication

```bash
skipfish -o results_cookie \
  -C "session=YOUR_SESSION_COOKIE" \
  -C "token=YOUR_TOKEN" \
  -S /usr/share/skipfish/dictionaries/complete.wl \
  -Y -O -U -G 256 \
  https://team-t1-wargames.vercel.app
```

## Complete Scan with All Features

```bash
skipfish -o results_complete \
  -S /usr/share/skipfish/dictionaries/complete.wl \
  -W /usr/share/skipfish/dictionaries/extensions-only.wl \
  -I ashishtest1@gmail.com:123456789 \
  -C "session=value" \
  -H "Authorization: Bearer TOKEN" \
  -H "X-Custom-Header: value" \
  -Y -O -U -L -V \
  -G 512 -m 10 -t 30 -w 120 -i 120 -l 500 -g 50 -k 20 \
  -X /logout -X /signout -X /exit \
  --log-mixed-content \
  --log-cookies \
  --flush-to-disk \
  https://team-t1-wargames.vercel.app
```

## Parameter Explanation

### Essential Options:
- `-o DIR` - Output directory for results
- `-S FILE` - Signature/wordlist file for scanning
- `-W FILE` - Extension wordlist

### Authentication:
- `-I user:pass` - HTTP Basic authentication
- `-C name=val` - Add custom cookie
- `-H header` - Add custom HTTP header

### Scan Behavior:
- `-Y` - Don't fuzz query parameters in URLs
- `-O` - Don't submit any forms
- `-U` - Disable on-the-fly learning
- `-L` - Don't do any link extraction
- `-V` - Verbose mode

### Performance:
- `-G num` - Max simultaneous connections (default: 16)
- `-m num` - Max requests per second (default: unlimited)
- `-t num` - Total request timeout in seconds
- `-w num` - Individual response timeout
- `-i num` - Idle timeout for connections
- `-l num` - Max requests per keyword
- `-g num` - Max consecutive failed requests
- `-k num` - Max crawl tree depth

### Exclusions:
- `-X /path` - Exclude specific path from scan

### Advanced:
- `--log-mixed-content` - Log mixed content issues
- `--log-cookies` - Log cookie operations
- `--flush-to-disk` - Flush report to disk periodically

## Installation (if not installed)

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install skipfish

# From source
git clone https://github.com/spinkham/skipfish.git
cd skipfish
make
sudo make install
```

## Usage Workflow

1. **Start with Fast Scan** to get quick overview:
   ```bash
   skipfish -o quick_scan -S /usr/share/skipfish/dictionaries/minimal.wl -Y -O https://team-t1-wargames.vercel.app
   ```

2. **Login and Get Token** (manual step):
   - Login via browser
   - Extract JWT token from localStorage
   - Extract session cookies

3. **Run Authenticated Scan**:
   ```bash
   skipfish -o auth_scan -H "Authorization: Bearer YOUR_TOKEN" -S /usr/share/skipfish/dictionaries/complete.wl -Y -O -U -G 256 https://team-t1-wargames.vercel.app
   ```

4. **Review Results**:
   - Open `results/index.html` in browser
   - Check high/medium severity findings
   - Focus on authentication/authorization issues

## Alternative: Using with Proxy (Burp Suite)

```bash
# Route through Burp Suite for manual inspection
skipfish -o results_proxy \
  -J 127.0.0.1:8080 \
  -S /usr/share/skipfish/dictionaries/complete.wl \
  -Y -O -U \
  https://team-t1-wargames.vercel.app
```

## Best Practice Command for This Target

```bash
# Step 1: Get JWT token first
# Login at https://team-t1-wargames.vercel.app
# Open DevTools > Application > Local Storage
# Copy the JWT token

# Step 2: Run comprehensive authenticated scan
skipfish -o team_t1_scan_$(date +%Y%m%d_%H%M%S) \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -S /usr/share/skipfish/dictionaries/complete.wl \
  -W /usr/share/skipfish/dictionaries/extensions-only.wl \
  -Y -O -U -G 256 -m 5 -t 30 -w 60 -i 60 -l 200 -g 25 -k 10 \
  -X /logout -X /signout \
  https://team-t1-wargames.vercel.app

# Step 3: Open results
# firefox team_t1_scan_*/index.html
```

## Expected Findings

Skipfish will detect:
- XSS vulnerabilities
- SQL injection points
- Directory traversal
- Authentication bypasses
- CSRF vulnerabilities
- Information disclosure
- Insecure configurations
- Hidden directories/files
- API endpoints
- Admin panels

## Notes

- Skipfish is aggressive - use only on authorized targets
- Rate limiting may affect scan completeness
- For SPAs (like this React app), results may be limited
- Combine with manual testing for best results
- Check robots.txt and sitemap.xml first
- Use authenticated scans for better coverage
