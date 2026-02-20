const playBtn = document.getElementById('playBtn');
const downloadBtn = document.getElementById('downloadBtn');
const player = document.getElementById('player');

let launched = false;
let downloaded = false;

playBtn.addEventListener('click', () => {
  launched = !launched;
  playBtn.textContent = launched ? 'LAUNCHING...' : 'PLAY';
  player.textContent = launched ? 'Steve • entering METAcraft VR' : 'Steve';
});

downloadBtn.addEventListener('click', () => {
  downloaded = !downloaded;
  downloadBtn.textContent = downloaded ? 'СКАЧАНО' : 'СКАЧАТЬ';
  player.textContent = downloaded ? 'Steve • METAcraft files ready' : 'Steve';
});
