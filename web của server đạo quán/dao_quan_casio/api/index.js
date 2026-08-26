require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');
const admin = require('firebase-admin');
let firebaseInitialized = false;
let db = null;
try {
  const saPath = path.join(__dirname, 'serviceAccount.json');
  const serviceAccount = require(saPath);
  admin.initializeApp({ credential: admin.credential.cert(serviceAccount) });
  db = admin.firestore();
  firebaseInitialized = true;
  console.log('✓ Firebase Admin initialized');
} catch (e) {
  console.warn('⚠ serviceAccount.json not found. Chat will use mock data.');
}

const app = express();
app.use(cors({ origin: true }));
app.use(express.json());

app.use((req, res, next) => {
  if (!req.path.includes('.') && !req.path.startsWith('/api/') && !req.path.startsWith('/auth/')) {
    try {
      const htmlPath = path.join(__dirname, '..', req.path + '.html');
      if (require('fs').existsSync(htmlPath)) return res.sendFile(htmlPath);
    } catch(e) {}
  }
  next();
});
app.use(express.static(path.join(__dirname, '..')));

const CONFIG = {
  clientId: process.env.DISCORD_CLIENT_ID,
  clientSecret: process.env.DISCORD_CLIENT_SECRET,
  redirectUri: process.env.REDIRECT_URI || 'http://localhost:4000/auth/discord/callback',
  port: process.env.PORT || 4000,
  frontendUrl: process.env.FRONTEND_URL || 'http://localhost:4000',
  botToken: process.env.DISCORD_BOT_TOKEN,
  chatChannelId: process.env.CHAT_CHANNEL_ID
};

let webhookUrl = null;
let webhookId = null;
let webhookToken = null;

let cachedMessages = [];
const CACHE_MAX = 200;

function addToCache(msg) {
  if (!msg.timestamp) msg.timestamp = Date.now();
  cachedMessages.push(msg);
  if (cachedMessages.length > CACHE_MAX * 2) cachedMessages = cachedMessages.slice(-CACHE_MAX);
}

async function loadCache() {
  if (!firebaseInitialized) return;
  try {
    const snapshot = await db.collection('messages').orderBy('timestamp', 'desc').limit(CACHE_MAX).get();
    const msgs = [];
    snapshot.forEach(doc => {
      const d = doc.data();
      msgs.push({ id: doc.id, text: d.text, uid: d.uid, author: d.author,
        avatar: d.avatar || '', timestamp: d.timestamp?.toMillis() || Date.now(), source: d.source || 'web' });
    });
    cachedMessages = msgs.reverse();
  } catch (e) { console.warn('Cache load:', e.message); }
}

async function ensureWebhook() {
  if (webhookUrl) return webhookUrl;
  if (!CONFIG.botToken || !CONFIG.chatChannelId) return null;
  try {
    const list = await axios.get(
      `https://discord.com/api/v10/channels/${CONFIG.chatChannelId}/webhooks`,
      { headers: { Authorization: `Bot ${CONFIG.botToken}` } }
    );
    const existing = list.data.find(w => w.name === 'Dao Quan Web');
    if (existing) {
      webhookId = existing.id; webhookToken = existing.token;
      webhookUrl = `https://discord.com/api/webhooks/${webhookId}/${webhookToken}`;
      return webhookUrl;
    }
    const created = await axios.post(
      `https://discord.com/api/v10/channels/${CONFIG.chatChannelId}/webhooks`,
      { name: 'Dao Quan Web' },
      { headers: { Authorization: `Bot ${CONFIG.botToken}` } }
    );
    webhookId = created.data.id; webhookToken = created.data.token;
    webhookUrl = `https://discord.com/api/webhooks/${webhookId}/${webhookToken}`;
    return webhookUrl;
  } catch (e) {
    console.error('Webhook error:', e.response?.data || e.message);
    return null;
  }
}

app.get('/auth/discord', (req, res) => {
  const url = 'https://discord.com/api/oauth2/authorize' +
    `?client_id=${CONFIG.clientId}` +
    `&redirect_uri=${encodeURIComponent(CONFIG.redirectUri)}` +
    '&response_type=code&scope=identify';
  res.redirect(url);
});

