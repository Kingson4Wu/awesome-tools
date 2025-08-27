from paddleocr import PaddleOCR
import pycorrector

# 初始化 OCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')  # lang='ch' 支持中英文混排


# 创建 Corrector 实例
corrector = pycorrector.Corrector()

def correct_text(text: str) -> str:
    corrected, _ = corrector.correct(text)
    return corrected



def ocr_and_correct(image_path: str):
    # 执行 OCR 识别
    results = ocr.predict(image_path)

    print("—— OCR 原始识别结果 ——")
    for line in results[0]:
        original_text = line[1][0]
        print(f"原文: {original_text}")

        corrected_text = correct_text(original_text)
        print(f"纠正: {corrected_text}")
        print("-" * 30)


if __name__ == "__main__":
    image_file = "IMG_6835.PNG"  # 替换为你的图片路径
    ocr_and_correct(image_file)

# pip install paddlepaddle
# pip install paddleocr
# pip install pycorrector
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118


# 效果差！！！
