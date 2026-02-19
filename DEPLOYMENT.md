# Deployment Instructions

## Backend Deployment on Render

### Steps:
1. **Create a Render account** at [render.com](https://render.com)

2. **Connect your GitHub repository** to Render

3. **Create a new Web Service**:
   - Select your repository (rift_money_mulling)
   - Set the root directory to `backend/`
   - Build command: `pip install -r requirements.txt`
   - Start command: `python -m app.main`

4. **Configure Environment Variables** in Render:
   - `PORT`: `8000`
   - `PYTHON_VERSION`: `3.11`
   - If using LLM features, add `LLM_API_KEY`: `<your-api-key>`

5. **Deploy** - Render will automatically deploy on every push to main

6. **Note your backend URL**: It will be something like `https://your-app-name.onrender.com`

---

## Frontend Deployment on Vercel

### Steps:
1. **Create a Vercel account** at [vercel.com](https://vercel.com)

2. **Import your GitHub project**:
   - Go to Vercel dashboard → Add New → Project
   - Import from Git
   - Select your rift_money_mulling repository

3. **Configure Build Settings**:
   - Root Directory: `frontend/`
   - Build Command: `npm run build`
   - Output Directory: `dist`

4. **Set Environment Variables** in Vercel:
   - `VITE_API_BASE_URL`: `https://your-render-app-name.onrender.com` (replace with your actual Render backend URL)

5. **Deploy** - Vercel will automatically deploy on every push to main

---

## Architecture Overview

After deployment:
```
Frontend (Vercel)
    ↓ (HTTPS requests to API)
Backend (Render)
    ↓ (Analysis & Processing)
Results
```

---

## Local Development

### Backend:
```bash
cd backend
pip install -r requirements.txt
python -m app.main
```
The backend runs on `http://localhost:8000`

### Frontend:
```bash
cd frontend
npm install
npm run dev
```
The frontend runs on `http://localhost:5173` and proxies `/api/*` requests to `http://localhost:8000`

---

## CORS Configuration

Your app already has CORS enabled for all origins. In production, consider restricting this:

In `backend/app/main.py`, update the CORS configuration:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-vercel-frontend-url.vercel.app",
        "http://localhost:5173"  # for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Troubleshooting

### Backend not connecting from frontend:
- Verify `VITE_API_BASE_URL` is set in Vercel environment variables
- Check that the backend URL is accessible in browser

### Build failures on Render:
- Ensure all dependencies are in `requirements.txt`
- Check Python version matches (3.11 recommended)

### Frontend build issues on Vercel:
- Verify `npm run build` works locally
- Check Node version compatibility (16+ recommended)
