from .confusion_matrix import confusion_matrix

def calculate_metrics(expected, predicted):
    n = len(expected)
    correct = sum(actual == predicted_label for actual, predicted_label in zip(expected, predicted))
    positive = "hallucination"
    tp = sum(actual == positive and predicted_label == positive for actual, predicted_label in zip(expected, predicted))
    tn = sum(actual != positive and predicted_label != positive for actual, predicted_label in zip(expected, predicted))
    fp = sum(actual != positive and predicted_label == positive for actual, predicted_label in zip(expected, predicted))
    fn = sum(actual == positive and predicted_label != positive for actual, predicted_label in zip(expected, predicted))
    precision = tp/(tp+fp) if tp+fp else 0.0; recall = tp/(tp+fn) if tp+fn else 0.0; f1 = 2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"total_samples": n, "correct_predictions": correct, "incorrect_predictions": n-correct, "accuracy": correct/n if n else 0.0, "precision": precision, "recall": recall, "f1_score": f1, "tp": tp, "tn": tn, "fp": fp, "fn": fn, "confusion_matrix": confusion_matrix(expected,predicted)}
