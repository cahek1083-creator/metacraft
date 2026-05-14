#pragma once

#include <cstdint>

namespace fh4vr {

enum class RuntimeStatus {
    Stopped,
    Running,
    DeviceLost,
    RestartRequired,
};

struct VrFrameInput {
    float hmdYawDeg;
    float hmdPitchDeg;
    float hmdRollDeg;
    float hmdPosX;
    float hmdPosY;
    float hmdPosZ;
};

struct CameraTransform {
    float yawDeg;
    float pitchDeg;
    float rollDeg;
    float posX;
    float posY;
    float posZ;
};

bool InitializeVrRuntime();
void ShutdownVrRuntime();
RuntimeStatus GetRuntimeStatus();

bool PollHmdPose(VrFrameInput* outInput);
CameraTransform ConvertHmdToCamera(const VrFrameInput& input);
void ApplyCameraTransform(const CameraTransform& transform);

void RenderStereoFrame();
void RenderDebugOverlay();
void NotifyResize(uint32_t width, uint32_t height);

} // namespace fh4vr
