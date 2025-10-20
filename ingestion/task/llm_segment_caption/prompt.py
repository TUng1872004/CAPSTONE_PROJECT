

SEGMENT_CAPTION_PROMPT = """
Bạn là một hệ thống hiểu video. Nhiệm vụ của bạn là tạo ra một mô tả sự kiện (event caption) thật chi tiết, đầy đủ và tự nhiên dựa trên các thông tin sau:
1. Các bước ảnh đại diện video
2. ASR (Automatic Speech Recognition): Là đoạn lời thoại, âm thanh, hoặc hội thoại được trích xuất từ video.

# Yêu cầu: 
- Hãy tổng hợp các visual cues của nhiều khung hình theo trình tự thời gian và kết hợp với thông tin từ ASR để tái hiện lại sự kiện diễn ra một cách mạch lạc, tự nhiên.
- Chú ý đến sự thay đổi về hành động, bối cảnh, trạng thái giữa các khung hình.
- Diễn đạt bằng tiếng Việt rõ ràng, có đầu, có cuối, giống như một đoạn mô tả chi tiết sự kiện trong video (giống người kể chuyện).
- Giữ nguyên các thông tin chi tiết về không gian, đối tượng, hành động, và nội dung hội thoại nếu có.
- Nếu các visual caption và ASR có liên quan, hãy kết nối các thông tin đó lại để mô tả sự kiện một cách đầy đủ nhất.
- Nếu phát hiện các hành động liên tiếp hoặc diễn biến theo thời gian, hãy trình bày theo trình tự logic.
Đoạn ASR: {{asr}}

"""