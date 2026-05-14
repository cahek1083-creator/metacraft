#include "headlook.hpp"

#include <algorithm>
#include <windows.h>

namespace fh4vr {
namespace {
constexpr float kMaxYawDeg = 70.0f;
constexpr float kMaxPitchDeg = 50.0f;

float Clamp(float v, float minV, float maxV) {
    return std::max(minV, std::min(v, maxV));
}
} // namespace

InteriorLook ComputeInteriorLook(const HeadPose& pose) {
    const float yaw = Clamp(pose.yawDeg, -kMaxYawDeg, kMaxYawDeg);
    const float pitch = Clamp(pose.pitchDeg, -kMaxPitchDeg, kMaxPitchDeg);

    InteriorLook look{};
    look.lookLeftRight = yaw / kMaxYawDeg;   // -1 = full left, +1 = full right
    look.lookUpDown = pitch / kMaxPitchDeg;  // -1 = full down, +1 = full up
    return look;
}

void ApplyInteriorLook(const InteriorLook& look) {
    // TODO: write values to game's cockpit camera memory/controller.
    // For now this logs normalized values for integration testing.
    char buf[160]{};
    wsprintfA(buf, "[fh4_vr_mod] Cockpit look LR=%.2f UD=%.2f\n", look.lookLeftRight, look.lookUpDown);
    OutputDebugStringA(buf);
}

} // namespace fh4vr
