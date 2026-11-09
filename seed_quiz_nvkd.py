"""
Nạp đề "Phỏng vấn NVKD – Sản phẩm Bricon" vào module trắc nghiệm.

- Phần A (44 câu) + Phần B (16 câu): trắc nghiệm, chấm điểm tự động.
- Phần C (10 câu) + Phần D (8 câu): tự luận, KHÔNG chấm điểm.
  HR xem bài làm cạnh đáp án tham khảo trong Admin > Kết quả.

Chạy:
    python seed_quiz_nvkd.py            # tạo đề (bỏ qua nếu slug đã tồn tại)
    python seed_quiz_nvkd.py --replace  # xóa đề cũ cùng slug (kể cả kết quả đã làm) rồi tạo lại

Yêu cầu: đã chạy `flask db upgrade` (migration a7c3e91d2b40 - câu tự luận).
"""
import sys

from app import create_app, db
from app.models.quiz import Quiz, Question, Answer

QUIZ_SLUG = 'phong-van-nvkd-bricon'
QUIZ_TITLE = 'Phỏng vấn NVKD – Kiến thức sản phẩm Bricon'
QUIZ_DESCRIPTION = (
    'Gồm 60 câu trắc nghiệm (kiến thức sản phẩm theo TDS và kỹ thuật thi công) '
    'và 18 câu tự luận (lỗi thi công, tình huống bán hàng). '
    'Phần tự luận không tính điểm, bộ phận nhân sự sẽ xem xét riêng.'
)

