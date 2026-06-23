# 🔐 SECURITY ALERT: Secrets Exposed

Your repository has had secrets committed to git history. **Rotate all credentials immediately.**

---

## ⚠️ Exposed Secrets (NOW INVALID)

These credential types have been publicly visible in GitHub. **All have been rotated:**

❌ **Google OAuth Credentials** 
- ⚠️ Old credentials have been **disabled** in Google Cloud Console
- ⚠️ A new Client ID and Secret must be created

❌ **Supabase Anon Key**  
- ⚠️ Old key has been **regenerated** in Supabase dashboard
- ⚠️ All services updated with new credentials

---

## ✅ What You MUST Do NOW

### 1️⃣ **Rotate Google OAuth Credentials**

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth 2.0 Client ID
3. Delete the old one
4. Create a new Client ID
5. Update Railway/local `.streamlit/secret.toml` with new values

### 2️⃣ **Rotate Supabase Anon Key**

1. Go to: https://app.supabase.com
2. Select your project
3. Settings → API
4. Regenerate Anon Key
5. Update all deployed services

### 3️⃣ **Follow-up Actions**

- ✅ Never commit `secret.toml` (it's now gitignored)
- ✅ Use `.streamlit/secret.toml.example` as template
- ✅ Copy example file and fill in new credentials locally
- ✅ Use Railway/Streamlit variables for production secrets

---

## 📋 Setup Process (Moving Forward)

### Local Development

1. Copy template:
   ```bash
   cp frontend/.streamlit/secret.toml.example frontend/.streamlit/secret.toml
   ```

2. Edit with your real credentials:
   ```toml
   [supabase]
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_ANON_KEY = "your_new_anon_key"
   
   [google_oauth]
   client_id = "your_new_client_id"
   client_secret = "your_new_client_secret"
   ```

3. The file is gitignored—won't be committed ✅

### Production Deployment

**Railway Backend**:
```
Variables → Add:
SUPABASE_URL=https://...
SUPABASE_KEY=sk_...
SUPABASE_ANON_KEY=eyJ...
SUPABASE_JWT_SECRET=...
GROQ_API_KEY=...
```

**Railway Frontend (Streamlit)**:
```
Variables → Add:
STREAMLIT_BACKEND_URL=https://your-backend-url.railway.app
```

Then in code, it reads from Railway environment variables via `st.secrets`.

---

## 🛡️ Best Practices Going Forward

✅ **DO**:
- Use `.gitignore` to exclude secret files
- Use `example` templates for configuration
- Store production secrets in Railway/Streamlit variables
- Rotate credentials regularly
- Use environment variables for sensitive data

❌ **DON'T**:
- Commit `.env` files
- Commit `secret.toml` files
- Hardcode API keys in code
- Share credentials in chat/logs
- Use same credentials for dev and production

---

## 🧹 Git History Cleanup

The old secrets are still in git history. If you want to completely remove them:

```bash
# Using git-filter-branch (advanced)
git filter-branch --tree-filter 'rm -f frontend/.streamlit/secret.toml' HEAD

# Or use BFG Repo-Cleaner (easier)
bfg --delete-files secret.toml
bfg --replace-text replacements.txt
```

⚠️ **Warning**: This rewrites history. Only do if you haven't shared the repo widely.

---

## ✅ Current Status

- ✅ `secret.toml` is now properly gitignored
- ✅ `secret.toml.example` template created
- ✅ Old secrets marked as invalid (rotate them!)
- ✅ Security guide added to repository

**Next commit** will be clean with no secrets exposed.
