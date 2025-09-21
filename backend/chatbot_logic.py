import re
from backend.openai_handler import OpenAIHandler
from backend.neo4j_handle import Neo4jHandler


class ChatbotLogic:
    def __init__(self, neo4j_handler: Neo4jHandler, openai_handler: OpenAIHandler):
        self.neo4j_handler = neo4j_handler
        self.openai_handler = OpenAIHandler()
        self._load_program_names()
        self._load_semester_names()
        self._load_course_names()
        self._load_language_and_certificate_names()
    
    def _get_prerequisites_for_course(self, course_name: str) -> list:
        """
        Trả về danh sách các học phần tiên quyết (unique, sorted) cho một học phần.
        """
        if not course_name:
            return []

        query = f"""
        MATCH (end_node)
        WHERE end_node.ten_mon = '{course_name}'
        OPTIONAL MATCH (end_node)<-[:LA_HOC_PHAN_TIEN_QUYET_CUA]-(start_node)
        RETURN DISTINCT start_node.ten_mon AS prereq
        """
        try:
            results = self.neo4j_handler.execute_query(query)
        except Exception as e:
            print("Lỗi khi lấy tiên quyết:", e)
            return []

        prereqs = []
        for r in results:
            p = r.get('prereq') if isinstance(r, dict) else r['prereq'] if 'prereq' in r else None
            if p:
                prereqs.append(p)

        # Loại trùng giữ thứ tự -> dùng dict.fromkeys
        uniq = list(dict.fromkeys(prereqs))
        return uniq


    # Các phương thức _load_... giữ nguyên như phiên bản trước
    def _load_program_names(self):
        query = """
        MATCH (c:ChuongTrinhDaoTao)
        RETURN c.ten_chuong_trinh AS ten_chuong_trinh
        """
        results = self.neo4j_handler.execute_query(query)
        self.program_name_mapping = {}
        self.program_alias_mapping = {}

        if results:
            for record in results:
                full_name = (record.get("ten_chuong_trinh") or "").strip()
                if not full_name:
                    continue

                lower_full = full_name.lower()
                self.program_name_mapping[lower_full] = full_name  # tên gốc

                # ====== ALIAS THEO DANH SÁCH 41 CTĐT ======
                if "chế tạo máy" in lower_full:
                    self.program_alias_mapping["chế tạo máy"] = full_name
                if "cơ khí hàng không" in lower_full:
                    self.program_alias_mapping["hàng không"] = full_name
                if "cơ điện tử" in lower_full:
                    self.program_alias_mapping["cơ điện tử"] = full_name
                    self.program_alias_mapping["kt cơ điện tử"] = full_name
                if "công nghệ thông tin  nhật" in lower_full:
                    self.program_alias_mapping["cntt nhật"] = full_name
                if "công nghệ thông tin  khoa học dữ liệu" in lower_full or "trí tuệ nhân tạo" in lower_full:
                    self.program_alias_mapping["cntt khdl"] = full_name
                    self.program_alias_mapping["cntt ai"] = full_name
                    self.program_alias_mapping["cntt dữ liệu"] = full_name
                if "công nghệ thông tin đặc thù" in lower_full:
                    self.program_alias_mapping["cntt đặc thù"] = full_name
                if "kỹ thuật tàu thủy" in lower_full:
                    self.program_alias_mapping["tàu thủy"] = full_name
                if "ô tô" in lower_full:
                    self.program_alias_mapping["kỹ thuật ô tô"] = full_name
                    self.program_alias_mapping["ô tô"] = full_name
                if "hệ thống công nghiệp" in lower_full:
                    self.program_alias_mapping["kt công nghiệp"] = full_name
                if "cơ khí - cơ khí động lực" in lower_full:
                    self.program_alias_mapping["cơ khí động lực"] = full_name
                if "kỹ thuật nhiệt" in lower_full:
                    self.program_alias_mapping["kỹ thuật nhiệt"] = full_name
                if "năng lượng & môi trường" in lower_full:
                    self.program_alias_mapping["năng lượng môi trường"] = full_name
                if "điều khiển & tự động hóa" in lower_full:
                    self.program_alias_mapping["tự động hóa"] = full_name
                    self.program_alias_mapping["điều khiển"] = full_name
                if  "kỹ thuật điện" in lower_full:
                    self.program_alias_mapping["kỹ thuật điện"] = full_name
                    self.program_alias_mapping["kt điện"] = full_name
                if "máy tính" in lower_full:
                    self.program_alias_mapping["kt máy tính"] = full_name
                    self.program_alias_mapping["máy tính"] = full_name
                if "điện tử và viễn thông" in lower_full:
                    self.program_alias_mapping["điện tử viễn thông"] = full_name
                if "vi điện tử" in lower_full or "thiết kế vi mạch" in lower_full:
                    self.program_alias_mapping["vi điện tử"] = full_name
                    self.program_alias_mapping["thiết kế vi mạch"] = full_name
                if "hóa học" in lower_full:
                    self.program_alias_mapping["kt hóa học"] = full_name
                    self.program_alias_mapping["hóa học"] = full_name
                if "dầu khí" in lower_full and "công nghệ" not in lower_full:
                    self.program_alias_mapping["kt dầu khí"] = full_name
                if "công nghệ dầu khí" in lower_full:
                    self.program_alias_mapping["cn dầu khí"] = full_name
                if "thực phẩm" in lower_full:
                    self.program_alias_mapping["thực phẩm"] = full_name
                if "tiên tiến việt - mỹ" in lower_full:
                    self.program_alias_mapping["tiên tiến việt mỹ"] = full_name
                    self.program_alias_mapping["việt mỹ"] = full_name
                if "kỹ sư chất lượng cao việt - pháp" in lower_full:
                    self.program_alias_mapping["việt pháp"] = full_name
                    self.program_alias_mapping["chất lượng cao việt pháp"] = full_name
                if "tiên tiến - điện tử - viễn thông" in lower_full:
                    self.program_alias_mapping["tiên tiến điện tử viễn thông"] = full_name
                if "tiên tiến - hệ thống nhúng" in lower_full:
                    self.program_alias_mapping["tiên tiến nhúng"] = full_name
                    self.program_alias_mapping["nhúng iot"] = full_name
                if "sản xuất tự động_pfiev" in lower_full:
                    self.program_alias_mapping["pfiev sản xuất tự động"] = full_name
                if "tin học công nghiệp_pfiev" in lower_full:
                    self.program_alias_mapping["pfiev tin học"] = full_name
                if "công nghệ phần mềm_pfiev" in lower_full:
                    self.program_alias_mapping["pfiev phần mềm"] = full_name
                if "kiến trúc" in lower_full:
                    self.program_alias_mapping["kiến trúc"] = full_name
                if "quản lý tài nguyên" in lower_full:
                    self.program_alias_mapping["ql tài nguyên"] = full_name
                if "kỹ thuật môi trường" in lower_full:
                    self.program_alias_mapping["môi trường"] = full_name
                if "kinh tế xây dựng" in lower_full:
                    self.program_alias_mapping["kinh tế xd"] = full_name
                if "quản lý công nghiệp" in lower_full:
                    self.program_alias_mapping["qlcn"] = full_name
                if "công trình giao thông" in lower_full:
                    self.program_alias_mapping["xd giao thông"] = full_name
                if "mô hình thông tin" in lower_full or "bim" in lower_full:
                    self.program_alias_mapping["bim"] = full_name
                if "vật liệu xây dựng" in lower_full:
                    self.program_alias_mapping["vlxd"] = full_name
                if "cơ sở hạ tầng" in lower_full:
                    self.program_alias_mapping["cshtr"] = full_name
                if "công trình thủy" in lower_full:
                    self.program_alias_mapping["xd thủy"] = full_name
                if "tin học xây dựng" in lower_full:
                    self.program_alias_mapping["tin học xd"] = full_name
                if "đô thị thông minh" in lower_full:
                    self.program_alias_mapping["xd đô thị thông minh"] = full_name
                if "xây dựng dân dụng" in lower_full:
                    self.program_alias_mapping["xd dân dụng"] = full_name




    def _load_semester_names(self):
        query = """
        MATCH (hk:HocKy)
        RETURN hk.ten_hoc_ky AS ten_hoc_ky
        """
        results = self.neo4j_handler.execute_query(query)
        self.semester_name_mapping = {}
        if results:
            for record in results:
                standard_name = record['ten_hoc_ky']
                self.semester_name_mapping[standard_name.lower()] = standard_name
                try:
                    semester_number = int(standard_name.split()[-1])
                    self.semester_name_mapping[f"học kỳ {semester_number}"] = standard_name
                except ValueError:
                    pass

    def _load_course_names(self):
        query = """
        MATCH (hp)
        WHERE hp:HocPhanDaiCuong OR hp:HocPhanTienQuyet OR hp:HocPhanSongHanh OR hp:HocPhanKeTiep OR hp:HocPhanTựDo
        RETURN hp.ten_mon AS ten_mon
        """
        results = self.neo4j_handler.execute_query(query)
        self.course_name_mapping = {}
        if results:
            for record in results:
                standard_name = record['ten_mon']
                self.course_name_mapping[standard_name.lower()] = standard_name

    def _load_language_and_certificate_names(self):
        self.language_and_certificate_mapping = {}
        
        # Tiếng Anh
        query_en = """MATCH (a:TiengAnh) RETURN a AS properties"""
        results_en = self.neo4j_handler.execute_query(query_en)
        if results_en:
            for record_wrapper in results_en:
                record = record_wrapper['properties']
                self.language_and_certificate_mapping["tiếng anh"] = "TiengAnh"
                if 'bac' in record and record['bac']: 
                    self.language_and_certificate_mapping[f"bậc {record['bac'].lower()}"] = "TiengAnh"
                if 'TOEIC' in record and record['TOEIC']: 
                    self.language_and_certificate_mapping[f"toeic"] = "TOEIC"
                    self.language_and_certificate_mapping[f"toeic {record['TOEIC']}".lower()] = "TOEIC_SCORE"
                if 'IELTS' in record and record['IELTS']: 
                    self.language_and_certificate_mapping[f"ielts"] = "IELTS"
                    self.language_and_certificate_mapping[f"ielts {record['IELTS']}".lower()] = "IELTS_SCORE"
                if 'TOEFL_iBT' in record and record['TOEFL_iBT']: 
                    self.language_and_certificate_mapping[f"toefl ibt"] = "TOEFL_iBT"
                    self.language_and_certificate_mapping[f"toefl ibt {record['TOEFL_iBT']}".lower()] = "TOEFL_iBT_SCORE"
                if 'chung_chi' in record and record['chung_chi']: 
                    self.language_and_certificate_mapping[record['chung_chi'].lower()] = "TiengAnh_ChungChi"
                if 'TOEFL_ITP' in record and record['TOEFL_ITP']: 
                    self.language_and_certificate_mapping[f"toefl itp"] = "TOEFL_ITP"
                    self.language_and_certificate_mapping[f"toefl itp {record['TOEFL_ITP']}".lower()] = "TOEFL_ITP_SCORE"
                if 'Cambridge' in record and record['Cambridge']: 
                    self.language_and_certificate_mapping[f"cambridge"] = "Cambridge"
                    self.language_and_certificate_mapping[f"cambridge {record['Cambridge']}".lower()] = "Cambridge_SCORE"
        
        self.language_and_certificate_mapping["toeic"] = "TOEIC"
        self.language_and_certificate_mapping["ielts"] = "IELTS"
        self.language_and_certificate_mapping["toefl ibt"] = "TOEFL_iBT"
        self.language_and_certificate_mapping["toefl itp"] = "TOEFL_ITP"
        self.language_and_certificate_mapping["cambridge"] = "Cambridge"
        
        # Tiếng Nhật
        query_jp = """MATCH (nhat:TiengNhat) RETURN nhat AS properties"""
        results_jp = self.neo4j_handler.execute_query(query_jp)
        if results_jp:
            for record_wrapper in results_jp:
                record = record_wrapper['properties']
                self.language_and_certificate_mapping["tiếng nhật"] = "TiengNhat"
                if 'bac' in record and record['bac']: self.language_and_certificate_mapping[f"bậc {record['bac'].lower()}"] = "TiengNhat"
                if 'chung_chi' in record and record['chung_chi']: self.language_and_certificate_mapping[record['chung_chi'].lower()] = "TiengNhat_ChungChi"
                if 'JLPT' in record and record['JLPT']: 
                    self.language_and_certificate_mapping[f"jlpt"] = "JLPT"
                    self.language_and_certificate_mapping[f"jlpt {record['JLPT']}".lower()] = "JLPT_SCORE"
                if 'TOP_J' in record and record['TOP_J']: 
                    self.language_and_certificate_mapping[f"top j"] = "TOP_J"
                    self.language_and_certificate_mapping[f"top j {record['TOP_J']}".lower()] = "TOP_J_SCORE"
                if 'NAT_TEST' in record and record['NAT_TEST']: 
                    self.language_and_certificate_mapping[f"nat test"] = "NAT_TEST"
                    self.language_and_certificate_mapping[f"nat test {record['NAT_TEST']}".lower()] = "NAT_TEST_SCORE"
        self.language_and_certificate_mapping["jlpt"] = "JLPT"
        self.language_and_certificate_mapping["top j"] = "TOP_J"
        self.language_and_certificate_mapping["nat test"] = "NAT_TEST"

        # Tiếng Trung
        query_cn = """MATCH (t:TiengTrung) RETURN t AS properties"""
        results_cn = self.neo4j_handler.execute_query(query_cn)
        if results_cn:
            for record_wrapper in results_cn:
                record = record_wrapper['properties']
                self.language_and_certificate_mapping["tiếng trung"] = "TiengTrung"
                if 'bac' in record and record['bac']: self.language_and_certificate_mapping[f"bậc {record['bac'].lower()}"] = "TiengTrung"
                if 'chung_chi' in record and record['chung_chi']: self.language_and_certificate_mapping[record['chung_chi'].lower()] = "TiengTrung_ChungChi"
                if 'HSK' in record and record['HSK']: 
                    self.language_and_certificate_mapping[f"hsk"] = "HSK"
                    self.language_and_certificate_mapping[f"hsk {record['HSK']}".lower()] = "HSK_SCORE"
                if 'TOCFL' in record and record['TOCFL']: 
                    self.language_and_certificate_mapping[f"tocfl"] = "TOCFL"
                    self.language_and_certificate_mapping[f"tocfl {record['TOCFL']}".lower()] = "TOCFL_SCORE"
        self.language_and_certificate_mapping["hsk"] = "HSK"
        self.language_and_certificate_mapping["tocfl"] = "TOCFL"

        # Tiếng Pháp
        query_fr = """MATCH (p:TiengPhap) RETURN p AS properties"""
        results_fr = self.neo4j_handler.execute_query(query_fr)
        if results_fr:
            for record_wrapper in results_fr:
                record = record_wrapper['properties']
                self.language_and_certificate_mapping["tiếng pháp"] = "TiengPhap"
                if 'bac' in record and record['bac']: self.language_and_certificate_mapping[f"bậc {record['bac'].lower()}"] = "TiengPhap"
                if 'chung_chi' in record and record['chung_chi']: self.language_and_certificate_mapping[record['chung_chi'].lower()] = "TiengPhap_ChungChi"
                if 'DELF_va_DALF' in record and record['DELF_va_DALF']: 
                    self.language_and_certificate_mapping[f"delf và dalf"] = "DELF_va_DALF"
                    self.language_and_certificate_mapping[f"delf dal f {record['DELF_va_DALF']}".lower()] = "DELF_va_DALF_SCORE"
                if 'TCF' in record and record['TCF']: 
                    self.language_and_certificate_mapping[f"tcf"] = "TCF"
                    self.language_and_certificate_mapping[f"tcf {record['TCF']}".lower()] = "TCF_SCORE"
        self.language_and_certificate_mapping["delf và dalf"] = "DELF_va_DALF"
        self.language_and_certificate_mapping["tcf"] = "TCF"

        self.language_and_certificate_mapping["khung năng lực ngoại ngữ việt nam"] = "KhungNangLucNgoaiNguVietNam"
        self.language_and_certificate_mapping["chuẩn năng lực ngoại ngữ"] = "KhungNangLucNgoaiNguVietNam"
        self.language_and_certificate_mapping["khung năng lực ngoại ngữ"] = "KhungNangLucNgoaiNguVietNam"

    def _extract_target_course_name(self, lower_question: str) -> str | None:
        """
        Tìm tên học phần mục tiêu (target) trong câu hỏi.
        Ví dụ: "... liên quan như thế nào đến môn Công nghệ phần mềm?"
        """
        # Tìm cụm "môn", "học phần" + tên
        triggers = ["đến môn", "đến học phần", "với môn", "với học phần"]
        for t in triggers:
            if t in lower_question:
                after = lower_question.split(t, 1)[1].strip(" ?.")
                return after.title()  # viết hoa chuẩn
        return None

    def _extract_program_name(self, lower_question: str) -> str | None:
        cleaned_question = lower_question.strip().lower()

        # ==== ƯU TIÊN: match "điện tử và viễn thông" trước ====
        if "kỹ thuật điện tử và viễn thông" in cleaned_question:
            return self.program_name_mapping.get("kỹ thuật điện tử và viễn thông", "Kỹ thuật điện tử và viễn thông")

        # ==== SAU ĐÓ mới check "kỹ thuật điện" ====
        if "kỹ thuật điện" in cleaned_question:
            return self.program_name_mapping.get("kỹ thuật điện", "Kỹ thuật Điện")

        # 1. Alias
        for alias, real_name in self.program_alias_mapping.items():
            if alias in cleaned_question:
                return real_name

        # 2. Full match tuyệt đối
        for keyword_variant, standard_name in self.program_name_mapping.items():
            if cleaned_question == keyword_variant:
                return standard_name

        # 3. Match cụm từ chính xác còn lại
        for keyword_variant, standard_name in self.program_name_mapping.items():
            if keyword_variant in cleaned_question:
                return standard_name

        # 4. Các dạng đặc biệt
        if "của chương trình" in cleaned_question:
            potential_name = cleaned_question.split("của chương trình", 1)[1].strip(" ?.")
            return self.program_name_mapping.get(potential_name.lower(), None)

        if "ngành" in cleaned_question:
            remaining = cleaned_question.split("ngành", 1)[1]
            stop_words = ["là", "gì", "?", "là gì"]
            parts = []
            for token in remaining.split():
                if token in stop_words:
                    break
                parts.append(token)
            potential_name = " ".join(parts).strip(" ?.")
            if potential_name:
                return self.program_name_mapping.get(potential_name.lower(), None)

        if "điều kiện tốt nghiệp" in cleaned_question:
            potential_name = cleaned_question.split("điều kiện tốt nghiệp", 1)[1].strip(" ?.")
            return self.program_name_mapping.get(potential_name.lower(), None)

        if "ra trường" in cleaned_question:
            for keyword_variant, standard_name in self.program_name_mapping.items():
                if keyword_variant in cleaned_question and cleaned_question.find(keyword_variant) < cleaned_question.find("ra trường"):
                    return standard_name

        return None

    def _extract_semester_name(self, lower_question: str) -> str | None:
        for keyword_variant, standard_name in self.semester_name_mapping.items():
            if keyword_variant in lower_question:
                return standard_name
        
        match = re.search(r'học kỳ\s*(\d+)', lower_question)
        if match:
            semester_number = match.group(1)
            return f"Học kỳ {semester_number}"
        
        return None

    def _extract_course_name(self, lower_question: str) -> str | None: 
        for keyword_variant, standard_name in self.course_name_mapping.items():
            if re.search(r'\b' + re.escape(keyword_variant) + r'\b', lower_question):
                return standard_name
        
        patterns = [
            r"của môn (.+)", r"của học phần (.+)", r"môn (.+) có", r"học phần (.+) có",
            r"môn (.+)\?", r"học phần (.+)\?", r"học môn (.+) trước", 
            r"môn (.+) trước", r"về môn (.+)", r"học phần (.+) với", 
            r"học môn (.+) với", r"học phần (.+) là học phần song hành", 
            r"môn (.+) là học phần song hành", 
        ]
        for pattern in patterns:
            match = re.search(pattern, lower_question)
            if match:
                potential_name = match.group(1).strip()
                for mapped_lower_name, standard_name in self.course_name_mapping.items():
                    if potential_name.lower() == mapped_lower_name:
                        return standard_name
        
        return None

    def _extract_multiple_course_names(self, lower_question: str) -> tuple[str | None, str | None]:
        found_courses = []
        
        for keyword_variant, standard_name in self.course_name_mapping.items():
            if re.search(r'\b' + re.escape(keyword_variant) + r'\b', lower_question):
                found_courses.append(standard_name)
        
        unique_found_courses = []
        for course in found_courses:
            if course not in unique_found_courses:
                unique_found_courses.append(course)

        if len(unique_found_courses) >= 2:
            return unique_found_courses[0], unique_found_courses[1]
        elif len(unique_found_courses) == 1:
            return unique_found_courses[0], None
        return None, None

    def _extract_language_or_certificate(self, lower_question: str) -> tuple[str | None, str | None, str | None, str | None]:
        found_language_label = None
        found_certificate_name = None
        found_level_or_score = None
        found_bac = None 

        # Ưu tiên tìm kiếm tên ngôn ngữ trước
        if "tiếng anh" in lower_question:
            found_language_label = "TiengAnh"
        elif "tiếng nhật" in lower_question:
            found_language_label = "TiengNhat"
        elif "tiếng trung" in lower_question:
            found_language_label = "TiengTrung"
        elif "tiếng pháp" in lower_question:
            found_language_label = "TiengPhap"
        elif "khung năng lực ngoại ngữ việt nam" in lower_question or \
             "chuẩn năng lực ngoại ngữ" in lower_question or \
             "khung năng lực ngoại ngữ" in lower_question:
            found_language_label = "KhungNangLucNgoaiNguVietNam"

        # Trích xuất bậc: Đảm bảo trích xuất cả "bậc X"
        bac_match = re.search(r'bậc\s*(\d+)', lower_question)
        if bac_match:
            found_bac = f"bậc {bac_match.group(1)}" # Lưu trữ dưới dạng "bậc 1", "bậc 2", v.v.
            found_level_or_score = found_bac # Cập nhật found_level_or_score nếu có bậc

        score_patterns = {
            "toeic": r'toeic\s*(\d+)',
            "ielts": r'ielts\s*(\d+(\.\d+)?)',
            "toefl ibt": r'toefl ibt\s*(\d+)',
            "toefl itp": r'toefl itp\s*(\d+)',
            "jlpt": r'jlpt\s*(N\d)',
            "hsk": r'hsk\s*(\d+)',
            "cambridge": r'cambridge\s*(\d+)' 
        }
        for cert_kw, pattern in score_patterns.items():
            score_match = re.search(pattern, lower_question)
            if score_match:
                found_certificate_name = cert_kw.upper().replace(" ", "_")
                found_level_or_score = score_match.group(1)
                break

        # Nếu chưa tìm thấy ngôn ngữ nhưng có chứng chỉ thì gán ngôn ngữ tương ứng
        if not found_language_label and found_certificate_name:
            if found_certificate_name in ["TOEIC", "IELTS", "TOEFL_iBT", "TOEFL_ITP", "CAMBRIDGE"]: 
                found_language_label = "TiengAnh"
            elif found_certificate_name in ["JLPT", "TOP_J", "NAT_TEST"]:
                found_language_label = "TiengNhat"
            elif found_certificate_name in ["HSK", "TOCFL"]:
                found_language_label = "TiengTrung"
            elif found_certificate_name in ["DELF_va_DALF", "TCF"]:
                found_language_label = "TiengPhap"

        return found_language_label, found_certificate_name, found_level_or_score, found_bac


    def _get_prerequisites_for_course(self, course_name: str) -> list[str]:
        query = f"""
        MATCH (end_node)
        WHERE end_node.ten_mon = '{course_name}' AND 
              (end_node:HocPhanDaiCuong OR end_node:HocPhanTienQuyet OR end_node:HocPhanSongHanh OR end_node:HocPhanKeTiep OR end_node:HocPhanTựDo)
        OPTIONAL MATCH (end_node)<-[r:LA_HOC_PHAN_TIEN_QUYET_CUA]-(start_node)
        RETURN start_node.ten_mon AS prerequisite_course
        """
        results = self.neo4j_handler.execute_query(query)
        prereqs = []
        if results:
            for res in results:
                if res['prerequisite_course']:
                    prereqs.append(res['prerequisite_course'])
        return prereqs
    
    def format_course_info_for_llm(self, course_name: str, course_info: dict) -> str:
        """
        Formats the course information from Neo4j into a human-readable string.
        """
        response_text = f"**Thông tin về học phần '{course_name}':**\n"
        
        # Lấy thông tin chung (labels, tín chỉ)
        if course_info:
            first_program_info = next(iter(course_info.values()))
            
            # Chuyển đổi nhãn tiếng Anh thành tiếng Việt
            labels_map = {
                "HocPhanDaiCuong": "Học phần đại cương",
                "HocPhanTienQuyet": "Học phần tiên quyết",
                "HocPhanSongHanh": "Học phần song hành",
                "HocPhanKeTiep": "Học phần kế tiếp",
                "HocPhanTựDo": "Học phần tự do"
            }
            loai_hoc_phan_labels = [labels_map.get(label, label) for label in first_program_info.get('NhomNode', [])]
            loai_hoc_phan_str = ", ".join(loai_hoc_phan_labels)
            
            response_text += f"- **Loại học phần:** {loai_hoc_phan_str}\n"
            response_text += f"- **Số tín chỉ:** {first_program_info.get('SoTinChi', 'Không có thông tin')}\n"

            # Thêm thông tin liên kết với các chương trình
            for program_name, info in course_info.items():
                if program_name:
                    response_text += f"\n- **Là học phần của chương trình:** {program_name}\n"
                    # Bạn có thể thêm các thông tin khác ở đây nếu cần, ví dụ:
                    # - Mối quan hệ của học phần với chương trình
            
            return response_text
        else:
            return f"Không tìm thấy thông tin cụ thể về học phần '{course_name}' trong đồ thị tri thức."

    def query_neo4j_for_context(self, user_question: str) -> str:
        context = []
        lower_question = user_question.lower()

        found_target_course_name = self._extract_target_course_name(lower_question)
        found_program_name = self._extract_program_name(lower_question)
        found_semester_name = self._extract_semester_name(lower_question)
        found_course_name = self._extract_course_name(lower_question)
        found_course1, found_course2 = self._extract_multiple_course_names(lower_question)
        found_language_label, found_certificate_name, found_level_or_score, found_bac = self._extract_language_or_certificate(lower_question) 

        valid_course_labels = [
            "HocPhanDaiCuong",
            "HocPhanTienQuyet",
            "HocPhanSongHanh",
            "HocPhanKeTiep",
            "HocPhanTựDo" 
        ]
        
        # --- Xử lý các câu hỏi liên quan đến Ngoại ngữ và Chứng chỉ (Ưu tiên cao hơn) ---
        # TRƯỜNG HỢP 17: Trong CTĐT A, học phần B liên quan tới những đồ án nào, tiên quyết hoặc song hành nào, 
        # và các học phần đó liên quan thế nào tới học phần C.
        # ================= TRƯỜNG HỢP 17 =================
        # Trong chương trình đào tạo A, học phần B liên quan đến đồ án,
        # tiên quyết, song hành, và các học phần đó liên quan thế nào đến C.
        if (
            found_program_name
            and found_course_name
            and (found_target_course_name := self._extract_target_course_name(lower_question))
            and any(
                kw in lower_question
                for kw in [
                    "liên quan đến những đồ án",
                    "liên quan đến đồ án",
                    "tiên quyết hoặc song hành",
                    "liên quan như thế nào đến",
                ]
            )
        ):
            query = f"""
            MATCH (ct:ChuongTrinhDaoTao {{ten_chuong_trinh: '{found_program_name}'}})
            MATCH (hp)-[:THUOC]->(ct)
            WHERE hp.ten_mon = '{found_course_name}'

            // --- tất cả các PBL trong CTĐT
            OPTIONAL MATCH (pbl_in_prog)-[:THUOC]->(ct)
            WHERE pbl_in_prog.ten_mon STARTS WITH 'PBL'

            // --- PBL liên kết trực tiếp với hp
            OPTIONAL MATCH (pbl_direct)-[:THUOC]->(ct)
            WHERE pbl_direct.ten_mon STARTS WITH 'PBL'
            AND (
                (pbl_direct)-[:LA_HOC_PHAN_SONG_HANH_VOI]-(hp)
                OR (pbl_direct)-[:LA_HOC_PHAN_TIEN_QUYET_CUA]->(hp)
                OR (hp)-[:LA_HOC_PHAN_TIEN_QUYET_CUA]->(pbl_direct)
            )

            // --- tiên quyết của hp trong CTĐT
            OPTIONAL MATCH (prereq)-[:THUOC]->(ct)
            WHERE (prereq)-[:LA_HOC_PHAN_TIEN_QUYET_CUA]->(hp)

            // --- song hành của hp trong CTĐT
            OPTIONAL MATCH (co)-[:THUOC]->(ct)
            WHERE (co)-[:LA_HOC_PHAN_SONG_HANH_VOI]-(hp)

            // --- quan hệ với môn target
            OPTIONAL MATCH (target {{ten_mon: '{found_target_course_name}'}})
            OPTIONAL MATCH (pbl_direct)-[r1]->(target)
            OPTIONAL MATCH (prereq)-[r2]->(target)
            OPTIONAL MATCH (co)-[r3]->(target)

            RETURN
            hp.ten_mon AS HocPhan,
            ct.ten_chuong_trinh AS ChuongTrinh,
            collect(DISTINCT pbl_in_prog.ten_mon) AS DoAn,
            collect(DISTINCT pbl_direct.ten_mon) AS DoAn_LienQuan_TrucTiep,
            collect(DISTINCT prereq.ten_mon) AS HocPhan_TienQuyet,
            collect(DISTINCT co.ten_mon) AS HocPhan_SongHanh,
            collect(DISTINCT type(r1)) AS QuanHe_DoAn_Voi_Target,
            collect(DISTINCT type(r2)) AS QuanHe_TienQuyet_Voi_Target,
            collect(DISTINCT type(r3)) AS QuanHe_SongHanh_Voi_Target
            """

            results = self.neo4j_handler.execute_query(query)

            if results:
                record = results[0]
                context.append(
                    f"Trong chương trình **{record['ChuongTrinh']}**, học phần **{record['HocPhan']}** "
                    f"có liên quan đến các đồ án: {', '.join([x for x in record['DoAn'] if x]) or 'Không có'}.\n\n"
                    f"- Đồ án liên quan trực tiếp: {', '.join([x for x in record['DoAn_LienQuan_TrucTiep'] if x]) or 'Không có'}\n"
                    f"- Học phần tiên quyết: {', '.join([x for x in record['HocPhan_TienQuyet'] if x]) or 'Không có'}\n"
                    f"- Học phần song hành: {', '.join([x for x in record['HocPhan_SongHanh'] if x]) or 'Không có'}\n\n"
                    f"Liên quan đến học phần **{found_target_course_name}** như sau:\n"
                    f"- Quan hệ Đồ án → {found_target_course_name}: {', '.join([x for x in record['QuanHe_DoAn_Voi_Target'] if x]) or 'Không có'}\n"
                    f"- Quan hệ Tiên quyết → {found_target_course_name}: {', '.join([x for x in record['QuanHe_TienQuyet_Voi_Target'] if x]) or 'Không có'}\n"
                    f"- Quan hệ Song hành → {found_target_course_name}: {', '.join([x for x in record['QuanHe_SongHanh_Voi_Target'] if x]) or 'Không có'}"
                )
                return "\n".join(context)
            else:
                return (
                    f"Không tìm thấy thông tin về học phần **{found_course_name}** trong chương trình "
                    f"**{found_program_name}** và mối liên hệ với **{found_target_course_name}**."
                )
        # TRƯỜNG HỢP 17: Nếu trượt môn B thì không được học những môn nào trong CTĐT A
        if found_course_name and found_program_name and any(
            kw in lower_question for kw in ["nếu tôi trượt", "nếu rớt", "không qua môn"]
        ):
            query = f"""
            MATCH (ct:ChuongTrinhDaoTao {{ten_chuong_trinh: '{found_program_name}'}})
            MATCH (hp {{ten_mon: '{found_course_name}'}})-[:THUOC]->(ct)

            MATCH (blocked)-[:THUOC]->(ct)
            WHERE (blocked)<-[:LA_HOC_PHAN_TIEN_QUYET_CUA*]-(hp)

            OPTIONAL MATCH (related)-[:THUOC]->(ct)
            WHERE (blocked)-[:LA_HOC_PHAN_TIEN_QUYET_CUA*]->(related)

            RETURN DISTINCT
                ct.ten_chuong_trinh AS ChuongTrinhDaoTao,
                collect(DISTINCT blocked.ten_mon) AS HocPhan_Bi_Chan,
                collect(DISTINCT related.ten_mon) AS AnhHuong_Den_HocPhan
            """

            results = self.neo4j_handler.execute_query(query)
            if results:
                lines = [
                    f"Nếu bạn **trượt môn {found_course_name}** trong chương trình **{found_program_name}**, thì:"
                ]
                for r in results:
                    bi_chan = r.get("HocPhan_Bi_Chan") or []
                    anh_huong = r.get("AnhHuong_Den_HocPhan") or []

                    if bi_chan:
                        lines.append(f"- Bạn **không thể học** các học phần: {', '.join(bi_chan)}")
                    if anh_huong:
                        lines.append(f"- Kéo theo đó bạn **không thể học thêm** các học phần: {', '.join(anh_huong)}")

                context.append("\n".join(lines))
            else:
                context.append(
                    f"Không tìm thấy thông tin về ảnh hưởng khi trượt môn **{found_course_name}** trong chương trình **{found_program_name}**."
                )

            return "\n".join(context)


        # TRƯỜNG HỢP 1: Chuẩn năng lực ngoại ngữ là gì? / Khung năng lực ngoại ngữ là gì?
        if "chuẩn năng lực ngoại ngữ là gì" in lower_question or \
        "khung năng lực ngoại ngữ việt nam là gì" in lower_question or \
        "khung năng lực ngoại ngữ là gì" in lower_question:
            query = """
            MATCH (kh:KhungNangLucNgoaiNguVietNam)
            RETURN kh.khai_niem AS khai_niem
            LIMIT 1
            """
            results = self.neo4j_handler.execute_query(query)
            if results and results[0]['khai_niem']:
                context.append(
                    f"**Chuẩn năng lực ngoại ngữ quốc gia (Khung năng lực ngoại ngữ 6 bậc dùng cho Việt Nam)** là:\n{results[0]['khai_niem']}"
                )
            else:
                context.append("Không tìm thấy thông tin về chuẩn năng lực ngoại ngữ quốc gia.")
            return "\n".join(context)

        # TRƯỜNG HỢP 2: Khung năng lực ngoại ngữ X gồm các bậc nào? / Khung năng lực ngoại ngữ X bậc Y là gì?
        if found_language_label and found_language_label != "KhungNangLucNgoaiNguVietNam" and \
           (any(kw in lower_question for kw in ["gồm các bậc nào","gồm những bậc nào" ,"có những bậc nào", "bao nhiêu bậc", "chuẩn năng lực tiếng"]) or found_bac): 
            
            # Đảm bảo lang_display_name được định nghĩa trước khi sử dụng
            lang_display_name = {
                "TiengAnh": "tiếng Anh", "TiengNhat": "tiếng Nhật",
                "TiengTrung": "tiếng Trung", "TiengPhap": "tiếng Pháp"
            }.get(found_language_label, found_language_label)

            query_parts = [f"MATCH (lang:{found_language_label})"]
            if found_bac: 
                # Sử dụng found_bac trực tiếp vì nó đã ở định dạng "bậc X"
                query_parts.append(f"WHERE lang.bac = '{found_bac}'")
            
            return_parts = ["lang.bac AS bac"]

            if found_language_label == "TiengAnh":
                return_parts.extend([
                    "lang.TOEIC AS TOEIC", 
                    "lang.IELTS AS IELTS", 
                    "lang.TOEFL_iBT AS TOEFL_iBT", 
                    "lang.chung_chi AS chung_chi", 
                    "lang.TOEFL_ITP AS TOEFL_ITP", 
                    "lang.Cambridge AS Cambridge"
                ])
            elif found_language_label == "TiengNhat":
                return_parts.extend([
                    "lang.chung_chi AS chung_chi", 
                    "lang.JLPT AS JLPT", 
                    "lang.TOP_J AS TOP_J", 
                    "lang.NAT_TEST AS NAT_TEST"
                ])
            elif found_language_label == "TiengTrung":
                return_parts.extend([
                    "lang.chung_chi AS chung_chi", 
                    "lang.HSK AS HSK", 
                    "lang.TOCFL AS TOCFL"
                ])
            elif found_language_label == "TiengPhap":
                return_parts.extend([
                    "lang.chung_chi AS chung_chi", 
                    "lang.DELF_va_DALF AS DELF_va_DALF", 
                    "lang.TCF AS TCF"
                ])
            
            # Thay đổi ORDER BY để sắp xếp theo số của bậc, không phải chuỗi
            query_str = f"{' '.join(query_parts)} RETURN {', '.join(return_parts)} ORDER BY toInteger(substring(lang.bac, 4))" 
            
            results = self.neo4j_handler.execute_query(query_str)

            if results:
                response_text = f"**Khung năng lực {lang_display_name}** gồm các bậc và chứng chỉ tương ứng:\n"
                for res in results: 
                    
                    bac = res.get('bac')
                    if not bac: 
                        continue

                    # Thay đổi cách hiển thị để đảm bảo 'Bậc' không bị lặp lại nếu dữ liệu đã là "bậc X"
                    display_bac = bac.capitalize() # Ví dụ: "bậc 1" -> "Bậc 1"
                    response_text += f"- **{display_bac}:** "
                    certs = []
                    
                    if found_language_label == "TiengAnh":
                        if res.get('TOEIC'): certs.append(f"TOEIC: {res['TOEIC']}")
                        if res.get('IELTS'): certs.append(f"IELTS: {res['IELTS']}")
                        if res.get('TOEFL_iBT'): certs.append(f"TOEFL iBT: {res['TOEFL_iBT']}")
                        if res.get('TOEFL_ITP'): certs.append(f"TOEFL ITP: {res['TOEFL_ITP']}")
                        if res.get('Cambridge'): certs.append(f"Cambridge: {res['Cambridge']}")
                    elif found_language_label == "TiengNhat":
                        if res.get('JLPT'): certs.append(f"JLPT: {res['JLPT']}")
                        if res.get('TOP_J'): certs.append(f"TOP J: {res['TOP_J']}")
                        if res.get('NAT_TEST'): certs.append(f"NAT TEST: {res['NAT_TEST']}")
                    elif found_language_label == "TiengTrung":
                        if res.get('HSK'): certs.append(f"HSK: {res['HSK']}")
                        if res.get('TOCFL'): certs.append(f"TOCFL: {res['TOCFL']}")
                    elif found_language_label == "TiengPhap":
                        if res.get('DELF_va_DALF'): certs.append(f"DELF/DALF: {res['DELF_va_DALF']}")
                        if res.get('TCF'): certs.append(f"TCF: {res['TCF']}")
                    
                    chung_chi_val = res.get('chung_chi')
                    if chung_chi_val:
                        is_duplicate = False
                        for c_added in certs:
                            if chung_chi_val in c_added: 
                                is_duplicate = True
                                break
                        if not is_duplicate:
                            certs.append(f"Chứng chỉ khác: {chung_chi_val}")
                    
                    if certs:
                        response_text += ", ".join(certs) + ".\n"
                    else:
                        response_text += "Không có thông tin chứng chỉ cụ thể.\n"
                context.append(response_text)
            else:
                if found_bac: # found_bac lúc này đã là "bậc X"
                    context.append(f"Không tìm thấy thông tin khung năng lực cho {lang_display_name} {found_bac}.")
                else:
                    context.append(f"Không tìm thấy thông tin khung năng lực cho {lang_display_name}.")
            return "\n".join(context)

        # TRƯỜNG HỢP 3: Khung năng lực ngoại ngữ gồm các ngoại ngữ nào?
        if any(kw in lower_question for kw in ["khung năng lực ngoại ngữ gồm các ngoại ngữ nào", "có những ngoại ngữ nào", "bao nhiêu ngoại ngữ"]):
            query = """
            MATCH (Kh:KhungNangLucNgoaiNguVietNam)-[:BAO_GOM]->(t)
            WHERE t:TiengAnh OR t:TiengNhat OR t:TiengTrung OR t:TiengPhap
            RETURN DISTINCT labels(t) AS language_labels
            """
            results = self.neo4j_handler.execute_query(query)
            if results:
                languages = []
                for res in results:
                    if res['language_labels'] and len(res['language_labels']) > 0:
                        label = res['language_labels'][0]
                        display_name = label.replace('Tieng', 'tiếng ')
                        if display_name == "tiếngAnh": display_name = "tiếng Anh"
                        if display_name == "tiếngNhat": display_name = "tiếng Nhật"
                        if display_name == "tiếngTrung": display_name = "tiếng Trung"
                        if display_name == "tiếngPhap": display_name = "tiếng Pháp"
                        languages.append(display_name)
                
                if languages:
                    context.append(f"Khung năng lực ngoại ngữ quốc gia hiện bao gồm các ngoại ngữ: {', '.join(sorted(languages))}.")
                else:
                    context.append("Không tìm thấy thông tin về các ngoại ngữ được liên kết trực tiếp với Khung năng lực trong đồ thị.")
            else:
                context.append("Không tìm thấy thông tin về các ngoại ngữ trong khung năng lực.")
            return "\n".join(context)
            
        # TRƯỜNG HỢP 4: Chuẩn đầu ra chứng chỉ/điểm số để ra trường
        if (found_program_name or found_certificate_name or found_level_or_score) and \
        any(kw in lower_question for kw in ["bao nhiêu thì mới ra trường",
            "bao nhiêu thì tốt nghiệp",
            "cần bao nhiêu điểm để tốt nghiệp",
            "cần bao nhiêu điểm thì ra trường",
            "chuẩn đầu ra",
            "đầu ra là bao nhiêu",
            "đầu ra bao nhiêu",
            "điểm đầu ra"]):
            cert_type = None
            if found_certificate_name:
                cert_type = found_certificate_name
            elif "toeic" in lower_question: cert_type = "TOEIC"
            elif "ielts" in lower_question: cert_type = "IELTS"
            elif "toefl ibt" in lower_question: cert_type = "TOEFL_iBT"
            elif "jlpt" in lower_question: cert_type = "JLPT"
            elif "hsk" in lower_question: cert_type = "HSK"
            elif "tcf" in lower_question: cert_type = "TCF"
            elif "delf" in lower_question or "dalf" in lower_question: cert_type = "DELF_va_DALF"
            elif "top j" in lower_question: cert_type = "TOP_J"
            elif "nat test" in lower_question: cert_type = "NAT_TEST"
            elif "cambridge" in lower_question: cert_type = "Cambridge"

            # 👉 Có chứng chỉ nhưng chưa biết chương trình đào tạo
            if cert_type and not found_program_name:
                program_query = """MATCH (c:ChuongTrinhDaoTao) RETURN c.ten_chuong_trinh AS ten_chuong_trinh"""
                all_programs = self.neo4j_handler.execute_query(program_query)
                program_names_list = [p['ten_chuong_trinh'] for p in all_programs]

                if program_names_list:
                    context.append(
                        f"Tôi đã nhận diện bạn đang hỏi về chuẩn đầu ra **{cert_type.upper()}**, "
                        f"nhưng chưa rõ bạn học chương trình đào tạo nào.<br><br>"
                        f"👉 Bạn vui lòng cho tôi biết rõ hơn: bạn đang theo học chương trình nào trong các chương trình sau?<br>"
                        f"{', '.join(program_names_list)}"
                    )
                else:
                    context.append(
                        f"Tôi nhận diện được chứng chỉ **{cert_type.upper()}**, nhưng hiện chưa tìm thấy thông tin về các chương trình đào tạo trong đồ thị."
                    )
                return "\n".join(context)

            # 👉 Có chứng chỉ + có chương trình đào tạo
            if cert_type and found_program_name:
                query = f"""
                MATCH (c:ChuongTrinhDaoTao {{ten_chuong_trinh: '{found_program_name}'}})
                -[r:CO_CHUAN_NGOAI_NGU_DAU_RA_TOI_THIEU_LA]->(lang)
                WHERE lang:{found_language_label if found_language_label else 'TiengAnh'} 
                RETURN lang.{cert_type} AS required_score, lang.bac AS required_level, labels(lang) AS language_type
                LIMIT 1
                """
                results = self.neo4j_handler.execute_query(query)

                if results:
                    result = results[0]
                    program_name = found_program_name
                    
                    score = result.get('required_score')
                    level = result.get('required_level', 'Không rõ')
                    lang_label_list = result.get('language_type', [found_language_label if found_language_label else 'TiengAnh'])
                    lang_label = lang_label_list[0] if lang_label_list else (found_language_label if found_language_label else "Không rõ")

                    lang_display = {
                        "TiengAnh": "Tiếng Anh", "TiengNhat": "Tiếng Nhật",
                        "TiengTrung": "Tiếng Trung", "TiengPhap": "Tiếng Pháp"
                    }.get(lang_label, lang_label)

                    if score:
                        context.append(
                            f"Để tốt nghiệp chương trình **{program_name}**, bạn cần đạt chuẩn **{cert_type.upper()} {score}** "
                            f"(tương đương {level.capitalize()} của Khung năng lực {lang_display})."
                        )
                    elif level and "Bậc" in found_level_or_score:
                        context.append(
                            f"Để tốt nghiệp chương trình **{program_name}**, bạn cần đạt chuẩn ngoại ngữ tối thiểu **{found_level_or_score}** "
                            f"của Khung năng lực {lang_display}."
                        )
                    else:
                        context.append(f"Không tìm thấy thông tin chuẩn đầu ra {cert_type.upper()} cụ thể cho chương trình **{program_name}**.")
                else:
                    context.append(f"Không tìm thấy thông tin chuẩn đầu ra {cert_type.upper()} cho chương trình **{found_program_name}** trong đồ thị.")

            # 👉 Không có chứng chỉ, không có chương trình
            elif not found_program_name and not cert_type:
                context.append(
                    "Xin lỗi, hiện chưa có dữ liệu trong đồ thị kiến thức.<br>"
                    "👉 Bạn vui lòng hỏi lại câu hỏi rõ hơn, trong đó có cả **chứng chỉ** và **chương trình đào tạo** mà bạn đang học để tôi kiểm tra.<br>"
                    "Ví dụ: *'TOEIC bao nhiêu thì mới ra trường ngành Công nghệ Thông tin đặc thù?'*"
                )

            else:
                context.append(f"Tôi không nhận diện được chứng chỉ ngoại ngữ bạn muốn hỏi. Vui lòng thử lại với tên chứng chỉ rõ ràng hơn (ví dụ: TOEIC, IELTS, JLPT, HSK).")

            return "\n".join(context)
        
        # TRƯỜNG HỢP 5 cải tiến: Tìm tiên quyết của một học phần trong một chương trình đào tạo cụ thể          
        # TRƯỜNG HỢP MỚI: Tìm học phần tiên quyết của học phần X trong chương trình Y
        if found_course_name and found_program_name and any(
            kw in lower_question
            for kw in ["tiên quyết của", "học trước môn", "học trước học phần", "có học trước được không", "điều kiện của", "tôi có thể học môn", "học môn"]
        ):
            query = f"""
            MATCH (c:ChuongTrinhDaoTao {{ten_chuong_trinh: '{found_program_name}'}})
            MATCH (end_node)-[:THUOC]->(c)
            WHERE end_node.ten_mon = '{found_course_name}'
            AND (end_node:HocPhanDaiCuong
                OR end_node:HocPhanTienQuyet
                OR end_node:HocPhanSongHanh
                OR end_node:HocPhanKeTiep
                OR end_node:HocPhanTuDo)
            OPTIONAL MATCH (start_node)-[:THUOC]->(c)
            WHERE (start_node)-[:LA_HOC_PHAN_TIEN_QUYET_CUA]->(end_node)
            RETURN DISTINCT start_node.ten_mon AS ban_can_hoc_truoc_mon
            """

            results = self.neo4j_handler.execute_query(query)

            prereqs = []
            seen = set()
            for r in results or []:
                name = r.get("ban_can_hoc_truoc_mon")
                if name and name not in seen:
                    seen.add(name)
                    prereqs.append(name)

            if prereqs:
                lines = [f"Để học học phần **{found_course_name}** trong chương trình **{found_program_name}**, bạn cần hoàn thành các học phần sau:"]
                lines.extend(f"- {p}" for p in prereqs)
                context.append("\n".join(lines))
            else:
                context.append(
                    f"Học phần **{found_course_name}** trong chương trình **{found_program_name}** không có học phần tiên quyết nào. "
                    f"Bạn có thể học môn này ngay."
                )

            return "\n".join(context)

        # TRƯỜNG HỢP 5: Tìm kiếm các học phần tiên quyết của một học phần bất kỳ (chưa chỉ rõ chương trình đào tạo)
        if found_course_name and any(
            kw in lower_question
            for kw in ["tiên quyết của", "học trước môn", "học trước học phần", "có học trước được không", "điều kiện của", "tôi có thể học môn", "học môn"]
        ):
            query = f"""
            MATCH (end_node)
            WHERE end_node.ten_mon = '{found_course_name}'
            AND (end_node:HocPhanDaiCuong
                OR end_node:HocPhanTienQuyet
                OR end_node:HocPhanSongHanh
                OR end_node:HocPhanKeTiep
                OR end_node:HocPhanTựDo)
            OPTIONAL MATCH (end_node)<-[:LA_HOC_PHAN_TIEN_QUYET_CUA]-(start_node)
            RETURN DISTINCT start_node.ten_mon AS ban_can_hoc_truoc_mon
            """
            results = self.neo4j_handler.execute_query(query)

            # Gom kết quả, loại trùng theo thứ tự
            prereqs = []
            seen = set()
            for r in results or []:
                name = r.get("ban_can_hoc_truoc_mon")
                if name and name not in seen:
                    seen.add(name)
                    prereqs.append(name)

            if prereqs:
                lines = [f"Để học học phần **{found_course_name}**, bạn cần hoàn thành các học phần sau:"]
                lines.extend(f"- {p}" for p in prereqs)

                lines.append("")  # ngắt đoạn
                lines.append("👉 Nếu bạn muốn biết chính xác cho **chương trình đào tạo cụ thể**, bạn có thể hỏi như sau:")
                lines.append(f'*Tôi có thể học trước môn **{found_course_name}** trong chương trình [Tên chương trình đào tạo] được không?*')

                context.append("\n".join(lines))
            else:
                context.append(f"Học phần **{found_course_name}** không có học phần tiên quyết nào. Bạn có thể học môn này ngay.")

            return "\n".join(context)


        # TRƯỜNG HỢP 6: Hỏi về học phần song hành với một học phần cụ thể
        if found_course_name and any(kw in lower_question for kw in ["là học phần song hành với học phần nào", "học phần nào là song hành với"]):
            query = f"""
            MATCH (end_node)
            WHERE end_node.ten_mon = '{found_course_name}' AND 
                  (end_node:HocPhanDaiCuong OR end_node:HocPhanTienQuyet OR end_node:HocPhanSongHanh OR end_node:HocPhanKeTiep OR end_node:HocPhanTựDo)
            OPTIONAL MATCH (end_node)<-[r:LA_HOC_PHAN_SONG_HANH_VOI]-(start_node)
            RETURN start_node.ten_mon AS song_hanh_course, type(r) AS relationship_type, end_node.ten_mon AS original_course
            """
            results = self.neo4j_handler.execute_query(query)

            if results and results[0]['song_hanh_course'] is not None:
                response_text = f"Học phần **{found_course_name}** là học phần song hành với các học phần sau:\n"
                unique_song_hanh = set()
                for res in results:
                    if res['song_hanh_course']:
                        unique_song_hanh.add(res['song_hanh_course'])
                
                for sh_name in sorted(list(unique_song_hanh)):
                    response_text += f"- {sh_name}\n"
                context.append(response_text)
            else:
                context.append(f"Học phần **{found_course_name}** không là học phần song hành với học phần nào khác.")
            
            return "\n".join(context)

        # TRƯỜNG HỢP 7: Kiểm tra xem hai học phần có thể học cùng lúc không
        if found_course1 and found_course2 and any(kw in lower_question for kw in ["cùng lúc với", "học với học phần nào", "cùng lúc có được không", "có thể học với", "học cùng lúc"]):

            # Kiểm tra quan hệ song hành (exists)
            query_song_hanh = f"""
            MATCH (c1) WHERE c1.ten_mon = '{found_course1}'
            MATCH (c2) WHERE c2.ten_mon = '{found_course2}'
            RETURN EXISTS( (c1)-[:LA_HOC_PHAN_SONG_HANH_VOI]-(c2) ) AS is_song_hanh
            """
            try:
                song_hanh_results = self.neo4j_handler.execute_query(query_song_hanh)
                is_song_hanh = bool(song_hanh_results and song_hanh_results[0].get('is_song_hanh'))
            except Exception as e:
                print("Lỗi kiểm tra song hành:", e)
                is_song_hanh = False

            # Lấy tiên quyết (unique)
            prereqs_course1 = self._get_prerequisites_for_course(found_course1)
            prereqs_course2 = self._get_prerequisites_for_course(found_course2)

            if is_song_hanh:
                response_text = f"Bạn **có thể** học học phần **{found_course1}** cùng lúc với học phần **{found_course2}** vì chúng có quan hệ **song hành**.\n\n"
                if prereqs_course1:
                    response_text += f"Lưu ý: Học phần **{found_course1}** có các học phần tiên quyết:\n"
                    for p in prereqs_course1:
                        response_text += f"- {p}\n"
                    response_text += "\n"
                if prereqs_course2:
                    response_text += f"Lưu ý: Học phần **{found_course2}** có các học phần tiên quyết:\n"
                    for p in prereqs_course2:
                        response_text += f"- {p}\n"
            else:
                response_text = (
                    f"Học phần **{found_course1}** không có mối quan hệ song hành với học phần **{found_course2}**, "
                    f"nên bạn **không thể** học hai học phần này cùng một lúc."
                )

            context.append(response_text)
            return "\n".join(context)


        # TRƯỜNG HỢP 8: Hỏi về tất cả các học phần trong một học kỳ cụ thể của một chương trình cụ thể
        if found_program_name and found_semester_name and \
           any(kw in lower_question for kw in ["tất cả học phần", "môn học", "học phần", "môn", "sẽ học trong"]) and \
           any(kw in lower_question for kw in ["chương trình", "ngành"]):
            
            query = f"""
            MATCH (c:ChuongTrinhDaoTao {{ten_chuong_trinh: '{found_program_name}'}})
            <-[:THUOC]-(hp) 
            -[r:SE_HOC_TRONG]->(hk:HocKy {{ten_hoc_ky: '{found_semester_name}'}})
            WHERE hp:HocPhanDaiCuong OR hp:HocPhanTienQuyet OR hp:HocPhanSongHanh OR hp:HocPhanKeTiep OR hp:HocPhanTựDo
            RETURN hp.ten_mon AS ten_mon, labels(hp) AS loai_hoc_phan, hk.ten_hoc_ky AS ten_hoc_ky, c.ten_chuong_trinh AS ten_chuong_trinh
            ORDER BY hp.ten_mon
            """
            results = self.neo4j_handler.execute_query(query)

            if results:
                response_text = f"Các học phần thuộc chương trình **{found_program_name}** sẽ học trong **{found_semester_name}**: \n"
                unique_courses = set() 
                for res in results:
                    unique_courses.add(res['ten_mon']) 
                
                for course_name in sorted(list(unique_courses)):
                    response_text += f"- {course_name}\n" 
                context.append(response_text)
            else:
                context.append(f"Không tìm thấy học phần nào trong **{found_semester_name}** thuộc chương trình **{found_program_name}**.")
            return "\n".join(context)

        # TRƯỜNG HỢP 9: Hỏi về loại học phần cụ thể trong một học kỳ cụ thể
        course_type_keywords = {
            "học phần đại cương": "HocPhanDaiCuong", "môn đại cương": "HocPhanDaiCuong",
            "học phần tiên quyết": "HocPhanTienQuyet", "môn tiên quyết": "HocPhanTienQuyet", 
            "học phần song hành": "HocPhanSongHanh", "môn song hành": "HocPhanSongHanh", 
            "học phần kế tiếp": "HocPhanKeTiep", "môn kế tiếp": "HocPhanKeTiep",
            "học phần tự do": "HocPhanTựDo", "môn tự do": "HocPhanTựDo"       
        }
        
        found_course_type_label = None
        for keyword, label in course_type_keywords.items():
            if keyword in lower_question and label in valid_course_labels:
                found_course_type_label = label
                break
        
        if found_course_type_label and found_semester_name:
            query = f"""
            MATCH (hp:{found_course_type_label})-[quan_he:SE_HOC_TRONG]->(hk:HocKy {{ten_hoc_ky: '{found_semester_name}'}})
            RETURN hp.ten_mon AS ten_mon, type(quan_he) AS moi_quan_he, hk.ten_hoc_ky AS ten_hoc_ky
            ORDER BY hp.ten_mon
            """
            results = self.neo4j_handler.execute_query(query)
            
            if results:
                type_display_name = found_course_type_label.replace('HocPhan', 'học phần ').replace('DaiCuong', 'đại cương').replace('TienQuyet', 'tiên quyết').replace('SongHanh', 'song hành').replace('KeTiep', 'kế tiếp').replace('TựDo', 'tự do').lower().strip()
                response_text = f"Các **{type_display_name}** trong **{found_semester_name}**: \n"
                unique_courses = set() 
                for res in results:
                    unique_courses.add(res['ten_mon']) 
                
                for course_name in sorted(list(unique_courses)):
                    response_text += f"- {course_name}\n"
                context.append(response_text)
            else:
                type_display_name = found_course_type_label.replace('HocPhan', '').lower()
                context.append(f"Không tìm thấy học phần {type_display_name} nào trong **{found_semester_name}**.")
            return "\n".join(context)

        # TRƯỜNG HỢP 10: Hỏi về tất cả các học phần trong một học kỳ bất kỳ
        if found_semester_name and any(kw in lower_question for kw in ["tất cả học phần", "môn học", "học phần", "môn", "sẽ học trong"]):
            query = f"""
            MATCH (hp)-[quan_he:SE_HOC_TRONG]->(hk:HocKy {{ten_hoc_ky: '{found_semester_name}'}})
            WHERE hp:HocPhanDaiCuong OR hp:HocPhanTienQuyet OR hp:HocPhanSongHanh OR hp:HocPhanKeTiep OR hp:HocPhanTựDo
            RETURN hp.ten_mon AS ten_mon, labels(hp) AS loai_hoc_phan, type(quan_he) AS moi_quan_he, hk.ten_hoc_ky AS ten_hoc_ky
            ORDER BY hp.ten_mon
            """
            results = self.neo4j_handler.execute_query(query)
            
            if results:
                response_text = f"Các học phần sẽ học trong **{found_semester_name}**: \n"
                unique_courses = set() 
                for res in results:
                    unique_courses.add(res['ten_mon']) 
                
                for course_name in sorted(list(unique_courses)):
                    response_text += f"- {course_name}\n"
                context.append(response_text)
            else:
                context.append(f"Không tìm thấy học phần nào trong **{found_semester_name}**.")
            return "\n".join(context)

        # TRƯỜNG HỢP 11: Hỏi về điều kiện tốt nghiệp CỤ THỂ của một chương trình
        if found_program_name and any(kw in lower_question for kw in ["điều kiện tốt nghiệp", "tốt nghiệp cần gì", "quy định tốt nghiệp"]):
            
            program_name_formatted = found_program_name 
            
            query_program_reqs = f"""
            MATCH (dk:DieuKienTotNghiep)-[d:ĐOI_VOI]->(c:ChuongTrinhDaoTao)
            WHERE c.ten_chuong_trinh = '{program_name_formatted}'
            
            OPTIONAL MATCH (c)-[qh:CO_CHUAN_NGOAI_NGU_DAU_RA_TOI_THIEU_LA ]->(b:TiengAnh)
            
            RETURN dk.dieu_kien_chung AS dieu_kien_rieng,
                    c.ten_chuong_trinh AS ten_chuong_trinh,
                    type(d) AS moi_quan_he_doi_voi,
                    CASE WHEN qh IS NOT NULL THEN type(qh) ELSE NULL END AS moi_quan_he_nn,
                    CASE WHEN b IS NOT NULL THEN labels(b) ELSE [] END AS nhan_nn,
                    CASE WHEN b IS NOT NULL THEN b.bac ELSE NULL END AS bac_nn
            LIMIT 1
            """
            results = self.neo4j_handler.execute_query(query_program_reqs)

            if results:
                result = results[0]
                program_name = result['ten_chuong_trinh']
                graduation_reqs = result['dieu_kien_rieng']
                english_level = result['bac_nn']

                response_text = f"**Điều kiện tốt nghiệp cho chương trình {program_name}:**\n"
                response_text += f"- {graduation_reqs}\n"
                if english_level:
                    response_text += f"- Chuẩn đầu ra tiếng Anh tối thiểu: **{english_level.capitalize()}**\n"
                else:
                    response_text += "- Không tìm thấy thông tin chuẩn đầu ra tiếng Anh cụ thể cho chương trình này."

                context.append(response_text)
            else:
                context.append(f"Không tìm thấy điều kiện tốt nghiệp cho chương trình '{program_name_formatted}' trong đồ thị.") # Sử dụng program_name_formatted
            
            return "\n".join(context)

        # TRƯỜNG HỢP 12: Hỏi về thông tin chương trình đào tạo CỤ THỂ
        if found_program_name and (
            "là gì" in lower_question or lower_question.startswith("chương trình") or
            re.match(r"^(chương trình|ngành)\s", lower_question)
        ) and not any(kw in lower_question for kw in ["điều kiện tốt nghiệp", "tốt nghiệp cần gì", "quy định tốt nghiệp", "học phần", "môn"]):

            
            program_info_name = found_program_name 

            query = f"""
            MATCH (ct:ChuongTrinhDaoTao {{ten_chuong_trinh: '{program_info_name}'}})
            RETURN ct.ten_chuong_trinh AS ten, ct.noi_dung AS noi_dung,
                     ct.ma_chuong_trinh AS ma, ct.tong_so_tin_chi_yeu_cau AS tin_chi
            """
            results = self.neo4j_handler.execute_query(query)
            if results:
                for res in results:
                    context.append(f"**Thông tin chương trình '{res['ten']}':**")
                    context.append(f"- Nội dung: {res['noi_dung']}")
                    context.append(f"- Mã chương trình: {res['ma']}")
                    context.append(f"- Tổng số tín chỉ yêu cầu: {res['tin_chi']}")
            else:
                context.append(f"Không tìm thấy thông tin cho chương trình '{program_info_name}' trong đồ thị.")
            
            return "\n".join(context)

        # TRƯỜNG HỢP 13: Hỏi về điều kiện tốt nghiệp chung
        if any(kw in lower_question for kw in ["điều kiện tốt nghiệp", "tốt nghiệp cần gì", "quy định tốt nghiệp"]) and not found_program_name:
            query = """
            MATCH (dk:DieuKienTotNghiep)
            RETURN dk.dieu_kien_chung AS dieu_kien
            LIMIT 1
            """
            results = self.neo4j_handler.execute_query(query)
            if results:
                context.append(f"**Điều kiện tốt nghiệp chung:** {results[0]['dieu_kien']}")
            else:
                context.append("Không tìm thấy thông tin về điều kiện tốt nghiệp chung trong đồ thị.")
            
            return "\n".join(context)

        # TRƯỜNG HỢP 14: Hỏi về danh sách các chương trình
        if any(kw in lower_question for kw in ["các chương trình", "những ngành học", "danh sách chương trình", "có ngành nào"]):
            query = """
            MATCH (ct:ChuongTrinhDaoTao)
            RETURN ct.ten_chuong_trinh AS ten
            ORDER BY ct.ten_chuong_trinh
            """
            results = self.neo4j_handler.execute_query(query)
            if results:
                program_names = [res['ten'] for res in results]
                context.append(f"Các chương trình đào tạo hiện có: {', '.join(program_names)}.")
            else:
                context.append("Hiện tại không có chương trình đào tạo nào trong đồ thị.")
            
            return "\n".join(context)
            
        # TRƯỜNG HỢP 15: Hỏi học phần X là học phần gì
        if found_course_name and any(kw in lower_question for kw in ["là học phần gì", "thuộc loại học phần nào", "thuộc loại nào"]):
            query = f"""
            MATCH (hp {{ten_mon: '{found_course_name}'}})
            OPTIONAL MATCH (hp)-[r:THUOC|TIEN_QUYET_VAO|KE_TIEP_TU]->(ct:ChuongTrinhDaoTao)
            RETURN labels(hp) AS NhomNode,
                     hp.so_tin_chi AS SoTinChi,
                     ct.ten_chuong_trinh AS ChuongTrinhDaoTao,
                     type(r) AS LoaiQuanHe
            """
            results = self.neo4j_handler.execute_query(query)
            if results:
                course_info_by_program = {}
                for record in results:
                    program_name = record['ChuongTrinhDaoTao']
                    if program_name not in course_info_by_program:
                        course_info_by_program[program_name] = {
                            'NhomNode': record['NhomNode'],
                            'SoTinChi': record['SoTinChi']
                        }
                formatted_context = self.format_course_info_for_llm(found_course_name, course_info_by_program)
                return formatted_context
            else:
                return f"Không tìm thấy thông tin cụ thể về học phần '{found_course_name}' trong đồ thị tri thức."
        # TRƯỜNG HỢP 16: Hỏi học phần X là học phần gì TRONG MỘT CHƯƠNG TRÌNH CỤ THỂ
        if found_course_name and found_program_name and any(
            kw in lower_question for kw in ["là học phần gì", "thuộc loại học phần nào", "thuộc loại nào"]
        ):
            query = f"""
            MATCH (hp {{ten_mon: '{found_course_name}'}})-[:THUOC]->(ct:ChuongTrinhDaoTao {{ten_chuong_trinh: '{found_program_name}'}})
            RETURN DISTINCT 
                ct.ten_chuong_trinh AS ChuongTrinhDaoTao,
                labels(hp) AS NhomHocPhan,
                hp.so_tin_chi AS SoTinChi
            """
            results = self.neo4j_handler.execute_query(query)

            if results:
                course_info_by_program = {}
                for record in results:
                    program_name = record['ChuongTrinhDaoTao']
                    if program_name not in course_info_by_program:
                        course_info_by_program[program_name] = {
                            'NhomNode': record['NhomHocPhan'],
                            'SoTinChi': record['SoTinChi']
                        }
                formatted_context = self.format_course_info_for_llm(found_course_name, course_info_by_program)
                return formatted_context
            else:
                return f"Không tìm thấy thông tin về học phần **{found_course_name}** trong chương trình **{found_program_name}**."

       
        # TRƯỜNG HỢP FALLBACK: Câu hỏi không nằm trong các quy tắc đã định
        else:
            # Trả về một chuỗi rỗng hoặc None để báo hiệu không tìm thấy context
            return None 

    def chat(self, question: str) -> str:
        user_message = question.strip()
        lower_question = user_message.lower()

        # Lấy ngữ cảnh từ Neo4j
        context = self.query_neo4j_for_context(user_message)  # Hàm bạn đã có, trả về chuỗi Markdown hoặc "".

        print(f"\n--- Câu hỏi gốc ---\n{user_message}")
        print(f"--- Ngữ cảnh từ Đồ thị Tri thức ---\n{context}\n----------------------------------\n")

        # Luôn gửi qua OpenAI để LLM DIỄN ĐẠT LẠI (nếu có context thì LLM CHỈ định dạng, KHÔNG bịa)
        if context and context.strip():
            prompt_context = context
        else:
            prompt_context = "KHÔNG_CÓ_CONTEXT"  # LLM sẽ biết không có dữ liệu - trả lời thân thiện

        reply = self.openai_handler.generate_response_with_context(user_message, prompt_context)

        # Trả về Markdown (frontend sẽ render Markdown->HTML)
        return reply






