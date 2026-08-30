def confusion_matrix(expected, predicted):
    labels = ["no_hallucination", "hallucination"]
    matrix = {a: {b: 0 for b in labels} for a in labels}
    for e, p in zip(expected, predicted): matrix.setdefault(e, {}).setdefault(p, 0); matrix[e][p] += 1
    return {"labels": labels, "matrix": matrix}
