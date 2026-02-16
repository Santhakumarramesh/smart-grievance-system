# 🔒 Security Firewall System

## Overview

The Smart Grievance System implements a comprehensive, multi-layered security firewall to protect user information and prevent various types of attacks. This document outlines all security measures implemented in the system.

---

## 🛡️ Security Layers

### 1. **Rate Limiting**
Prevents abuse and DDoS attacks by limiting requests per IP address.

**Implementation:**
- **Registration**: Max 5 attempts per 10 minutes
- **Login**: Max 10 attempts per 5 minutes
- **OTP Requests**: Max 10 per 10 minutes
- **Grievance Submission**: Max 20 per hour

**How it works:**
```python
@require_firewall(max_requests=10, window_minutes=5)
def login():
    # Login logic
```

**Response when limit exceeded:**
```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Please try again later."
}
```

---

### 2. **Input Validation & Sanitization**
Prevents SQL injection, XSS, and code injection attacks.

**Blocked Patterns:**
- SQL keywords: `SELECT`, `UNION`, `INSERT`, `UPDATE`, `DELETE`, `DROP`, `CREATE`, `ALTER`
- XSS tags: `<script>`, `<iframe>`, `<object>`, `<embed>`, `javascript:`
- Path traversal: `../`, `..\`
- Code injection: `exec`, `eval`, `system`, `shell_exec`

**Sanitization:**
- All user input is sanitized using `bleach` library
- Only safe HTML tags allowed: `b`, `i`, `u`, `strong`, `em`, `p`, `br`
- Dangerous content is stripped automatically

**Example:**
```python
# Input: "<script>alert('XSS')</script>Hello"
# Output: "Hello"
```

---

### 3. **Email Validation**
Ensures only valid email addresses are accepted.

**Features:**
- Format validation
- Domain validation
- Normalization (converts to lowercase, removes extra spaces)
- Uses `email-validator` library

**Example:**
```python
# Input: "User@EXAMPLE.COM  "
# Output: "user@example.com"
```

---

### 4. **Phone Number Validation**
Validates Indian phone numbers.

**Format accepted:**
- 10 digits starting with 6-9
- Optional +91 prefix
- Examples: `9876543210`, `+919876543210`

---

### 5. **Password Strength Validation**
Enforces strong password policies.

**Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- Not in common weak passwords list

**Rejected passwords:**
- `password`, `12345678`, `admin123`, `qwerty123`

---

### 6. **Security Headers**
Protects against various browser-based attacks.

**Headers added to all responses:**

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Frame-Options` | `SAMEORIGIN` | Prevents clickjacking |
| `X-Content-Type-Options` | `nosniff` | Prevents MIME sniffing |
| `X-XSS-Protection` | `1; mode=block` | Enables XSS filter |
| `Content-Security-Policy` | (detailed policy) | Prevents XSS, injection attacks |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Controls referrer information |
| `Permissions-Policy` | (restrictive) | Limits browser features |

---

### 7. **IP Blocking System**
Automatically blocks suspicious IP addresses.

**Triggers:**
- 5+ suspicious activities within 1 hour
- Multiple rate limit violations
- Repeated authentication failures
- Malicious input patterns detected

**Blocked IP response:**
```json
{
  "error": "Access Denied",
  "message": "Your IP has been blocked due to suspicious activity"
}
```

---

### 8. **Content Moderation**
Detects threatening or abusive language in complaints.

**Features:**
- Keyword-based detection
- Pattern matching for threats
- Admin notification for flagged content
- Automatic flagging of suspicious complaints

---

### 9. **AI Image Detection**
Prevents fraudulent complaints with AI-generated images.

**Detection methods:**
- Metadata analysis
- EXIF data inspection
- File size patterns
- Image characteristics

**Confidence levels:**
- **High (85%+)**: Submission rejected
- **Medium (60-84%)**: Flagged for officer verification
- **Low (<60%)**: Allowed

---

### 10. **Account Suspension System**
Protects against fraudulent users.

**Suspension triggers:**
- 3+ fraud warnings
- Officer-reported fraudulent complaints
- Repeated violations

**Features:**
- Automatic suspension after threshold
- Reason tracking
- Login blocked for suspended accounts

---

## 🔐 Authentication Security

### JWT Token Security
- Tokens expire after configured time
- Signed with secret key
- Validated on every protected route

### Password Security
- Passwords hashed using Werkzeug (PBKDF2)
- Never stored in plain text
- Salted automatically

### OTP Security
- 6-digit random codes
- Expires after 10 minutes
- One-time use only
- Sent via secure email

---

## 📊 Security Logging

All security events are logged with:
- Timestamp
- IP address
- Event type
- Details

**Event types logged:**
- `BLOCKED`: IP blocking events
- `SUSPICIOUS`: Suspicious activity detected
- `AUTH_FAILURE`: Failed login attempts

**Example log:**
```
🔒 SECURITY [2026-02-16T10:30:45] AUTH_FAILURE from 192.168.1.100: Failed login for user@example.com
```

---

## 🚨 Suspicious Activity Tracking

The system tracks and monitors:
1. **Invalid input patterns** (SQL injection attempts, XSS)
2. **Rate limit violations**
3. **Failed authentication attempts**
4. **Malformed requests**
5. **Path traversal attempts**

