# SMART KOPARGAON HACKATHON - SECURITY FIXES IMPLEMENTATION GUIDE

## IMMEDIATE FIXES REQUIRED

### 1. Add Security Headers

**For Vercel Deployment (vercel.json):**
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        },
        {
          "key": "Permissions-Policy",
          "value": "geolocation=(), microphone=(), camera=()"
        },
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://fonts.googleapis.com https://fonts.gstatic.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://*.firebaseio.com https://*.googleapis.com;"
        }
      ]
    }
  ]
}
```

**For Express.js Backend:**
```javascript
const helmet = require('helmet');

app.use(helmet());
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
    styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
    fontSrc: ["'self'", "https://fonts.gstatic.com"],
    imgSrc: ["'self'", "data:", "https:"],
    connectSrc: ["'self'", "https://*.firebaseio.com", "https://*.googleapis.com"]
  }
}));
```

---

### 2. Implement Rate Limiting

**For Express.js Backend:**
```javascript
const rateLimit = require('express-rate-limit');

// General API rate limiter
const apiLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 100, // 100 requests per minute
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});

// Strict limiter for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 requests per 15 minutes
  skipSuccessfulRequests: true,
  message: 'Too many login attempts, please try again later.',
});

// Apply to routes
app.use('/api/', apiLimiter);
app.use('/api/auth/login', authLimiter);
app.use('/api/auth/register', authLimiter);
```

**For Vercel Serverless Functions:**
```javascript
// utils/rateLimit.js
import { LRUCache } from 'lru-cache';

const rateLimit = (options) => {
  const tokenCache = new LRUCache({
    max: options.uniqueTokenPerInterval || 500,
    ttl: options.interval || 60000,
  });

  return {
    check: (limit, token) =>
      new Promise((resolve, reject) => {
        const tokenCount = tokenCache.get(token) || [0];
        if (tokenCount[0] === 0) {
          tokenCache.set(token, tokenCount);
        }
        tokenCount[0] += 1;

        const currentUsage = tokenCount[0];
        const isRateLimited = currentUsage >= limit;

        return isRateLimited ? reject() : resolve();
      }),
  };
};

// In your API route
import { rateLimit } from '../../utils/rateLimit';

const limiter = rateLimit({
  interval: 60 * 1000, // 60 seconds
  uniqueTokenPerInterval: 500,
});

export default async function handler(req, res) {
  try {
    await limiter.check(10, req.headers['x-forwarded-for'] || req.connection.remoteAddress);
    // Your API logic here
  } catch {
    return res.status(429).json({ error: 'Rate limit exceeded' });
  }
}
```

---

### 3. Input Validation & Sanitization

**Install dependencies:**
```bash
npm install express-validator
npm install xss
npm install validator
```

**Implementation:**
```javascript
const { body, validationResult } = require('express-validator');
const xss = require('xss');

// Validation middleware
const validateRegistration = [
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Invalid email address'),
  body('password')
    .isLength({ min: 8 })
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
    .withMessage('Password must be at least 8 characters with uppercase, lowercase, number, and special character'),
  body('name')
    .trim()
    .isLength({ min: 2, max: 50 })
    .customSanitizer(value => xss(value))
    .withMessage('Name must be between 2 and 50 characters'),
];

// Use in route
app.post('/api/auth/register', validateRegistration, (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  // Proceed with registration
});
```

---

### 4. Authentication & Authorization

**JWT Implementation:**
```javascript
const jwt = require('jsonwebtoken');

// Generate token
const generateToken = (userId, role) => {
  return jwt.sign(
    { userId, role },
    process.env.JWT_SECRET,
    { expiresIn: '24h' }
  );
};

// Verify token middleware
const authenticateToken = (req, res, next) => {
  const token = req.headers['authorization']?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid or expired token' });
    }
    req.user = user;
    next();
  });
};

// Role-based authorization
const authorizeRole = (...roles) => {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
};

// Use in routes
app.get('/api/admin/users', authenticateToken, authorizeRole('admin'), (req, res) => {
  // Admin-only logic
});
```

---

### 5. CORS Configuration

**Proper CORS setup:**
```javascript
const cors = require('cors');

const corsOptions = {
  origin: function (origin, callback) {
    const allowedOrigins = [
      'https://smartkopargaonhackathon.vercel.app',
      'https://www.smartkopargaonhackathon.com',
      // Add your production domains
    ];
    
    if (!origin || allowedOrigins.indexOf(origin) !== -1) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  optionsSuccessStatus: 200
};

app.use(cors(corsOptions));
```

---

### 6. Environment Variables Security

**Create .env file (NEVER commit this):**
```env
# Database
DATABASE_URL=your_database_url

# JWT
JWT_SECRET=your_very_long_random_secret_key_here

# Firebase (if using)
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id

# Razorpay
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret

# Other
NODE_ENV=production
```

**Add to .gitignore:**
```
.env
.env.local
.env.*.local
```

**Use in code:**
```javascript
require('dotenv').config();

const config = {
  jwtSecret: process.env.JWT_SECRET,
  databaseUrl: process.env.DATABASE_URL,
  // Never expose secrets to client
};
```

---

### 7. Logging & Monitoring

**Install Winston for logging:**
```bash
npm install winston
```

**Setup logger:**
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
});

// Log security events
logger.info('Login attempt', { email, ip: req.ip, timestamp: new Date() });
logger.warn('Failed login', { email, ip: req.ip, attempts: failedAttempts });
logger.error('Unauthorized access attempt', { endpoint: req.path, ip: req.ip });
```

---

### 8. Database Security

**Use parameterized queries (example with PostgreSQL):**
```javascript
// BAD - SQL Injection vulnerable
const query = `SELECT * FROM users WHERE email = '${email}'`;

// GOOD - Parameterized query
const query = 'SELECT * FROM users WHERE email = $1';
const result = await pool.query(query, [email]);
```

**For MongoDB:**
```javascript
// Use Mongoose with schema validation
const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    validate: {
      validator: (v) => /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(v),
      message: 'Invalid email format'
    }
  },
  password: {
    type: String,
    required: true,
    minlength: 8
  }
});
```

---

## DEPLOYMENT CHECKLIST

- [ ] Add security headers to vercel.json
- [ ] Implement rate limiting on all API endpoints
- [ ] Add input validation to all user inputs
- [ ] Implement proper authentication with JWT
- [ ] Add role-based authorization
- [ ] Configure CORS properly
- [ ] Move all secrets to environment variables
- [ ] Set up logging and monitoring
- [ ] Use parameterized database queries
- [ ] Test all security fixes
- [ ] Update documentation
- [ ] Schedule regular security audits

---

## TESTING AFTER FIXES

Run these commands to verify fixes:

```bash
# Test security headers
curl -I https://smartkopargaonhackathon.vercel.app

# Test rate limiting
for i in {1..20}; do curl https://smartkopargaonhackathon.vercel.app/api/health; done

# Test authentication
curl -X POST https://smartkopargaonhackathon.vercel.app/api/admin/users
# Should return 401 Unauthorized
```

---

**Document Version:** 1.0
**Last Updated:** 2026-05-16