app.get('/auth/discord/callback', async (req, res) => {
  const { code } = req.query;
  if (!code) return res.status(400).send('Missing code');
  try {
    const tokenResp = await axios.post('https://discord.com/api/oauth2/token',
      new URLSearchParams({
        client_id: CONFIG.clientId, client_secret: CONFIG.clientSecret,
        code, grant_type: 'authorization_code',
        redirect_uri: CONFIG.redirectUri, scope: 'identify'
      }), { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
    const accessToken = tokenResp.data.access_token;
    const userResp = await axios.get('https://discord.com/api/users/@me', {
      headers: { Authorization: `Bearer ${accessToken}` }
    });
    const { id, username, global_name, avatar, discriminator } = userResp.data;
    const displayName = global_name || username;
    const avatarUrl = avatar
      ? `https://cdn.discordapp.com/avatars/${id}/${avatar}.png`
      : `https://cdn.discordapp.com/embed/avatars/${discriminator % 5}.png`;

    let token = null;
    let firebaseMock = false;
    if (firebaseInitialized) {
      token = await admin.auth().createCustomToken(id, {
        discord_name: displayName, discord_avatar: avatarUrl
      });
    } else {
      firebaseMock = true;
      token = JSON.stringify({ id, username: displayName, avatar: avatarUrl });
    }
    res.redirect(`${CONFIG.frontendUrl}/?token=${encodeURIComponent(token)}&mock=${firebaseMock}&name=${encodeURIComponent(displayName)}&avatar=${encodeURIComponent(avatarUrl)}`);
  } catch (error) {
    console.error('OAuth error:', error.response?.data || error.message);
    res.status(500).send('Authentication failed');
  }
});

app.post('/api/chat/send', async (req, res) => {
  const { text, uid, author, avatar } = req.body;
  if (!text || !uid || !author) return res.status(400).json({ error: 'Missing fields' });
  addToCache({ id: 'cache-' + Date.now(), text, uid, author, avatar: avatar || '', timestamp: Date.now(), source: 'web' });
  if (firebaseInitialized) {
    db.collection('messages').add({
      text, uid, author, avatar: avatar || '',
      timestamp: admin.firestore.FieldValue.serverTimestamp(), source: 'web'
    }).catch(() => {});
  }
  const wh = await ensureWebhook();
  if (wh) axios.post(wh, { content: text, username: author, avatar_url: avatar || undefined }).catch(() => {});
  res.json({ ok: true });
});

app.get('/api/chat/messages', async (req, res) => {
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  if (!firebaseInitialized) return res.json([]);
  // Lazy-load cache from Firestore if empty (cold start on Vercel)
  if (!cachedMessages.length) {
    try {
      const snapshot = await db.collection('messages').orderBy('timestamp', 'desc').limit(CACHE_MAX).get();
      snapshot.forEach(doc => {
        const d = doc.data();
        cachedMessages.push({ id: doc.id, text: d.text, uid: d.uid, author: d.author,
          avatar: d.avatar || '', timestamp: d.timestamp?.toMillis() || Date.now(), source: d.source || 'web' });
      });
      cachedMessages = cachedMessages.reverse();
    } catch (e) { return res.json([]); }
  }
  if (req.query.since) {
    const since = parseInt(req.query.since);
    if (!isNaN(since)) return res.json(cachedMessages.filter(m => m.timestamp > since));
  }
  return res.json(cachedMessages);
});

app.get('/api/chat/webhook', async (req, res) => {
  const wh = await ensureWebhook();
  res.json({ webhook: !!wh, channelId: CONFIG.chatChannelId });
});

app.post('/api/bridge/discord-message', async (req, res) => {
  const { text, uid, author, avatar } = req.body;
  if (!text || !uid || !author) return res.status(400).json({ error: 'Missing fields' });
  addToCache({ id: 'bridge-' + Date.now(), text, uid, author, avatar: avatar || '', timestamp: Date.now(), source: 'discord' });
  if (firebaseInitialized) {
    db.collection('messages').add({
      text, uid, author, avatar: avatar || '',
      timestamp: admin.firestore.FieldValue.serverTimestamp(), source: 'discord'
    }).catch(() => {});
  }
  res.json({ ok: true });
});

// Bridge poll endpoint (called by cron-job.org every 5s)
app.get('/api/bridge/poll', async (req, res) => {
  if (req.query.secret !== process.env.BRIDGE_SECRET) return res.status(403).json({ error: 'Forbidden' });
  if (!CONFIG.botToken || !CONFIG.chatChannelId || !firebaseInitialized) return res.json({ error: 'Not configured' });
  try {
    const stateDoc = db.collection('bridge_state').doc(CONFIG.chatChannelId);
    const stateSnap = await stateDoc.get();
    const lastId = stateSnap.exists ? stateSnap.data().lastDiscordId : null;
    const url = `https://discord.com/api/v10/channels/${CONFIG.chatChannelId}/messages?limit=10` + (lastId ? `&after=${lastId}` : '');
    const r = await axios.get(url, { headers: { Authorization: `Bot ${CONFIG.botToken}` }, timeout: 10000 });
    const msgs = r.data;
    if (!msgs || !msgs.length) return res.json({ bridged: 0 });
    let bridged = 0;
    for (const msg of msgs.reverse()) {
      if (msg.author.bot || msg.webhook_id) continue;
      if (lastId && BigInt(msg.id) <= BigInt(lastId)) continue;
      const entry = {
        text: msg.content, uid: msg.author.id,
        author: msg.author.global_name || msg.author.username,
        avatar: msg.author.avatar ? `https://cdn.discordapp.com/avatars/${msg.author.id}/${msg.author.avatar}.png` : '',
        timestamp: Date.now(), source: 'discord'
      };
      addToCache({ id: 'discord-' + msg.id, ...entry });
      db.collection('messages').add({ ...entry, timestamp: admin.firestore.FieldValue.serverTimestamp() }).catch(() => {});
      bridged++;
    }
    const newLastId = msgs[msgs.length - 1].id;
    await stateDoc.set({ lastDiscordId: newLastId }, { merge: true });
    res.json({ ok: true, bridged });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.post('/api/webhook/discord', async (req, res) => {
  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
    if (body.type === 1) return res.json({ type: 1 });
    const msg = body.message || body;
    if (!msg.content || msg.author?.bot || msg.webhook_id) return res.status(200).end();
    addToCache({
      id: 'wh-' + Date.now(), text: msg.content, uid: msg.author.id,
      author: msg.author.global_name || msg.author.username,
      avatar: msg.author.avatar ? `https://cdn.discordapp.com/avatars/${msg.author.id}/${msg.author.avatar}.png` : '',
      timestamp: Date.now(), source: 'discord'
    });
    if (firebaseInitialized) {
      db.collection('messages').add({
        text: msg.content, uid: msg.author.id,
        author: msg.author.global_name || msg.author.username,
        avatar: msg.author.avatar ? `https://cdn.discordapp.com/avatars/${msg.author.id}/${msg.author.avatar}.png` : '',
        timestamp: admin.firestore.FieldValue.serverTimestamp(), source: 'discord'
      }).catch(() => {});
    }
    res.status(200).end();
  } catch (e) { res.status(200).end(); }
});

app.post('/auth/verify', async (req, res) => {
  const { token } = req.body;
  if (!token) return res.json({ valid: false });
  try {
    if (firebaseInitialized) {
      const decoded = await admin.auth().verifyIdToken(token);
      res.json({ valid: true, uid: decoded.uid, name: decoded.discord_name, avatar: decoded.discord_avatar });
    } else {
      const data = JSON.parse(token);
      res.json({ valid: true, uid: data.id, name: data.username, avatar: data.avatar });
    }
  } catch { res.json({ valid: false }); }
});

if (!process.env.VERCEL) {
  app.listen(CONFIG.port, () => {
    console.log(`✓ Server running at http://localhost:${CONFIG.port}`);
    if (!firebaseInitialized) console.log('⚠ No Firebase — mock mode');
    ensureWebhook();
    loadCache();
  });
}

module.exports = app;
