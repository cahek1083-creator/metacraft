#pragma once

namespace fh4vr {

bool InstallDx12Hooks();
void RemoveDx12Hooks();
void OnPresent(float hmdYawDeg, float hmdPitchDeg);

} // namespace fh4vr
