#pragma once

namespace fh4vr {

bool InstallDx12Hooks();
void RemoveDx12Hooks();
void OnPresent(float hmdYawDeg, float hmdPitchDeg);
void OnPresent1(float hmdYawDeg, float hmdPitchDeg);
void OnResize(unsigned width, unsigned height);

} // namespace fh4vr
