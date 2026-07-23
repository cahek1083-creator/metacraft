# Metacraft VR Physics Prototype

Starter Unity kit for a VR physics sandbox with gorilla-style physical locomotion, props, multiple locations, and quick prototype shaders.

## Included systems

- `VRGorillaLocomotion` — Rigidbody VR locomotion driven by headset and hand/controller Transforms. Push from walls/floors with hands to move, climb, and launch.
- `ItemSpawner`, `SpawnableItem`, and `VRHandItemSpawner` — weighted prop spawning from world points or from VR hand positions. Hook `SpawnLeftHand` / `SpawnRightHand` to XR input events.
- `LocationManager` — switches between location roots with number keys and moves the VR rig to matching spawn points.
- `ProceduralWall` and `LocationFloor` shaders — simple procedural wall/floor materials for fast arena prototyping.

## Quick VR setup

1. Create a Unity 3D or URP VR project with an XR Origin / camera rig.
2. Add a `Rigidbody`, `CapsuleCollider`, and `VRGorillaLocomotion` to the rig root.
3. Assign the headset camera to `head`, and assign left/right controller Transforms to `leftHand` and `rightHand`.
4. Add small sphere visuals or collider proxy objects for the hands and assign them to `leftHandCollider` / `rightHandCollider`.
5. Put climbable/pushable walls, floor, and props on layers included by `locomotionMask`.
6. Create prop prefabs with `Rigidbody`, colliders, and `SpawnableItem`; assign them to an `ItemSpawner`.
7. Add `VRHandItemSpawner` beside `ItemSpawner` and wire XR input events to `SpawnLeftHand` or `SpawnRightHand`.
8. Put each map/location under its own root GameObject and assign those roots to `LocationManager`.

## Tuning tips

- Increase `launchMultiplier` and `maxLaunchSpeed` for more arcade-like Gorilla Tag jumps.
- Increase `handRadius` if hands clip through thin walls.
- Lower `wallSlide` if hands feel too slippery on surfaces.
- Keep player physics materials low-friction so hand pushes feel responsive.
