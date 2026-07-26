# Metacraft VR Physics Prototype

Starter Unity kit for a VR physics sandbox with gorilla-style physical locomotion, props, multiple locations, and quick prototype shaders. The runtime input scripts are designed for Unity XR Interaction Toolkit and the Unity Input System.

## Included systems

- `VRGorillaLocomotion` — Rigidbody VR locomotion driven by headset and hand/controller Transforms. Push from walls/floors with hands to move, climb, and launch.
- `ItemSpawner`, `SpawnableItem`, and `VRHandItemSpawner` — weighted prop spawning from world points or from VR hand positions. Hook `SpawnLeftHand` / `SpawnRightHand` to XR input events.
- `LocationManager` — switches between location roots with number keys and moves the VR rig to matching spawn points.
- `SpawnMenuController` and `SpawnItemButton` — opens an item menu with `Y`; each button can spawn its assigned prefab in front of the player.
- `Bonelab Style Wall` and `LocationFloor` shaders — wall shader accepts an image/city texture, blurs it, and draws broken horizontal stripes over the wall surface.

## Required Unity packages

Install these Unity packages before importing the scripts:

- XR Interaction Toolkit
- Input System
- XR Plugin Management

Use the XR Interaction Toolkit Starter Assets or your own Input Action Asset for controller actions.

## Quick VR setup

1. Create a Unity 3D or URP VR project with an XR Origin / camera rig.
2. Add a `Rigidbody`, `CapsuleCollider`, and `VRGorillaLocomotion` to the rig root.
3. Assign the headset camera to `head`, and assign left/right controller Transforms to `leftHand` and `rightHand`.
4. Add small sphere visuals or collider proxy objects for the hands and assign them to `leftHandCollider` / `rightHandCollider`.
5. Put climbable/pushable walls, floor, and props on layers included by `locomotionMask`.
6. Create prop prefabs with `Rigidbody`, colliders, and `SpawnableItem`; assign them to an `ItemSpawner`.
7. Add `VRHandItemSpawner` beside `ItemSpawner`, assign left/right hand spawn Transforms, and bind `leftSpawnAction` / `rightSpawnAction` to XR Interaction Toolkit controller Input Actions.
8. Create a world-space Canvas for the item menu with `TrackedDeviceGraphicRaycaster`, assign it to `SpawnMenuController.menuRoot`, then bind `SpawnMenuController.toggleAction` to the left controller secondary button / Y button action. Keyboard `Y` remains only an editor fallback.
9. Add `SpawnItemButton` to each UI Button, assign an item prefab and the headset transform, then connect the Button OnClick event to `SpawnItemInFrontOfPlayer`.
10. Put each map/location under its own root GameObject and assign those roots to `LocationManager`.

## Tuning tips

- Increase `launchMultiplier` and `maxLaunchSpeed` for more arcade-like Gorilla Tag jumps.
- Increase `handRadius` if hands clip through thin walls.
- Lower `wallSlide` if hands feel too slippery on surfaces.
- Keep player physics materials low-friction so hand pushes feel responsive.

## Wall shader image setup

Use the `Metacraft/Bonelab Style Wall` shader on wall materials. Assign a city or environment image to `Wall Image / City Texture`; the shader samples a blurred version of that image and overlays broken horizontal stripes directly on the wall geometry. Tune `Blur Strength`, `Stripe Scale`, `Stripe Width`, and `Stripe Strength` per location.

## XR Interaction Toolkit input notes

`SpawnMenuController` and `VRHandItemSpawner` use `InputActionProperty`, so you can drag actions from the XR Interaction Toolkit Starter Assets directly into the inspector. Recommended bindings are `<XRController>{LeftHand}/secondaryButton` for the item menu and grip/trigger actions for hand spawning. For UI interaction, keep an `EventSystem` with `XRUIInputModule` in the scene and put `TrackedDeviceGraphicRaycaster` on the menu Canvas.
