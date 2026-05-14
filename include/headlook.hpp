#pragma once

namespace fh4vr {

struct HeadPose {
    float yawDeg;
    float pitchDeg;
};

struct InteriorLook {
    float lookLeftRight;
    float lookUpDown;
};

InteriorLook ComputeInteriorLook(const HeadPose& pose);
void ApplyInteriorLook(const InteriorLook& look);

} // namespace fh4vr
