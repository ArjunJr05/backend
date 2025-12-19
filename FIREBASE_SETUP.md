# Firebase Credentials Setup

This guide explains how to securely configure Firebase credentials for the ML Hackathon Platform.

## 🔒 Security Best Practices

**Never commit Firebase credentials to GitHub!** This project uses environment variables to keep credentials secure.

## 📋 Setup Methods

### Method 1: Automatic Setup (Recommended)

If you have the Firebase JSON file locally:

```bash
cd backend
./setup_env.sh
```

This will:
- Read your Firebase service account JSON file
- Create a `.env` file with the credentials
- The `.env` file is automatically ignored by git

### Method 2: Manual Setup

1. **Create a `.env` file** in the `backend` directory:

```bash
cd backend
touch .env
```

2. **Add your Firebase credentials** to `.env`:

```bash
FIREBASE_CREDENTIALS_JSON='{"type":"service_account","project_id":"portal-11326",...}'
```

Copy the entire contents of your Firebase JSON file as a single line (no newlines).

3. **Add other environment variables**:

```bash
SECRET_KEY=your-secret-key-change-in-production
```

## 🚀 How It Works

The backend loads Firebase credentials in this order:

1. **Environment Variable** (`FIREBASE_CREDENTIALS_JSON`) - Used in production
2. **Local JSON File** - Fallback for local development
3. **Default Credentials** - For Google Cloud environments

## 📁 Files to Keep Private

These files are already in `.gitignore`:

- `.env` - Contains environment variables
- `*.json` - Firebase service account files
- `portal-11326-firebase-adminsdk-fbsvc-*.json` - Specific Firebase credentials

## 🔄 For Production Deployment

When deploying to a server:

1. **Set the environment variable** on your server:

```bash
export FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'
```

2. **Or use your platform's secrets management**:
   - Vercel: Add to Environment Variables in dashboard
   - Heroku: Use `heroku config:set`
   - Docker: Use secrets or environment files
   - Google Cloud: Use Secret Manager

## ✅ Verify Setup

Start the backend and check for successful Firebase initialization:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Application startup complete.
```

Without errors about Firebase credentials.

## 🆘 Troubleshooting

**Error: "Failed to resolve 'www.googleapis.com'"**
- This is a network issue, not a credentials issue
- The development mode bypass will handle this automatically

**Error: "FIREBASE_CREDENTIALS_JSON not found"**
- Run `./setup_env.sh` to create the `.env` file
- Or manually create `.env` with your credentials

**Error: "Invalid credentials"**
- Verify your Firebase JSON file is valid
- Check that the JSON is properly formatted in `.env`
- Ensure no extra newlines or spaces

## 📚 Additional Resources

- [Firebase Admin SDK Setup](https://firebase.google.com/docs/admin/setup)
- [Service Account Keys](https://cloud.google.com/iam/docs/creating-managing-service-account-keys)
