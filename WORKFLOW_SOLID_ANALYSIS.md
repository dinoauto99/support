# Workflow & SOLID Analysis - C Incident Detector

Tài liệu này mô tả trực quan luồng đi của dữ liệu (Workflow) bên trong công cụ và phân tích nguyên do kiến trúc này hoàn toàn tuân thủ các nguyên lý thiết kế **SOLID**.

---

## 1. 🔄 Luồng xử lý dữ liệu (Workflow)

Quá trình quét và tìm kiếm lỗi được chia làm 5 giai đoạn độc lập được điều phối bởi `main.py`:

```mermaid
graph TD
    A[📄 Input CSV] -->|io_handlers.py| B(CSVInputProvider)
    B -->|Bóc tách File & Hàm| C[Danh sách Target]
    
    C -->|Core.py| D(CFileAnalyzer)
    
    subgraph Engine Phân Tích (Analyzer)
        D --> E{Read C File}
        E -->|utils.py| F[Masking Comments/Strings]
        F --> G[Extract Function Context]
    end
    
    subgraph Chiến Lược Dò Tim (Strategy Detectors)
        G -. Context .-> H[EmptyFunctionDetector]
        G -. Context .-> I[UnusedParameterDetector]
        G -. Context .-> J[EmptyIfDetector]
        G -. Context .-> K[EmptySwitchDetector]
    end
    
    H & I & J & K -->|Trả về List Incidents| L[Tập hợp lỗi]
    L -->|io_handlers.py| M(CSVReportGenerator)
    M --> N[📊 Output Report CSV]
```

**Mô tả các bước:**
1. **Khởi tạo (Injection):** `main.py` lắp ráp `CSVInputProvider`, `CFileAnalyzer` và truy xuất danh sách các Detectors từ `Registry` (Singleton).
2. **Thu thập dữ liệu đầu vào:** `CSVInputProvider` đọc file danh sách các target (File - Function cần quét).
3. **Phân tích bối cảnh (Context Extraction):** `CFileAnalyzer` mở source code C, sử dụng `utils.py` để làm phẳng file (xóa nhiễu từ comments/strings). Tìm ranh giới của hàm bằng kĩ thuật ngoặc nhọn `{...}` và sinh ra object `FunctionContext`.
4. **Phát hiện (Detection):** `FunctionContext` được đẩy song song vào tất cả các **Detectors**. Mỗi Detector chạy regex đặc thù để tìm Incident của riêng nó.
5. **Báo cáo (Reporting):** Tất cả các Incident thu thập được đẩy cho `CSVReportGenerator` để ghi ra file kết quả.

---

## 2. 🧱 Phân tích việc áp dụng 5 Nguyên lý SOLID

Giống như việc lắp ráp những khối Lego độc lập, việc tái cấu trúc (refactor) tool này đã được thiết kế dựa trên 5 nguyên tắc SOLID kinh điển để đảm bảo chất lượng kỹ thuật cao nhất.

### [S] Single Responsibility Principle (Đơn Trách Nhiệm)
Mỗi Class và Module trong hệ thống chỉ làm đúng **một việc duy nhất** và có đúng **một lý do duy nhất để thay đổi**:
* `CSVInputProvider` chỉ biết cách đọc định dạng Input CSV. Thậm chí nếu sau này data lấy từ JSON hay DB, thay vì sửa class này, ta tạo JsonInputProvider.
* Trách nhiệm IO (io_handlers) và Trách nhiệm xử lý Regex (detectors) hoàn toàn tách biệt.
* Từng Detector cụ thể thiết lập giới hạn ranh giới an toàn: `EmptyIfDetector` tuyệt đối không biết quan tâm xem tham số hàm có unused hay không.

### [O] Open/Closed Principle (Đóng / Mở)
*Hệ thống mở cho việc mở rộng, nhưng đóng với việc sửa chữa.*
* **Thực tế:** Nếu ngày mai dự án cần dò tìm lỗi vòng lặp `while` rỗng, bạn **không bao giờ phải đụng vào** hay thay đổi mã nguồn của luồng chạy chính (`core.py`, `CFileAnalyzer`).
* Bạn chỉ việc tạo thêm class `EmptyWhileDetector` kế thừa `BaseDetector` và quăng vào thư mục `detectors/`. `CFileAnalyzer` mở cửa chấp nhận mọi loại detector miễn nó có định dạng là BaseDetector (Do `registry` quản lý).

### [L] Liskov Substitution Principle (Thay thế Liskov)
*Class con có thể thay thế class cha mà không làm hỏng tính đúng đắn của chương trình.*
* `CFileAnalyzer` luôn lặp qua toàn bộ mảng `self.detectors` và gọi `detector.detect(context)`.
* Tất cả `EmptyFunctionDetector`, `EmptySwitchDetector`... đều trả về chính xác một kết quả chuẩn (`List[Incident]`). Hệ thống đối xử với tất cả chúng y hệt cách đối xử với Interface `BaseDetector` ban đầu mà không bị Crashes do chênh lệch kiểu dữ liệu hay params.

### [I] Interface Segregation Principle (Phân tách Interface)
*Nên chia nhỏ Interface thành các tập cụ thể thay vì nhồi nhét quá nhiều vào 1 Interface khổng lồ.*
* Interface `BaseDetector` của chúng ta cực kỳ nhỏ gọn và tối giản rành mạch. Nó chỉ ép buộc triển khai đúng 1 phương thức duy nhất:
  ```python
  def detect(self, context: FunctionContext) -> List[Incident]: pass
  ```
* Bất cứ ai tạo Rule Mới cũng không bị ép buộc phải implement những hàm dư thừa rườm rà (ví dụ các hàm set_config, hay string_parse như các kiến trúc lỗi thời khác). Các hàm xử lý string đã được tống vào thư viện tiện ích riêng (`utils.py`).

### [D] Dependency Inversion Principle (Đảo ngược Phụ thuộc)
*Các module cấp cao (Core) không được phụ thuộc vào class cấp thấp (Từng Rule cụ thể), cả 2 phải phụ thuộc vào Trừu tượng (Abstraction).*
* **Trước kia**: Hàm phân tích chính gọi chết tên (hardcode) từng check: `if rỗng: ...`, `if if empty: ...`. Nếu thêm check, phải sửa hàm chính.
* **Hiện tại**: Module cấp cao `CFileAnalyzer` nhận một mảng danh sách các Interface Trừu Tượng `List[BaseDetector]` thông qua tham số vào constructor `__init__(self, detectors)`.
* Trách nhiệm gắn (inject) những module cấp thấp (các Detector cụ thể như EmptyIf) vào module cấp cao (CFileAnalyzer) được đẩy toàn bộ về mặt trận ở ngoài cùng là file main: `main.py`. Nhờ thế, Engine phân tích hoàn toàn vô danh hóa trước các luật quét cụ thể. Cấu trúc tuyệt đối an toàn.
