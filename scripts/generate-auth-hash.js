/**
 * AUTH_HASH érték készítése a Vercel Environment Variable-hoz.
 * NFC normalizálás, hogy a böngészővel egyezzen.
 * Használat: node scripts/generate-auth-hash.js "Jelszó"
 */
const crypto = require('crypto');
const password = (process.argv[2] || '');
const normalized = typeof password.normalize === 'function' ? password.normalize('NFC') : password;
const hash = crypto.createHash('sha256').update(normalized, 'utf8').digest('hex');
console.log(hash);
