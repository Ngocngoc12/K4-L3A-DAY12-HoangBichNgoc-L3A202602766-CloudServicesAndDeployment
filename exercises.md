# Phiếu Phản Ánh — K4 Level 3A, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay dòng `> *Câu trả lời của bạn*` bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: ..........................  Mã học viên: ..........................

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> Nếu để mặc định là "changeme", khi ứng dụng được đưa lên môi trường thật (production) mà lập trình viên quên không cấu hình biến môi trường, ứng dụng vẫn sẽ khởi động thành công thay vì báo lỗi. Hacker hoặc bất kỳ ai biết được giá trị mặc định "changeme" này (do mã nguồn công khai hoặc đoán được) đều có thể sử dụng API một cách miễn phí và tùy ý. Việc không thiết lập giá trị mặc định sẽ buộc hệ thống phải chết ngay lập tức (fail fast) trong quá trình khởi động nếu thiếu cấu hình bảo mật quan trọng, qua đó báo động cho nhà phát triển để cài đặt đúng API Key trước khi bất cứ ai có thể truy cập được ứng dụng.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

> Dòng log JSON: `{"event": "ask_completed", "level": "info", "timestamp": "2026-09-28T07:44:00+00:00", "user_id": "sv-test", "tokens_in": 10, "tokens_out": 20, "cost_usd": 0.0003}`
> 
> Hai việc làm được:
> 1. Dễ dàng query, đếm, tính toán tổng chi phí (`cost_usd`) hoặc số token đã sử dụng của một người dùng cụ thể (`user_id`) thông qua các công cụ phân tích log (như Datadog, ELK).
> 2. Có thể tạo cảnh báo tự động khi tổng số request hoặc chi phí trong một khoảng thời gian nhất định vượt quá một ngưỡng cảnh báo. 
> Việc dùng `print("đã trả lời xong")` chỉ cho ta dữ liệu văn bản phi cấu trúc, không thể lọc hoặc tính toán trực tiếp mà không cần viết regex phức tạp.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | ~1 GB |
| Multi-stage | ~150 MB |

> Phần dung lượng chênh lệch đó chính là các trình biên dịch (như gcc), các thư viện phát triển (dev-headers), pip cache, mã nguồn công cụ cài đặt và hệ điều hành đầy đủ không cần thiết ở lúc chạy. Bằng cách dùng multi-stage, ta chỉ copy các thư viện đã biên dịch (virtual environment hoặc wheel) từ bước `builder` sang môi trường runtime (chỉ dùng bản slim hoặc alpine cực nhỏ).

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> Khi sửa `app/main.py` và build lại, Docker layer chứa `COPY requirements.txt` và lệnh cài `pip install` sẽ được lấy nguyên từ cache, do nội dung của file `requirements.txt` không hề thay đổi. Việc cài đặt thư viện không bị lặp lại, tiết kiệm rất nhiều thời gian. Cache chỉ bị phá vỡ từ lệnh `COPY . .` trở về sau.
> Nếu đặt `COPY . .` lên trước `RUN pip install`, mọi sự thay đổi trong source code (bất kỳ file nào) đều sẽ phá vỡ bộ nhớ đệm (cache) tại lớp `COPY` đó, dẫn đến việc `RUN pip install` đứng sau phải tải và cài lại toàn bộ các thư viện dù `requirements.txt` không hề có sự thay đổi nào.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> 1. Nếu có một lỗ hổng trong code Python (ví dụ: command injection do không filter đầu vào), hacker có thể thực thi mã tùy ý từ trong container. 2. Nếu container đang chạy với quyền root, mã của hacker sẽ có quyền lớn nhất trong không gian của container. Nếu hacker khai thác thêm lỗ hổng thoát container (container escape) như chia sẻ volume cấu hình nhạy cảm, host socket hoặc lỗi kernel, chúng sẽ dễ dàng trở thành root trên máy host thật sự.
> Việc sử dụng lệnh `USER appuser` ngay sau khi cài đặt các file hệ thống sẽ hạ quyền của container xuống thành một người dùng không có quyền quản trị. Qua đó, ngay cả khi hacker thực thi được mã, quyền hạn của mã này vẫn bị giới hạn khắt khe bởi `appuser`. Hệ thống máy host sẽ giảm thiểu rủi ro bị kiểm soát toàn phần.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

