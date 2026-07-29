using TMPro;
using UnityEngine;

public class MM2UIController : MonoBehaviour
{
    public enum IntermissionHideMode
    {
        SetActive,
        RenderersAndColliders
    }

    [Header("=== UI ===")]
    public TMP_Text roleText;
    public TMP_Text timerText;
    public GameObject intermissionObject;

    [Header("=== АВТО-ПОИСК, ЕСЛИ ЗАБЫЛ НАЗНАЧИТЬ ===")]
    public bool autoFindMissingReferences = true;
    public string roleTextObjectName = "RoleText";
    public string timerTextObjectName = "TimerText";
    public string intermissionObjectName = "IntermissionObject";
    public string timerTextContains = "Starting in";

    [Header("=== КАК СКРЫВАТЬ ОТДЫХ ===")]
    public IntermissionHideMode hideMode = IntermissionHideMode.RenderersAndColliders;

    private Renderer[] intermissionRenderers;
    private Collider[] intermissionColliders;
    private Canvas[] intermissionCanvases;

    private void Awake()
    {
        ResolveReferences();
        CacheIntermissionVisuals();
    }

    private void Start()
    {
        ResolveReferences();
        CacheIntermissionVisuals();
    }

    public void SetRole(string value)
    {
        if (roleText == null && autoFindMissingReferences)
            ResolveReferences();

        if (roleText == null)
        {
            Debug.LogWarning("⚠️ roleText не назначен в MM2UIController.");
            return;
        }

        roleText.SetText(value);
        roleText.ForceMeshUpdate();
    }

    public void SetTimer(string value)
    {
        if (timerText == null && autoFindMissingReferences)
            ResolveReferences();

        if (timerText == null)
        {
            Debug.LogWarning("⚠️ timerText не назначен в MM2UIController. Перетащи TMP объект с текстом Starting in в поле Timer Text.");
            return;
        }

        timerText.SetText(value);
        timerText.ForceMeshUpdate();
    }

    public void ShowIntermission(bool show)
    {
        if (intermissionObject == null && autoFindMissingReferences)
            ResolveReferences();

        if (intermissionObject == null)
        {
            Debug.LogWarning("⚠️ intermissionObject не назначен в MM2UIController.");
            return;
        }

        if (intermissionObject == gameObject || transform.IsChildOf(intermissionObject.transform))
        {
            Debug.LogError("❌ IntermissionObject нельзя ставить на объект с MM2UIController или его родителя. Иначе скрипт выключит сам себя.");
            return;
        }

        if (hideMode == IntermissionHideMode.SetActive)
        {
            intermissionObject.SetActive(show);
            return;
        }

        SetIntermissionVisuals(show);
    }

    [ContextMenu("MM2/UI Найти ссылки")]
    public void ResolveReferences()
    {
        if (!autoFindMissingReferences)
            return;

        if (roleText == null)
            roleText = FindTextByNameOrContent(roleTextObjectName, string.Empty);

        if (timerText == null)
            timerText = FindTextByNameOrContent(timerTextObjectName, timerTextContains);

        if (intermissionObject == null)
            intermissionObject = FindObjectByName(intermissionObjectName);

        if (intermissionObject == null && timerText != null)
            intermissionObject = FindHighestSafeParent(timerText.transform).gameObject;
    }

    [ContextMenu("MM2/UI Показать отдых")]
    public void ShowIntermissionObject()
    {
        ShowIntermission(true);
    }

    [ContextMenu("MM2/UI Скрыть отдых")]
    public void HideIntermissionObject()
    {
        ShowIntermission(false);
    }

    private void CacheIntermissionVisuals()
    {
        if (intermissionObject == null)
            return;

        intermissionRenderers = intermissionObject.GetComponentsInChildren<Renderer>(true);
        intermissionColliders = intermissionObject.GetComponentsInChildren<Collider>(true);
        intermissionCanvases = intermissionObject.GetComponentsInChildren<Canvas>(true);
    }

    private void SetIntermissionVisuals(bool show)
    {
        if (intermissionRenderers == null || intermissionColliders == null || intermissionCanvases == null)
            CacheIntermissionVisuals();

        foreach (Renderer targetRenderer in intermissionRenderers)
        {
            if (targetRenderer != null)
                targetRenderer.enabled = show;
        }

        foreach (Collider targetCollider in intermissionColliders)
        {
            if (targetCollider != null)
                targetCollider.enabled = show;
        }

        foreach (Canvas targetCanvas in intermissionCanvases)
        {
            if (targetCanvas != null)
                targetCanvas.enabled = show;
        }
    }

    private TMP_Text FindTextByNameOrContent(string objectName, string textContains)
    {
        TMP_Text[] texts = Resources.FindObjectsOfTypeAll<TMP_Text>();
        foreach (TMP_Text text in texts)
        {
            if (!text.gameObject.scene.IsValid())
                continue;

            if (!string.IsNullOrEmpty(objectName) && text.gameObject.name == objectName)
                return text;

            if (!string.IsNullOrEmpty(textContains) && text.text.Contains(textContains))
                return text;
        }

        return null;
    }

    private GameObject FindObjectByName(string objectName)
    {
        if (string.IsNullOrEmpty(objectName))
            return null;

        Transform[] transforms = Resources.FindObjectsOfTypeAll<Transform>();
        foreach (Transform foundTransform in transforms)
        {
            if (foundTransform.gameObject.scene.IsValid() && foundTransform.gameObject.name == objectName)
                return foundTransform.gameObject;
        }

        return null;
    }

    private Transform FindHighestSafeParent(Transform start)
    {
        Transform current = start;

        while (current.parent != null && !transform.IsChildOf(current.parent))
            current = current.parent;

        return current;
    }
}
