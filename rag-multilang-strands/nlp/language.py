from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

def detect_lang(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"
