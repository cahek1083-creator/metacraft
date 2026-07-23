using UnityEngine;

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
        [SerializeField] private KeyCode keyboardFallback = KeyCode.Q;

        private ItemSpawner itemSpawner;

        private void Awake()
        {
            itemSpawner = GetComponent<ItemSpawner>();
        }

        private void Update()
        {
            if (Input.GetKeyDown(keyboardFallback))
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
