# ChatBot-Gemini-SaleBot
## Giới thiệu
- Dự án này là một giải pháp tích hợp toàn diện từ thu thập dữ liệu (web scraping) đến phân tích dữ liệu và triển khai Trí tuệ Nhân tạo (AI) để tư vấn khách hàng. Chúng tôi sử dụng Selenium và Scrapy để thu thập dữ liệu từ các website, xử lý và chuẩn bị dữ liệu với Scikit-learn cho các tác vụ Machine Learning, và tích hợp Google Gemini AI để cung cấp trải nghiệm tư vấn sản phẩm tương tác dựa trên dữ liệu đã xử lý.

## Tính năng chính
### Thu thập dữ liệu web (Web Scraping)
- Selenium: Dùng để thu thập dữ liệu từ các trang web có nội dung động hoặc yêu cầu tương tác trình duyệt (JavaScript).
- Scrapy: Sử dụng cho việc crawl dữ liệu hiệu quả từ các trang tĩnh hoặc quy mô lớn.
### Xử lý và phân tích dữ liệu
- Scikit-learn: Hỗ trợ tiền xử lý dữ liệu, phân tích và xây dựng mô hình dự đoán (tùy yêu cầu cụ thể).
- Tạo dữ liệu sạch để phục vụ cho mô hình AI.
- Tư vấn khách hàng bằng AI
- Google Gemini AI: Cung cấp khả năng trò chuyện thông minh, trả lời các câu hỏi của khách hàng dựa trên dữ liệu đã thu thập.
Ví dụ: "Laptop nào có giá dưới 10 triệu?", "Laptop nào có 8GB RAM?", v.v.
### Yêu cầu hệ thống
Python 3.7 hoặc cao hơn.
Hệ điều hành: Windows, macOS, hoặc Linux.

### Cài đặt
1. Clone Repository 
```
git clone https://github.com/baokhanh546123/Gemini-ChatBot-SaleBot.git
cd Gemini-ChatBot-SaleBot
```
2. Tạo và kích hoạt môi trường ảo (khuyên dùng)
```
python -m venv venv
```
# Trên Windows:
```
.\venv\Scripts\activate
```
# Trên macOS/Linux:
```
source venv/bin/activate
```
3. Cài đặt các thư viện cần thiết
```
pip install selenium scrapy scikit-learn pandas google-generativeai
```
4. Cấu hình API Key của Gemini
- Tạo file api_key.py trong thư mục ai_agent (hoặc thư mục chứa script).
Thêm khóa API của bạn vào file:
**api_key.py**
```
gemini_api_key = "YOUR_GEMINI_API_KEY_HERE"
```
QUAN TRỌNG: Thêm api_key.py vào file .gitignore để tránh đẩy lên GitHub công khai.
Cách sử dụng
1. Thu thập dữ liệu
Chạy Scrapy Spider: 


**Bằng lệnh sau ```scrapy crawl name -o name_file.type_file```**

Trong đó : 

- **name** phải trùng với name trong file laptop/spiders/laptop_spiders hoặc trùng với file spider của bạn (ở đây của tôi là ***"laptop_spider"***)

- **name_file** là tên file xuất , đặt tên dễ nhớ , dễ lưu 

- **type_file** là kiểu file xuất như csv , json , ...

```
scrapy crawl laptop_spider -o output.csv
```

**Lưu ý : Ở đây , tôi đã cào dữ liệu tuy nhiên cần xem xét về mặt thời gian nếu thời gian làm dự án xa với thời phát hành nên cào lại dữ liệu vì dữ liệu có bị cũ.**

2. Tiền xử lý và chuẩn bị dữ liệu
- Chạy script tiền xử lý dữ liệu:
```
python ai_agent/model.py
```
- Sau khi chạy script sẽ xuất một file ***recommendation_model.pkl*** , đây file mô hình đã được đóng gói sau khi là sạch dữ liệu.
3. Bắt đầu tư vấn với Gemini
Chạy script chính để tương tác với Gemini:
```
python ai_agent/ai_agent.py
```
- Bạn có thể hỏi các câu như: "Laptop nào có giá dưới 10 triệu?", "Gợi ý laptop có 8GB RAM".

### Giấy phép
- Dự án này được phát hành dưới Giấy phép MIT. Xem tệp LICENSE để biết chi tiết.