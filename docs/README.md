# GitHub Pages Frontend Mirror

`docs/` is a mirrored copy of `frontend/` for GitHub Pages hosting.

- It uses the same production UI code as the main frontend.
- It does **not** use the old localStorage demo system.
- API requests are resolved by `runtime-config.js`.

## API Base Resolution

`runtime-config.js` resolves API base in this order:

1. `window.APP_RUNTIME_CONFIG.apiBaseUrl`
2. `<meta name="app-api-base-url" ...>`
3. `localStorage['app_api_base_url']`
4. Default fallback:
   - `https://smart-grievance-system.onrender.com/api` on `*.github.io`
   - `<current-origin>/api` elsewhere

If your backend URL changes, set `window.APP_RUNTIME_CONFIG.apiBaseUrl` before loading `app.js`, or define `app_api_base_url` in localStorage.
