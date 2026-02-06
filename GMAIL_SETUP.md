# Gmail Setup for Password Reset Emails

## 🔐 How to Set Up Gmail App Password

To send password reset emails, you need to create a Gmail App Password. Follow these steps:

### **Step 1: Enable 2-Factor Authentication**
1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** (left sidebar)
3. Under "How you sign in to Google", click **2-Step Verification**
4. Follow the steps to enable 2FA if not already enabled

### **Step 2: Create App Password**
1. Go to: https://myaccount.google.com/apppasswords
2. You might need to sign in again
3. Under "Select app", choose **Mail**
4. Under "Select device", choose **Other (Custom name)**
5. Type: `LifeLens App`
6. Click **Generate**
7. **Copy the 16-character password** (it will look like: `abcd efgh ijkl mnop`)

### **Step 3: Set Environment Variables**

#### **For Local Development (Windows):**

**Option 1: Set in PowerShell (Temporary - for current session)**
```powershell
$env:MAIL_USERNAME="lifelenspptt@gmail.com"
$env:MAIL_PASSWORD="your-16-char-app-password"
```

**Option 2: Set Permanently (Recommended)**
1. Search for "Environment Variables" in Windows
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "User variables", click "New"
5. Add:
   - Variable name: `MAIL_USERNAME`
   - Variable value: `lifelenspptt@gmail.com`
6. Click "New" again and add:
   - Variable name: `MAIL_PASSWORD`
   - Variable value: `your-16-char-app-password` (no spaces)
7. Click OK
8. **Restart your terminal/IDE**

#### **For Vercel Deployment:**
1. Go to your Vercel project dashboard
2. Click on **Settings** tab
3. Click on **Environment Variables**
4. Add two variables:
   - Name: `MAIL_USERNAME`, Value: `lifelenspptt@gmail.com`
   - Name: `MAIL_PASSWORD`, Value: `your-16-char-app-password`
5. Click **Save**
6. Redeploy your app

---

## 📧 Email Configuration (Already Done)

The following is already configured in `app.py`:

```python
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') or 'lifelenspptt@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or ''
app.config['MAIL_DEFAULT_SENDER'] = 'lifelenspptt@gmail.com'
```

---

## ✅ How It Works Now

### **User Flow:**
1. User clicks "Forgot Password?" on login page
2. Enters their email address
3. System sends a professional email with reset link
4. User clicks the link in email
5. User enters new password
6. Password is updated securely

### **Email Features:**
- ✅ Professional HTML email template
- ✅ Branded with LifeLens colors
- ✅ Secure reset button
- ✅ 1-hour expiration
- ✅ Plain text fallback
- ✅ Security notice

---

## 🧪 Testing

### **Without Gmail App Password (Development):**
- Email sending will fail gracefully
- Reset link will be shown in flash message
- You can copy/paste the link to test

### **With Gmail App Password (Production):**
- Email will be sent automatically
- User receives professional email
- Click link to reset password

---

## 🔒 Security Features

✅ **App Password** - Not your actual Gmail password  
✅ **Secure tokens** - Cryptographically signed  
✅ **1-hour expiry** - Links expire automatically  
✅ **TLS encryption** - Secure email transmission  
✅ **No password storage** - Passwords are hashed  

---

## 📝 Quick Start

1. **Create Gmail App Password** (see Step 2 above)
2. **Set environment variables:**
   ```powershell
   $env:MAIL_USERNAME="lifelenspptt@gmail.com"
   $env:MAIL_PASSWORD="your-app-password-here"
   ```
3. **Restart your Flask app**
4. **Test password reset** - Go to login page → Forgot Password?

---

## ⚠️ Important Notes

- **Never commit** your app password to Git
- **Use environment variables** for sensitive data
- **App passwords** are safer than your actual password
- **Revoke** app passwords you're not using
- **Each app** should have its own app password

---

## 🎯 Email Template Preview

**Subject:** LifeLens - Password Reset Request

**Body:**
```
Hello,

You requested to reset your password for LifeLens.

Click the button below to reset your password:

[Reset Password Button]

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
LifeLens Team
```

---

**Your password reset feature is now fully functional!** 🎉

Just set up the Gmail App Password and you're ready to go!
