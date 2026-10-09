SENSITIVITY = {
    "PUBLIC": 0, "INTERNAL": 10, "CONFIDENTIAL": 20,
    "HIGHLY_SENSITIVE": 35, "CRITICAL": 40
}
ACTION = {
    "FILE_ACCESS": 0, "READ": 0, "DOWNLOAD": 10, "UPLOAD": 25, "SHARE": 30, "CLOUD_UPLOAD": 30,
    "EMAIL_ATTACHMENT": 30, "USB_COPY": 35, "CLIPBOARD": 15, "PRINT": 10
}
DESTINATION = {
    "PERSONAL_CLOUD": 30, "PERSONAL_EMAIL": 35, "USB": 30,
    "EXTERNAL_MESSAGING": 30, "UNKNOWN": 20
}

def evaluate_rules(action, sensitivity, destination, permission_allowed):
    action = action.upper()
    sensitivity = sensitivity.upper()
    destination = (destination or "").upper()
    score, reasons = 0, []

    if not permission_allowed:
        score += 30
        reasons.append("User is not authorized to perform this action")

    score += SENSITIVITY.get(sensitivity, 10)
    if sensitivity in {"CONFIDENTIAL", "HIGHLY_SENSITIVE", "CRITICAL"}:
        reasons.append(f"File is classified as {sensitivity}")

    score += ACTION.get(action, 5)
    if action in {"UPLOAD", "SHARE", "CLOUD_UPLOAD", "USB_COPY", "EMAIL_ATTACHMENT"}:
        reasons.append(f"Potential data transfer action detected: {action}")

    score += DESTINATION.get(destination, 0)
    if destination in DESTINATION:
        reasons.append(f"Destination is considered risky: {destination}")

    return score, reasons
