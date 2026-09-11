## Usage
# Front-end

```bash
cd front-end
npm install
npm run dev
```
# Back-end

Create `back-end/src/.env` with your Gemini API key:

```bash
GOOGLE_AI_KEY=your_key_here
```

Then, in a second terminal:

```bash
cd back-end
uv sync
uv run fastapi dev src/main.py --port 8000
```

The frontend posts the selected video to `http://localhost:8000/analyse-video`.
Set `VITE_API_URL` to a different endpoint when deploying the API elsewhere.
