using System.Collections;
using TMPro;
using UnityEngine;

public class MM2Manager : MonoBehaviour
{
    [Header("=== НАСТРОЙКИ РАУНДОВ ===")]
    [Min(1f)] public float intermissionDuration = 10f;
    [Min(1f)] public float roundDuration = 120f;
    public bool useUnscaledTime = true;
    public bool startOnPlay = true;

    [Header("=== UI КАК В SimpleMM2 ===")]
    public TMP_Text timerText;
    public TMP_Text roleText;
    public GameObject intermissionObject;

    [Header("=== ССЫЛКИ НА ДРУГИЕ MM2 СКРИПТЫ ===")]
    public MM2UIController uiController;
    public MM2WeaponController weaponController;
    public MM2PlayFabLogin playFabLogin;

    public enum PlayerRole { Innocent, Sheriff, Murderer }

    public static MM2Manager Instance { get; private set; }

    public PlayerRole CurrentRole { get; private set; } = PlayerRole.Innocent;
    public bool IsIntermission { get; private set; } = true;

    private Coroutine gameLoopCoroutine;

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
        ResolveLocalComponents();
    }

    private void Start()
    {
        ResolveLocalComponents();
        playFabLogin?.Login();

        if (startOnPlay)
            StartGameLoop();
    }

    private void OnDisable()
    {
        StopGameLoop();
    }

    [ContextMenu("MM2/Запустить цикл")]
    public void StartGameLoop()
    {
        StopGameLoop();
        gameLoopCoroutine = StartCoroutine(GameLoop());
    }

    [ContextMenu("MM2/Остановить цикл")]
    public void StopGameLoop()
    {
        if (gameLoopCoroutine == null)
            return;

        StopCoroutine(gameLoopCoroutine);
        gameLoopCoroutine = null;
    }

    private IEnumerator GameLoop()
    {
        while (true)
        {
            StartIntermission();
            yield return RunTimer(intermissionDuration, seconds => SetTimer($"Новый раунд через: {seconds} сек."));

            StartRound();
            yield return RunTimer(roundDuration, seconds => SetTimer($"Раунд: {seconds} сек."));
        }
    }

    private void StartIntermission()
    {
        IsIntermission = true;
        CurrentRole = PlayerRole.Innocent;
        weaponController?.ClearWeapons();
        SetIntermissionVisible(true);
        SetRoleText("Ожидание...");
    }

    private void StartRound()
    {
        IsIntermission = false;
        SetIntermissionVisible(false);
        AssignRandomRole();
    }

    private IEnumerator RunTimer(float duration, System.Action<int> onTick)
    {
        float timeLeft = Mathf.Max(1f, duration);

        while (timeLeft > 0f)
        {
            onTick?.Invoke(Mathf.CeilToInt(timeLeft));

            if (useUnscaledTime)
                yield return new WaitForSecondsRealtime(1f);
            else
                yield return new WaitForSeconds(1f);

            timeLeft--;
        }

        onTick?.Invoke(0);
    }

    private void AssignRandomRole()
    {
        int roleCount = System.Enum.GetValues(typeof(PlayerRole)).Length;
        SetRole(Random.Range(0, roleCount), true);
    }

    public void SetRole(int roleIndex)
    {
        SetRole(roleIndex, true);
    }

    private void SetRole(int roleIndex, bool forceWeaponRefresh)
    {
        if (roleIndex < 0 || roleIndex >= System.Enum.GetValues(typeof(PlayerRole)).Length)
        {
            Debug.LogWarning($"⚠️ Неверный индекс роли: {roleIndex}");
            return;
        }

        CurrentRole = (PlayerRole)roleIndex;
        SetRoleText("Роль: " + CurrentRole);

        if (forceWeaponRefresh)
            weaponController?.GiveWeapon(CurrentRole);

        Debug.Log($"🔑 Роль: {CurrentRole}");
    }

    public PlayerRole GetCurrentRole()
    {
        return CurrentRole;
    }

    private void SetTimer(string value)
    {
        if (timerText != null)
        {
            timerText.text = value;
            return;
        }

        if (uiController != null)
        {
            uiController.SetTimer(value);
            return;
        }

        Debug.Log(value);
    }

    private void SetRoleText(string value)
    {
        if (roleText != null)
        {
            roleText.text = value;
            return;
        }

        uiController?.SetRole(value);
    }

    private void SetIntermissionVisible(bool visible)
    {
        if (intermissionObject != null)
        {
            intermissionObject.SetActive(visible);
            return;
        }

        uiController?.ShowIntermission(visible);
    }

    private void ResolveLocalComponents()
    {
        if (uiController == null)
            uiController = GetComponent<MM2UIController>();

        if (weaponController == null)
            weaponController = GetComponent<MM2WeaponController>();

        if (playFabLogin == null)
            playFabLogin = GetComponent<MM2PlayFabLogin>();
    }
}
