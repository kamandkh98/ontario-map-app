# Render Deployment Checklist

## ✅ Files Prepared

The following files have been created/updated for Render deployment:

- ✅ `requirements.txt` - Updated with correct dependencies and numpy<2.0.0 constraint
- ✅ `render.yaml` - Configuration file for easy Blueprint deployment
- ✅ `.gitignore` - Excludes venv and unnecessary files from git
- ✅ `README.md` - Updated with comprehensive deployment instructions

## 📝 Quick Deployment Steps

### Option 1: Manual Web Service (Recommended for First Time)

1. **Prepare Your Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Ontario Map App"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

2. **Go to Render**
   - Visit https://render.com
   - Sign in (or create account)
   - Click "New +" → "Web Service"

3. **Connect Repository**
   - Connect your GitHub account
   - Select your repository

4. **Configure Settings**
   - Name: `ontario-map-app`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Instance Type: **Free**

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Access at: `https://your-app-name.onrender.com`

### Option 2: Blueprint (Even Easier)

1. Push code to GitHub (step 1 above)
2. Go to Render → "New +" → "Blueprint"
3. Select your repository
4. Click "Apply" (render.yaml auto-configures everything)

## ⚠️ Important Notes

- **Free Tier Limitations**: 
  - 750 hours/month
  - App spins down after 15 minutes of inactivity
  - First request after sleep takes 30-60 seconds to wake up

- **Required Files** (all included):
  - `app.py` - Main application
  - `ontario_regions.geojson` - Map data
  - `index.html` - Frontend
  - `app.js` - Frontend JavaScript
  - `requirements.txt` - Python dependencies

## 🔍 Verify Deployment

After deployment, test these endpoints:
- `https://your-app.onrender.com/` - Main page
- `https://your-app.onrender.com/api/health` - Health check
- `https://your-app.onrender.com/api/regions` - GeoJSON data

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Build fails | Verify requirements.txt is in root directory |
| App won't start | Check logs in Render dashboard |
| 502 Error | Wait 60 seconds for app to fully spin up |
| Module not found | Ensure all dependencies in requirements.txt |
| NumPy errors | Verify numpy<2.0.0 constraint in requirements.txt |

## 🔄 Updates After Deployment

Simply push to your main branch:
```bash
git add .
git commit -m "Your update message"
git push
```

Render will automatically rebuild and redeploy!

## 📊 Monitoring

- **Logs**: View real-time logs in Render dashboard
- **Metrics**: Monitor request counts and response times
- **Alerts**: Set up email notifications for deployment failures

## 🎉 Success!

Once deployed, share your app:
`https://your-app-name.onrender.com`


