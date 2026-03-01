# Deploying Frontend to Vercel

## Prerequisites

- GitHub/GitLab/Bitbucket account
- Vercel account (free tier works great)
- Google OAuth credentials configured
- API Backend deployed and running

## Method 1: Deploy via Vercel Dashboard (Recommended for First-Time)

### Step 1: Push Code to Git Repository

```bash
cd rag-production
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/geeky-brahma/qna_bot_colpali.git
git push -u origin main
```

### Step 2: Import Project to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New Project"**
3. Import your Git repository
4. Select the `frontend` folder as the root directory
5. Framework Preset: **Next.js** (auto-detected)
6. Click **"Deploy"**

### Step 3: Configure Environment Variables

After the initial deployment (it might fail, that's okay):

1. Go to your project dashboard on Vercel
2. Navigate to **Settings → Environment Variables**
3. Add the following variables:

| Name | Value | Environment |
|------|-------|-------------|
| `NEXTAUTH_URL` | `https://your-app.vercel.app` | Production |
| `NEXTAUTH_SECRET` | Generate with: `openssl rand -base64 32` | Production, Preview, Development |
| `GOOGLE_CLIENT_ID` | Your Google OAuth Client ID | Production, Preview, Development |
| `GOOGLE_CLIENT_SECRET` | Your Google OAuth Client Secret | Production, Preview, Development |
| `NEXT_PUBLIC_API_URL` | Your API backend URL (e.g., `https://rag-api-xxx.a.run.app`) | Production, Preview, Development |

4. Click **"Save"**

### Step 4: Update Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **APIs & Services → Credentials**
3. Select your OAuth 2.0 Client ID
4. Add Vercel URLs to:
   - **Authorized JavaScript origins:**
     - `https://your-app.vercel.app`
   - **Authorized redirect URIs:**
     - `https://your-app.vercel.app/api/auth/callback/google`
5. Save changes

### Step 5: Redeploy

1. Go to **Deployments** tab in Vercel
2. Click on the latest deployment
3. Click **"Redeploy"** button
4. Or push a new commit to trigger automatic deployment

### Step 6: Verify Deployment

Visit your Vercel URL (e.g., `https://your-app.vercel.app`) and test:
- ✅ Page loads correctly
- ✅ Google OAuth login works
- ✅ API connections work
- ✅ Subject selection and queries function

---

## Method 2: Deploy via Vercel CLI

### Step 1: Install Vercel CLI

```powershell
npm install -g vercel
```

### Step 2: Login to Vercel

```powershell
vercel login
```

### Step 3: Navigate to Frontend Directory

```powershell
cd rag-production/frontend
```

### Step 4: Deploy

For first deployment:
```powershell
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- What's your project's name? `rag-production-frontend`
- In which directory is your code located? `./`
- Want to override settings? **N**

For production deployment:
```powershell
vercel --prod
```

### Step 5: Set Environment Variables via CLI

```powershell
# Set production environment variables
vercel env add NEXTAUTH_URL production
vercel env add NEXTAUTH_SECRET production
vercel env add GOOGLE_CLIENT_ID production
vercel env add GOOGLE_CLIENT_SECRET production
vercel env add NEXT_PUBLIC_API_URL production
```

You'll be prompted to enter values for each variable.

### Step 6: Redeploy with Environment Variables

```powershell
vercel --prod
```

---

## Method 3: One-Click Deploy

### Create Deploy Button (Optional)

Add this button to your README for easy deployment:

```markdown
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/rag-production&project-name=rag-frontend&repository-name=rag-production&root-directory=frontend&env=NEXTAUTH_URL,NEXTAUTH_SECRET,GOOGLE_CLIENT_ID,GOOGLE_CLIENT_SECRET,NEXT_PUBLIC_API_URL)
```

---

## Post-Deployment Configuration

### Custom Domain (Optional)

1. Go to project **Settings → Domains**
2. Add your custom domain
3. Configure DNS records as instructed
4. Update `NEXTAUTH_URL` environment variable
5. Update Google OAuth authorized URLs

### Performance Optimization

Vercel automatically provides:
- ✅ Global CDN
- ✅ Edge caching
- ✅ Automatic SSL/TLS
- ✅ Image optimization
- ✅ Analytics (with Pro plan)

### Monitoring

1. Enable **Vercel Analytics** in project settings
2. View real-time performance metrics
3. Monitor deployment status and logs

---

## Environment Variables Reference

Create `.env.production` locally for reference (don't commit):

```bash
# Production Environment Variables for Vercel

# NextAuth
NEXTAUTH_URL=https://your-app.vercel.app
NEXTAUTH_SECRET=<generate-with-openssl-rand-base64-32>

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-google-client-secret

# API Backend (update after backend deployment)
NEXT_PUBLIC_API_URL=https://your-api-backend.run.app
```

---

## Continuous Deployment

Once connected to Git, Vercel automatically:
- 🔄 Deploys on every push to `main` branch
- 🔄 Creates preview deployments for pull requests
- 🔄 Runs build checks before deployment

### Branch Deployments

- **Production:** Commits to `main` branch
- **Preview:** Commits to feature branches or PRs
- **Development:** Local development with `npm run dev`

---

## Troubleshooting

### Build Fails

**Check build logs in Vercel dashboard:**
```
Deployments → Click on failed deployment → View Logs
```

**Common issues:**
- Missing environment variables
- TypeScript errors
- Dependency installation issues

### OAuth Redirect Error

**Error:** `redirect_uri_mismatch`

**Fix:**
1. Verify `NEXTAUTH_URL` matches your Vercel URL exactly
2. Ensure redirect URI is added to Google OAuth settings
3. Clear browser cache and cookies

### API Connection Issues

**Error:** CORS or network errors when calling backend

**Fix:**
1. Verify `NEXT_PUBLIC_API_URL` is correct
2. Ensure API backend allows CORS from your Vercel domain
3. Check API backend is deployed and accessible

### Environment Variables Not Updating

**Fix:**
1. Update environment variables in Vercel dashboard
2. Trigger a new deployment (redeploy or push commit)
3. Clear browser cache

---

## Production Checklist

Before going live:

- [ ] All environment variables set correctly
- [ ] Google OAuth credentials updated with production URLs
- [ ] API backend deployed and tested
- [ ] Frontend builds successfully
- [ ] OAuth login works
- [ ] API queries return results
- [ ] Error pages configured
- [ ] Custom domain configured (optional)
- [ ] Analytics enabled
- [ ] Security headers configured (already in next.config.js)

---

## Cost

Vercel Pricing:
- **Hobby (Free):** Perfect for this project
  - Unlimited deployments
  - Automatic HTTPS
  - 100GB bandwidth/month
  - Serverless function executions included
  
- **Pro ($20/month):** For production apps
  - 1TB bandwidth
  - Advanced analytics
  - Team collaboration
  - Password protection

---

## Quick Reference Commands

```powershell
# Install dependencies
npm install

# Local development
npm run dev

# Build for production
npm run build

# Deploy to preview
vercel

# Deploy to production
vercel --prod

# View deployment logs
vercel logs

# List deployments
vercel ls

# Remove deployment
vercel rm <deployment-url>
```

---

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Vercel CLI Reference](https://vercel.com/docs/cli)
- [NextAuth.js with Vercel](https://next-auth.js.org/deployment)

---

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Review environment variables
3. Test API backend separately
4. Check Google OAuth configuration
5. Review [DEPLOYMENT.md](docs/DEPLOYMENT.md) for full system deployment

---

**Ready to deploy? Start with Method 1 (Dashboard) for the easiest experience!** 🚀
