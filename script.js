const playBtn = document.getElementById('playBtn');
const status = document.getElementById('status');

let launched = false;

playBtn.addEventListener('click', () => {
  launched = !launched;
  playBtn.textContent = launched ? 'LAUNCHING...' : 'PLAY';
  status.textContent = launched ? 'Статус: запуск METAcraft VR...' : 'Статус: готово';
});
