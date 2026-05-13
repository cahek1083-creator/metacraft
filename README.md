# Forza Horizon 4 VR Mod (Prototype)

> ⚠️ This is a **research prototype scaffold**. It does **not** guarantee a working or ban-safe online experience.

Этот репозиторий содержит каркас DLL-мода для экспериментов с VR в DirectX 12 игре (например, Forza Horizon 4):

- инжект в процесс игры;
- перехват DXGI swap chain (`Present`);
- инициализация OpenXR runtime;
- места расширения для стерео-рендера (left/right eye views), head tracking и UI layers.

## Важно

- Использование модов может нарушать EULA игры.
- Не используйте в онлайне/мультиплеере.
- Прототип предназначен только для обучения и оффлайн-исследований.

## Быстрый старт (Windows)

1. Установите:
   - Visual Studio 2022 (MSVC, C++ build tools)
   - CMake 3.21+
   - OpenXR Loader SDK
   - MinHook (можно через vcpkg)
2. Сконфигурируйте:

```powershell
cmake -S . -B build -G "Visual Studio 17 2022" -A x64
cmake --build build --config Release
```

3. Получите `fh4_vr_mod.dll` и загружайте его в процесс (только в оффлайн-тестах).

## Что реализовано сейчас

- базовый `DllMain`;
- запуск рабочего потока;
- заглушка инициализации OpenXR;
- заглушка установки DXGI/D3D12 хуков;
- пример функции `OnPresent` для будущей интеграции stereo pipeline.

## Что делать дальше

- найти и перехватить правильный `IDXGISwapChain::Present`/`Present1`;
- добавить получение и конвертацию позы HMD в camera transform игры;
- реализовать двойной рендер (или view instancing);
- интегрировать runtime menu/debug overlay;
- добавить safety checks (device lost, resize, runtime restarts).


## Новый функционал

- Добавлен прототип осмотра салона: при поворотах/наклонах головы вычисляются нормализованные значения `lookLeftRight` и `lookUpDown` для камеры кокпита.
- Сейчас значения выводятся в `OutputDebugStringA`; следующий шаг — привязать к реальным контроллерам камеры игры.

- Переключение VR добавлено на кнопку `Delete` (toggle ON/OFF).


## Прогресс по задачам

- Перехват `Present/Present1`: добавлены точки интеграции и единая обработка `OnPresent`/`OnPresent1`.
- Поза HMD -> camera transform: добавлен pipeline `PollHmdPose -> ConvertHmdToCamera -> ApplyCameraTransform`.
- Двойной рендер: добавлен stub `RenderStereoFrame` для left/right eye (или view instancing).
- Runtime overlay: добавлен debug overlay c переключением на `Insert`.
- Safety checks: добавлен runtime status (`DeviceLost`, `RestartRequired`) и обработка resize/restart.


## Universal VR Launcher (Profiles)

Добавлено отдельное приложение `tools/vr_launcher_app.py` с вкладками профилей игр (Forza Horizon 3/4/5 и Counter-Strike 2):

- хранение launch-команды и VR-параметров по игре;
- кнопка запуска выбранной игры по пользовательской команде;
- сохранение профилей в `~/.vr_launcher_profiles.json`.

> Приложение не включает инжект/обход защиты; это безопасный менеджер профилей и запусков.

Запуск:

```bash
python tools/vr_launcher_app.py
```

- В лаунчере добавлен выбор `.exe` через проводник и ограничение имени файла по игре (например, для FH4 только `forzahorizon4.exe`).

- Лаунчер запускает игру с рабочей папкой каталога `.exe` (fix для ошибок типа `Could not find SWconfig.ini`).
