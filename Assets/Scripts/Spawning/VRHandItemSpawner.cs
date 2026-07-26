using UnityEngine;
using UnityEngine.InputSystem;

namespace Metacraft.Spawning
{
    /// <summary>
    /// VR-friendly bridge for spawning props from either hand.
    /// Hook SpawnLeftHand or SpawnRightHand to XR controller input events in the Unity Input System.
    /// </summary>
    [RequireComponent(typeof(ItemSpawner))]
    public class VRHandItemSpawner : MonoBehaviour
    {
        [SerializeField] private Transform leftHandSpawnPoint;
        [SerializeField] private Transform rightHandSpawnPoint;
        [SerializeField] private InputActionProperty leftSpawnAction;
        [SerializeField] private InputActionProperty rightSpawnAction;
        [SerializeField] private Key editorKeyboardFallback = Key.Q;
        [SerializeField] private bool allowKeyboardFallback = true;

        private ItemSpawner itemSpawner;

        private void Awake()
        {
            itemSpawner = GetComponent<ItemSpawner>();
        }

        private void OnEnable()
        {
            leftSpawnAction.action?.Enable();
            rightSpawnAction.action?.Enable();
        }

        private void OnDisable()
        {
            leftSpawnAction.action?.Disable();
            rightSpawnAction.action?.Disable();
        }

        private void Update()
        {
            if (leftSpawnAction.action != null && leftSpawnAction.action.WasPressedThisFrame())
            {
                SpawnLeftHand();
            }

            if (rightSpawnAction.action != null && rightSpawnAction.action.WasPressedThisFrame())
            {
                SpawnRightHand();
            }

            if (allowKeyboardFallback && Keyboard.current != null && Keyboard.current[editorKeyboardFallback].wasPressedThisFrame)
            {
                SpawnRightHand();
            }
        }

        public void SpawnLeftHand()
        {
            SpawnAt(leftHandSpawnPoint);
        }

        public void SpawnRightHand()
        {
            SpawnAt(rightHandSpawnPoint);
        }

        private void SpawnAt(Transform spawnPoint)
        {
            if (spawnPoint != null)
            {
                itemSpawner.SpawnRandomAt(spawnPoint.position);
                return;
            }

            itemSpawner.SpawnRandom();
        }
    }
}
