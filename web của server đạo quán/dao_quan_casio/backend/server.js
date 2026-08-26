require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');
const admin = require('firebase-admin');

// ============== FIREBASE INIT ==============
let firebaseInitialized = false;
let db = null;
try {
  const serviceAccount = require('./serviceAccount.json');
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
  });
  db = admin.firestore();
  firebaseInitialized = true;
  console.log('✓ Firebase Admin initialized');
} catch (e) {
  console.warn('⚠ serviceAccount.json not found. Chat will use mock data.');
}

const app = express();
app.use(cors({ origin: true }));
app.use(express.json());
// Try .html extension for clean URLs
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

// ============== CONFIG ==============
const CONFIG = {
  clientId: process.env.DISCORD_CLIENT_ID,
  clientSecret: process.env.DISCORD_CLIENT_SECRET,
  redirectUri: process.env.REDIRECT_URI || 'http://localhost:4000/auth/discord/callback',
  port: process.env.PORT || 4000,
  frontendUrl: process.env.FRONTEND_URL || 'http://localhost:4000',
  botToken: process.env.DISCORD_BOT_TOKEN,
  chatChannelId: process.env.CHAT_CHANNEL_ID
};

// Discord webhook cache
let webhookUrl = null;
let webhookId = null;
let webhookToken = null;

// ============== MESSAGE CACHE ==============
let cachedMessages = [];
const CACHE_MAX = 200;

function addToCache(msg) {
  if (!msg.timestamp) msg.timestamp = Date.now();
  cachedMessages.push(msg);
  if (cachedMessages.length > CACHE_MAX * 2) {
    cachedMessages = cachedMessages.slice(-CACHE_MAX);
  }
}

async function loadCache() {
  if (!firebaseInitialized) return;
  try {
    const snapshot = await db.collection('messages')
      .orderBy('timestamp', 'desc').limit(CACHE_MAX).get();
    const msgs = [];
    snapshot.forEach(doc => {
      const d = doc.data();
      msgs.push({
        id: doc.id, text: d.text, uid: d.uid, author: d.author,
        avatar: d.avatar || '', timestamp: d.timestamp?.toMillis() || Date.now(), source: d.source || 'web'
      });
    });
    cachedMessages = msgs.reverse();
    console.log(`✓ Cache loaded: ${cachedMessages.length} messages`);
  } catch (e) {
    console.warn('⚠ Cache load failed:', e.message);
  }
}

async function ensureWebhook() {
  if (webhookUrl) return webhookUrl;
  if (!CONFIG.botToken || !CONFIG.chatChannelId) {
    console.warn('⚠ No DISCORD_BOT_TOKEN or CHAT_CHANNEL_ID — webhook disabled');
    return null;
  }
  try {
    // List existing webhooks
    const list = await axios.get(
      `https://discord.com/api/v10/channels/${CONFIG.chatChannelId}/webhooks`,
      { headers: { Authorization: `Bot ${CONFIG.botToken}` } }
    );
    const existing = list.data.find(w => w.name === 'Đạo Quán Web');
    if (existing) {
      webhookId = existing.id;
      webhookToken = existing.token;
      webhookUrl = `https://discord.com/api/webhooks/${webhookId}/${webhookToken}`;
      console.log('✓ Reusing existing webhook');
      return webhookUrl;
    }
    // Create new webhook
    const created = await axios.post(
      `https://discord.com/api/v10/channels/${CONFIG.chatChannelId}/webhooks`,
      { name: 'Đạo Quán Web' },
      { headers: { Authorization: `Bot ${CONFIG.botToken}` } }
    );
    webhookId = created.data.id;
    webhookToken = created.data.token;
    webhookUrl = `https://discord.com/api/webhooks/${webhookId}/${webhookToken}`;
    console.log('✓ Webhook created');
    return webhookUrl;
  } catch (e) {
    console.error('Webhook error:', e.response?.data || e.message);
    return null;
  }
}

// ============== DISCORD OAUTH ==============
app.get('/auth/discord', (req, res) => {
  const discordAuthUrl = 'https://discord.com/api/oauth2/authorize' +
    `?client_id=${CONFIG.clientId}` +
    `&redirect_uri=${encodeURIComponent(CONFIG.redirectUri)}` +
    '&response_type=code' +
    '&scope=identify';
  res.redirect(discordAuthUrl);
});

