const actionBtn = document.getElementById('actionBtn');
const message = document.getElementById('message');

let clickCount = 0;

actionBtn.addEventListener('click', () => {
  clickCount += 1;
  message.textContent = `Кнопка нажата ${clickCount} раз(а).`;
});
