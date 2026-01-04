import PyPDF2


def remove_pages(input_pdf_path, output_pdf_path, pages_to_remove):
    """
    删除 PDF 指定页码（从1开始计数）

    :param input_pdf_path: 输入 PDF 文件路径
    :param output_pdf_path: 输出 PDF 文件路径
    :param pages_to_remove: 要删除的页码列表，例如 [1, 3, 5]
    """
    # 打开 PDF
    with open(input_pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        writer = PyPDF2.PdfWriter()

        total_pages = len(reader.pages)
        print(f"PDF 总页数: {total_pages}")

        # 转成0-based索引
        pages_to_remove_zero_index = [p - 1 for p in pages_to_remove]

        for i in range(total_pages):
            if i not in pages_to_remove_zero_index:
                writer.add_page(reader.pages[i])

        # 写入新 PDF
        with open(output_pdf_path, "wb") as out_f:
            writer.write(out_f)

    print(f"已生成新 PDF: {output_pdf_path}")


if __name__ == "__main__":
    input_pdf = "/Users/kingsonwu/Downloads/Python编程：从入门到实践（第3版）.pdf"  # 输入 PDF
    output_pdf = "/Users/kingsonwu/Downloads/Python编程：从入门到实践1（第3版）.pdf"  # 输出 PDF
    pages_to_remove = [3, 732]  # 要删除的页码

    remove_pages(input_pdf, output_pdf, pages_to_remove)


# pip install PyPDF2
# python remove_pdf_pages.py book.pdf book_new.pdf 2 5 10