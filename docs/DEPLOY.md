# Deploying the website (Vercel + FalkorDB Cloud)

The public site is two pieces that Vercel runs side by side (see `vercel.json`):

| Piece | Folder | What it is |
|---|---|---|
| `web` | `web/` | The Next.js website: home page, live demo, under the hood |
| `api` | `api/server.py` | The FastAPI engine the demo talks to, at `/api/...` |

The API needs a FalkorDB it can reach over the internet, so the database lives on FalkorDB
Cloud's free tier. Each visitor gets a private copy of one template graph (`nodus/sandbox.py`),
so visitors never see each other's clicks.

Everything costs nothing: Vercel Hobby, FalkorDB Cloud free (100 MB, no card).

## Why the repo looks the way it does

- **`requirements.txt` is tiny on purpose.** Vercel installs it for the API, and only five
  packages are needed there. Everything for local use (Streamlit, tests, LLM SDKs) is in
  `requirements-local.txt`.
- **There is no `pyproject.toml`.** Vercel's Python builder installs a repo that has one as a
  package, and this repo isn't one. Pytest settings live in `pytest.ini` instead.
- **`.vercelignore`** keeps `.env`, caches, `node_modules` and tests out of the upload.

This setup was checked with Vercel's own local runner (`vercel dev -L`, CLI 64.1): every page
returned 200, `/api/health` answered, and a visitor sandbox was created.

## Steps

### 1. Create the database (5 minutes)

1. Sign up at <https://app.falkordb.cloud> and create a **Free** instance.
   Pick **AWS, us-east-1** so it sits next to Vercel's default region (Washington, `iad1`).
2. Open the instance's **Connect** page and keep it open: you need host, port, username and
   password.

### 2. Load the demo company into it (1 minute)

From your own Terminal, in `~/Desktop/nodus`:

```bash
.venv/bin/python scripts/build_cloud_template.py
```

It asks for the four values; the password is typed hidden and never saved. It ends with
"The cloud database is ready."

### 3. Create the Vercel project (5 minutes)

1. Sign up at <https://vercel.com> with your GitHub account.
2. **Add New → Project → Import** `hey-shiv/nodus`. Vercel reads `vercel.json` and shows two
   services, `web` and `api`. Leave the root directory as the repo root.
3. Before pressing Deploy, open **Environment Variables** and add:

   | Name | Value |
   |---|---|
   | `NODUS_DB_HOST` | host from the Connect page |
   | `NODUS_DB_PORT` | port from the Connect page |
   | `NODUS_DB_USERNAME` | username from the Connect page |
   | `NODUS_DB_PASSWORD` | password from the Connect page |

   No Gemini key is needed: the website never calls an LLM.
4. Press **Deploy**. When it finishes, open the URL and click **Try it**.

### 4. Check it

- `https://<your-site>/api/health` shows `{"ok":true}`.
- On **Live demo**, saving the plan shows the heads-up and the "4 of 5" checklist.

## Known limits (honest list)

- **No TLS on the free database tier.** Traffic between Vercel and FalkorDB Cloud is not
  encrypted. Acceptable here because every record is synthetic (Tern & Tally Freight is made
  up); a real company would use a paid tier with TLS.
- **Cold starts.** The first click after a quiet spell can take a few seconds while Vercel
  wakes the API.
- **Sandboxes expire.** Old visitor graphs are removed automatically (`sandbox.cleanup`), so a
  tab left open for hours shows "start a new one".
