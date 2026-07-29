using System.Collections.Generic;
using UnityEngine;

public class MM2WeaponController : MonoBehaviour
{
    [Header("=== МОДЕЛИ ОРУЖИЯ ===")]
    public GameObject revolverModel;
    public GameObject knifeModel;

    [Header("=== РУКИ ===")]
    public string handTag = "HandTag";
    public string weaponTag = "Weapon";
    public bool refreshHandsBeforeGive = true;

    [Header("=== ПОЗИЦИЯ РЕВОЛЬВЕРА ===")]
    public Vector3 revolverPosition = new Vector3(0f, 0.01f, 0.1f);
    public Vector3 revolverRotation = Vector3.zero;

    [Header("=== ПОЗИЦИЯ НОЖА ===")]
    public Vector3 knifePosition = new Vector3(0f, -0.02f, 0.05f);
    public Vector3 knifeRotation = new Vector3(90f, 0f, 0f);

    private readonly List<Transform> hands = new List<Transform>();
    private readonly List<GameObject> spawnedWeapons = new List<GameObject>();

    private void Awake()
    {
        RefreshHands();
    }

    [ContextMenu("MM2/Обновить руки")]
    public void RefreshHands()
    {
        hands.Clear();

        GameObject[] foundHands = GameObject.FindGameObjectsWithTag(handTag);
        foreach (GameObject hand in foundHands)
            hands.Add(hand.transform);

        if (hands.Count == 0)
            Debug.LogWarning($"⚠️ Руки с тегом {handTag} не найдены.");
    }

    public void GiveWeapon(MM2Manager.PlayerRole role)
    {
        ClearWeapons();

        GameObject prefab = GetWeaponPrefab(role);
        if (prefab == null)
            return;

        if (refreshHandsBeforeGive || hands.Count == 0)
            RefreshHands();

        foreach (Transform hand in hands)
            SpawnWeapon(prefab, hand, role);
    }

    public void ClearWeapons()
    {
        for (int i = spawnedWeapons.Count - 1; i >= 0; i--)
        {
            if (spawnedWeapons[i] != null)
                Destroy(spawnedWeapons[i]);
        }

        spawnedWeapons.Clear();

        GameObject[] oldWeapons = GameObject.FindGameObjectsWithTag(weaponTag);
        foreach (GameObject oldWeapon in oldWeapons)
            Destroy(oldWeapon);
    }

    private GameObject GetWeaponPrefab(MM2Manager.PlayerRole role)
    {
        switch (role)
        {
            case MM2Manager.PlayerRole.Sheriff:
                return revolverModel;
            case MM2Manager.PlayerRole.Murderer:
                return knifeModel;
            default:
                return null;
        }
    }

    private void SpawnWeapon(GameObject prefab, Transform hand, MM2Manager.PlayerRole role)
    {
        GameObject weapon = Instantiate(prefab, hand);
        weapon.tag = weaponTag;
        weapon.SetActive(true);

        if (role == MM2Manager.PlayerRole.Sheriff)
        {
            weapon.transform.localPosition = revolverPosition;
            weapon.transform.localRotation = Quaternion.Euler(revolverRotation);
        }
        else if (role == MM2Manager.PlayerRole.Murderer)
        {
            weapon.transform.localPosition = knifePosition;
            weapon.transform.localRotation = Quaternion.Euler(knifeRotation);
        }

        spawnedWeapons.Add(weapon);
        Debug.Log($"🔫 Выдано оружие {weapon.name} на руку {hand.name}");
    }
}
