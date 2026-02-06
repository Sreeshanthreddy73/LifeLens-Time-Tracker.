# 📱 How to Access LifeLens from Your Phone

## 🔧 Problem:
The password reset email link shows `127.0.0.1:5001` which only works on your computer, not your phone.

## ✅ Solution:

### **Step 1: Find Your Computer's IP Address**

Run this command:
```powershell
python get_ip.py
```

It will show something like:
```
IP Address: 192.168.1.100
Access your app from phone:
http://192.168.1.100:5001
```

### **Step 2: Restart Your Flask App**

Stop the current app (Ctrl+C) and restart:
```powershell
python app.py
```

Now it will show:
```
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5001
* Running on http://192.168.1.100:5001
```

### **Step 3: Access from Phone**

1. **Make sure phone and computer are on the SAME WiFi**
2. Open browser on phone
3. Go to: `http://YOUR-IP:5001` (use the IP from Step 1)
4. Example: `http://192.168.1.100:5001`

### **Step 4: Test Password Reset**

1. On your phone, go to the login page
2. Click "Forgot Password?"
3. Enter your email
4. Check email on phone
5. Click the reset link - **it will now work!**

---

## 🎯 Quick Test:

### **On Computer:**
```powershell
# 1. Get your IP
python get_ip.py

# 2. Restart app
python app.py
```

### **On Phone:**
1. Connect to same WiFi as computer
2. Open browser
3. Go to: `http://YOUR-IP:5001`
4. Test the app!

---

## 🔍 Troubleshooting:

### **"Site can't be reached" on phone:**
- ✅ Check both devices on same WiFi
- ✅ Check Windows Firewall (may need to allow port 5001)
- ✅ Verify IP address is correct
- ✅ Make sure Flask app is running

### **Allow Flask through Windows Firewall:**
1. Search "Windows Defender Firewall"
2. Click "Allow an app through firewall"
3. Click "Allow another app"
4. Browse to Python executable
5. Check both Private and Public
6. Click OK

### **Still not working?**
Try using your computer's IP in the browser:
```
http://192.168.1.XXX:5001
```
Replace XXX with your actual IP from `get_ip.py`

---

## 📧 Email Links Will Now Use:

- **Before:** `http://127.0.0.1:5001/reset-password/...` ❌ (only works on computer)
- **After:** `http://192.168.1.100:5001/reset-password/...` ✅ (works on phone too!)

The email will automatically use the correct URL based on how you access the site.

---

## 💡 Pro Tip:

For testing password reset:
1. Open email on your **computer** (not phone)
2. Click the reset link
3. It will open in your computer's browser
4. Reset your password there

OR

1. Make sure Flask is running with `host='0.0.0.0'` ✅ (already done!)
2. Access from phone using your computer's IP
3. Email links will work from phone too!

---

**Your app is now accessible from any device on your WiFi network!** 🎉
