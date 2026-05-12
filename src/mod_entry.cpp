#include "mod_entry.hpp"

#include <atomic>
#include <thread>

#include <windows.h>

#include "dx12_hooks.hpp"
#include "openxr_bridge.hpp"

namespace fh4vr {
namespace {
std::atomic<bool> g_running{false};
std::thread g_worker;

void ModThreadMain() {
    if (!InitializeOpenXR()) {
        return;
    }

    if (!InstallDx12Hooks()) {
        ShutdownOpenXR();
        return;
    }

    bool vrEnabled = false;
    bool deleteWasDown = false;
    float demoYaw = 0.0f;
    float demoPitch = 0.0f;

    OutputDebugStringA("[fh4_vr_mod] Press Delete to toggle VR ON/OFF\n");

    while (g_running.load()) {
        const bool deleteDown = (GetAsyncKeyState(VK_DELETE) & 0x8000) != 0;
        if (deleteDown && !deleteWasDown) {
            vrEnabled = !vrEnabled;
            OutputDebugStringA(vrEnabled
                                   ? "[fh4_vr_mod] VR enabled\n"
                                   : "[fh4_vr_mod] VR disabled\n");
        }
        deleteWasDown = deleteDown;

        if (vrEnabled) {
            // TODO: replace demo values with real OpenXR head pose extraction.
            demoYaw += 1.0f;
            if (demoYaw > 70.0f) {
                demoYaw = -70.0f;
            }

            demoPitch += 0.5f;
            if (demoPitch > 35.0f) {
                demoPitch = -35.0f;
            }

            OnPresent(demoYaw, demoPitch);
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(8));
    }

    RemoveDx12Hooks();
    ShutdownOpenXR();
}
} // namespace

void StartMod() {
    bool expected = false;
    if (!g_running.compare_exchange_strong(expected, true)) {
        return;
    }

    g_worker = std::thread(ModThreadMain);
}

void StopMod() {
    bool expected = true;
    if (!g_running.compare_exchange_strong(expected, false)) {
        return;
    }

    if (g_worker.joinable()) {
        g_worker.join();
    }
}

} // namespace fh4vr
