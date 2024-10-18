import re
from difflib import SequenceMatcher
from fpdf import FPDF


# 删除空格和特殊字符的函数
def clean_text(text):
    import re
    # 去掉空格，换行符，回车符，制表符
    return re.sub(r'[\s\n\r\t]+', '', text)


# 读取文件并清理
def read_and_clean_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return clean_text(text)


# 比较两个字符串并标记不匹配部分
def compare_strings(text1, text2):
    matcher = SequenceMatcher(None, text1, text2)
    result = []
    last_match_end_1 = 0
    last_match_end_2 = 0

    for match in matcher.get_matching_blocks():
        # 添加不匹配部分，用 '/' 隔开file1和file2的不匹配部分 (标红)
        if match.a > last_match_end_1 or match.b > last_match_end_2:
            file1_diff = text1[last_match_end_1:match.a]
            file2_diff = text2[last_match_end_2:match.b]
            if file1_diff or file2_diff:  # 确保不为空
                result.append(f"<red>{file1_diff}/{file2_diff}</red>")

        # 添加匹配部分
        result.append(text1[match.a: match.a + match.size])

        last_match_end_1 = match.a + match.size
        last_match_end_2 = match.b + match.size

    # 添加最后一段不匹配部分
    if last_match_end_1 < len(text1) or last_match_end_2 < len(text2):
        file1_diff = text1[last_match_end_1:]
        file2_diff = text2[last_match_end_2:]
        result.append(f"<red>{file1_diff}/{file2_diff}</red>")

    return ''.join(result)


# 将结果写入PDF
class PDF(FPDF):
    def add_comparison(self, comparison_result):
        self.set_font("ArialUnicode", size=12)
        for part in comparison_result.split("<red>"):
            if "</red>" in part:
                red_text, normal_text = part.split("</red>")
                if red_text:
                    self.set_text_color(255, 0, 0)  # Red color
                    self.multi_cell(0, 10, red_text)
                if normal_text:
                    self.set_text_color(0, 0, 0)  # Black color
                    self.multi_cell(0, 10, normal_text)
            else:
                self.set_text_color(0, 0, 0)  # Black color
                self.multi_cell(0, 10, part)


def main(file1, file2, output_pdf):
    # 读取并清理文件
    text1 = read_and_clean_file(file1)
    text2 = read_and_clean_file(file2)

    # 比较字符串
    comparison_result = compare_strings(text1, text2)

    # 生成PDF
    pdf = PDF()
    pdf.add_page()

    # 设置支持Unicode的字体，确保字体文件ArialUnicodeMS.ttf存在
    pdf.add_font('ArialUnicode', '', './Arial Unicode MS.ttf', uni=True)
    pdf.set_font('ArialUnicode', '', 12)

    pdf.add_comparison(comparison_result)
    pdf.output(output_pdf)


# 示例调用
if __name__ == "__main__":
    file1 = "file1.txt"
    file2 = "file2.txt"
    output_pdf = "comparison_output.pdf"
    main(file1, file2, output_pdf)
