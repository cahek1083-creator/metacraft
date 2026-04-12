# MysticEntityPlugin

Плагин для Paper/Spigot-серверов Minecraft (1.20.4), добавляющий атмосферные мистические явления и NPC в стиле городских легенд (Herobrine, Lucas, Error303, Null).

## Возможности
- Команда `/mystic start|stop|status`
- Команда `/mystic pulse [entity]` для ручного запуска явления
- Команда `/mystic npc spawn <entity> [count]` и `/mystic npc clear`
- Команда `/mystic lore <entity>` — краткая справка и ссылка на источник из интернета
- Случайные «импульсы» по таймеру: частицы, звуки, сообщения и временные NPC
- Настраиваемые сущности и сообщения через `config.yml`

## Сборка (рекомендуется через Maven Wrapper)
Linux/macOS:
```bash
./mvnw clean package
```

Windows PowerShell:
```powershell
.\mvnw.cmd clean package
```

Готовый jar будет в папке `target/`.

## Если `mvn clean package` падает с `NoClassDefFoundError: org/slf4j/Logger`
Это проблема локальной установки Maven (битая/неполная установка), а не кода плагина.
Используйте wrapper-команды выше (`mvnw` / `mvnw.cmd`) — они скачивают рабочий Maven автоматически.
