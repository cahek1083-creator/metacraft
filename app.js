const STORAGE_KEY = 'webcraft_worlds_v1';

const ui = {
  menuOverlay: document.getElementById('menu-overlay'),
  hud: document.getElementById('hud'),
  crosshair: document.getElementById('crosshair'),
  activeWorld: document.getElementById('active-world'),
  activeBlock: document.getElementById('active-block'),

  screenMain: document.getElementById('screen-main'),
  screenSingle: document.getElementById('screen-singleplayer'),
  screenMulti: document.getElementById('screen-multiplayer'),
  screenCreate: document.getElementById('screen-create-world'),
  screenOptions: document.getElementById('options-panel'),

  worldList: document.getElementById('world-list'),
  worldEmpty: document.getElementById('world-empty'),
  worldName: document.getElementById('world-name'),
  worldSeed: document.getElementById('world-seed'),
  worldGamemode: document.getElementById('world-gamemode'),

  sensitivity: document.getElementById('sensitivity'),

  btnSingle: document.getElementById('btn-singleplayer'),
  btnMulti: document.getElementById('btn-multiplayer'),
  btnRealms: document.getElementById('btn-realms'),
  btnOptions: document.getElementById('btn-options'),
  btnQuit: document.getElementById('btn-quit'),
  btnCloseOptions: document.getElementById('btn-close-options'),

  btnPlayWorld: document.getElementById('btn-play-world'),
  btnCreateWorld: document.getElementById('btn-create-world'),
  btnDeleteWorld: document.getElementById('btn-delete-world'),
  btnSingleBack: document.getElementById('btn-single-back'),

  btnConfirmCreate: document.getElementById('btn-confirm-create'),
  btnCreateBack: document.getElementById('btn-create-back'),

  mpName: document.getElementById('mp-name'),
  mpRoom: document.getElementById('mp-room'),
  mpServerUrl: document.getElementById('mp-server-url'),
  mpWorldList: document.getElementById('mp-world-list'),
  mpWorldEmpty: document.getElementById('mp-world-empty'),
  btnJoinMp: document.getElementById('btn-join-mp'),
  btnRefreshMp: document.getElementById('btn-refresh-mp'),
  btnMpBack: document.getElementById('btn-mp-back'),
};

const MP_WS_URL = `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}`;
ui.mpServerUrl.textContent = MP_WS_URL;

const state = {
  sensitivity: 1,
  running: false,
  engineReady: false,
  worlds: loadWorlds(),
  selectedWorldId: null,
  startSession: null,
  stopSession: null,
  setSpawn: null,
  pendingSeed: 'default',
  multiplayer: {
    socket: null,
    connected: false,
    room: null,
    playerName: null,
    remotePlayers: new Map(),
    sendPosition: null,
    clearRemotes: null,
    applyRemoteBlock: null,
    pendingEdits: [],
  },
};

if (state.worlds.length > 1) {
  state.worlds = [state.worlds[0]];
  saveWorlds();
}

function loadWorlds() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const arr = raw ? JSON.parse(raw) : [];
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

function saveWorlds() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state.worlds));
  } catch (error) {
    console.warn('Failed to save worlds to localStorage:', error);
  }
}

