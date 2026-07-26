using UnityEngine;
using UnityEngine.InputSystem;

namespace Metacraft.UI
{
    /// <summary>
    /// Opens and closes the VR item menu. By default the Y key toggles it for editor testing;
    /// XR controller input can call ToggleMenu, OpenMenu, or CloseMenu directly.
    /// </summary>
    public class SpawnMenuController : MonoBehaviour
    {
        [SerializeField] private GameObject menuRoot;
        [SerializeField] private Transform playerHead;
        [SerializeField] private float menuDistance = 1.25f;
        [SerializeField] private float menuHeightOffset = -0.15f;
        [SerializeField] private InputActionProperty toggleAction;
        [SerializeField] private Key editorToggleKey = Key.Y;
        [SerializeField] private bool allowKeyboardFallback = true;
        [SerializeField] private bool facePlayerOnOpen = true;
        [SerializeField] private bool startClosed = true;

        private void Awake()
        {
            if (playerHead == null && Camera.main != null)
            {
                playerHead = Camera.main.transform;
            }

            if (menuRoot != null && startClosed)
            {
                menuRoot.SetActive(false);
            }
        }

        private void OnEnable()
        {
            toggleAction.action?.Enable();
        }

        private void OnDisable()
        {
            toggleAction.action?.Disable();
        }

        private void Update()
        {
            if (WasTogglePressed())
            {
                ToggleMenu();
            }
        }

        private bool WasTogglePressed()
        {
            if (toggleAction.action != null && toggleAction.action.WasPressedThisFrame())
            {
                return true;
            }

            return allowKeyboardFallback && Keyboard.current != null && Keyboard.current[editorToggleKey].wasPressedThisFrame;
        }

        public void ToggleMenu()
        {
            if (menuRoot == null)
            {
                return;
            }

            bool shouldOpen = !menuRoot.activeSelf;
            menuRoot.SetActive(shouldOpen);

            if (shouldOpen)
            {
                PositionMenuInFrontOfPlayer();
            }
        }

        public void OpenMenu()
        {
            if (menuRoot == null)
            {
                return;
            }

            menuRoot.SetActive(true);
            PositionMenuInFrontOfPlayer();
        }

        public void CloseMenu()
        {
            if (menuRoot != null)
            {
                menuRoot.SetActive(false);
            }
        }

        private void PositionMenuInFrontOfPlayer()
        {
            if (menuRoot == null || playerHead == null)
            {
                return;
            }

            Vector3 forward = Vector3.ProjectOnPlane(playerHead.forward, Vector3.up).normalized;
            if (forward.sqrMagnitude < 0.001f)
            {
                forward = playerHead.forward;
            }

            menuRoot.transform.position = playerHead.position + forward * menuDistance + Vector3.up * menuHeightOffset;

            if (facePlayerOnOpen)
            {
                Vector3 toPlayer = playerHead.position - menuRoot.transform.position;
                toPlayer.y = 0f;
                if (toPlayer.sqrMagnitude > 0.001f)
                {
                    menuRoot.transform.rotation = Quaternion.LookRotation(-toPlayer.normalized, Vector3.up);
                }
            }
        }
    }
}