**Automatic actions:**
- Log all suspicious activity
- Track per IP address
- Auto-block after threshold
- Alert administrators

---

## 🔍 File Upload Security

### Filename Sanitization
- Removes path traversal characters (`../`, `..\\`)
- Strips special characters
- Only allows: alphanumeric, dash, underscore, dot

**Example:**
```python
# Input: "../../etc/passwd.jpg"
# Output: "etcpasswd.jpg"
```

### Image Validation
- File type verification
- Size limits enforced
- AI-generated image detection
- Metadata inspection

---

## 🌐 CORS Security

**Configuration:**
- Specific origins allowed (configurable)
- Limited HTTP methods
- Credentials support
- Preflight caching

**Production recommendation:**
Replace `origins: "*"` with your actual domain:
```python
CORS(app, resources={
    r"/*": {
        "origins": "https://yourdomain.com"
    }
})
```

---

## 📋 Security Checklist

### ✅ Implemented
- [x] Rate limiting on all sensitive endpoints
- [x] Input validation and sanitization
- [x] SQL injection prevention
- [x] XSS protection
- [x] CSRF protection via JWT
- [x] Password strength validation
- [x] Email validation
- [x] Phone validation
- [x] Security headers
- [x] IP blocking system
- [x] Content moderation
- [x] AI image detection
- [x] Account suspension system
- [x] Security logging
- [x] File upload sanitization
- [x] JWT authentication

### 🔄 Recommended for Production
- [ ] HTTPS enforcement (SSL/TLS)
- [ ] Database encryption at rest
- [ ] Regular security audits
- [ ] Penetration testing
- [ ] WAF (Web Application Firewall)
- [ ] DDoS protection service
- [ ] Backup and disaster recovery
- [ ] Security monitoring dashboard

---

## 🛠️ Usage Examples

### Applying Firewall to Routes

```python
from backend.security import require_firewall

@app.route('/api/sensitive-endpoint', methods=['POST'])
@require_firewall(max_requests=5, window_minutes=10)
def sensitive_endpoint():
    # Your logic here
    pass
```

### Validating Input

```python
from backend.security import SecurityFirewall

# Validate text input
is_valid, sanitized, error = SecurityFirewall.validate_input(user_input, 'field_name')
if not is_valid:
    return jsonify({'error': error}), 400

# Validate email
is_valid, normalized_email, error = SecurityFirewall.validate_email_address(email)

# Validate phone
is_valid, error = SecurityFirewall.validate_phone(phone)

# Check password strength
is_strong, error = SecurityFirewall.check_password_strength(password)
```

### Logging Security Events

```python
from backend.security import SecurityLogger

# Log suspicious activity
SecurityLogger.log_suspicious_activity(ip_address, "SQL injection attempt detected")

# Log blocked attempt
SecurityLogger.log_blocked_attempt(ip_address, "Rate limit exceeded")

# Log authentication failure
SecurityLogger.log_authentication_failure(ip_address, email)
```

---

## 🔧 Configuration

### Environment Variables

```bash
# .env file
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

### Rate Limit Configuration

Edit in `backend/security/firewall.py`:

```python
# Adjust these values as needed
MAX_REGISTRATION_ATTEMPTS = 5
MAX_LOGIN_ATTEMPTS = 10
MAX_OTP_REQUESTS = 10
MAX_GRIEVANCES_PER_HOUR = 20
```

---

## 🚀 Testing Security

### Test Rate Limiting

```bash
# Send multiple requests rapidly
for i in {1..15}; do
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"test123"}'
done
```

### Test Input Validation

```bash
# Try SQL injection
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"test OR 1=1","email":"test@example.com","password":"Test123"}'
```

### Test XSS Protection

```bash
# Try XSS attack
curl -X POST http://localhost:8000/api/grievances/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"complaint_text":"<script>alert(\"XSS\")</script>Test complaint"}'
```

---

## 📞 Security Incident Response

If you detect a security incident:

1. **Identify**: Check security logs for the IP address
2. **Block**: IP is automatically blocked after threshold
3. **Review**: Check `suspicious_ips` dictionary in logs
4. **Report**: Document the incident
5. **Update**: Enhance security rules if needed

---

## 📚 Dependencies

Security-related packages:

```
Flask-Limiter==3.5.0      # Rate limiting
Flask-Talisman==1.1.0     # Security headers
bleach>=6.1.0             # Input sanitization
email-validator>=2.1.0    # Email validation
Werkzeug==3.0.1           # Password hashing
PyJWT==2.8.0              # JWT authentication
```

---

## 🎓 Best Practices

1. **Never trust user input** - Always validate and sanitize
2. **Use HTTPS in production** - Encrypt data in transit
3. **Keep dependencies updated** - Regular security patches
4. **Monitor logs regularly** - Detect attacks early
5. **Use strong secrets** - Generate random SECRET_KEY
6. **Limit data exposure** - Only return necessary information
7. **Regular backups** - Protect against data loss
8. **Security training** - Educate team members

---

## 📖 References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

## 📝 License

This security implementation is part of the Smart Grievance System.

---

**Last Updated**: February 16, 2026

**Security Version**: 1.0.0

**Status**: ✅ Production Ready
