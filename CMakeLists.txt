cmake_minimum_required(VERSION 3.21)
project(fh4_vr_mod LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(fh4_vr_mod SHARED
    src/dllmain.cpp
    src/mod_entry.cpp
    src/openxr_bridge.cpp
    src/dx12_hooks.cpp
    src/headlook.cpp
    src/vr_runtime.cpp
)

target_include_directories(fh4_vr_mod PRIVATE include)

target_compile_definitions(fh4_vr_mod PRIVATE WIN32_LEAN_AND_MEAN NOMINMAX)

if(MSVC)
    target_compile_options(fh4_vr_mod PRIVATE /W4 /permissive-)
endif()
