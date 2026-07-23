using System.Collections.Generic;
using UnityEngine;

namespace Metacraft.Locations
{
    /// <summary>
    /// Simple location switcher for prototype arenas/maps.
    /// Assign location root prefabs or scene objects and press number keys to switch.
    /// </summary>
    public class LocationManager : MonoBehaviour
    {
        [SerializeField] private List<GameObject> locations = new List<GameObject>();
        [SerializeField] private Transform player;
        [SerializeField] private List<Transform> playerSpawnPoints = new List<Transform>();
        [SerializeField] private int activeLocationIndex;

        private void Start()
        {
            ActivateLocation(activeLocationIndex);
        }

        private void Update()
        {
            for (int i = 0; i < Mathf.Min(locations.Count, 9); i++)
            {
                if (Input.GetKeyDown((KeyCode)((int)KeyCode.Alpha1 + i)))
                {
                    ActivateLocation(i);
                }
            }
        }

        public void ActivateLocation(int index)
        {
            if (index < 0 || index >= locations.Count)
            {
                return;
            }

            activeLocationIndex = index;
            for (int i = 0; i < locations.Count; i++)
            {
                if (locations[i] != null)
                {
                    locations[i].SetActive(i == activeLocationIndex);
                }
            }

            MovePlayerToSpawn(index);
        }

        private void MovePlayerToSpawn(int index)
        {
            if (player == null || index >= playerSpawnPoints.Count || playerSpawnPoints[index] == null)
            {
                return;
            }

            Rigidbody playerBody = player.GetComponent<Rigidbody>();
            if (playerBody != null)
            {
                playerBody.velocity = Vector3.zero;
                playerBody.angularVelocity = Vector3.zero;
            }

            player.SetPositionAndRotation(playerSpawnPoints[index].position, playerSpawnPoints[index].rotation);
        }
    }
}
