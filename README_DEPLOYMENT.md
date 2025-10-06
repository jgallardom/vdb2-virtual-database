# VDB2 - Deployment Guide

## Render.com Deployment

This guide will help you deploy the VDB2 Virtual Database System to Render.com with cloud file storage.

### Prerequisites
- GitHub account
- Render.com account
- Git repository with this code

### Deployment Steps

#### 1. Prepare Repository
```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial VDB2 deployment setup"

# Push to GitHub
git remote add origin https://github.com/yourusername/vdb2.git
git push -u origin main
```

#### 2. Deploy to Render

1. **Go to Render Dashboard**
   - Visit [render.com](https://render.com)
   - Sign in to your account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing this code

3. **Configure Service**
   - **Name**: `vdb2-virtual-database`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `flexible/VDB2` if in subfolder)

4. **Build & Deploy Settings**
   - **Build Command**: `echo "No build command needed"`
   - **Start Command**: `python server.py`
   - **Python Version**: `3.11.0`

5. **Environment Variables**
   - `PORT`: `8080` (Render will override this)
   - `RENDER`: `true` (enables cloud storage mode)

6. **Add Persistent Disk**
   - Go to "Disks" tab
   - Click "Connect Disk"
   - **Name**: `vdb2-storage`
   - **Mount Path**: `/opt/render/project/vdb2-storage`
   - **Size**: `1 GB` (can be increased as needed)

#### 3. Deploy
- Click "Create Web Service"
- Wait for deployment to complete
- Your app will be available at: `https://vdb2-virtual-database.onrender.com`

### Features After Deployment

✅ **Cloud File Storage**: Files are stored on Render's persistent disk  
✅ **Automatic Scaling**: Handles traffic spikes  
✅ **HTTPS**: Secure connections  
✅ **Custom Domain**: Can be configured  
✅ **Data Persistence**: Data survives deployments  

### File Storage

- **Local Development**: Files stored in `vdb_files/` directory
- **Cloud Production**: Files stored in `/opt/render/project/vdb2-storage/vdb_files/`
- **Database**: JSON files stored in persistent disk
- **Automatic Migration**: App detects cloud environment and adjusts paths

### Monitoring

- **Logs**: Available in Render dashboard
- **Metrics**: CPU, Memory, Response time
- **Health Checks**: Automatic monitoring
- **Uptime**: 99.9% SLA on paid plans

### Troubleshooting

**Common Issues:**
1. **Build Fails**: Check Python version (3.11.0)
2. **Files Not Saving**: Ensure persistent disk is connected
3. **Port Issues**: App automatically uses Render's PORT variable
4. **CORS Issues**: Already configured for cross-origin requests

**Debug Commands:**
```bash
# Check if running on Render
echo $RENDER

# Check disk mount
ls -la /opt/render/project/vdb2-storage/

# Check logs
# Available in Render dashboard
```

### Cost

- **Free Tier**: 750 hours/month, 1GB disk
- **Starter Plan**: $7/month, unlimited hours, 1GB disk
- **Professional**: $25/month, better performance, more disk space

### Security

- **HTTPS**: Automatic SSL certificates
- **Environment Variables**: Secure configuration
- **File Upload**: Base64 encoded, secure handling
- **CORS**: Configured for web security

---

**Need Help?** Check Render's documentation or create an issue in the repository.
