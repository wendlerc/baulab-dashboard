# GPU Dashboard (static frontend)

Deploy this folder to GitHub Pages. The frontend fetches GPU status from your backend API.

## Setup

1. **Edit `config.js`** — set `GPU_DASHBOARD_API` to your cloudflared tunnel URL:
   ```javascript
   window.GPU_DASHBOARD_API = "https://your-actual-url.trycloudflare.com";
   ```

2. **Deploy to GitHub Pages** — either:
   - Push the `public` folder to a repo and set Pages to publish from the root or `/public` folder, or
   - Copy these files into your repo’s `docs/` folder (if using GitHub Pages with `docs`), or
   - Use a separate repo where the root is this `public` folder

3. **Update the URL** whenever you restart the cloudflared tunnel — the trycloudflare.com URL changes each time.

## Note

The backend (Flask + collector) must be running and the tunnel must be active for the dashboard to show data.
