using UnityEngine;

namespace Metacraft.Player
{
    /// <summary>
    /// Physical VR gorilla-style locomotion driven by hand/controller movement.
    /// Put this on the rig root with a Rigidbody. Assign the headset/camera and both hand targets.
    /// </summary>
    [RequireComponent(typeof(Rigidbody))]
    [RequireComponent(typeof(CapsuleCollider))]
    public class VRGorillaLocomotion : MonoBehaviour
    {
        [Header("VR Tracking")]
        [SerializeField] private Transform head;
        [SerializeField] private Transform leftHand;
        [SerializeField] private Transform rightHand;
        [SerializeField] private Transform leftHandCollider;
        [SerializeField] private Transform rightHandCollider;

        [Header("Player Body")]
        [SerializeField] private float bodyRadius = 0.28f;
        [SerializeField] private float minimumBodyHeight = 0.7f;
        [SerializeField] private float maximumBodyHeight = 2.2f;
        [SerializeField] private float bodyHeightOffset = 0.08f;

        [Header("Hand Collision")]
        [SerializeField] private LayerMask locomotionMask = ~0;
        [SerializeField] private float handRadius = 0.12f;
        [SerializeField] private float handCastPadding = 0.02f;
        [SerializeField] private float stickyHandReleaseDistance = 0.55f;
        [SerializeField] private float wallSlide = 0.04f;

        [Header("Velocity")]
        [SerializeField] private int velocityHistorySize = 12;
        [SerializeField] private float maxArmLength = 1.45f;
        [SerializeField] private float launchMultiplier = 1.35f;
        [SerializeField] private float maxLaunchSpeed = 9f;
        [SerializeField] private float minimumLaunchSpeed = 1.2f;
        [SerializeField] private float airControlDamping = 0.98f;

        [Header("Comfort")]
        [SerializeField] private bool rotateWithHeadYaw = true;
        [SerializeField] private bool lockCursorInEditor;

        private Rigidbody body;
        private CapsuleCollider capsule;
        private Vector3 lastLeftHandPosition;
        private Vector3 lastRightHandPosition;
        private Vector3 lastHeadPosition;
        private Vector3[] velocityHistory;
        private int velocityIndex;
        private Vector3 currentAverageVelocity;
        private bool leftHandTouching;
        private bool rightHandTouching;

        private void Awake()
        {
            body = GetComponent<Rigidbody>();
            capsule = GetComponent<CapsuleCollider>();
            velocityHistory = new Vector3[Mathf.Max(1, velocityHistorySize)];

            body.useGravity = true;
            body.freezeRotation = true;
            body.interpolation = RigidbodyInterpolation.Interpolate;

            if (head == null && Camera.main != null)
            {
                head = Camera.main.transform;
            }

            lastHeadPosition = GetHeadPosition();
            lastLeftHandPosition = GetHandPosition(leftHand);
            lastRightHandPosition = GetHandPosition(rightHand);

            if (lockCursorInEditor)
            {
                Cursor.lockState = CursorLockMode.Locked;
                Cursor.visible = false;
            }
        }

        private void FixedUpdate()
        {
            UpdateBodyCollider();
            MoveFromHands();
            StoreVelocity();
            lastHeadPosition = GetHeadPosition();
        }

        private void LateUpdate()
        {
            UpdateVisualHand(leftHandCollider, lastLeftHandPosition);
            UpdateVisualHand(rightHandCollider, lastRightHandPosition);
        }

        private void UpdateBodyCollider()
        {
            Vector3 headPosition = GetHeadPosition();
            float height = Mathf.Clamp(headPosition.y - transform.position.y + bodyHeightOffset, minimumBodyHeight, maximumBodyHeight);
            capsule.height = height;
            capsule.radius = bodyRadius;
            capsule.center = new Vector3(0f, height * 0.5f, 0f);

            if (!rotateWithHeadYaw || head == null)
            {
                return;
            }

            Vector3 flatForward = Vector3.ProjectOnPlane(head.forward, Vector3.up);
            if (flatForward.sqrMagnitude > 0.001f)
            {
                transform.rotation = Quaternion.LookRotation(flatForward.normalized, Vector3.up);
            }
        }