function createId() {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
  return `world-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function showScreen(name) {
  const screens = {
    main: ui.screenMain,
    single: ui.screenSingle,
    multi: ui.screenMulti,
    create: ui.screenCreate,
    options: ui.screenOptions,
  };
  Object.values(screens).forEach((el) => el.classList.add('hidden'));
  screens[name].classList.remove('hidden');
}

function renderWorldList() {
  ui.worldList.innerHTML = '';
  ui.worldEmpty.classList.toggle('hidden', state.worlds.length !== 0);

  for (const world of state.worlds) {
    const li = document.createElement('li');
    li.dataset.id = world.id;
    li.innerHTML = `<strong>${world.name}</strong><br><small>${world.gamemode} • seed: ${world.seed || 'random'}</small>`;
    if (world.id === state.selectedWorldId) li.classList.add('selected');
    li.addEventListener('click', () => {
      state.selectedWorldId = world.id;
      renderWorldList();
    });
    ui.worldList.appendChild(li);
  }

  const hasWorld = Boolean(state.worlds[0]);
  ui.btnPlayWorld.disabled = !state.selectedWorldId;
  ui.btnDeleteWorld.disabled = true;
  ui.btnCreateWorld.disabled = hasWorld;
}

function renderMpWorlds(worlds) {
  ui.mpWorldList.innerHTML = '';
  const safe = Array.isArray(worlds) ? worlds : [];
  ui.mpWorldEmpty.classList.toggle('hidden', safe.length !== 0);
  for (const world of safe) {
    const li = document.createElement('li');
    li.innerHTML = `<strong>${world.room}</strong><br><small>players: ${world.players}</small>`;
    li.addEventListener('click', () => {
      ui.mpRoom.value = world.room;
    });
    ui.mpWorldList.appendChild(li);
  }
}

async function refreshMpWorlds() {
  try {
    const response = await fetch('/api/worlds');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    renderMpWorlds(payload.worlds || []);
  } catch (error) {
    console.warn('Failed to load multiplayer worlds', error);
    renderMpWorlds([]);
  }
}

ui.sensitivity.addEventListener('input', () => {
  state.sensitivity = Number(ui.sensitivity.value);
});

ui.btnSingle.addEventListener('click', () => {
  if (state.worlds[0]) {
    state.selectedWorldId = state.worlds[0].id;
    ui.btnPlayWorld.click();
    return;
  }
  showScreen('single');
  renderWorldList();
});

ui.btnSingleBack.addEventListener('click', () => showScreen('main'));
ui.btnMpBack.addEventListener('click', () => showScreen('main'));
ui.btnCreateWorld.addEventListener('click', () => showScreen('create'));
ui.btnCreateBack.addEventListener('click', () => showScreen('single'));

ui.btnConfirmCreate.addEventListener('click', () => {
  if (state.worlds[0]) {
    alert('Мир уже создан. Доступен только один мир.');
    showScreen('single');
    return;
  }
  const world = {
    id: createId(),
    name: ui.worldName.value.trim() || 'New World',
    seed: ui.worldSeed.value.trim(),
    gamemode: ui.worldGamemode.value,
    spawn: { x: 0, y: 18, z: 0 },
  };
  state.worlds.unshift(world);
  state.selectedWorldId = world.id;
  saveWorlds();
  showScreen('single');
  renderWorldList();
});

ui.btnDeleteWorld.addEventListener('click', () => {
  if (!state.selectedWorldId) return;
  const yes = confirm('Delete selected world?');
  if (!yes) return;
  state.worlds = state.worlds.filter((w) => w.id !== state.selectedWorldId);
  state.selectedWorldId = state.worlds[0]?.id ?? null;
  saveWorlds();
  renderWorldList();
});

ui.btnOptions.addEventListener('click', () => showScreen('options'));
ui.btnCloseOptions.addEventListener('click', () => showScreen('main'));
ui.btnMulti.addEventListener('click', async () => {
  showScreen('multi');
  await refreshMpWorlds();
});
ui.btnRealms.addEventListener('click', () => alert('Minecraft Realms пока не реализован в этом прототипе.'));
ui.btnQuit.addEventListener('click', () => alert('В браузере закрой вкладку вручную.'));
ui.btnRefreshMp.addEventListener('click', refreshMpWorlds);

ui.btnJoinMp.addEventListener('click', async () => {
  const name = (ui.mpName.value || '').trim() || 'Player';
  const room = (ui.mpRoom.value || '').trim() || 'default';

  ui.btnJoinMp.disabled = true;
  ui.btnJoinMp.textContent = 'Connecting...';
  try {
    state.pendingSeed = world.seed || world.name || 'default';
    await connectMultiplayer(name, room);
    const world = state.worlds[0] ?? {
      id: 'mp-local',
      name: `MP: ${room}`,
      spawn: { x: 0, y: 18, z: 0 },
      gamemode: 'creative',
      seed: '',
    };
    if (!state.engineReady) {
      await initEngine();
      state.engineReady = true;
    }
    state.setSpawn?.(world.spawn);
    ui.activeWorld.textContent = `${world.name} (MP)`;
    state.startSession?.();
  } catch (error) {
    console.error(error);
    alert(`Не удалось подключиться к multiplayer (${MP_WS_URL}). Проверь, что сервер запущен: npm install && npm run serve`);
  } finally {
    ui.btnJoinMp.disabled = false;
    ui.btnJoinMp.textContent = 'Join World';
  }
});

ui.btnPlayWorld.addEventListener('click', async () => {
  const world = state.worlds.find((w) => w.id === state.selectedWorldId);
  if (!world) return;

  ui.btnPlayWorld.disabled = true;
  ui.btnPlayWorld.textContent = state.engineReady ? 'Loading world...' : 'Preparing engine...';

  try {
    state.pendingSeed = world.seed || world.name || 'default';
    if (!state.engineReady) {
      await initEngine();
      state.engineReady = true;
    }
    state.setSpawn?.(world.spawn);
    ui.activeWorld.textContent = world.name;
    state.startSession?.();
  } catch (error) {
    console.error(error);
    alert(`Не удалось запустить 3D-сцену: ${error.message}`);
  } finally {
    ui.btnPlayWorld.disabled = false;
    ui.btnPlayWorld.textContent = 'Play Selected World';
  }
});

async function connectMultiplayer(playerName, room) {
  if (state.multiplayer.connected && state.multiplayer.socket?.readyState === WebSocket.OPEN) {
    state.multiplayer.playerName = playerName;
    state.multiplayer.room = room;
    return;
  }

  await new Promise((resolve, reject) => {
    const socket = new WebSocket(MP_WS_URL);
    let settled = false;

    const fail = (error) => {
      if (settled) return;
      settled = true;
      reject(error);
    };
    const pass = () => {
      if (settled) return;
      settled = true;
      resolve();
    };

    socket.addEventListener('open', () => {
      state.multiplayer.socket = socket;
      state.multiplayer.connected = true;
      state.multiplayer.playerName = playerName;
      state.multiplayer.room = room;
      socket.send(JSON.stringify({ type: 'join', room, name: playerName }));
      pass();
    });

    socket.addEventListener('message', (event) => {
      let msg = null;
      try {
        msg = JSON.parse(event.data);
      } catch {
        return;
      }
      if (msg.type === 'peers' && state.multiplayer.clearRemotes) {
        state.multiplayer.clearRemotes(msg.players || []);
      }
      if (msg.type === 'player_move' && state.multiplayer.remotePlayers.has(msg.id)) {
        const mesh = state.multiplayer.remotePlayers.get(msg.id);
        mesh.position.set(msg.pos.x, msg.pos.y, msg.pos.z);
      }
      if (msg.type === 'player_join' && state.multiplayer.clearRemotes) {
        state.multiplayer.clearRemotes([msg.player]);
      }
      if (msg.type === 'player_leave' && state.multiplayer.remotePlayers.has(msg.id)) {
        const mesh = state.multiplayer.remotePlayers.get(msg.id);
        mesh.parent?.remove(mesh);
        state.multiplayer.remotePlayers.delete(msg.id);
      }
      if ((msg.type === 'world_state' || msg.type === 'block_set' || msg.type === 'block_remove')) {
        if (state.multiplayer.applyRemoteBlock) {
          state.multiplayer.applyRemoteBlock(msg);
        } else {
          state.multiplayer.pendingEdits.push(msg);
        }
      }
    });

    socket.addEventListener('close', () => {
      state.multiplayer.connected = false;
      state.multiplayer.socket = null;
    });
    socket.addEventListener('error', () => fail(new Error('Multiplayer socket error')));
    setTimeout(() => fail(new Error('Multiplayer timeout')), 3500);
  });
}

async function initEngine() {
  const probeCanvas = document.createElement('canvas');
  const hasWebGL = Boolean(probeCanvas.getContext('webgl') || probeCanvas.getContext('experimental-webgl'));
  if (!hasWebGL) {
    throw new Error('WebGL недоступен в браузере/устройстве.');
  }

  const sources = [
    {
      three: 'https://esm.sh/three@0.164.1',
      controls: 'https://esm.sh/three@0.164.1/examples/jsm/controls/PointerLockControls.js',
    },
    {
      three: 'https://unpkg.com/three@0.164.1/build/three.module.js?module',
      controls: 'https://unpkg.com/three@0.164.1/examples/jsm/controls/PointerLockControls.js?module',
    },
    {
      three: 'https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js',
      controls: 'https://cdn.jsdelivr.net/npm/three@0.164.1/examples/jsm/controls/PointerLockControls.js',
    },
    {
      three: 'https://ga.jspm.io/npm:three@0.164.1/build/three.module.js',
      controls: 'https://ga.jspm.io/npm:three@0.164.1/examples/jsm/controls/PointerLockControls.js',
    },
  ];

  let THREE;
  let PointerLockControls;
  let lastError = null;
  for (const source of sources) {
    try {
      const [threeMod, controlsMod] = await Promise.all([
        import(source.three),
        import(source.controls),
      ]);
      THREE = threeMod;
      PointerLockControls = controlsMod.PointerLockControls;
      lastError = null;
      break;
    } catch (error) {
      lastError = error;
    }
  }
  if (!THREE || !PointerLockControls) {
    throw new Error(`Three.js CDN недоступен (${lastError?.message || 'unknown error'}). Проверь интернет или сетевые ограничения.`);
  }

  const canvas = document.getElementById('game');
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x79b6ff);
  scene.fog = new THREE.Fog(0x79b6ff, 28, 180);

  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 700);
  camera.position.set(0, 18, 0);

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: false });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  const controls = new PointerLockControls(camera, document.body);
  scene.add(controls.getObject());

  scene.add(new THREE.HemisphereLight(0xdaf0ff, 0x5b704a, 0.85));
  const sun = new THREE.DirectionalLight(0xffffff, 1.0);
  sun.position.set(44, 80, 35);
  scene.add(sun);

  const remoteGeom = new THREE.BoxGeometry(0.8, 1.8, 0.8);
  const remoteMat = new THREE.MeshLambertMaterial({ color: 0xffcc33 });
  const ensureRemote = (player) => {
    if (!player?.id) return null;
    if (state.multiplayer.remotePlayers.has(player.id)) return state.multiplayer.remotePlayers.get(player.id);
    const mesh = new THREE.Mesh(remoteGeom, remoteMat);
    mesh.position.set(player.pos?.x ?? 0, player.pos?.y ?? 18, player.pos?.z ?? 0);
    scene.add(mesh);
    state.multiplayer.remotePlayers.set(player.id, mesh);
    return mesh;
  };
  state.multiplayer.clearRemotes = (players) => {
    const ids = new Set(players.map((p) => p.id));
    for (const [id, mesh] of state.multiplayer.remotePlayers.entries()) {
      if (!ids.has(id)) {
        scene.remove(mesh);
        state.multiplayer.remotePlayers.delete(id);
      }
    }
    for (const p of players) ensureRemote(p);
  };

  const BLOCKS = [
    { id: 'grass', label: 'Grass', color: 0x66bb4f, texture: 'textures/grass.png' },
    { id: 'dirt', label: 'Dirt', color: 0x7a5330, texture: 'textures/dirt.png' },
    { id: 'stone', label: 'Stone', color: 0x8a8a8a, texture: 'textures/stone.png' },
    { id: 'sand', label: 'Sand', color: 0xded195, texture: 'textures/sand.png' },
    { id: 'water', label: 'Water', color: 0x3d77d8, transparent: true, opacity: 0.72, texture: 'textures/water.png' },
    { id: 'wood', label: 'Oak Log', color: 0x8d6a43, texture: 'textures/wood.png' },
    { id: 'leaves', label: 'Leaves', color: 0x4f8d45, texture: 'textures/leaves.png' },
    { id: 'planks', label: 'Planks', color: 0xb89061, texture: 'textures/planks.png' },
    { id: 'glass', label: 'Glass', color: 0xb9dbff, transparent: true, opacity: 0.35, texture: 'textures/glass.png' },
    { id: 'bricks', label: 'Bricks', color: 0x994a3f, texture: 'textures/bricks.png' },
  ];

  const textureLoader = new THREE.TextureLoader();
  const makeProceduralTexture = (color) => {
    const canvas = document.createElement('canvas');
    canvas.width = 16;
    canvas.height = 16;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = `#${color.toString(16).padStart(6, '0')}`;
    ctx.fillRect(0, 0, 16, 16);
    ctx.fillStyle = 'rgba(255,255,255,0.14)';
    for (let i = 0; i < 16; i += 4) {
      ctx.fillRect(i, 0, 1, 16);
      ctx.fillRect(0, i, 16, 1);
    }
    const texture = new THREE.CanvasTexture(canvas);
    texture.magFilter = THREE.NearestFilter;
    texture.minFilter = THREE.NearestFilter;
    return texture;
  };
  const loadBlockMaterial = async (block) => {
    const fallbackTexture = makeProceduralTexture(block.color);
    const fallback = new THREE.MeshLambertMaterial({
      map: fallbackTexture,
      color: 0xffffff,
      transparent: Boolean(block.transparent),
      opacity: block.opacity ?? 1,
    });
    if (!block.texture) return fallback;
    try {
      const texture = await textureLoader.loadAsync(block.texture);
      texture.magFilter = THREE.NearestFilter;
      texture.minFilter = THREE.NearestFilter;
      return new THREE.MeshLambertMaterial({
        map: texture,
        color: 0xffffff,
        transparent: Boolean(block.transparent),
        opacity: block.opacity ?? 1,
      });
    } catch {
      return fallback;
    }
  };
  const materialEntries = await Promise.all(BLOCKS.map(async (b) => [b.id, await loadBlockMaterial(b)]));
  const materials = Object.fromEntries(materialEntries);
  const blockGeom = new THREE.BoxGeometry(1, 1, 1);
  const blocks = new Map();
  const blockTypes = new Map();

  const key = (x, y, z) => `${x},${y},${z}`;
  const addBlock = (x, y, z, blockId, broadcast = false) => {
    const k = key(x, y, z);
    if (blocks.has(k)) return;
    const mesh = new THREE.Mesh(blockGeom, materials[blockId] ?? materials.grass);
    mesh.position.set(x, y, z);
    scene.add(mesh);
    blocks.set(k, mesh);
    blockTypes.set(k, blockId);
    if (broadcast && state.multiplayer.connected && state.multiplayer.socket?.readyState === WebSocket.OPEN) {
      state.multiplayer.socket.send(JSON.stringify({
        type: 'block_set',
        room: state.multiplayer.room,
        x,
        y,
        z,
        blockId,
      }));
    }
  };
  const removeBlock = (x, y, z, broadcast = false) => {
    const k = key(x, y, z);
    const mesh = blocks.get(k);
    if (!mesh) return;
    scene.remove(mesh);
    blocks.delete(k);
    blockTypes.delete(k);
    if (broadcast && state.multiplayer.connected && state.multiplayer.socket?.readyState === WebSocket.OPEN) {
      state.multiplayer.socket.send(JSON.stringify({
        type: 'block_remove',
        room: state.multiplayer.room,
        x,
        y,
        z,
      }));
    }
  };
  const isSolidAt = (x, y, z) => {
    const id = blockTypes.get(key(Math.round(x), Math.round(y), Math.round(z)));
    if (!id) return false;
    return id !== 'water';
  };
  state.multiplayer.applyRemoteBlock = (msg) => {
    if (msg.type === 'world_state' && Array.isArray(msg.blocks)) {
      for (const b of msg.blocks) addBlock(b.x, b.y, b.z, b.blockId, false);
      return;
    }
    if (msg.type === 'block_set') addBlock(msg.x, msg.y, msg.z, msg.blockId, false);
    if (msg.type === 'block_remove') removeBlock(msg.x, msg.y, msg.z, false);
  };
  if (state.multiplayer.pendingEdits.length) {
    for (const msg of state.multiplayer.pendingEdits) state.multiplayer.applyRemoteBlock(msg);
    state.multiplayer.pendingEdits = [];
  }

  const seedString = String(state.pendingSeed || 'default');
  const seedHash = Array.from(seedString).reduce((acc, ch) => (acc * 31 + ch.charCodeAt(0)) % 1000003, 7);
  const hash = (x, z, s = 1337) => {
    const v = Math.sin(x * 127.1 + z * 311.7 + (s + seedHash) * 0.01) * 43758.5453123;
    return v - Math.floor(v);
  };
  const smoothNoise = (x, z, scale, seed = 1337) => {
    const fx = x / scale;
    const fz = z / scale;
    const x0 = Math.floor(fx);
    const z0 = Math.floor(fz);
    const x1 = x0 + 1;
    const z1 = z0 + 1;
    const tx = fx - x0;
    const tz = fz - z0;
    const a = hash(x0, z0, seed);
    const b = hash(x1, z0, seed);
    const c = hash(x0, z1, seed);
    const d = hash(x1, z1, seed);
    const i1 = a * (1 - tx) + b * tx;
    const i2 = c * (1 - tx) + d * tx;
    return i1 * (1 - tz) + i2 * tz;
  };

  const biomeAt = (x, z) => {
    const b = smoothNoise(x, z, 42, 7);
    if (b < 0.32) return 'desert';
    if (b > 0.7) return 'mountain';
    return 'plains';
  };

  const terrainHeight = (x, z) => {
    const biome = biomeAt(x, z);
    const base = smoothNoise(x, z, 28, 11) * 7 + smoothNoise(x, z, 12, 19) * 4;
    if (biome === 'desert') return Math.floor(base * 0.8) - 1;
    if (biome === 'mountain') return Math.floor(base * 1.8) + 4;
    return Math.floor(base) + 1;
  };

  const isCave = (x, y, z) => {
    if (y > 3 || y < -12) return false;
    const n = smoothNoise(x * 1.6 + y, z * 1.6 - y, 7, 23);
    return n > 0.68;
  };

  const pickOre = (x, y, z) => {
    if (y > -2) return null;
    const n = hash(x + y * 3, z - y * 5, 29);
    if (y < -8 && n > 0.92) return 'glass';
    if (n > 0.86) return 'bricks';
    return null;
  };

  const CHUNK_SIZE = 16;
  const generatedChunks = new Set();
  const chunkKey = (cx, cz) => `${cx},${cz}`;

  const generateChunk = (cx, cz) => {
    const ck = chunkKey(cx, cz);
    if (generatedChunks.has(ck)) return;
    generatedChunks.add(ck);
    const sx = cx * CHUNK_SIZE;
    const sz = cz * CHUNK_SIZE;
    for (let x = sx; x < sx + CHUNK_SIZE; x++) {
      for (let z = sz; z < sz + CHUNK_SIZE; z++) {
        const biome = biomeAt(x, z);
        const h = terrainHeight(x, z);
        const isBeach = h <= 1 || biome === 'desert';
        for (let y = -12; y <= h; y++) {
          if (isCave(x, y, z) && y < h - 1) continue;
          let id = 'dirt';
          if (y === h) id = isBeach ? 'sand' : 'grass';
          else if (y < h - 3) id = 'stone';
          const ore = id === 'stone' ? pickOre(x, y, z) : null;
          addBlock(x, y, z, ore || id);
        }
        if (h <= 0) for (let wy = h + 1; wy <= 1; wy++) addBlock(x, wy, z, 'water');
      }
    }
  };

  const addTree = (cx, cz, tall = false) => {
    const base = terrainHeight(cx, cz) + 1;
    const trunk = tall ? 7 : 5;
    for (let y = 0; y < trunk; y++) addBlock(cx, base + y, cz, 'wood');
    const leafStart = tall ? 4 : 3;
    const leafTop = tall ? 7 : 5;
    for (let x = -2; x <= 2; x++) for (let z = -2; z <= 2; z++) for (let y = leafStart; y <= leafTop; y++) {
      if (Math.abs(x) + Math.abs(z) <= 3) addBlock(cx + x, base + y, cz + z, 'leaves');
    }
  };

  const addHouse = (cx, cz) => {
    const base = terrainHeight(cx, cz) + 1;
    const w = 6;
    const d = 6;
    const h = 4;
    for (let x = -w; x <= w; x++) for (let z = -d; z <= d; z++) addBlock(cx + x, base - 1, cz + z, 'planks');
    for (let y = 0; y < h; y++) {
      for (let x = -w; x <= w; x++) {
        addBlock(cx + x, base + y, cz - d, 'bricks');
        addBlock(cx + x, base + y, cz + d, 'bricks');
      }
      for (let z = -d; z <= d; z++) {
        addBlock(cx - w, base + y, cz + z, 'bricks');
        addBlock(cx + w, base + y, cz + z, 'bricks');
      }
    }
    for (let x = -w; x <= w; x++) for (let z = -d; z <= d; z++) addBlock(cx + x, base + h, cz + z, 'wood');
    removeBlock(cx, base + 1, cz - d);
    removeBlock(cx, base + 2, cz - d);
    addBlock(cx - 2, base + 1, cz - d, 'glass');
    addBlock(cx + 2, base + 1, cz - d, 'glass');
    addBlock(cx - w, base + 1, cz, 'glass');
    addBlock(cx + w, base + 1, cz, 'glass');
  };

  const addTower = (cx, cz) => {
    const base = terrainHeight(cx, cz) + 1;
    const radius = 3;
    const height = 14;
    for (let y = 0; y < height; y++) {
      for (let x = -radius; x <= radius; x++) {
        for (let z = -radius; z <= radius; z++) {
          if (Math.abs(x) === radius || Math.abs(z) === radius) addBlock(cx + x, base + y, cz + z, 'stone');
        }
      }
    }
    for (let x = -radius; x <= radius; x++) for (let z = -radius; z <= radius; z++) addBlock(cx + x, base + height, cz + z, 'planks');
  };

  const addRuin = (cx, cz) => {
    const base = terrainHeight(cx, cz) + 1;
    for (let x = -3; x <= 3; x++) for (let z = -3; z <= 3; z++) addBlock(cx + x, base - 1, cz + z, 'stone');
    for (let y = 0; y < 4; y++) {
      addBlock(cx - 3, base + y, cz - 3, 'bricks');
      addBlock(cx + 3, base + y, cz - 3, 'bricks');
      addBlock(cx - 3, base + y, cz + 3, 'bricks');
      addBlock(cx + 3, base + y, cz + 3, 'bricks');
    }
  };

  const ensureChunksAround = (x, z, radius = 2) => {
    const ccx = Math.floor(x / CHUNK_SIZE);
    const ccz = Math.floor(z / CHUNK_SIZE);
    for (let dx = -radius; dx <= radius; dx++) {
      for (let dz = -radius; dz <= radius; dz++) {
        generateChunk(ccx + dx, ccz + dz);
      }
    }
  };

  ensureChunksAround(0, 0, 3);
  for (let i = 0; i < 24; i++) {
    const tx = Math.floor(Math.random() * 74 - 37);
    const tz = Math.floor(Math.random() * 74 - 37);
    if (biomeAt(tx, tz) !== 'desert') addTree(tx, tz, Math.random() > 0.74);
  }
  addHouse(18, 12);
  addTower(-20, -18);
  addRuin(0, -8);

  const raycaster = new THREE.Raycaster();
  const center = new THREE.Vector2(0, 0);
  const getTarget = () => {
    raycaster.setFromCamera(center, camera);
    const hit = raycaster.intersectObjects(Array.from(blocks.values()), false)[0];
    if (!hit || hit.distance > 7) return null;
    return { removeAt: hit.object.position.clone().round(), placeAt: hit.object.position.clone().add(hit.face.normal).round() };
  };

  let activeBlockIndex = 0;
  const setActiveBlock = (index) => {
    activeBlockIndex = (index + BLOCKS.length) % BLOCKS.length;
    ui.activeBlock.textContent = BLOCKS[activeBlockIndex].label;
  };
  setActiveBlock(0);

  const pressed = new Set();
  document.addEventListener('keydown', (e) => {
    pressed.add(e.code);
    if (e.code === 'Escape' && state.running) state.stopSession?.();
    if (e.code.startsWith('Digit')) {
      const n = Number(e.code.replace('Digit', ''));
      setActiveBlock(n === 0 ? 9 : n - 1);
    }
  });
  document.addEventListener('keyup', (e) => pressed.delete(e.code));

  document.addEventListener('mousedown', (e) => {
    if (!controls.isLocked) return;
    const target = getTarget();
    if (!target) return;
    if (e.button === 0) removeBlock(target.removeAt.x, target.removeAt.y, target.removeAt.z, true);
    if (e.button === 2) addBlock(target.placeAt.x, target.placeAt.y, target.placeAt.z, BLOCKS[activeBlockIndex].id, true);
  });
  document.addEventListener('contextmenu', (e) => e.preventDefault());

  const velocity = new THREE.Vector3();
  const direction = new THREE.Vector3();
  const clock = new THREE.Clock();
  let syncElapsed = 0;

  const animate = () => {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    syncElapsed += dt;
    if (controls.isLocked) {
      velocity.set(0, 0, 0);
      const speed = 11 * state.sensitivity;
      direction.z = Number(pressed.has('KeyW')) - Number(pressed.has('KeyS'));
      direction.x = Number(pressed.has('KeyD')) - Number(pressed.has('KeyA'));
      direction.y = Number(pressed.has('Space')) - Number(pressed.has('ShiftLeft') || pressed.has('ShiftRight'));
      if (direction.lengthSq() > 0) direction.normalize();
      const prev = camera.position.clone();
      controls.moveRight(direction.x * speed * dt);
      controls.moveForward(direction.z * speed * dt);
      camera.position.y += direction.y * speed * dt;

      const headBlocked = isSolidAt(camera.position.x, camera.position.y, camera.position.z);
      const bodyBlocked = isSolidAt(camera.position.x, camera.position.y - 1, camera.position.z);
      if (headBlocked || bodyBlocked) {
        camera.position.copy(prev);
      }
      ensureChunksAround(camera.position.x, camera.position.z, 2);
    }
    if (state.multiplayer.connected && state.multiplayer.socket?.readyState === WebSocket.OPEN && syncElapsed > 0.08) {
      syncElapsed = 0;
      state.multiplayer.socket.send(JSON.stringify({
        type: 'move',
        room: state.multiplayer.room,
        pos: { x: camera.position.x, y: camera.position.y, z: camera.position.z },
      }));
    }
    renderer.render(scene, camera);
  };
  animate();

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  state.setSpawn = (spawn) => {
    camera.position.set(spawn?.x ?? 0, spawn?.y ?? 18, spawn?.z ?? 0);
  };

  state.startSession = () => {
    state.running = true;
    ui.menuOverlay.classList.add('hidden');
    ui.hud.classList.remove('hidden');
    ui.crosshair.classList.remove('hidden');
    controls.lock();
  };

  state.stopSession = () => {
    state.running = false;
    controls.unlock();
    ui.menuOverlay.classList.remove('hidden');
    ui.hud.classList.add('hidden');
    ui.crosshair.classList.add('hidden');
    showScreen('main');
  };
}

showScreen('main');
renderWorldList();
