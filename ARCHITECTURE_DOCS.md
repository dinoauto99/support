# Tài Liệu Thiết Kế Trạm C Incident Detector

Tài liệu này ghi chú lại tất cả những thảo luận, quyết định kiến trúc và thủ thuật kỹ thuật đã được thống nhất thiết kế trong quá trình xây dựng công cụ `C Incident Detector`. (Lưu trữ để thuận tiện cho việc maintain và onboard sau này).

## 1. Bối Cảnh (Context)
- **Mục tiêu**: Xây dựng công cụ phân tích tĩnh (Static Analyzer) gọn nhẹ bằng Python cho C/C++ nhằm tìm ra các code smell ("Incident") mà không bắt buộc phải cài đặt một frontend trình biên dịch (Compiler Frontend) cực nặng như LibClang.
- **Các luật kiểm tra (Incidents)**:
  1. `Unused Parameter`: Tham số được khai báo trong hàm nhưng không dùng đến trong thân hàm.
  2. `Empty Function`: Hàm hoàn toàn trống (không có bất kỳ câu lệnh logic nào).
  3. `Empty IF`: Câu lệnh điều kiện `if` rỗng (Ví dụ `if(x) {}` hoặc `if(y) ;`).
  4. `Empty SWITCH`: Khối lệnh `switch` không có block nội dung (Ví dụ `switch(z) {}`).

## 2. Các Quyết định Kiến Trúc (Architecture Decisions)

Công cụ đã được tái cấu trúc thành một dạng **Mô-đun hóa (Modular Package)** thay vì làm một file script dài tuyến tính, tuân thủ chặt ngặt các nguyên lý **SOLID**:

* **[S] Single Responsibility Principle**: Hệ thống bị bóc tách dứt điểm chức năng.
  * Phân tích Cú Pháp (Parsing) bị giới hạn và đóng kín tại `utils.py`.
  * Bộ máy quét và đọc mã (Orchestrator) nằm ở `core.py`.
  * Trách nhiệm giao tiếp Input/Output xử lý CSV nằm ở `io_handlers.py`.
  * Quản lý hình thái dữ liệu luân chuyển nằm ở `models.py`.

* **[O] Open/Closed Principle** & **[L] Liskov Substitution**:
   * Hệ thống luôn sẵn sàng **mở rộng** để chèn thêm các luật (Detecting Rules) mới trong tương lai. Bạn có thể xây dựng rule quét "Vòng lặp rỗng" (Empty Loop) mà **không cần sửa lại mã nguồn cũ** bằng cách tạo ra một Class mới ở thư mục `detectors/` và kế thừa class cha `BaseDetector`.

## 3. Các Design Pattern được áp dụng

1. **Strategy Pattern (Chiến lược)**:
   - Thay vì việc dùng đống lệnh `if/else` để check từng loại lỗi bên trong bộ lõi của cấu trúc. Chúng ta định nghĩa một class cha Interface định hình là `BaseDetector` (Tất cả luật phải gọi phương thức `.detect(context)`). Mã lõi (Core Engine) tự động thực thi các function đa hình này.
   
2. **Singleton Pattern (Khởi tạo duy nhất)**:
   - Các detector/checker thực tế là các đoạn mã (stateless strategy), chúng chỉ chứa thuật toán Regex mà không chứa dữ liệu thay đổi.
   - Hệ thống được trang bị class `SingletonABCMeta`.
   - Kết quả: Khi các lớp con (Detector) được truyền vào thông qua `DetectorRegistry`, hệ thống sẽ tự nhận dạng Metaclass này và ép cấp phát để chúng luôn được tái sử dụng trên 1 vùng nhớ RAM duy nhất. Đảm bảo dù chương trình quét hàng vạn file C thì không có 2 object EmptyFunctionDetector giống hệt nhau sinh ra chật bộ nhớ. Thỏa mãn tuyệt đối mục tiêu "Lightweight".

## 4. Kỹ thuật Phân tích mã tự thân (Heuristic Parsing)

Do không truy cập theo mô hình Abstract Syntax Tree (AST) thật của C-Compiler, Project sử dụng kỹ năng kết hợp giữa Regex và Thuật toán thăng bằng (Balancing):

- **Tẩy Code (Masking)**: Trước khi code được quét Regex, thuật toán State Machine trong Utils sẽ phát hiện các Comment dạng khối (`/* */`), Comment tuyến dòng (`//`) cùng tất cả các Chuỗi String text `"..."` đóng băng nó bằng các khoảng trắng (Space). Việc này giữ nguyên vị trí Line/Column của Code nhưng loại bỏ sự nhiễu sóng của String/Comments khi Regex đọc.
- **Chỉ mục Cú Pháp**: Điểm bắt đầu và kết thúc của các khối Block Code (`{ ... }`) và thông số Parameters `(...)` được chiết xuất nhờ thuật toán đếm dấu ngoặc đệ quy (Parentheses Balancing) từ hàm gốc mà không phải cắt xén String trực tiếp một cách hớ hênh.

## 5. Cấu trúc Source Code
```
/incident_detection
 ├── main.py                    # Khởi tạo Dependency và Bootstrap App
 ├── core.py                    # CFileAnalyzer: Phân tích file sang Context Function -> Trả về lỗi
 ├── io_handlers.py             # CSVInputProvider & CSVReportGenerator
 ├── models.py                  # Dto Model (Incident, FunctionContext)
 ├── utils.py                   # Parsing Logic Algorithms
 └── detectors/
     ├── __init__.py            # Khởi tạo DetectorRegistry nổ máy Detector
     ├── base.py                # Abstract Singleton Meta Class
     ├── empty_function.py      # Rule: Empty Function Logic
     ├── empty_if.py            # Rule: Empty If Logic
     ├── empty_switch.py        # Rule: Empty Switch Logic
     └── unused_param.py        # Rule: Unused Param Logic
```
