# neo4j_handler.py

from neo4j import GraphDatabase

class Neo4jHandler:
    def __init__(self, uri, user, password):
        #  Khởi tạo và kết nối với cơ sở dữ liệu Neo4j. 
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            print("Kết nối Neo4j thành công!")
        except Exception as e:
            print(f"Lỗi kết nối Neo4j: {e}")
            self.driver = None
            raise # Ném lại ngoại lệ để main.py có thể bắt và xử lý

    def close(self):
        
      #  Đóng kết nối cơ sở dữ liệu Neo4j một cách an toàn.
      
        if self.driver:
            self.driver.close()
            print("Đã đóng kết nối Neo4j.")

    def execute_query(self, query, params=None):
        
        # Thực thi một truy vấn Cypher trong Neo4j và trả về kết quả.
        # params: Các tham số tùy chọn cho truy vấn.
        
        if not self.driver:
            # Nếu driver là None, nghĩa là kết nối ban đầu thất bại
            raise ConnectionError("Không có kết nối Neo4j hoạt động.")
        
        with self.driver.session() as session:
            try:
                result = session.run(query, params)
                return [record for record in result]
            except Exception as e:
                print(f"Lỗi khi thực thi truy vấn Cypher: {e}")
                return []
# Giả sử hàm này được thêm vào lớp Neo4jHandler hoặc ChatbotLogic
def format_course_info_for_llm(self, course_name, course_info_by_program):
        """
        Định dạng dữ liệu học phần đã truy vấn từ Neo4j thành một chuỗi văn bản 
        có cấu trúc để Gemini dễ dàng xử lý.
        """
        formatted_text = f"Thông tin về học phần '{course_name}':\n\n"
        
        for program, details in course_info_by_program.items():
            loai_hoc_phan_str = ", ".join(details['loai_hoc_phan'])
            so_tin_chi_str = f", có {details['so_tin_chi']} tín chỉ" if details['so_tin_chi'] else ""
            
            # Kiểm tra xem có thông tin nào không
            if loai_hoc_phan_str or so_tin_chi_str:
                formatted_text += f"- Trong chương trình **{program}**, học phần này là {loai_hoc_phan_str}{so_tin_chi_str}.\n"
            else:
                # Trường hợp không có thông tin cụ thể nào
                formatted_text += f"- Trong chương trình **{program}**, không có thông tin chi tiết về loại học phần hay số tín chỉ.\n"
                
        return formatted_text