# backend/openai_handler.py
import os
from openai import OpenAI
from backend import config

class OpenAIHandler:
    def __init__(self):
        # Ưu tiên lấy API key từ config.py, nếu không có thì lấy từ biến môi trường
        self.api_key = getattr(config, "OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ OPENAI_API_KEY chưa được đặt trong biến môi trường hoặc config.py")

        # Kết nối OpenAI
        self.client = OpenAI(api_key=self.api_key)

        # Model LLM (ưu tiên gpt-4o-mini để rẻ/nhanh; có thể đổi sang gpt-4o nếu muốn)
        self.model = getattr(config, "MODEL_LLM", "gpt-4o-mini")

    def generate_response_with_context(self, user_message: str, context: str) -> str:
        """
        Gửi prompt đến OpenAI. Nếu context chứa dữ liệu (Markdown), bắt buộc LLM:
        - CHỈ sử dụng facts có trong `context` (không bịa).
        - Nếu context là "KHÔNG_CÓ_CONTEXT" -> trả lời tự nhiên.
        - Luôn format kết quả bằng Markdown: dùng **bold**, gạch đầu dòng, xuống dòng.
        """
        try:
            system_prompt = (
                "Bạn là trợ lý ảo cho sinh viên Đại học Bách Khoa Đà Nẵng.\n"
                "QUY TẮC:\n"
                "1) Nếu người dùng cung cấp 'context' (dữ liệu từ đồ thị), bạn **PHẢI** chỉ dùng CHÍNH XÁC những fact trong context. "
                "KHÔNG ĐƯỢC BÁO THÊM/HALLUCINATE.\n"
                "2) Trả lời bằng **Markdown**. Dùng **bold** cho tên chủ thể, dùng danh sách '-' cho liệt kê, xuống dòng thông thường.\n"
                "3) Nếu context = 'KHÔNG_CÓ_CONTEXT' hoặc rỗng thì trả lời thân thiện, tự nhiên, ngắn gọn.\n"
                "4) Nếu context không đủ để trả lời, hãy nói rõ 'Tôi chưa tìm thấy thông tin ...' và yêu cầu người dùng cung cấp thêm (ví dụ: tên chương trình đào tạo).\n"
            )

            user_prompt = f"Context:\n{context}\n\nUser question:\n{user_message}\n\nHÃY TRẢ LẠI THEO QUY TẮC Ở TRÊN (Markdown):"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.15,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[LỖI OpenAI (Context)]: {str(e)}"


    def generate_llm_only_response(self, question: str) -> str:
        """
        Khi không có context → KHÔNG cho phép LLM bịa ra.
        Trả lời an toàn, yêu cầu người dùng cung cấp thêm dữ liệu để truy vấn đồ thị.
        """
        return (
            "<p>Xin lỗi, mình chưa tìm thấy thông tin trong đồ thị kiến thức cho câu hỏi này.</p>"
            "<p>Bạn có thể cung cấp rõ hơn (ví dụ: tên <strong>chương trình đào tạo</strong>, "
            "<strong>ngoại ngữ/chứng chỉ</strong> mà bạn quan tâm) để mình hỗ trợ chính xác hơn nhé.</p>"
        )
