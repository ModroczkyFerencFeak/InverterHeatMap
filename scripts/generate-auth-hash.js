/**
 * AUTH_HASH érték készítése a Vercel Environment Variable-hoz.
 * Használat: node scripts/generate-auth-hash.js "Jelszó"
 * Kimenet: a jelszó SHA-256 hash-e (kisbetűs hex) – ezt másold be az AUTH_HASH-ba.
 */
const crypto = require('crypto');
const password = process.argv[2] || '';
if (!password) {
  console.error('Hasznalat: node scripts/generate-auth-hash.js "Jelszó"');
  process.exit(1);
}
const hash = crypto.createHash('sha256').update(password, 'utf8').digest('hex');
console.log(hash);
