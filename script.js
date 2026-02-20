const launchBtn = document.getElementById('launchBtn');
const status = document.getElementById('status');

const states = [
  'Статус: подключение VR-шлема...',
  'Статус: синхронизация мира METAcraft...',
  'Статус: телепорт в блоковый мир выполнен!',
];

let step = 0;

launchBtn.addEventListener('click', () => {
  status.textContent = states[step % states.length];
  step += 1;
});
