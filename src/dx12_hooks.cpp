#include "dx12_hooks.hpp"

#include <windows.h>

#include "headlook.hpp"
#include "vr_runtime.hpp"

namespace fh4vr {

bool InstallDx12Hooks() {
    OutputDebugStringA("[fh4_vr_mod] InstallDx12Hooks (stub)\n");
    // TODO: initialize MinHook and patch IDXGISwapChain::Present / Present1 vtable entries.
    OutputDebugStringA("[fh4_vr_mod] Hook target: IDXGISwapChain::Present + Present1\n");
    return true;
}

void RemoveDx12Hooks() {
    OutputDebugStringA("[fh4_vr_mod] RemoveDx12Hooks (stub)\n");
}

void OnPresent(float hmdYawDeg, float hmdPitchDeg) {
    // TODO: run OpenXR frame lifecycle:
    // xrWaitFrame -> xrBeginFrame -> render both eyes -> xrEndFrame.

    const HeadPose pose{hmdYawDeg, hmdPitchDeg};
    const InteriorLook look = ComputeInteriorLook(pose);
    ApplyInteriorLook(look);
}

void OnPresent1(float hmdYawDeg, float hmdPitchDeg) {
    OnPresent(hmdYawDeg, hmdPitchDeg);
}

void OnResize(unsigned width, unsigned height) {
    NotifyResize(width, height);
}

} // namespace fh4vr
