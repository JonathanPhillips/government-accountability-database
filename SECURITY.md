# Security Policy

## Supported Versions

We release patches for security vulnerabilities. The following versions are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please DO NOT report security vulnerabilities through public GitHub issues.**

### Preferred Method

Please report security vulnerabilities by email to:
**security@yourdomain.com**

### What to Include

Please include the following information in your report:

1. **Description**: A clear description of the vulnerability
2. **Impact**: What an attacker could potentially do
3. **Affected Component**: Which part of the system is affected
4. **Steps to Reproduce**: Detailed steps to reproduce the vulnerability
5. **Proof of Concept**: If possible, include a proof of concept
6. **Suggested Fix**: If you have ideas on how to fix it
7. **Disclosure Timeline**: Your preferred disclosure timeline

### Example Report Template

```markdown
**Summary:**
Brief description of the vulnerability

**Severity:** Critical / High / Medium / Low

**Affected Component:**
- Backend API / Frontend / Database / Authentication / etc.

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Impact:**
What an attacker could do with this vulnerability

**Proposed Fix:**
How this could be fixed (if known)

**Your Name/Handle:**
How you'd like to be credited (optional)
```

## Response Timeline

- **Initial Response**: Within 48 hours of report
- **Assessment**: Within 7 days, we'll assess the severity
- **Fix Development**: Depends on severity:
  - **Critical**: Within 24-48 hours
  - **High**: Within 7 days
  - **Medium**: Within 30 days
  - **Low**: Next minor release
- **Public Disclosure**: After fix is deployed and users are notified

## Security Update Process

1. **Triage**: Security team reviews and confirms the vulnerability
2. **Assessment**: Determine severity and impact
3. **Fix Development**: Develop and test a fix
4. **Internal Testing**: Thoroughly test the fix
5. **Release**: Deploy fix to production
6. **Notification**: Notify users via security advisory
7. **Public Disclosure**: 30 days after fix deployment

## Bug Bounty Program

We currently do not have a formal bug bounty program. However, we:
- Acknowledge security researchers in our SECURITY.md
- Provide detailed credit in security advisories
- Are open to discussing rewards for critical vulnerabilities

## Security Best Practices

### For Developers

1. **Code Review**: All code must be reviewed before merging
2. **Dependency Scanning**: Use Dependabot and security scanners
3. **Secrets Management**: Never commit secrets or credentials
4. **Input Validation**: Always validate and sanitize user input
5. **Authentication**: Use strong authentication (JWT with secure secrets)
6. **Authorization**: Implement proper RBAC
7. **SQL Injection**: Use parameterized queries (SQLAlchemy ORM)
8. **XSS Prevention**: Sanitize output, use Content Security Policy
9. **CSRF Protection**: Use CSRF tokens for state-changing operations
10. **Security Headers**: Implement security headers (X-Frame-Options, etc.)

### For Deployers

1. **Environment Variables**: Use environment variables for sensitive data
2. **HTTPS Only**: Always use HTTPS in production
3. **Database Security**: Use strong passwords, restrict access
4. **Firewall**: Configure firewall to restrict unnecessary ports
5. **Updates**: Keep all dependencies and systems updated
6. **Backups**: Implement automated encrypted backups
7. **Monitoring**: Set up security monitoring and alerting
8. **Access Control**: Restrict SSH access, use key-based auth
9. **Secrets Rotation**: Regularly rotate secrets and API keys
10. **Audit Logs**: Enable and monitor audit logs

## Security Features

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Bcrypt password hashing (12 rounds)
- Role-based access control (RBAC)
- Token expiration and refresh mechanism
- Secure session cookies (HTTPOnly, Secure, SameSite)

### Data Protection
- SQL injection prevention (ORM)
- XSS protection (CSP headers)
- CSRF protection
- Input validation (Pydantic schemas)
- Output sanitization

### Infrastructure Security
- HTTPS enforcement in production
- Security middleware (TrustedHost, GZip, Sessions)
- Rate limiting
- Database connection pooling with limits
- Secure default configurations

### Monitoring & Logging
- Health check endpoints
- Structured logging
- Error tracking (Sentry integration)
- Security event logging
- Audit trail for sensitive operations

## Known Security Considerations

### Default Credentials
⚠️ **CRITICAL**: Change default admin credentials immediately after deployment
- Default Email: `admin@gadb.local`
- Default Password: `changeme123`

### Environment Variables
⚠️ **IMPORTANT**: Generate strong values for:
- `SECRET_KEY`: Use `openssl rand -hex 32`
- `POSTGRES_PASSWORD`: Use strong random password
- `REDIS_PASSWORD`: Use strong random password

### Docker Security
- Non-root user in containers
- Multi-stage builds to minimize attack surface
- Regular base image updates
- No secrets in Docker images

## Security Checklist for Deployment

Before deploying to production, ensure:

- [ ] Changed default admin password
- [ ] Generated strong SECRET_KEY (32+ characters)
- [ ] Using HTTPS with valid SSL certificate
- [ ] Database using strong passwords
- [ ] Firewall configured properly
- [ ] Rate limiting enabled
- [ ] CORS origins restricted to your domain
- [ ] Debug mode disabled (DEBUG=False)
- [ ] Secure cookies enabled (SECURE_COOKIES=True)
- [ ] HTTPS-only mode enabled (HTTPS_ONLY=True)
- [ ] Monitoring and alerting configured
- [ ] Automated backups configured
- [ ] All dependencies updated
- [ ] Security headers configured
- [ ] SSH access restricted (key-based only)

## Security Contacts

- **Security Email**: security@yourdomain.com
- **Security Team**: [@security-team](https://github.com/orgs/yourorg/teams/security-team)
- **PGP Key**: Available upon request

## Security Advisories

View published security advisories:
https://github.com/JonathanPhillips/government-accountability-database/security/advisories

## Credits

We thank the following security researchers for responsibly disclosing vulnerabilities:

<!-- This section will be updated as security researchers report vulnerabilities -->

*Be the first to help us improve security!*

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

**Last Updated**: January 2026

**Questions?** Email security@yourdomain.com
