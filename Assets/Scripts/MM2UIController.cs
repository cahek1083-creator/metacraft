using TMPro;
using UnityEngine;

public class MM2UIController : MonoBehaviour
{
    [Header("=== UI ===")]
    public TMP_Text roleText;
    public TMP_Text timerText;
    public GameObject intermissionObject;

    public void SetRole(string value)
    {
        if (roleText == null)
        {
            Debug.LogWarning("⚠️ roleText не назначен в MM2UIController.");
            return;
        }

        roleText.SetText(value);
    }

    public void SetTimer(string value)
    {
        if (timerText == null)
        {
            Debug.LogWarning("⚠️ timerText не назначен в MM2UIController.");
            return;
        }

        timerText.SetText(value);
    }

    public void ShowIntermission(bool show)
    {
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

        intermissionObject.SetActive(show);
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
}
