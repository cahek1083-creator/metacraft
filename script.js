const playBtn = document.getElementById('playBtn');
const player = document.getElementById('player');

let launched = false;

playBtn.addEventListener('click', () => {
  launched = !launched;
  playBtn.textContent = launched ? 'LAUNCHING...' : 'PLAY';
  player.textContent = launched ? 'Steve • entering METAcraft VR' : 'Steve';
});
