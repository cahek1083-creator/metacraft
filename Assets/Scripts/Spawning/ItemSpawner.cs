using System.Collections.Generic;
using UnityEngine;

namespace Metacraft.Spawning
{
    /// <summary>
    /// Spawns weighted physics props at designer-defined points or near the spawner.
    /// </summary>
    public class ItemSpawner : MonoBehaviour
    {
        [SerializeField] private List<SpawnableItem> itemPrefabs = new List<SpawnableItem>();
        [SerializeField] private List<Transform> spawnPoints = new List<Transform>();
        [SerializeField] private int spawnOnStart = 12;
        [SerializeField] private float randomRadius = 8f;
        [SerializeField] private float upwardImpulse = 1.5f;
        [SerializeField] private KeyCode spawnHotkey = KeyCode.Q;

        private void Start()
        {
            for (int i = 0; i < spawnOnStart; i++)
            {
                SpawnRandom();
            }
        }

        private void Update()
        {
            if (Input.GetKeyDown(spawnHotkey))
            {
                SpawnRandom();
            }
        }

        public GameObject SpawnRandom()
        {
            return SpawnRandomAt(GetSpawnPosition());
        }

        public GameObject SpawnRandomAt(Vector3 position)
        {
            SpawnableItem prefab = PickWeightedPrefab();
            if (prefab == null)
            {
                Debug.LogWarning("ItemSpawner has no spawnable prefabs.", this);
                return null;
            }

            Quaternion rotation = Random.rotation;
            SpawnableItem instance = Instantiate(prefab, position, rotation);

            if (instance.TryGetComponent(out Rigidbody rigidbody))
            {
                rigidbody.AddForce(Vector3.up * upwardImpulse, ForceMode.VelocityChange);
            }

            return instance.gameObject;
        }

        private SpawnableItem PickWeightedPrefab()
        {
            float totalWeight = 0f;
            foreach (SpawnableItem prefab in itemPrefabs)
            {
                if (prefab != null)
                {
                    totalWeight += prefab.SpawnWeight;
                }
            }

            float roll = Random.value * totalWeight;
            foreach (SpawnableItem prefab in itemPrefabs)
            {
                if (prefab == null)
                {
                    continue;
                }

                roll -= prefab.SpawnWeight;
                if (roll <= 0f)
                {
                    return prefab;
                }
            }

            return itemPrefabs.Count > 0 ? itemPrefabs[0] : null;
        }

        private Vector3 GetSpawnPosition()
        {
            if (spawnPoints.Count > 0)
            {
                Transform point = spawnPoints[Random.Range(0, spawnPoints.Count)];
                if (point != null)
                {
                    return point.position;
                }
            }

            Vector2 circle = Random.insideUnitCircle * randomRadius;
            return transform.position + new Vector3(circle.x, 1f, circle.y);
        }
    }
}
