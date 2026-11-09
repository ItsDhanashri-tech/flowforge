# FlowForge AI – Convert Ideas into Working Processes

Frontend: HTML/CSS/JavaScript (`public/`) · Backend: Python serverless function (`api/generate.py`) · AI: Google Gemini

## Deploy to Vercel
1. Push this folder to a GitHub repo.
2. On vercel.com → **Add New Project** → import the repo → Deploy (no build settings needed).
3. Get a Gemini key at https://aistudio.google.com/apikey
4. In Vercel: **Project → Settings → Environment Variables** → add
   `GEMINI_API_KEY` = your key (optional: `GEMINI_MODEL`, default `gemini-2.5-flash`).
5. **Redeploy**. Open your site and enter an idea.

Your key stays only on Vercel's server – it is never sent to the browser.

## Run locally
```
npm i -g vercel
vercel dev        # set GEMINI_API_KEY in a local .env file first
```
