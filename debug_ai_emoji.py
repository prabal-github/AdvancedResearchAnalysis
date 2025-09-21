from models.ai_detection import AIDetector

if __name__ == "__main__":
    detector = AIDetector()
    sample_texts = [
        "This is a regular sentence without emoji.",
        "Markets rallied today 😊 as investors cheered earnings.",
        "Strong quarter 🚀📈 with revenue growth and margin expansion.",
    ]
    for i, t in enumerate(sample_texts, 1):
        res = detector.detect_ai_content(t)
        print(f"Case {i}: ai_probability={res.get('ai_probability')}, class={res.get('classification')}, details={res.get('detailed_analysis')}")