app.get('/auth/discord/callback', async (req, res) => {
  const { code } = req.query;
  if (!code) return res.status(400).send('Missing code');
  try {
    const tokenResp = await axios.post('https://discord.com/api/oauth2/token',
      new URLSearchParams({
        client_id: CONFIG.clientId,
        client_secret: CONFIG.clientSecret,
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

// ============== CHAT API ==============
// Send a message
app.post('/api/chat/send', async (req, res) => {
  const { text, uid, author, avatar } = req.body;
  if (!text || !uid || !author) return res.status(400).json({ error: 'Missing fields' });

  const entry = {
    text, uid, author, avatar: avatar || '',
    timestamp: Date.now(), source: 'web'
  };

  try {
    addToCache({ ...entry, id: 'cache-' + Date.now() });
    if (firebaseInitialized) {
      db.collection('messages').add({
        text, uid, author, avatar: avatar || '',
        timestamp: admin.firestore.FieldValue.serverTimestamp(), source: 'web'
      }).catch(() => {});
    }
    const wh = await ensureWebhook();
    if (wh) {
      axios.post(wh, { content: text, username: author, avatar_url: avatar || undefined }).catch(() => {});
    }
    res.json({ ok: true });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// Get recent messages (from cache, zero Firestore reads on subsequent polls)
app.get('/api/chat/messages', async (req, res) => {
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  if (!firebaseInitialized) return res.json([]);
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

// Get webhook info
app.get('/api/chat/webhook', async (req, res) => {
  const wh = await ensureWebhook();
  res.json({ webhook: !!wh, channelId: CONFIG.chatChannelId });
});

// Bridge: Discord message → cache + Firestore
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

// Bridge poll endpoint (for cron-job.org or external trigger)
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
    await stateDoc.set({ lastDiscordId: msgs[msgs.length - 1].id }, { merge: true });
    res.json({ ok: true, bridged });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ============== VERIFY TOKEN API ==============
app.post('/auth/verify', async (req, res) => {
  const { token } = req.body;
  if (!token) return res.status(400).json({ valid: false });
  try {
    if (firebaseInitialized) {
      const decoded = await admin.auth().verifyIdToken(token);
      res.json({ valid: true, uid: decoded.uid, name: decoded.discord_name, avatar: decoded.discord_avatar });
    } else {
      const data = JSON.parse(token);
      res.json({ valid: true, uid: data.id, name: data.username, avatar: data.avatar });
    }
  } catch {
    res.json({ valid: false });
  }
});

// ============== START ==============
app.listen(CONFIG.port, () => {
  console.log(`✓ Server running at http://localhost:${CONFIG.port}`);
  if (!firebaseInitialized) console.log('⚠ No Firebase — mock mode');
  ensureWebhook();
  loadCache();

  // ── Discord → Firestore Bridge (built-in) ──
  const BRIDGE_CHANNEL = process.env.CHAT_CHANNEL_ID || '1481167996461252652';
  const BRIDGE_TOKEN = process.env.DISCORD_BOT_TOKEN;
  if (BRIDGE_TOKEN && firebaseInitialized) {
    let bridgeLastId = null;
    let bridgeFailCount = 0;
    async function bridgePoll() {
      try {
        const url = `https://discord.com/api/v10/channels/${BRIDGE_CHANNEL}/messages?limit=10` + (bridgeLastId ? `&after=${bridgeLastId}` : '');
        const r = await axios.get(url, { headers: { Authorization: `Bot ${BRIDGE_TOKEN}` }, timeout: 8000 });
        const msgs = r.data;
        if (!msgs || !msgs.length) { bridgeFailCount = 0; return; }
        let bridged = 0;
        for (const msg of msgs.reverse()) {
          if (msg.author.bot || msg.webhook_id) continue;
          if (bridgeLastId && BigInt(msg.id) <= BigInt(bridgeLastId)) continue;
          const bridgeEntry = {
            id: 'discord-' + msg.id, text: msg.content, uid: msg.author.id,
            author: msg.author.global_name || msg.author.username,
            avatar: msg.author.avatar ? `https://cdn.discordapp.com/avatars/${msg.author.id}/${msg.author.avatar}.png` : '',
            timestamp: Date.now(), source: 'discord'
          };
          addToCache(bridgeEntry);
          db.collection('messages').add({
            text: msg.content, uid: msg.author.id,
            author: msg.author.global_name || msg.author.username,
            avatar: msg.author.avatar ? `https://cdn.discordapp.com/avatars/${msg.author.id}/${msg.author.avatar}.png` : '',
            timestamp: admin.firestore.FieldValue.serverTimestamp(), source: 'discord'
          }).catch(() => {});
          bridged++;
        }
        if (msgs.length) bridgeLastId = msgs[msgs.length - 1].id;
        bridgeFailCount = 0;
        if (bridged) console.log(`[Bridge] Synced ${bridged} messages`);
      } catch(e) {
        bridgeFailCount++;
        if (bridgeFailCount <= 3 || bridgeFailCount % 10 === 0)
          console.error(`[Bridge] Error (${bridgeFailCount}):`, e.response?.data?.message || e.message);
      }
    }
    bridgePoll();
    setInterval(bridgePoll, 3000);
    console.log(`✓ Discord bridge active — polling channel ${BRIDGE_CHANNEL} every 3s`);
  } else {
    console.log('⚠ Discord bridge disabled (no token or Firebase)');
  }
});
