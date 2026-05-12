#include "vr_runtime.hpp"

#include <windows.h>

namespace fh4vr {
namespace {
RuntimeStatus g_status = RuntimeStatus::Stopped;
uint32_t g_width = 0;
uint32_t g_height = 0;
}

bool InitializeVrRuntime() {
    g_status = RuntimeStatus::Running;
    OutputDebugStringA("[fh4_vr_mod] VR runtime initialized\n");
    return true;
}

void ShutdownVrRuntime() {
    g_status = RuntimeStatus::Stopped;
    OutputDebugStringA("[fh4_vr_mod] VR runtime shutdown\n");
}

RuntimeStatus GetRuntimeStatus() {
    return g_status;
}

bool PollHmdPose(VrFrameInput* outInput) {
    if (!outInput || g_status != RuntimeStatus::Running) {
        return false;
    }

    static float yaw = -45.0f;
    static float pitch = -10.0f;
    yaw += 0.8f;
    if (yaw > 45.0f) yaw = -45.0f;
    pitch += 0.2f;
    if (pitch > 20.0f) pitch = -20.0f;

    *outInput = VrFrameInput{yaw, pitch, 0.0f, 0.0f, 0.05f, 0.0f};
    return true;
}

CameraTransform ConvertHmdToCamera(const VrFrameInput& input) {
    // Conversion placeholder (OpenXR space -> game cockpit space).
    return CameraTransform{input.hmdYawDeg, input.hmdPitchDeg, input.hmdRollDeg,
                           input.hmdPosX, input.hmdPosY, input.hmdPosZ};
}

void ApplyCameraTransform(const CameraTransform& transform) {
    char msg[192]{};
    wsprintfA(msg,
              "[fh4_vr_mod] Camera yaw=%.2f pitch=%.2f pos=(%.2f %.2f %.2f)\n",
              transform.yawDeg, transform.pitchDeg, transform.posX, transform.posY, transform.posZ);
    OutputDebugStringA(msg);
}

void RenderStereoFrame() {
    // Placeholder for dual render or view-instancing path.
    OutputDebugStringA("[fh4_vr_mod] RenderStereoFrame (left/right eye)\n");
}

void RenderDebugOverlay() {
    OutputDebugStringA("[fh4_vr_mod] Overlay: DEL=VR toggle, INSERT=Overlay toggle\n");
}

void NotifyResize(uint32_t width, uint32_t height) {
    g_width = width;
    g_height = height;
    if (g_width == 0 || g_height == 0) {
        g_status = RuntimeStatus::DeviceLost;
        OutputDebugStringA("[fh4_vr_mod] Resize -> device lost state\n");
        return;
    }

    if (g_status == RuntimeStatus::DeviceLost) {
        g_status = RuntimeStatus::RestartRequired;
        OutputDebugStringA("[fh4_vr_mod] Resize recovered -> restart required\n");
    }
}

} // namespace fh4vr
