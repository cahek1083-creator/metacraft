#include <windows.h>

#include "mod_entry.hpp"

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID) {
    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
        DisableThreadLibraryCalls(hModule);
        fh4vr::StartMod();
        break;
    case DLL_PROCESS_DETACH:
        fh4vr::StopMod();
        break;
    default:
        break;
    }

    return TRUE;
}
