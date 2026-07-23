using UnityEngine;

namespace Metacraft.Spawning
{
    /// <summary>
    /// Metadata for objects that can be spawned by ItemSpawner.
    /// </summary>
    public class SpawnableItem : MonoBehaviour
    {
        [SerializeField] private string displayName = "Physics Prop";
        [SerializeField] private float spawnWeight = 1f;

        public string DisplayName => displayName;
        public float SpawnWeight => Mathf.Max(0.01f, spawnWeight);
    }
}
