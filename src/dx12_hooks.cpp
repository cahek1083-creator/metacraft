#include "dx12_hooks.hpp"

#include <windows.h>

#include "headlook.hpp"

namespace fh4vr {

bool InstallDx12Hooks() {
    OutputDebugStringA("[fh4_vr_mod] InstallDx12Hooks (stub)\n");
    // TODO: initialize MinHook and patch IDXGISwapChain::Present vtable entry.
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

} // namespace fh4vr
