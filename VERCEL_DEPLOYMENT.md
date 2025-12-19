# Deploying Backend to Vercel

## ⚠️ Important Limitations

Your FastAPI backend uses **background workers** and **Firebase**, which have specific constraints on Vercel's serverless platform:

### Known Issues:
1. **Background Worker Won't Run**: The queue worker in `app/main.py` (lines 19-22) won't work on Vercel serverless functions
2. **10-Second Timeout**: Vercel functions have a 10-second execution limit (Pro plan: 60 seconds)
3. **Cold Starts**: First requests may be slower
4. **Stateless Functions**: Each request runs in a new container

### Recommendation:
For a production ML evaluation platform with background workers, consider:
- **Railway** (supports long-running processes)
- **Render** (you already have render.yaml in README)
- **Fly.io** (supports background workers)
- **AWS ECS/EC2** (full control)

However, if you still want to deploy to Vercel for testing API endpoints, follow these steps:

---

## Prerequisites

1. **Vercel Account**: Sign up at https://vercel.com
2. **Vercel CLI**: Install globally
   ```bash
   npm install -g vercel
   ```

---

## Deployment Steps

### Step 1: Prepare Environment Variables

Create a `.env` file locally (don't commit it):
```env
SECRET_KEY=your-super-secret-key-here
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

### Step 2: Add Firebase Credentials

Your app uses Firebase (`app/db/firebase_service.py`). You need to:

**Option A: Use Environment Variable (Recommended)**
1. Convert your Firebase JSON to a single-line string
2. Add to Vercel as environment variable `FIREBASE_CREDENTIALS`

**Option B: Include in deployment**
- Ensure `app/data/portal-11326-firebase-adminsdk-fbsvc-2cd1059886.json` exists
- Vercel will include it in the deployment

### Step 3: Deploy to Vercel

#### Option 1: Deploy via CLI (Recommended)

```bash
cd backend
vercel
```

Follow the prompts:
- **Set up and deploy?** → Yes
- **Which scope?** → Your account
- **Link to existing project?** → No (first time)
- **Project name?** → ml-hackathon-backend
- **Directory?** → ./
- **Override settings?** → No

#### Option 2: Deploy via Git Integration

1. Push your code to GitHub
2. Go to https://vercel.com/new
3. Import your repository
4. Select the `backend` directory as root
5. Vercel auto-detects Python and uses `vercel.json`
6. Click **Deploy**

### Step 4: Configure Environment Variables in Vercel

After deployment, add environment variables:

1. Go to your project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add:
   - `SECRET_KEY`: Your JWT secret key
   - `ALLOWED_ORIGINS`: Comma-separated list of allowed origins
   - `FIREBASE_CREDENTIALS`: (if using Option A above)

### Step 5: Redeploy

```bash
vercel --prod
```

---

## Configuration Files

### ✅ Already Configured

- `vercel.json` - Vercel deployment configuration
- `requirements.txt` - Python dependencies
- `.vercelignore` - Files to exclude from deployment

---

## Testing Your Deployment

Once deployed, Vercel provides a URL like: `https://ml-hackathon-backend.vercel.app`

### Test the API:

```bash
# Health check
curl https://your-deployment.vercel.app/health

# Root endpoint
curl https://your-deployment.vercel.app/

# Submit endpoint (example)
curl -X POST https://your-deployment.vercel.app/submit-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "test_team",
    "team_name": "Test Team",
    "endpoint_url": "https://example.com/predict"
  }'
```

---

## Known Issues & Workarounds

### Issue 1: Background Worker Not Running

**Problem**: The queue worker (`start_worker()` in lifespan) won't run on serverless.

**Workaround Options**:
1. **Trigger evaluation via API**: Instead of background worker, trigger evaluation on-demand
2. **Use Vercel Cron Jobs**: Schedule periodic checks (limited to once per minute on free tier)
3. **External Worker**: Deploy worker separately on Railway/Render

### Issue 2: Large Dependencies (numpy, pandas, scikit-learn)

**Problem**: Large packages may exceed Vercel's 250MB limit.

**Solution**: Vercel's Python runtime handles this, but deployment may be slower.

### Issue 3: Firebase Connection

**Problem**: Firebase needs credentials file or environment variable.

**Solution**: Ensure Firebase credentials are properly configured in environment variables.

---

## Monitoring & Logs

View logs in real-time:
```bash
vercel logs
```

Or view in dashboard:
1. Go to your project
2. Click **Deployments**
3. Select a deployment
4. View **Functions** logs

---

## Custom Domain (Optional)

1. Go to **Settings** → **Domains**
2. Add your custom domain
3. Configure DNS records as instructed

---

## Rollback

If something goes wrong:
```bash
vercel rollback
```

Or use the Vercel dashboard to promote a previous deployment.

---

## Alternative: Deploy Worker Separately

Since Vercel doesn't support background workers well, consider this architecture:

1. **Vercel**: Host API endpoints only (no worker)
2. **Railway/Render**: Host background worker separately
3. **Shared Firebase**: Both connect to same Firebase database

This requires modifying `app/main.py` to disable the worker on Vercel:

```python
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase()
    
    # Only start worker if not on Vercel
    if not os.getenv("VERCEL"):
        global worker
        worker = await start_worker()
    
    yield
    
    if not os.getenv("VERCEL"):
        await stop_worker()
```

---

## Cost Considerations

**Vercel Free Tier**:
- 100GB bandwidth/month
- Serverless function execution time limits
- Good for testing and small projects

**Vercel Pro ($20/month)**:
- 1TB bandwidth
- 60-second function timeout (vs 10 seconds)
- Better for production

---

## Recommended: Use Railway or Render Instead

Given your app's architecture (background workers, queue processing), I recommend:

### Railway (Easiest)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Render (You already have config in README)
- Supports long-running processes
- Better for background workers
- Free tier available

---

## Summary

✅ **Your backend is configured for Vercel**
⚠️ **Background worker won't work on Vercel serverless**
💡 **Consider Railway/Render for full functionality**

To deploy now:
```bash
cd backend
vercel
```

For production with workers, use Railway or Render instead.