# (câu hỏi, [A, B, C, D], đáp án đúng, căn cứ/giải thích)
MULTIPLE_CHOICE = [
    # ===================== PHẦN A – KEO DÁN GẠCH =====================
    ('Tỉ lệ trộn keo dán gạch Bricon là:',
     ['2 keo : 1 nước', '3 keo : 1 nước', '4 keo : 1 nước', '1 keo : 1 nước'], 'B',
     'TDS: trộn 3 keo : 1 nước.'),
    ('Keo dán gạch Bricon được trộn bằng máy trộn tốc độ chậm trong bao lâu?',
     ['30 giây', '1 phút', '3–4 phút', '10–15 phút'], 'C',
     'TDS: dùng máy trộn tốc độ chậm 3–4 phút.'),
    ('Định mức sử dụng keo dán gạch Bricon khoảng:',
     ['5 kg/m²', '2 kg/m²', '1 kg/5 m²', '12 kg/m²'], 'A',
     'TDS: định mức ~5 kg/m².'),
    ('Thời gian mở của keo dán gạch Bricon là:',
     ['5 phút', '30–45 phút', '2 giờ', '15–20 phút'], 'D',
     'TDS: thời gian mở 15–20 phút.'),
    ('Thời gian chỉnh gạch của Keo Nội thất và Keo Ngoại thất Extra lần lượt là:',
     ['10 phút và 5 phút', '5 phút và 10 phút', '15 phút và 20 phút', 'Cả hai đều 30 phút'], 'B',
     'TDS: Nội thất 5 phút, Extra 10 phút.'),
    ('Keo dán gạch Nội thất phù hợp với kích thước gạch tối đa:',
     ['40×40 cm', '60×60 cm', '80×80 cm', '120×240 cm'], 'C',
     'TDS Nội thất: gạch kích thước lớn tối đa 80×80 cm.'),
    ('Keo dán gạch Nội thất phù hợp với gạch/đá có trọng lượng tối đa:',
     ['45 kg/m²', '25 kg/m²', '80 kg/m²', 'Không giới hạn'], 'A',
     'TDS Nội thất: trọng lượng tối đa 45 kg/m².'),
    ('Khổ gạch/đá thi công tối ưu của Keo Ngoại thất Extra lên đến:',
     ['60×60 cm', '80×80 cm', '60×120 cm', '1 m × 1 m'], 'D',
     'TDS Extra: khổ gạch/đá thi công tối ưu lên đến 1 m × 1 m.'),
    ('Keo Ngoại thất Extra ốp tường được đến độ cao:',
     ['1,5 m', '3 m', '6 m', 'Không được dùng ốp tường'], 'B',
     'TDS Extra: ốp tường cao lên đến 3 m.'),
    ('Khách muốn lát gạch mới đè lên gạch cũ (gạch chồng gạch). Sản phẩm Bricon nào có ghi trong TDS là thi công được?',
     ['Keo dán gạch Ngoại thất Extra', 'Keo dán gạch Nội thất', 'Chống thấm Sàn 106', 'Cả hai loại keo dán gạch'], 'A',
     'TDS Extra: sử dụng được phương pháp thi công gạch chồng gạch.'),
    ('Thành phần chính của keo dán gạch Bricon gồm:',
     ['Xi măng trắng, CaCO₃, phụ gia', 'Nhựa epoxy hai thành phần',
      'Cát khô siêu mịn (độ ẩm dưới 1%), xi măng chuyên dụng, phụ gia nhập khẩu',
      'Silica qua lưới 200 mesh, nhựa, chất bảo quản'], 'C',
     'TDS: cát khô siêu mịn (<1% độ ẩm), xi măng chuyên dụng, phụ gia nhập khẩu.'),
    ('Quy cách đóng gói của keo dán gạch Bricon là:',
     ['Cả hai loại đều có bao 25 kg và túi 5 kg', 'Nội thất: túi 1 kg; Extra: bao 20 kg',
      'Cả hai loại chỉ có bao 40 kg', 'Nội thất: bao 25 kg và túi 5 kg; Extra: bao 25 kg'], 'D',
     'TDS: Nội thất 25 kg/bao, 5 kg/túi; Extra 25 kg/bao.'),
    ('Keo dán gạch Bricon đạt tiêu chuẩn nào?',
     ['TCVN 7899-3:2008', 'TCVN 7899-1:2008', 'TCVN 12692:2020', 'Không công bố tiêu chuẩn'], 'B',
     'TDS: đạt TCVN 7899-1:2008.'),
    ('Theo TDS, khu vực nào dưới đây là phạm vi dùng của Keo Ngoại thất Extra?',
     ['Hồ bơi, sân thượng, WC, kho lạnh, phòng xông hơi, showroom ô tô', 'Chỉ phòng khách, phòng ngủ',
      'Chỉ tường nội thất khô ráo', 'Chỉ khe ron'], 'A',
     'TDS Extra: hồ bơi, sân thượng, WC, kho lạnh, phòng xông hơi, showroom ô tô...'),
    ('Điều nào TDS keo dán gạch Bricon cấm làm?',
     ['Dùng máy trộn tốc độ chậm', 'Dùng bay răng cưa', 'Pha thêm xi măng hoặc phụ gia khác',
      'Làm sạch bề mặt trước khi thi công'], 'C',
     'TDS: không pha thêm xi măng hoặc phụ gia khác.'),
    ('Dụng cụ đúng để trải keo dán gạch lên bề mặt là:',
     ['Bay cao su', 'Chổi quét', 'Con lăn', 'Bay răng cưa'], 'D',
     'TDS: dùng bay răng cưa trải keo đều trên bề mặt.'),
    ('Sau khi dán gạch, phải chờ ít nhất bao lâu mới được chà ron?',
     ['2 giờ', '24 giờ', '3 ngày', '7 ngày'], 'B',
     'TDS: chờ ít nhất 24 giờ trước khi chà ron.'),

    # ===================== PHẦN A – KEO CHÀ RON GỐC XI MĂNG =====================
    ('Thành phần chính của keo chà ron gốc xi măng Bricon:',
     ['CaCO₃, xi măng trắng cao cấp, phụ gia đặc biệt', 'Cát vàng, xi măng xám', 'Nhựa epoxy',
      'Silica, nhựa, chất bảo quản'], 'A',
     'TDS: CaCO₃, xi măng trắng cao cấp và phụ gia đặc biệt.'),
    ('Keo chà ron gốc xi măng Bricon đạt tiêu chuẩn:',
     ['TCVN 7899-1:2008', 'TCVN 12692:2020', 'TCVN 7899-3:2008', 'TCVN 2682:2009'], 'C',
     'TDS: đạt TCVN 7899-3:2008.'),
    ('Định mức keo chà ron gốc xi măng Bricon:',
     ['1 kg/m²', '1 kg/2 m²', '1 kg/10 m²', '1 kg/5 m²'], 'D',
     'TDS: định mức ~1 kg/5 m².'),
    ('Độ rộng mạch ron phù hợp với keo chà ron gốc xi măng Bricon:',
     ['Dưới 0,5 mm', '1–6 mm', '6–15 mm', 'Trên 15 mm'], 'B',
     'TDS: độ rộng mạch ron 1–6 mm.'),
    ('Thời gian trộn và sử dụng keo chà ron sau khi pha:',
     ['30 phút', '5 phút', '2 giờ', 'Cả ngày'], 'A',
     'TDS: thời gian trộn & sử dụng 30 phút.'),
    ('Sau khi chà ron, phải chờ ít nhất bao lâu mới đưa vào sử dụng hoặc lưu thông?',
     ['1 giờ', '6 giờ', '24 giờ', '7 ngày'], 'C',
     'TDS: chờ ít nhất 24 giờ trước khi đưa vào sử dụng hoặc lưu thông.'),
    ('Cách ép keo chà ron vào mạch đúng theo TDS:',
     ['Dùng bay răng cưa kéo dọc mạch', 'Dùng tay miết từng đoạn', 'Dùng chổi quét',
      'Dùng bay cao su, kéo theo đường chéo với mạch gạch'], 'D',
     'TDS: dùng bay cao su ép keo vào mạch ron theo đường chéo với mạch gạch.'),
    ('Keo chà ron thừa trên mặt gạch được loại bỏ bằng:',
     ['Giấy nhám', 'Miếng xốp hoặc khăn ẩm', 'Axit tẩy rửa', 'Để khô rồi cạo'], 'B',
     'TDS: loại bỏ phần keo thừa bằng miếng xốp hoặc khăn ẩm.'),
    ('Keo chà ron Nội thất (túi 1 kg) KHÔNG nên dùng cho:',
     ['Khu vực thường xuyên tiếp xúc nước hoặc yêu cầu chống thấm cao', 'Sàn phòng khách',
      'Tường phòng ngủ', 'Sàn nội thất chịu ẩm'], 'A',
     'TDS ron Nội thất: không sử dụng cho khu vực thường xuyên tiếp xúc nước hoặc yêu cầu chống thấm cao.'),
    ('Quy cách đóng gói keo chà ron gốc xi măng Bricon:',
     ['Túi 5 kg, thùng 4 túi', 'Bao 25 kg', 'Túi 1 kg (thùng 24 túi); hộp 1 kg (thùng 30 hộp)', 'Tuýp 380 ml'], 'C',
     'TDS: túi 1 kg – thùng 24 túi; hộp 1 kg – thùng 30 hộp.'),
    ('Khách cần chà ron hồ bơi, phòng xông hơi, kho lạnh. Loại ron gốc xi măng nào phù hợp?',
     ['Chỉ ron Nội thất (túi)', 'Không loại nào phù hợp', 'Pha thêm chống thấm vào ron Nội thất',
      'Ron Ngoại thất Extra hoặc ron Hộp Nội & Ngoại thất'], 'D',
     'TDS ron Ngoại thất Extra và ron Hộp N&N: thích hợp hồ bơi, phòng xông hơi, WC, kho lạnh, sân thượng.'),
    ('Lưu ý nào đúng khi pha keo chà ron?',
     ['Pha càng loãng càng dễ vào mạch và càng bền', 'Không pha quá loãng vì sẽ làm giảm chất lượng',
      'Pha với dầu để ron bóng', 'Pha sẵn từ hôm trước cho ngấm'], 'B',
     'TDS: không pha quá loãng sẽ làm giảm chất lượng sản phẩm.'),
    ('Tính năng của keo chà ron gốc xi măng Bricon theo TDS:',
     ['Kháng axit mạnh, chịu hóa chất công nghiệp', 'Dùng được cho mạch ron 20 mm',
      'Độ mịn cao, bề mặt ron bóng đẹp, chống nấm mốc, chống bám bẩn', 'Không cần vệ sinh keo thừa'], 'C',
     'TDS: độ mịn cao, bề mặt ron bóng đẹp, chống nấm mốc, bám bẩn.'),

    # ===================== PHẦN A – KEO CHÀ RON EPOXY =====================
    ('Keo chà ron Epoxy Bricon có quy cách và tỉ lệ trộn:',
     ['Túi 1 kg, trộn với nước', 'Tuýp 380 ml hai thành phần, tỉ lệ 1:1 (trộn qua vòi)',
      'Hộp 1 kg, trộn 3:1', 'Lon 5 kg, pha dung môi'], 'B',
     'TDS Epoxy: 380 ml, 2 thành phần, tỉ lệ 1:1.'),
    ('Khi bắt đầu bơm Epoxy, vì sao phải bỏ khoảng 10 g keo đầu tiên?',
     ['Để tiết kiệm keo', 'Vì keo đầu bị đông', 'Để làm sạch khe ron',
      'Để đảm bảo hai thành phần đã trộn đều'], 'D',
     'TDS Epoxy: thải bỏ khoảng 10 g keo đầu để đảm bảo trộn đều.'),
    ('Ngừng bơm Epoxy quá bao lâu thì phải thay vòi trộn mới?',
     ['20 phút', '5 phút', '2 giờ', 'Không cần thay'], 'A',
     'TDS Epoxy: ngừng thi công trên 20 phút keo trong vòi có thể đông, thay vòi mới.'),
    ('Sau khi bơm và miết ron Epoxy, khi nào tháo băng keo và vệ sinh; khi nào đạt độ cứng tối đa?',
     ['Ngay lập tức; sau 1 giờ', 'Sau 24 giờ; sau 7 ngày', 'Sau 4–5 giờ; sau 24 giờ', 'Sau 30 phút; sau 3 ngày'], 'C',
     'TDS Epoxy: sau 4–5 giờ tháo băng và vệ sinh; sau 24 giờ đạt cứng tối đa.'),
    ('Điều nào đúng khi thi công Epoxy?',
     ['Pha thêm dung môi nếu keo đặc', 'Không pha dung môi, luôn đeo găng tay và đồ bảo hộ',
      'Trộn thêm nước cho dễ bơm', 'Bơm keo lên khe ron còn ướt'], 'B',
     'TDS Epoxy: không pha dung môi, luôn đeo găng tay và đồ bảo hộ.'),
    ('Keo Epoxy dính lên mặt gạch, xử lý đúng là:',
     ['Luôn dùng axit tẩy', 'Để khô rồi lau bằng xăng', 'Để nguyên, tự bong',
      'Còn ướt: lau ngay bằng khăn sạch; đã khô: dùng dụng cụ cơ học, máy mài, không làm hỏng mặt gạch'], 'D',
     'TDS Epoxy: khi còn ướt lau ngay bằng khăn sạch; khi đã khô dùng dụng cụ cơ học, máy mài.'),
    ('Tính năng của keo chà ron Epoxy Bricon:',
     ['Chống thấm vượt trội, kháng hóa chất, chống rêu mốc, màu bền, khó bám bẩn, VOC Free',
      'Chỉ dùng cho nội thất khô ráo', 'Pha với nước như ron xi măng',
      'Chỉ dùng cho gạch men, không dùng cho đá tự nhiên, mosaic'], 'A',
     'TDS Epoxy: chống thấm vượt trội, không hóa chất, chống rêu mốc, màu bền, khó bám bẩn, VOC Free.'),

    # ===================== PHẦN A – CHỐNG THẤM 102 / 106 =====================
    ('Thành phần chính của Chống thấm Tường 102 / Sàn 106:',
     ['Bitum, xăng thơm', 'Xi măng trắng, CaCO₃',
      'Silica siêu mịn qua lưới 200 mesh, nhựa, phụ gia, chất bảo quản', 'Nhựa epoxy hai thành phần'], 'C',
     'TDS chống thấm: silica siêu mịn qua lưới 200 mesh, nhựa, phụ gia và chất bảo quản.'),
    ('Cách trộn đúng của Chống thấm 102 / 106:',
     ['1 chống thấm : 1 nước, dùng ngay',
      '1 chống thấm : 0,5 nước : 1 keo dán gạch Bricon, trộn chống thấm với nước trước',
      '1 chống thấm : 1 xi măng : 0,5 nước', 'Dùng nguyên chất, không pha'], 'B',
     'TDS: 1 chống thấm : 0,5 nước sạch : 1 keo dán gạch Bricon, trộn chống thấm với nước trước.'),
    ('Số lớp thi công chống thấm theo TDS:',
     ['1 lớp là đủ', 'Luôn 4 lớp', '2 lớp, thi công liên tục không chờ khô',
      '2 lớp, chờ khô giữa các lớp; khu vực thấm nhanh nên thi công 3 lớp'], 'D',
     'TDS: thi công 2 lớp, đảm bảo thời gian khô giữa các lớp; khu vực thấm nhanh nên thi công 3 lớp.'),
    ('Định mức chống thấm là 2,0–2,5 m²/kg cho 2 lớp. Sàn 50 m² thi công 2 lớp cần khoảng bao nhiêu kg chống thấm?',
     ['20–25 kg', '5–10 kg', '50 kg', '100–125 kg'], 'A',
     '50 ÷ 2,5 = 20 kg; 50 ÷ 2,0 = 25 kg.'),
    ('Phát biểu nào SAI về Chống thấm 102 / 106?',
     ['Bảo dưỡng tối thiểu 3 ngày để đông cứng hoàn toàn, hạn chế co ngót',
      'Không chứa chì, thủy ngân; tuổi thọ trên 15 năm; đạt TCVN 12692:2020',
      'Nên thi công dưới nắng gắt, gió mạnh để lớp chống thấm khô nhanh',
      'Chịu mài mòn, chịu nước mặn, kháng kiềm cao'], 'C',
     'TDS: tránh thi công dưới trời nắng gắt và gió mạnh.'),
    ('Quy cách đóng gói Chống thấm 102 / 106:',
     ['Chỉ có thùng 20 kg', 'Bao 25 kg và túi 5 kg', 'Tuýp 380 ml',
      'Lon 1 kg (thùng 18 lon), lon 5 kg (thùng 4 lon), thùng 18 kg'], 'D',
     'TDS: lon 1 kg – thùng 18 lon; lon 5 kg – thùng 4 lon; thùng 18 kg.'),

    # ===================== PHẦN A – CHUNG =====================
    ('Hạn sử dụng của các sản phẩm Bricon (keo dán gạch, keo chà ron, Epoxy, chống thấm) tính từ ngày sản xuất là:',
     ['6 tháng', '12 tháng', '24 tháng', '36 tháng'], 'B',
     'Hạn sử dụng 12 tháng kể từ ngày sản xuất.'),

    # ===================== PHẦN B – KỸ THUẬT THI CÔNG THỰC TẾ =====================
    ('Thợ quen ngâm gạch vào nước trước khi dán, kể cả khi dùng keo. Bạn khuyên thế nào?',
     ['Ngâm càng lâu càng bám chắc',
      'Không cần ngâm; gạch chỉ cần sạch, không bụi – gạch ướt sũng nước làm giảm bám dính của keo',
      'Ngâm nước pha xi măng', 'Chỉ ngâm gạch granite'], 'B',
     'Dán bằng keo không cần ngâm gạch; gạch ướt sũng làm giảm bám dính.'),
    ('Vì sao gạch granite, porcelain khổ lớn dán bằng hồ xi măng cát hay bị bộp, bong?',
     ['Gạch gần như không hút nước nên hồ xi măng bám kém, lớp hồ dày dễ rỗng và co ngót',
      'Do gạch quá nhẹ', 'Do xi măng quá tốt', 'Do ron quá rộng'], 'A',
     'Gạch hút nước thấp, hồ xi măng bám cơ học kém, lớp dày dễ rỗng.'),
    ('Cách kiểm tra nhanh keo đã trải trên nền còn dán được gạch hay không:',
     ['Nhìn màu keo', 'Ngửi mùi keo',
      'Chạm ngón tay: keo còn dính tay là còn dán được; nếu đã tạo màng không dính thì cạo bỏ, trải lớp mới',
      'Tưới nước lên keo rồi dán tiếp'], 'C',
     'Keo tạo màng là đã quá thời gian mở, phải cạo bỏ.'),
    ('Gạch khổ lớn (từ 60×60 trở lên), ốp tường ngoài trời nên thi công thế nào để keo phủ kín?',
     ['Chấm keo 4 góc và giữa viên', 'Chỉ trải keo lên mặt sau gạch', 'Trải keo thật dày bằng bay phẳng',
      'Trải keo cả trên nền và mặt sau gạch (phết hai mặt)'], 'D',
     'Phết hai mặt để keo phủ kín, không bộp.'),
    ('Sau khi đặt gạch lên lớp keo, thao tác đúng là:',
     ['Ấn và gõ nhẹ bằng búa cao su cho keo dàn đều; thỉnh thoảng nhấc thử một viên kiểm tra độ phủ keo',
      'Đặt nhẹ, không ấn để khỏi lệch', 'Đứng lên gạch ngay để ép chặt', 'Tưới nước lên mặt gạch'], 'A',
     'Ấn, gõ búa cao su, nhấc thử kiểm tra độ phủ.'),
    ('Chọn cỡ răng bay răng cưa theo nguyên tắc nào?',
     ['Loại gạch nào cũng dùng một cỡ', 'Gạch càng lớn, nền càng kém phẳng thì dùng răng bay càng lớn',
      'Gạch càng lớn dùng răng càng nhỏ để tiết kiệm keo', 'Chỉ dùng bay phẳng'], 'B',
     'Gạch lớn, nền kém phẳng → răng bay lớn.'),
    ('Yêu cầu về nền trước khi dán gạch bằng keo:',
     ['Nền càng nhẵn càng tốt', 'Nền còn đọng nước vẫn dán được',
      'Nền chắc, phẳng, sạch bụi, dầu mỡ; lớp tô trát mới phải đủ thời gian khô cứng',
      'Keo tự bù được nền lồi lõm vài cm'], 'C',
     'Nền chắc, phẳng, sạch; keo dán lớp mỏng, không dùng để bù nền.'),
    ('Thứ tự thi công đúng cho sàn nhà vệ sinh:',
     ['Lát gạch → chà ron → quét chống thấm lên mặt gạch', 'Chống thấm → chà ron → lát gạch',
      'Lát gạch → chống thấm → ngâm nước',
      'Xử lý bề mặt, cổ ống, góc tường → chống thấm → bảo dưỡng, ngâm thử nước → dán gạch bằng keo → chà ron'], 'D',
     'Chống thấm, ngâm thử trước rồi mới ốp lát và chà ron.'),
    ('Vì sao nên ngâm thử nước sau khi chống thấm sàn, trước khi lát gạch?',
     ['Để phát hiện điểm rò rỉ và xử lý ngay, tránh phải đập gạch về sau', 'Để chống thấm khô nhanh hơn',
      'Để làm sạch bề mặt', 'Không cần thiết'], 'A',
     'Phát hiện rò rỉ khi còn sửa được.'),
    ('Khi chống thấm nhà vệ sinh, vị trí nào dễ thấm nhất và cần xử lý kỹ hơn?',
     ['Giữa sàn', 'Cổ ống xuyên sàn, ga thoát sàn, góc tường và chân tường', 'Trần nhà vệ sinh', 'Khung cửa'], 'B',
     'Cổ ống, ga thoát sàn, góc và chân tường là điểm yếu.'),
    ('Khi quét lớp chống thấm thứ hai, nên quét thế nào?',
     ['Quét ngay khi lớp 1 còn ướt', 'Cùng chiều với lớp 1',
      'Chờ lớp 1 khô, quét vuông góc với chiều lớp 1 để phủ kín lỗ kim', 'Chỉ quét chỗ nào thấy mỏng'], 'C',
     'Chờ khô, quét vuông góc để không sót lỗ kim.'),
    ('Sân thượng, sân ngoài trời diện tích lớn khi lát gạch cần lưu ý gì để tránh gạch phồng, đội?',
     ['Lát khít ron 0 mm', 'Dùng keo nội thất cho rẻ', 'Lát vào buổi trưa nắng cho keo khô nhanh',
      'Chừa khe co giãn theo mảng và ở chân tường, dùng keo và ron ngoại thất'], 'D',
     'Khe co giãn + keo, ron ngoại thất.'),
    ('Bếp nhà hàng, khu nhiều dầu mỡ và chất tẩy rửa nên tư vấn loại ron nào?',
     ['Keo chà ron Epoxy', 'Ron Nội thất (túi)', 'Xi măng trắng pha nước', 'Không cần chà ron'], 'A',
     'Epoxy kháng hóa chất, khó bám bẩn.'),
    ('Khách hỏi cách vệ sinh ron xi măng mới chà. Lời khuyên đúng:',
     ['Dùng axit mạnh tẩy ngay cho sạch',
      'Lau keo thừa bằng xốp/khăn ẩm khi thi công; không dùng axit mạnh vì làm ron mục, bạc màu',
      'Xịt nước áp lực cao ngay hôm sau', 'Chà bàn chải sắt'], 'B',
     'Axit mạnh làm ron mục, bạc màu.'),
    ('Bảo quản bao keo dán gạch đã mở dở tại công trình thế nào?',
     ['Để mở miệng ngoài trời', 'Đổ ra xô nước để sẵn',
      'Buộc kín miệng, để nơi khô ráo, kê cao khỏi nền ẩm, tránh nắng mưa', 'Đặt trực tiếp trên nền đất'], 'C',
     'Keo hút ẩm sẽ vón cục, giảm chất lượng.'),
    ('Công trình thi công chậm (1 thợ, gạch lớn). Nên trộn keo thế nào?',
     ['Trộn cả bao 25 kg một lần cho tiện', 'Trộn sẵn từ chiều hôm trước', 'Trộn lỏng hơn để keo lâu khô',
      'Trộn từng mẻ vừa đủ dùng trước khi keo bắt đầu đông kết, trải keo từng mảng nhỏ'], 'D',
     'Không dùng keo đã đông kết; trộn mẻ nhỏ, trải mảng nhỏ.'),
]

