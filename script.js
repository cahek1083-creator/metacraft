const actionBtn = document.getElementById('actionBtn');
const message = document.getElementById('message');

const tips = [
  'Ты собрал дерево. Верстак разблокирован!',
  'Каменная кирка готова — время копать глубже.',
  'Наступает ночь: зажги факелы и укрепи базу.',
  'Найдено железо! Можно крафтить броню.',
];

let progress = 0;

actionBtn.addEventListener('click', () => {
  const tip = tips[progress % tips.length];
  progress += 1;
  message.textContent = `День ${progress}: ${tip}`;
});
