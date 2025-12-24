def calculate_risk(events):
    """
    Calculate overall risk level based on cheating events.
    """

    score = 0
    score += events.get("NO_FACE", 0) * 3
    score += events.get("MULTIPLE_FACES", 0) * 5
    score += events.get("LOOKING_AWAY", 0) * 2
    score += events.get("AUDIO_DETECTED", 0) * 3

    if score >= 12:
        return "HIGH"
    elif score >= 6:
        return "MEDIUM"
    return "LOW"