> Nếu đếm theo phút đồng hồ, số lượng request được tính lại từ 0 khi chuyển giao phút (ví dụ từ 10:00:59 sang 10:01:00). Một người dùng có thể gửi ngay 10 request vào giây 10:00:59 và 10 request nữa vào giây 10:01:00. Như vậy, trong 2 giây liên tiếp, họ đã gửi tối đa được 20 request mà vẫn không bị chặn vì giới hạn hệ thống.
> Sliding window giải quyết việc này bằng cách luôn nhìn lại chính xác 60 giây gần nhất thay vì phụ thuộc vào đồng hồ hệ thống reset tại giây 00.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

> - Rate limit giới hạn **tốc độ và số lượng** request (ví dụ 10 request/phút) để chống spam, DDOS, bảo vệ tài nguyên tính toán ở thời điểm hiện tại.
> - Cost guard giới hạn **tổng chi tiêu / tài chính** của người dùng (ví dụ 10 USD/tháng) để tránh tình trạng phát sinh hóa đơn đám mây khổng lồ.
> - **Tình huống 1 (Rate limit cho qua nhưng Cost guard chặn):** Người dùng gọi request đầu tiên trong tháng nhưng câu hỏi có token size cực kỳ khủng, tiêu tốn ngay 15$. Rate limit cho qua vì đây là request đầu tiên, nhưng Cost Guard chặn vì 15$ lớn hơn ngân sách 10$.
> - **Tình huống 2 (Rate limit chặn nhưng Cost guard cho qua):** Người dùng gửi liên tục 20 câu hỏi cực ngắn "Hi" trong 10 giây đầu. Chi phí chưa tới 0.01$ (Cost guard rất thỏa mãn), nhưng Rate limit chặn ở request thứ 11 vì quá 10 req/phút.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> Nếu gộp liveness và readiness vào làm một kiểm tra cả Redis, khi Redis mất kết nối tạm thời 30 giây:
> 1. Load balancer hoặc orchestrator (ví dụ Kubernetes, Docker Swarm) sẽ gọi endpoint gộp này.
> 2. Do Redis mất mạng, hàm ping trả về lỗi. Endpoint trả về 503 thay vì 200.
> 3. Hệ thống coi container đã "chết" (fail liveness probe) và quyết định tiêu diệt (SIGKILL) cả 3 container đang chạy để khởi động lại.
> 4. Toàn bộ API của ta ngừng hoạt động, tất cả các request đang xử lý dở cũng bị cắt đứt oan uổng dù ứng dụng FastAPI chưa chết, dẫn đến sập toàn hệ thống thay vì chỉ gián đoạn database tạm thời. Liveness chỉ nên báo cáo tình trạng sống còn của riêng process.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> Con số `history_length` sẽ thay đổi loạn xạ và bất nhất (ví dụ: 1, rồi 1, rồi 2, rồi 1). Lý do là vì mỗi request từ người dùng có thể được load balancer điều phối ngẫu nhiên tới 1 trong 3 instance độc lập. Nếu instance A lưu request đầu tiên vào biến dict RAM của nó, thì instance B không hề biết gì về biến này. Khi người dùng gọi tiếp và trúng instance B, lịch sử chat (từ RAM B) vẫn trống rỗng nên agent bị "mất trí nhớ". Redis là store tập trung nên dù request vào instance nào, nó cũng truy cập cùng một CSDL và `history_length` sẽ tăng dần đều.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> Một lỗi thường gặp là **app không chịu khởi động và crash với lỗi "ValueError: missing agent_api_key"**.
> - **Nguyên nhân:** Do khi deploy lên Render/Railway, môi trường chưa được thiết lập (chưa add các Env vars). Theo cấu hình CP1, biến `AGENT_API_KEY` là bắt buộc, không có giá trị mặc định nên Pydantic sẽ fail-fast.
> - **Tìm nguyên nhân:** Truy cập mục Log Viewer (Deploy logs) trên dashboard của Railway/Render. Log chỉ ra `pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings`.
> - **Cách sửa:** Vào trang cấu hình Environment / Variables của dashboard, tạo biến `AGENT_API_KEY` (và `REDIS_URL`, `PORT` v.v), rồi trigger quá trình deploy/restart lại service.
