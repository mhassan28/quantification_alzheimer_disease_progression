import numpy as np

def Dice3d(a, b):
    if len(a.shape) != 3 or len(b.shape) != 3:
        raise Exception(f"Expecting 3 dimensional inputs, got {a.shape} and {b.shape}")

    if a.shape != b.shape:
        raise Exception(f"Expecting inputs of the same shape, got {a.shape} and {b.shape}")

    intersection = np.sum((a > 0) * (b > 0))
    volumes = np.sum(a > 0) + np.sum(b > 0)

    if volumes == 0:
        return -1
    return 2. * float(intersection) / float(volumes)

def Jaccard3d(a, b):
    if len(a.shape) != 3 or len(b.shape) != 3:
        raise Exception(f"Expecting 3 dimensional inputs, got {a.shape} and {b.shape}")

    if a.shape != b.shape:
        raise Exception(f"Expecting inputs of the same shape, got {a.shape} and {b.shape}")
        
    intersection = np.sum((a > 0) * (b > 0))
    union = np.sum(a > 0) + np.sum(b > 0) - intersection

    if union == 0:
        return -1
    return float(intersection) / float(union)