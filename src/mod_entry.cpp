#include "mod_entry.hpp"

#include <atomic>
#include <thread>

#include <windows.h>

#include "dx12_hooks.hpp"
#include "openxr_bridge.hpp"
#include "vr_runtime.hpp"

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

    if (!InitializeVrRuntime()) {
        RemoveDx12Hooks();
        ShutdownOpenXR();
        return;
    }

    bool vrEnabled = false;
    bool overlayEnabled = true;
    bool deleteWasDown = false;
    float demoYaw = 0.0f;
    float demoPitch = 0.0f;

    OutputDebugStringA("[fh4_vr_mod] Press Delete to toggle VR ON/OFF\n");
    OutputDebugStringA("[fh4_vr_mod] Press Insert to toggle debug overlay\n");

    while (g_running.load()) {
        const bool deleteDown = (GetAsyncKeyState(VK_DELETE) & 0x8000) != 0;
        if (deleteDown && !deleteWasDown) {
            vrEnabled = !vrEnabled;
            OutputDebugStringA(vrEnabled
                                   ? "[fh4_vr_mod] VR enabled\n"
                                   : "[fh4_vr_mod] VR disabled\n");
        }
        deleteWasDown = deleteDown;

        const bool insertDown = (GetAsyncKeyState(VK_INSERT) & 0x8000) != 0;
        static bool insertWasDown = false;
        if (insertDown && !insertWasDown) {
            overlayEnabled = !overlayEnabled;
        }
        insertWasDown = insertDown;

        const RuntimeStatus status = GetRuntimeStatus();
        if (status == RuntimeStatus::RestartRequired) {
            ShutdownVrRuntime();
            InitializeVrRuntime();
        }

        if (vrEnabled) {
            VrFrameInput frame{};
            if (PollHmdPose(&frame)) {
                demoYaw = frame.hmdYawDeg;
                demoPitch = frame.hmdPitchDeg;
                const CameraTransform camera = ConvertHmdToCamera(frame);
                ApplyCameraTransform(camera);
                OnPresent(demoYaw, demoPitch);
                OnPresent1(demoYaw, demoPitch);
                RenderStereoFrame();
            }

            if (overlayEnabled) {
                RenderDebugOverlay();
            }
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(8));
    }

    ShutdownVrRuntime();
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
