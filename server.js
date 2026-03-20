const http = require('node:http');
const path = require('node:path');
const fs = require('node:fs');
const { WebSocketServer } = require('ws');

const PORT = 8080;
const ROOT = __dirname;

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
};

const rooms = new Map();

function roomOf(name) {
  if (!rooms.has(name)) rooms.set(name, new Map());
  return rooms.get(name);
}

const server = http.createServer((req, res) => {
  const pathname = new URL(req.url, `http://localhost:${PORT}`).pathname;
  const rawPath = pathname === '/' ? '/index.html' : pathname;
  const safe = path.normalize(rawPath).replace(/^\.\.(\/|\\|$)+/, '');
  const filePath = path.join(ROOT, safe);

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not Found');
      return;
    }
    const ext = path.extname(filePath).toLowerCase();
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
    res.end(data);
  });
});

const wss = new WebSocketServer({ server });

function broadcast(roomName, payload, skipClient = null) {
  const room = rooms.get(roomName);
  if (!room) return;
  const data = JSON.stringify(payload);
  for (const player of room.values()) {
    if (player.ws === skipClient) continue;
    if (player.ws.readyState === 1) player.ws.send(data);
  }
}

wss.on('connection', (ws) => {
  let playerId = `p_${Math.random().toString(36).slice(2, 9)}`;
  let currentRoom = null;

  ws.on('message', (buf) => {
    let msg;
    try {
      msg = JSON.parse(String(buf));
    } catch {
      return;
    }

    if (msg.type === 'join') {
      currentRoom = msg.room || 'default';
      const room = roomOf(currentRoom);
      room.set(playerId, {
        id: playerId,
        name: msg.name || 'Player',
        ws,
        pos: { x: 0, y: 18, z: 0 },
      });

      const peers = [...room.values()]
        .filter((p) => p.id !== playerId)
        .map((p) => ({ id: p.id, name: p.name, pos: p.pos }));
      ws.send(JSON.stringify({ type: 'peers', players: peers }));
      broadcast(currentRoom, {
        type: 'player_join',
        player: { id: playerId, name: msg.name || 'Player', pos: { x: 0, y: 18, z: 0 } },
      }, ws);
      return;
    }

    if (msg.type === 'move' && currentRoom) {
      const room = rooms.get(currentRoom);
      const me = room?.get(playerId);
      if (!me) return;
      me.pos = msg.pos || me.pos;
      broadcast(currentRoom, { type: 'player_move', id: playerId, pos: me.pos }, ws);
    }
  });

  ws.on('close', () => {
    if (!currentRoom) return;
    const room = rooms.get(currentRoom);
    if (!room) return;
    room.delete(playerId);
    broadcast(currentRoom, { type: 'player_leave', id: playerId });
    if (room.size === 0) rooms.delete(currentRoom);
  });
});

server.listen(PORT, () => {
  console.log(`WebCraft server running at http://localhost:${PORT}`);
});
