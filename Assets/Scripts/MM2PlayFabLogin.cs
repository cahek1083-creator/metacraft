using PlayFab;
using PlayFab.ClientModels;
using UnityEngine;

public class MM2PlayFabLogin : MonoBehaviour
{
    public bool loginOnStart = false;

    private void Start()
    {
        if (loginOnStart)
            Login();
    }

    public void Login()
    {
        var request = new LoginWithCustomIDRequest
        {
            CustomId = SystemInfo.deviceUniqueIdentifier,
            CreateAccount = true
        };

        PlayFabClientAPI.LoginWithCustomID(request, OnLoginSuccess, OnLoginFailure);
    }

    private void OnLoginSuccess(LoginResult result)
    {
        Debug.Log("✅ Успешный вход в PlayFab!");
    }

    private void OnLoginFailure(PlayFabError error)
    {
        Debug.LogError($"❌ Ошибка входа в PlayFab: {error.GenerateErrorReport()}");
    }
}