        private void MoveFromHands()
        {
            Vector3 leftTarget = ClampHandToArmLength(leftHand);
            Vector3 rightTarget = ClampHandToArmLength(rightHand);
            Vector3 leftDelta = leftTarget - lastLeftHandPosition;
            Vector3 rightDelta = rightTarget - lastRightHandPosition;

            Vector3 movement = Vector3.zero;
            bool leftCollided = ResolveHandMovement(lastLeftHandPosition, leftDelta, out Vector3 leftResolved);
            bool rightCollided = ResolveHandMovement(lastRightHandPosition, rightDelta, out Vector3 rightResolved);

            if (leftCollided)
            {
                movement += lastLeftHandPosition - leftResolved;
            }

            if (rightCollided)
            {
                movement += lastRightHandPosition - rightResolved;
            }

            int touchCount = (leftCollided ? 1 : 0) + (rightCollided ? 1 : 0);
            if (touchCount > 0)
            {
                movement /= touchCount;
                body.MovePosition(body.position + movement);
                ApplyLaunchVelocity();
            }
            else
            {
                body.velocity *= airControlDamping;
            }

            lastLeftHandPosition = leftCollided ? leftResolved : leftTarget;
            lastRightHandPosition = rightCollided ? rightResolved : rightTarget;
            leftHandTouching = leftCollided;
            rightHandTouching = rightCollided;
        }

        private bool ResolveHandMovement(Vector3 startPosition, Vector3 delta, out Vector3 resolvedPosition)
        {
            float distance = delta.magnitude;
            if (distance <= Mathf.Epsilon)
            {
                resolvedPosition = startPosition;
                return false;
            }

            Vector3 direction = delta / distance;
            if (Physics.SphereCast(startPosition, handRadius, direction, out RaycastHit hit, distance + handCastPadding, locomotionMask, QueryTriggerInteraction.Ignore))
            {
                Vector3 slide = Vector3.ProjectOnPlane(delta, hit.normal) * wallSlide;
                resolvedPosition = hit.point + hit.normal * (handRadius + handCastPadding) + slide;
                return true;
            }

            resolvedPosition = startPosition + delta;
            return false;
        }

        private void ApplyLaunchVelocity()
        {
            if (currentAverageVelocity.magnitude < minimumLaunchSpeed)
            {
                return;
            }

            Vector3 launchVelocity = Vector3.ClampMagnitude(currentAverageVelocity * launchMultiplier, maxLaunchSpeed);
            body.velocity = launchVelocity;
        }

        private void StoreVelocity()
        {
            Vector3 headVelocity = (GetHeadPosition() - lastHeadPosition) / Time.fixedDeltaTime;
            velocityHistory[velocityIndex] = headVelocity;
            velocityIndex = (velocityIndex + 1) % velocityHistory.Length;

            currentAverageVelocity = Vector3.zero;
            for (int i = 0; i < velocityHistory.Length; i++)
            {
                currentAverageVelocity += velocityHistory[i];
            }

            currentAverageVelocity /= velocityHistory.Length;
        }

        private Vector3 ClampHandToArmLength(Transform hand)
        {
            Vector3 headPosition = GetHeadPosition();
            Vector3 handPosition = GetHandPosition(hand);
            Vector3 headToHand = handPosition - headPosition;

            if (headToHand.magnitude > maxArmLength)
            {
                return headPosition + headToHand.normalized * maxArmLength;
            }

            return handPosition;
        }

        private Vector3 GetHeadPosition()
        {
            return head != null ? head.position : transform.position + Vector3.up * capsule.height;
        }

        private Vector3 GetHandPosition(Transform hand)
        {
            return hand != null ? hand.position : GetHeadPosition();
        }

        private void UpdateVisualHand(Transform visualHand, Vector3 targetPosition)
        {
            if (visualHand != null)
            {
                visualHand.position = targetPosition;
            }
        }

        public bool IsLeftHandTouching => leftHandTouching;
        public bool IsRightHandTouching => rightHandTouching;
        public float StickyHandReleaseDistance => stickyHandReleaseDistance;
    }
}
