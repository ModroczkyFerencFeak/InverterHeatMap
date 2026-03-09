/**
 * Vercel build: AUTH_USER és AUTH_HASH env-ből generálja az auth-config.js-t.
 * A repóban nincs titkos adat; a Vercel Environment Variables-ban állíts be:
 *   AUTH_USER = felhasználónév
 *   AUTH_HASH = jelszó SHA-256 hash-e (kisbetűs hex)
 */
const fs = require('fs');
const path = require('path');

const user = process.env.AUTH_USER || '';
const hash = (process.env.AUTH_HASH || '').trim().toLowerCase();
const outPath = path.join(__dirname, '..', 'auth-config.js');

const content = `// Generálva a build során (Vercel: AUTH_USER, AUTH_HASH)
window.__AUTH_USER__ = ${JSON.stringify(user)};
window.__AUTH_HASH__ = ${JSON.stringify(hash)};
`;

fs.writeFileSync(outPath, content, 'utf8');
console.log('auth-config.js generated from env');
