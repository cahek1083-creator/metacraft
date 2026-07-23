# Metacraft VR Physics Prototype

Starter Unity kit for a VR physics sandbox with gorilla-style physical locomotion, props, multiple locations, and quick prototype shaders.

## Included systems

- `VRGorillaLocomotion` — Rigidbody VR locomotion driven by headset and hand/controller Transforms. Push from walls/floors with hands to move, climb, and launch.
- `ItemSpawner`, `SpawnableItem`, and `VRHandItemSpawner` — weighted prop spawning from world points or from VR hand positions. Hook `SpawnLeftHand` / `SpawnRightHand` to XR input events.
- `LocationManager` — switches between location roots with number keys and moves the VR rig to matching spawn points.
- `SpawnMenuController` and `SpawnItemButton` — opens an item menu with `Y`; each button can spawn its assigned prefab in front of the player.
- `Bonelab Style Wall` and `LocationFloor` shaders — wall shader accepts an image/city texture, blurs it, and draws broken horizontal stripes over the wall surface.

## Quick VR setup

1. Create a Unity 3D or URP VR project with an XR Origin / camera rig.
2. Add a `Rigidbody`, `CapsuleCollider`, and `VRGorillaLocomotion` to the rig root.
3. Assign the headset camera to `head`, and assign left/right controller Transforms to `leftHand` and `rightHand`.
4. Add small sphere visuals or collider proxy objects for the hands and assign them to `leftHandCollider` / `rightHandCollider`.
5. Put climbable/pushable walls, floor, and props on layers included by `locomotionMask`.
6. Create prop prefabs with `Rigidbody`, colliders, and `SpawnableItem`; assign them to an `ItemSpawner`.
7. Add `VRHandItemSpawner` beside `ItemSpawner` and wire XR input events to `SpawnLeftHand` or `SpawnRightHand`.
8. Create a world-space Canvas for the item menu, assign it to `SpawnMenuController.menuRoot`, and press `Y` to open/close it in editor testing.
9. Add `SpawnItemButton` to each UI Button, assign an item prefab and the headset transform, then connect the Button OnClick event to `SpawnItemInFrontOfPlayer`.
10. Put each map/location under its own root GameObject and assign those roots to `LocationManager`.

## Tuning tips

- Increase `launchMultiplier` and `maxLaunchSpeed` for more arcade-like Gorilla Tag jumps.
- Increase `handRadius` if hands clip through thin walls.
- Lower `wallSlide` if hands feel too slippery on surfaces.
- Keep player physics materials low-friction so hand pushes feel responsive.

## Wall shader image setup

Use the `Metacraft/Bonelab Style Wall` shader on wall materials. Assign a city or environment image to `Wall Image / City Texture`; the shader samples a blurred version of that image and overlays broken horizontal stripes directly on the wall geometry. Tune `Blur Strength`, `Stripe Scale`, `Stripe Width`, and `Stripe Strength` per location.
