# perception/face_provider.py

def get_best_face(state):
    """
    Expects `state` to hold the latest frame + detected faces.
    Returns (x, y, w, h, W, H) or None.
    """
    frame = state.frame
    faces = state.faces  # list of {"box": [x,y,w,h], ...}

    if not faces:
        return None

    # pick largest face
    faces_sorted = sorted(faces, key=lambda f: f["box"][2] * f["box"][3], reverse=True)
    best = faces_sorted[0]

    x, y, w, h = best["box"]
    H, W = frame.shape[:2]
    return (x, y, w, h, W, H)
