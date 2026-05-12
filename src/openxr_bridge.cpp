#include "openxr_bridge.hpp"

#include <windows.h>

namespace fh4vr {

bool InitializeOpenXR() {
    OutputDebugStringA("[fh4_vr_mod] InitializeOpenXR (stub)\n");
    // TODO: create XrInstance, XrSession (D3D12 binding), swapchains for both eyes.
    return true;
}

void ShutdownOpenXR() {
    OutputDebugStringA("[fh4_vr_mod] ShutdownOpenXR (stub)\n");
}

} // namespace fh4vr
