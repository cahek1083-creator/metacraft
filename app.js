const STORAGE_KEY = 'webcraft_worlds_v1';

const ui = {
  menuOverlay: document.getElementById('menu-overlay'),
  hud: document.getElementById('hud'),
  crosshair: document.getElementById('crosshair'),
  activeWorld: document.getElementById('active-world'),
  activeBlock: document.getElementById('active-block'),

  screenMain: document.getElementById('screen-main'),
  screenSingle: document.getElementById('screen-singleplayer'),
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
};

const state = {
  sensitivity: 1,
  running: false,
  engineReady: false,
  worlds: loadWorlds(),
  selectedWorldId: null,
  startSession: null,
  stopSession: null,
  setSpawn: null,
};

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

  ui.btnPlayWorld.disabled = !state.selectedWorldId;
  ui.btnDeleteWorld.disabled = !state.selectedWorldId;
}

ui.sensitivity.addEventListener('input', () => {
  state.sensitivity = Number(ui.sensitivity.value);
});

ui.btnSingle.addEventListener('click', () => {
  showScreen('single');
  if (!state.selectedWorldId && state.worlds[0]) state.selectedWorldId = state.worlds[0].id;
  renderWorldList();
});

ui.btnSingleBack.addEventListener('click', () => showScreen('main'));
ui.btnCreateWorld.addEventListener('click', () => showScreen('create'));
ui.btnCreateBack.addEventListener('click', () => showScreen('single'));

ui.btnConfirmCreate.addEventListener('click', () => {
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
ui.btnMulti.addEventListener('click', () => alert('Multiplayer пока не реализован в этом прототипе.'));
ui.btnRealms.addEventListener('click', () => alert('Minecraft Realms пока не реализован в этом прототипе.'));
ui.btnQuit.addEventListener('click', () => alert('В браузере закрой вкладку вручную.'));

ui.btnPlayWorld.addEventListener('click', async () => {
  const world = state.worlds.find((w) => w.id === state.selectedWorldId);
  if (!world) return;

  ui.btnPlayWorld.disabled = true;
  ui.btnPlayWorld.textContent = state.engineReady ? 'Loading world...' : 'Preparing engine...';

  try {
    if (!state.engineReady) {
      await initEngine();
      state.engineReady = true;
    }
    state.setSpawn?.(world.spawn);
    ui.activeWorld.textContent = world.name;
    state.startSession?.();
  } catch (error) {
    console.error(error);
    alert('Не удалось запустить 3D-сцену. Открой через http:// и проверь доступ к CDN.');
  } finally {
    ui.btnPlayWorld.disabled = false;
    ui.btnPlayWorld.textContent = 'Play Selected World';
  }
});

async function initEngine() {
  const [THREE, { PointerLockControls }] = await Promise.all([
    import('https://unpkg.com/three@0.164.1/build/three.module.js'),
    import('https://unpkg.com/three@0.164.1/examples/jsm/controls/PointerLockControls.js'),
  ]);

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

  const BLOCKS = [
    { id: 'grass', label: 'Grass', color: 0x66bb4f },
    { id: 'dirt', label: 'Dirt', color: 0x7a5330 },
    { id: 'stone', label: 'Stone', color: 0x8a8a8a },
    { id: 'sand', label: 'Sand', color: 0xded195 },
    { id: 'water', label: 'Water', color: 0x3d77d8, transparent: true, opacity: 0.72 },
    { id: 'wood', label: 'Oak Log', color: 0x8d6a43 },
    { id: 'leaves', label: 'Leaves', color: 0x4f8d45 },
    { id: 'planks', label: 'Planks', color: 0xb89061 },
    { id: 'glass', label: 'Glass', color: 0xb9dbff, transparent: true, opacity: 0.35 },
    { id: 'bricks', label: 'Bricks', color: 0x994a3f },
  ];

  const materials = Object.fromEntries(BLOCKS.map((b) => [b.id, new THREE.MeshLambertMaterial({ color: b.color, transparent: Boolean(b.transparent), opacity: b.opacity ?? 1 })]));
  const blockGeom = new THREE.BoxGeometry(1, 1, 1);
  const blocks = new Map();

  const key = (x, y, z) => `${x},${y},${z}`;
  const addBlock = (x, y, z, blockId) => {
    const k = key(x, y, z);
    if (blocks.has(k)) return;
    const mesh = new THREE.Mesh(blockGeom, materials[blockId] ?? materials.grass);
    mesh.position.set(x, y, z);
    scene.add(mesh);
    blocks.set(k, mesh);
  };
  const removeBlock = (x, y, z) => {
    const mesh = blocks.get(key(x, y, z));
    if (!mesh) return;
    scene.remove(mesh);
    blocks.delete(key(x, y, z));
  };

  const terrainHeight = (x, z) => Math.floor(Math.sin(x * 0.12) * 3 + Math.cos(z * 0.09) * 4 + Math.sin((x + z) * 0.04) * 3);

  const generateTerrain = () => {
    const radius = 55;
    for (let x = -radius; x <= radius; x++) {
      for (let z = -radius; z <= radius; z++) {
        const h = terrainHeight(x, z);
        const isBeach = h <= 1;
        for (let y = -8; y <= h; y++) {
          let id = 'dirt';
          if (y === h) id = isBeach ? 'sand' : 'grass';
          else if (y < h - 3) id = 'stone';
          addBlock(x, y, z, id);
        }
        if (h <= 0) for (let wy = h + 1; wy <= 1; wy++) addBlock(x, wy, z, 'water');
      }
    }
  };

  const addTree = (cx, cz) => {
    const base = terrainHeight(cx, cz) + 1;
    for (let y = 0; y < 5; y++) addBlock(cx, base + y, cz, 'wood');
    for (let x = -2; x <= 2; x++) for (let z = -2; z <= 2; z++) for (let y = 3; y <= 5; y++) {
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

  generateTerrain();
  for (let i = 0; i < 24; i++) addTree(Math.floor(Math.random() * 90 - 45), Math.floor(Math.random() * 90 - 45));
  addHouse(18, 12);
  addTower(-20, -18);

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
    if (e.button === 0) removeBlock(target.removeAt.x, target.removeAt.y, target.removeAt.z);
    if (e.button === 2) addBlock(target.placeAt.x, target.placeAt.y, target.placeAt.z, BLOCKS[activeBlockIndex].id);
  });
  document.addEventListener('contextmenu', (e) => e.preventDefault());

  const velocity = new THREE.Vector3();
  const direction = new THREE.Vector3();
  const clock = new THREE.Clock();

  const animate = () => {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    if (controls.isLocked) {
      velocity.set(0, 0, 0);
      const speed = 11 * state.sensitivity;
      direction.z = Number(pressed.has('KeyW')) - Number(pressed.has('KeyS'));
      direction.x = Number(pressed.has('KeyD')) - Number(pressed.has('KeyA'));
      direction.y = Number(pressed.has('Space')) - Number(pressed.has('ShiftLeft') || pressed.has('ShiftRight'));
      if (direction.lengthSq() > 0) direction.normalize();
      controls.moveRight(direction.x * speed * dt);
      controls.moveForward(direction.z * speed * dt);
      camera.position.y += direction.y * speed * dt;
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
