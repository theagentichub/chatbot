````markdown
## Setup virtual environment (Windows)

```bash
python -m venv venv
.\venv\Scripts\activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Environment variables

Create a `.env` file in the project root with:

```
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

## Run FastAPI app locally with hot reload

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Run FastAPI app locally without hot reload

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Run with custom port (replace 1234 with your port)

```bash
uvicorn main:app --host 0.0.0.0 --port 1234
```

## Run using Python script (optional)

Make sure the following is at the bottom of `main.py`:

```python
if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
```

Then run:

```bash
python main.py
```

## Notes for deployment (e.g., Render.com)

- Use the command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

- Ensure `uvicorn[standard]` is installed

```
