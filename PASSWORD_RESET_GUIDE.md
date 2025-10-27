# Password Reset with Email - Setup Guide

## ✅ Features Implemented

1. **Forgot Password Page** - `/forgot-password/`
2. **Reset Password Page** - `/reset-password/<token>/`
3. **Email with Reset Link** - Sent to user's email
4. **Token-based Security** - Links expire after use
5. **Password Validation** - Confirmation matching

## 🚀 How to Test

### Option 1: Console Email (Development - Default)

By default, emails are printed to the console for testing.

1. **Start the server:**
   ```bash
   python manage.py runserver
   ```

2. **Test the flow:**
   - Go to: `http://127.0.0.1:8000/login/`
   - Click **"Forgot Password?"**
   - Enter your email
   - Check the **terminal console** for the email
   - Copy the reset link from the console
   - Paste it in your browser
   - Create new password

### Option 2: Gmail SMTP (Production)

To send real emails using Gmail:

1. **Enable 2-Factor Authentication** on your Gmail account
   
2. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Update `.env` file:**
   ```env
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-char-app-password
   DEFAULT_FROM_EMAIL=SmartCampus <noreply@smartcampus.com>
   ```

4. **Restart the server**

## 📧 Email Template

The email includes:
- Branded header with SmartCampus logo
- Clear call-to-action button
- Fallback link for copy/paste
- Security notice (24-hour expiration)
- Professional footer

## 🔗 URLs Created

- `/forgot-password/` - Request password reset
- `/reset-password/<uidb64>/<token>/` - Reset with token
- Link in login page: "Forgot Password?"

## 🛡️ Security Features

✅ Token-based authentication
✅ One-time use links
✅ User verification via email
✅ Password confirmation
✅ Secure token generation
✅ Invalid/expired link handling

## 🎨 Pages Created

1. **forgot_password.html** - Email submission form
2. **reset_password.html** - New password form
3. **password_reset_email.html** - Email template

## 📝 Testing Checklist

- [ ] Visit forgot password page
- [ ] Submit email address
- [ ] Receive success message
- [ ] Check console/email for reset link
- [ ] Click reset link
- [ ] Create new password
- [ ] Confirm passwords match
- [ ] Login with new password
- [ ] Test expired/invalid link

## 💡 Tips

- In development, check the **console/terminal** for emails
- Links are valid for **24 hours** (Django default)
- Links are **one-time use** only
- Make sure user has valid email in profile

---

**Ready to test!** 🚀
