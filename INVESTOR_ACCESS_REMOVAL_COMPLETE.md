# Certificate Access Control - Investor Removal Summary

## 🚫 Access Control Update Completed

**Date**: August 8, 2025  
**Objective**: Remove investor access from certificate management pages

## 📍 Affected Routes

1. **Certificate Request Page**

   - URL: `http://127.0.0.1:80/analyst/certificate_request`
   - Methods: GET, POST
   - Previous Access: Analyst only
   - **Current Access**: Admin OR Analyst only (Investors explicitly blocked)

2. **Certificate Status Page**
   - URL: `http://127.0.0.1:80/analyst/certificate_status`
   - Methods: GET
   - Previous Access: Analyst only
   - **Current Access**: Admin OR Analyst only (Investors explicitly blocked)

## 🔒 Security Implementation

### Updated Decorator: `@admin_or_analyst_required`

```python
def admin_or_analyst_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Explicitly deny investor access
        if 'investor_id' in session and 'analyst_id' not in session and session.get('user_role') != 'admin':
            flash('Certificate management is not available for investor accounts.', 'error')
            return redirect(url_for('index'))

        # Check if user is admin
        if session.get('user_role') == 'admin':
            session['is_admin'] = True
            return f(*args, **kwargs)
        # Check if user is analyst
        elif 'analyst_id' in session:
            return f(*args, **kwargs)
        else:
            flash('Admin or Analyst access required for certificate management.', 'error')
            return redirect(url_for('index'))
    return decorated_function
```

## 🎯 Access Control Matrix

| User Type           | Certificate Request | Certificate Status | Admin Certificates |
| ------------------- | ------------------- | ------------------ | ------------------ |
| **Admin**           | ✅ ALLOWED          | ✅ ALLOWED         | ✅ ALLOWED         |
| **Analyst**         | ✅ ALLOWED          | ✅ ALLOWED         | 🚫 BLOCKED         |
| **Investor**        | 🚫 **BLOCKED**      | 🚫 **BLOCKED**     | 🚫 BLOCKED         |
| **Unauthenticated** | 🚫 BLOCKED          | 🚫 BLOCKED         | 🚫 BLOCKED         |

## 🛡️ Security Features

### 1. **Explicit Investor Detection**

- Checks for `'investor_id'` in session
- Ensures user is not also an analyst or admin
- Immediate blocking with clear error message

### 2. **Role-Based Access Control**

- **Admin Access**: `session.get('user_role') == 'admin'`
- **Analyst Access**: `'analyst_id' in session`
- **Investor Blocking**: `'investor_id' in session` without admin/analyst roles

### 3. **User-Friendly Error Messages**

- **Investors**: "Certificate management is not available for investor accounts."
- **Others**: "Admin or Analyst access required for certificate management."

### 4. **Secure Redirects**

- All unauthorized access redirected to home page (`url_for('index')`)
- Flash messages provide clear feedback

## ✅ Verification Results

- **Syntax Check**: ✅ No compilation errors
- **Flask App**: ✅ Running successfully
- **Access Control Test**: ✅ All tests passed
- **Investor Blocking**: ✅ Explicitly blocked with appropriate messages
- **Admin/Analyst Access**: ✅ Preserved and working

## 📋 Testing Summary

**Test Results**:

- ✅ Explicit investor exclusion logic implemented
- ✅ Specific error message for investors
- ✅ Both certificate routes properly protected
- ✅ Flask application syntax valid
- ✅ No impact on existing admin/analyst functionality

## 🔐 Security Conclusion

Certificate management pages at:

- `/analyst/certificate_request`
- `/analyst/certificate_status`

Are now **securely restricted** to admin and analyst users only, with **explicit blocking** of investor access and clear error messaging for unauthorized access attempts.
