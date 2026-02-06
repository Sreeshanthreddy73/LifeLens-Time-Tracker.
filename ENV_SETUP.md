# 🔐 Environment Setup Instructions

## ✅ Files Created:

1. **`.env`** - Your actual environment variables (NEVER commit to Git!)
2. **`.env.example`** - Template for others (safe to commit)
3. **`.gitignore`** - Updated to ignore .env files

---

## 📝 How to Set Up Gmail for Password Reset

### **Step 1: Get Gmail App Password**

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in with `lifelenspptt@gmail.com`
3. Create App Password:
   - App: **Mail**
   - Device: **LifeLens App**
4. Click **Generate**
5. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

### **Step 2: Update .env File**

1. Open the `.env` file in your project root
2. Find the line: `MAIL_PASSWORD=`
3. Paste your app password (remove spaces):
   ```
   MAIL_PASSWORD=abcdefghijklmnop
   ```
4. Save the file

### **Step 3: Install python-dotenv**

```powershell
pip install python-dotenv
```

### **Step 4: Restart Your App**

```powershell
python app.py
```

---

## 📧 Your .env File Should Look Like:

```env
# Gmail Configuration
MAIL_USERNAME=lifelenspptt@gmail.com
MAIL_PASSWORD=abcdefghijklmnop

# Flask Secret Key
SECRET_KEY=lifelens-secret-key-12345
```

---

## ✅ How It Works:

1. **`.env` file** stores your sensitive credentials
2. **`python-dotenv`** loads them automatically when app starts
3. **`.gitignore`** prevents .env from being committed to Git
4. **`.env.example`** shows others what variables are needed

---

## 🔒 Security Best Practices:

✅ **NEVER commit `.env` to Git** - It's in .gitignore  
✅ **Use App Passwords** - Not your actual Gmail password  
✅ **Keep credentials secret** - Don't share your .env file  
✅ **Use .env.example** - For documentation only  
✅ **Rotate passwords** - Change them periodically  

---

## 🚀 Testing Password Reset:

1. Make sure `.env` has your Gmail App Password
2. Restart Flask app: `python app.py`
3. Go to: http://127.0.0.1:5001/login
4. Click "Forgot Password?"
5. Enter a test email
6. Check your email for reset link!

---

## 🌐 For Vercel Deployment:

1. Go to Vercel Dashboard → Your Project
2. Settings → Environment Variables
3. Add:
   - `MAIL_USERNAME` = `lifelenspptt@gmail.com`
   - `MAIL_PASSWORD` = `your-app-password`
   - `SECRET_KEY` = `your-secret-key`
4. Redeploy

---

## ⚠️ Important Notes:

- `.env` is **local only** - not deployed to Vercel
- For Vercel, use their Environment Variables UI
- Each environment (local, production) has its own variables
- **Never** hardcode passwords in code

---

## 🎯 Quick Checklist:

- [ ] Created Gmail App Password
- [ ] Updated `.env` file with password
- [ ] Installed `python-dotenv`
- [ ] Restarted Flask app
- [ ] Tested password reset
- [ ] Verified email is sent

---

**You're all set!** 🎉

Password reset emails will now be sent from `lifelenspptt@gmail.com`!