# (câu hỏi, đáp án tham khảo cho HR)
ESSAY_C_PREFIX = 'Lỗi thi công – nêu NGUYÊN NHÂN và CÁCH PHÒNG TRÁNH / KHẮC PHỤC:\n'
ESSAYS = [
    # ===================== PHẦN C – LỖI THƯỜNG GẶP KHI THI CÔNG =====================
    (ESSAY_C_PREFIX + 'Khách báo: sàn gạch 60×60 lát được 2 tháng, gõ vào nhiều viên nghe "bộp", có viên bắt đầu lệch.',
     'Nguyên nhân: dùng vữa hoặc keo không phù hợp gạch lớn; độ phủ keo thấp (chấm điểm); đặt gạch quá thời gian mở; '
     'nền bụi, dầu, không phẳng; không phết keo hai mặt.\n'
     'Giải pháp: bóc gạch bộp, vệ sinh nền, dán lại bằng bay răng cưa + phết hai mặt; nên dùng Keo Extra cho gạch lớn.'),
    (ESSAY_C_PREFIX + 'Thợ thấy keo đặc lại trong xô nên đổ thêm nước trộn lại để dùng tiếp cho "đỡ phí". Hậu quả và cách làm đúng?',
     'Keo đã bắt đầu đông kết, thêm nước làm giảm mạnh cường độ bám dính, dễ bong. '
     'TDS ghi rõ không sử dụng / không trộn lại keo đã đông kết.\n'
     'Đúng: trộn vừa đủ dùng, đúng tỉ lệ 3 keo : 1 nước.'),
    (ESSAY_C_PREFIX + 'Để làm nhanh, thợ trải keo một lần cho cả mảng sàn 10 m² rồi mới đặt gạch dần. Những viên đặt sau bị bong. Vì sao?',
     'Keo quá thời gian mở 15–20 phút, bề mặt tạo màng khô nên mất bám dính. '
     'Kiểm tra bằng cách ấn ngón tay – keo không dính tay là đã quá.\n'
     'Đúng: trải từng mảng nhỏ, cạo bỏ keo đã tạo màng rồi trải lớp mới.'),
    (ESSAY_C_PREFIX + 'Thợ pha thêm xi măng vào keo dán gạch "cho chắc và tiết kiệm". Bạn giải thích thế nào?',
     'Pha xi măng phá vỡ công thức phụ gia, giảm bám dính, dễ co ngót nứt. '
     'TDS: không pha thêm xi măng hoặc phụ gia khác; nếu xảy ra sự cố hãng không thể bảo hành.'),
    (ESSAY_C_PREFIX + 'Mạch ron sau vài tuần bị nứt, rỗ, bạc màu, loang màu không đều.',
     'Pha quá nhiều nước (TDS cảnh báo); mạch bẩn, ướt khi chà; chà ron khi keo dán chưa đủ 24 giờ; '
     'vệ sinh quá sớm hoặc quá ướt; dùng ron Nội thất cho khu ướt; tẩy bằng axit.\n'
     'Khắc phục: cạo ron hỏng, vệ sinh mạch, chà lại đúng tỉ lệ nước, đúng loại ron cho khu vực.'),
    (ESSAY_C_PREFIX + 'Chủ nhà gấp nên thợ chà ron ngay chiều hôm đó sau khi dán gạch buổi sáng, tối đó cho người đi lại. Rủi ro gì?',
     'Keo dán chưa đủ cường độ, gạch xê dịch, ron nứt, hơi ẩm bị nhốt gây loang ron.\n'
     'Đúng: chờ ≥ 24 giờ sau khi dán mới chà ron và ≥ 24 giờ sau khi chà ron mới lưu thông.'),
    (ESSAY_C_PREFIX + 'Thi công keo chà ron Epoxy: có đoạn ron không đông cứng, có đoạn loang màu; mặt gạch bị dính lớp keo khô rất khó lau. Thợ đã làm sai ở đâu?',
     'Không bỏ ~10 g keo đầu nên chưa trộn đều; ngừng > 20 phút không thay vòi; có thể pha dung môi (cấm); '
     'không lau keo thừa khi còn ướt, để quá 4–5 giờ mới tháo băng và vệ sinh.\n'
     'Keo đã khô: xử lý cơ học / máy mài cẩn thận, không làm hỏng mặt gạch.'),
    (ESSAY_C_PREFIX + 'Nhà vệ sinh đã chống thấm nhưng trần tầng dưới vẫn ố nước quanh ống thoát sàn và góc tường.',
     'Nguyên nhân: bỏ sót cổ ống, góc tường, chân tường; chỉ quét 1 lớp hoặc không đợi khô giữa lớp; '
     'không ngâm thử nước; đục phá sau khi chống thấm; không bảo dưỡng đủ 3 ngày.\n'
     'Xử lý: xác định điểm rò, xử lý cổ ống, thi công lại 2–3 lớp, ngâm thử trước khi lát.'),
    (ESSAY_C_PREFIX + 'Lớp chống thấm sân thượng bị nứt chân chim, có chỗ bong rộp sau 1 tuần.',
     'Thi công dưới nắng gắt, gió mạnh; lớp quá dày; sai tỉ lệ trộn hoặc không trộn chống thấm với nước trước; '
     'bề mặt bụi, dầu mỡ; không bảo dưỡng tối thiểu 3 ngày.\n'
     'Khắc phục: cạo bỏ chỗ hỏng, vệ sinh, thi công lại đúng tỉ lệ, tránh nắng gió, bảo dưỡng đủ 3 ngày.'),
    (ESSAY_C_PREFIX + 'Gạch sân thượng 80 m² sau mùa nắng bị phồng rộp, đội lên thành hình mái nhà.',
     'Không chừa khe co giãn và khe chân tường; ron quá nhỏ/khít; dùng keo Nội thất hoặc vữa cho ngoại thất; độ phủ keo thấp.\n'
     'Phòng tránh: keo Extra, phủ keo kín, khe co giãn theo mảng, ron ngoại thất.'),

    # ===================== PHẦN D – TÌNH HUỐNG THỰC TẾ =====================
    ('Tình huống – Tư vấn trọn gói & tính khối lượng:\n'
     'Chủ nhà xây nhà phố có 4 phòng vệ sinh. Tổng diện tích cần chống thấm (sàn + chân tường) là 24 m²; '
     'tổng diện tích ốp lát gạch 30×60 (sàn + tường) là 60 m², ron 2 mm. Anh muốn ron không bị ố vàng, đen mốc.\n'
     'Hãy đề xuất sản phẩm Bricon cho từng hạng mục, tính số lượng và quy đổi ra quy cách cần mua (bao, lon, túi/hộp).',
     'Chống thấm: Sàn 106 cho sàn, Tường 102 cho chân tường; 24 ÷ 2,0–2,5 ≈ 10–12 kg (ví dụ 2 lon 5 kg + 2 lon 1 kg), '
     'cộng khoảng 10–12 kg keo dán gạch Bricon để trộn theo tỉ lệ 1 CT : 0,5 nước : 1 keo.\n'
     'Keo dán gạch: Ngoại thất Extra (TDS ghi phù hợp WC): 60 m² × 5 kg = 300 kg = 12 bao 25 kg, '
     'cộng phần trộn chống thấm và hao hụt → khoảng 13 bao.\n'
     'Ron: Ngoại thất Extra hoặc Hộp N&N (dùng được cho WC): 60 ÷ 5 = 12 kg → 12 túi/hộp; '
     'tư vấn nâng cấp Epoxy cho khu tắm đứng (chống thấm, chống rêu mốc, khó bám bẩn).\n'
     'Điểm trừ: chọn ron Nội thất (túi) cho WC.\n'
     'Gợi ý đánh giá: đúng sản phẩm – tính đúng – quy đổi ra quy cách mua cụ thể.'),
    ('Tình huống – Xử lý từ chối về giá:\n'
     'Khách nói: "Keo dán gạch đắt hơn xi măng cát nhiều, nhà tôi xưa giờ lát bằng hồ vẫn ổn, sao phải tốn tiền?" '
     'Bạn trả lời thế nào?',
     'Không chê khách; so sánh trên tổng chi phí chứ không chỉ giá bao; gạch hiện nay (granite, porcelain, khổ lớn) '
     'hút nước thấp nên vữa dễ bộp; không ngâm gạch, thi công nhanh, lớp mỏng; chi phí đập lát lại gấp nhiều lần tiền keo; '
     'đưa dẫn chứng, hình ảnh công trình.'),
    ('Tình huống – Chinh phục thợ thi công:\n'
     'Một đội thợ lâu năm quen dùng hãng khác, nói: "Keo Bricon tao chưa dùng, không quen tay, đổi làm gì cho rủi ro." '
     'Thợ lại là người quyết định mua hàng cho chủ nhà. Bạn tiếp cận ra sao?',
     'Tôn trọng kinh nghiệm thợ; đề xuất dùng thử miễn phí hoặc demo tại công trình; tự hướng dẫn kỹ thuật tận nơi '
     '(tỉ lệ 3:1, thời gian mở, thời gian chỉnh gạch); nhấn điểm thợ được lợi (dễ trải, chống trượt khi ốp tường); '
     'xây quan hệ lâu dài, chương trình thợ nếu công ty có.\n'
     'Điểm trừ: chê hãng khác.'),
    ('Tình huống – Xử lý khiếu nại:\n'
     'Khách gọi điện rất bực: ron sàn khu tắm đứng sau 2 tháng bị đen mốc, bợ ra, đòi Bricon đền. '
     'Khi kiểm tra, bạn thấy thợ đã dùng Keo chà ron Nội thất (túi 1 kg). Bạn xử lý từng bước thế nào?',
     'Lắng nghe, xin lỗi vì sự bất tiện, không đổ lỗi ngay; xuống hiện trường, chụp ảnh, ghi lô hàng/NSX; '
     'giải thích nhẹ nhàng theo TDS (ron Nội thất không dùng cho khu thường xuyên tiếp xúc nước); '
     'đề xuất giải pháp: cạo ron, chà lại bằng Epoxy hoặc ron Ngoại thất Extra, có thể xin hỗ trợ một phần để giữ khách; '
     'báo cáo quản lý; rút kinh nghiệm tư vấn đúng ngay từ đầu.'),
    ('Tình huống – Đàm phán với đại lý:\n'
     'Một đại lý vật liệu xây dựng nói: "Hãng X cho chiết khấu cao hơn và công nợ 60 ngày. Bricon không bằng thì tôi không lấy." '
     'Bạn trả lời và xử lý thế nào?',
     'Không hứa vượt thẩm quyền; hỏi rõ sản lượng, tệp khách của đại lý; bán giá trị chứ không chỉ giá: chất lượng ổn định, '
     'ít khiếu nại, hỗ trợ kỹ thuật, dòng sản phẩm đồng bộ (keo + ron + chống thấm) tăng giá trị đơn; '
     'đề xuất chính sách theo bậc sản lượng và xin ý kiến quản lý; đánh giá rủi ro công nợ.'),
    ('Tình huống – Chọn đúng loại keo:\n'
     'Chủ nhà muốn ốp gạch granite 80×80 lên tường mặt tiền ngoài trời, cao khoảng 3 m, và nói: '
     '"Lấy keo Nội thất cho rẻ, TDS ghi chịu được gạch 80×80 mà." Bạn tư vấn thế nào (loại keo, cách thi công, loại ron)?',
     'Không đồng ý dùng keo Nội thất: keo Nội thất chỉ dùng cho khu nội thất, mức 80×80 là giới hạn trong nhà chứ không phải ngoài trời.\n'
     'Đúng là Keo Ngoại thất Extra: ngoại thất, ốp tường cao đến 3 m, khổ đến 1 × 1 m, chỉnh gạch 10 phút.\n'
     'Thi công: bề mặt sạch, phẳng; trộn 3:1 bằng máy tốc độ chậm; bay răng cưa, phết keo hai mặt cho gạch 80×80; '
     'chờ 24 giờ mới chà ron.\n'
     'Ron: Ngoại thất Extra hoặc Hộp N&N, mạch 1–6 mm.\n'
     'Giải thích chênh lệch chi phí nhỏ so với rủi ro gạch rơi ở mặt tiền.\n'
     'Gợi ý đánh giá: đúng keo và lý do – cách thi công – đúng ron.'),
    ('Tình huống – Cải tạo gạch chồng gạch:\n'
     'Khách cải tạo nhà cũ, muốn lát gạch mới đè lên sàn gạch cũ phòng khách và WC để khỏi đục phá. '
     'Bạn tư vấn sản phẩm nào và cần kiểm tra những gì trước khi thi công?',
     'Keo Extra (TDS ghi rõ thi công được gạch chồng gạch).\n'
     'Kiểm tra: gạch cũ còn bám chắc, gõ không bộp (viên bộp phải đục bỏ, bù phẳng); tẩy sạch dầu mỡ, sáp, xà phòng; '
     'độ phẳng; cao độ cửa và độ dốc thoát nước; riêng WC cần đánh giá lại chống thấm.'),
    ('Tình huống – Giới thiệu nhanh 60 giây:\n'
     'Gặp một chủ thầu mới tại công trình, anh ta hỏi: "Bricon là hãng gì, có gì hơn mấy hãng lớn?" '
     'Hãy viết phần trình bày của bạn trong khoảng 60 giây.',
     'Có cấu trúc (chào – hỏi nhu cầu – lợi ích – chốt bước tiếp); nêu điểm mạnh có căn cứ: đạt TCVN 7899-1, 7899-3, '
     '12692:2020; Extra thi công gạch chồng gạch, gạch đến 1 × 1 m; Epoxy VOC Free; chống thấm không chì, thủy ngân, '
     'tuổi thọ trên 15 năm; giải pháp đồng bộ một hãng; không chê đối thủ; '
     'kết thúc bằng đề nghị cụ thể (gửi mẫu, demo, báo giá).'),
]


