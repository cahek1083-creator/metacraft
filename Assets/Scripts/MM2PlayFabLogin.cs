using UnityEngine;

public class MM2PlayFabLogin : MonoBehaviour
{
    [Tooltip("Оставлено отдельным скриптом, чтобы MM2Manager не зависел от PlayFab SDK и таймер работал даже без PlayFab в проекте.")]
    public bool loginOnStart = false;

    private void Start()
    {
        if (loginOnStart)
            Login();
    }

    public void Login()
    {
        Debug.Log("ℹ️ PlayFab login отключён в этой версии скрипта. Таймер, роли и скрытие intermission работают без PlayFab SDK.");
    }
}
