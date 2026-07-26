using UnityEngine;
using UnityEngine.Events;

namespace Metacraft.UI
{
    /// <summary>
    /// Attach this to a UI Button. Assign SpawnItemInFrontOfPlayer to the Button OnClick event.
    /// It spawns the configured prefab in front of the player/head with optional physics impulse.
    /// </summary>
    public class SpawnItemButton : MonoBehaviour
    {
        [SerializeField] private GameObject itemPrefab;
        [SerializeField] private Transform playerHead;
        [SerializeField] private float spawnDistance = 1.2f;
        [SerializeField] private float spawnHeightOffset = -0.15f;
        [SerializeField] private float forwardImpulse = 0.75f;
        [SerializeField] private bool alignToPlayerYaw = true;
        [SerializeField] private UnityEvent afterSpawn;

        private void Awake()
        {
            if (playerHead == null && Camera.main != null)
            {
                playerHead = Camera.main.transform;
            }
        }

        public void SpawnItemInFrontOfPlayer()
        {
            if (itemPrefab == null || playerHead == null)
            {
                Debug.LogWarning("SpawnItemButton needs an item prefab and player head transform.", this);
                return;
            }

            Vector3 forward = Vector3.ProjectOnPlane(playerHead.forward, Vector3.up).normalized;
            if (forward.sqrMagnitude < 0.001f)
            {
                forward = playerHead.forward.normalized;
            }

            Vector3 position = playerHead.position + forward * spawnDistance + Vector3.up * spawnHeightOffset;
            Quaternion rotation = alignToPlayerYaw ? Quaternion.LookRotation(forward, Vector3.up) : itemPrefab.transform.rotation;
            GameObject instance = Instantiate(itemPrefab, position, rotation);

            if (instance.TryGetComponent(out Rigidbody rigidbody))
            {
                rigidbody.AddForce(forward * forwardImpulse, ForceMode.VelocityChange);
            }

            afterSpawn?.Invoke();
        }
    }
}