def seed(replace=False):
    existing = Quiz.query.filter_by(slug=QUIZ_SLUG).first()
    if existing:
        if not replace:
            print(f'⚠️  Đề "{QUIZ_SLUG}" đã tồn tại (id={existing.id}). Dùng --replace để xóa và tạo lại.')
            return
        db.session.delete(existing)
        db.session.commit()
        print(f'🗑️  Đã xóa đề cũ id={existing.id}')

    quiz = Quiz(
        title=QUIZ_TITLE,
        slug=QUIZ_SLUG,
        description=QUIZ_DESCRIPTION,
        duration_minutes=80,
        pass_score=66,              # Đạt khi trắc nghiệm ≥ 20/30 điểm (≥ 40/60 câu)
        show_correct_answers=False,  # Không lộ đáp án cho ứng viên sau
        shuffle_questions=False,     # Giữ thứ tự A → B → C → D
        shuffle_answers=True,
        category='Phong-van',
        is_active=True,
    )
    db.session.add(quiz)
    db.session.flush()

    order = 0
    for text, options, correct, explanation in MULTIPLE_CHOICE:
        assert len(options) == 4 and correct in 'ABCD', text
        order += 1
        q = Question(quiz_id=quiz.id, question_text=text, question_type='multiple_choice',
                     points=1, explanation=explanation, order=order)
        db.session.add(q)
        db.session.flush()
        for idx, opt in enumerate(options):
            db.session.add(Answer(question_id=q.id, answer_text=opt,
                                  is_correct=('ABCD'[idx] == correct), order=idx))

    for text, model_answer in ESSAYS:
        order += 1
        db.session.add(Question(quiz_id=quiz.id, question_text=text, question_type='essay',
                                points=0, model_answer=model_answer, order=order))

    quiz.total_questions = order
    db.session.commit()
    print(f'✅ Đã tạo đề "{QUIZ_TITLE}" (id={quiz.id}, slug={QUIZ_SLUG}): '
          f'{len(MULTIPLE_CHOICE)} câu trắc nghiệm + {len(ESSAYS)} câu tự luận')


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed(replace='--replace' in sys.argv)
