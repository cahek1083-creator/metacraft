using UnityEngine;

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
        [SerializeField] private KeyCode toggleKey = KeyCode.Y;
        [SerializeField] private KeyCode vrYButtonFallback = KeyCode.JoystickButton3;
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

        private void Update()
        {
            if (Input.GetKeyDown(toggleKey) || Input.GetKeyDown(vrYButtonFallback))
            {
                ToggleMenu();
            }
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
