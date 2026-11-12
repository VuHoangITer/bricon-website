"""
Nạp đề "Kiến thức sản phẩm – Keo chà ron & Epoxy Bricon" vào module trắc nghiệm.

- 45 câu trắc nghiệm (chấm điểm tự động): keo chà ron gốc xi măng (Nội thất, Ngoại thất Extra,
  Hộp Nội & Ngoại thất), keo chà ron màu, keo chà ron Epoxy.
- 5 câu tự luận (KHÔNG chấm điểm): HR xem bài làm cạnh đáp án tham khảo trong Admin > Kết quả.

Chạy:
    python seed_quiz_ron_epoxy.py            # tạo đề (bỏ qua nếu slug đã tồn tại)
    python seed_quiz_ron_epoxy.py --update   # cập nhật nội dung đề đã có, GIỮ kết quả đã làm
    python seed_quiz_ron_epoxy.py --replace  # xóa đề cũ cùng slug (kể cả kết quả đã làm) rồi tạo lại

Yêu cầu: đã chạy `flask db upgrade` (migration a7c3e91d2b40 - câu tự luận).
"""
import sys

from app import create_app, db
from app.models.quiz import Quiz, Question, Answer

QUIZ_SLUG = 'kien-thuc-keo-cha-ron-epoxy-bricon'
QUIZ_TITLE = 'Kiến thức sản phẩm – Keo chà ron & Epoxy Bricon'
QUIZ_DESCRIPTION = (
    'Gồm 45 câu trắc nghiệm về keo chà ron gốc xi măng, keo chà ron màu và keo chà ron Epoxy Bricon, '
    'cùng 5 câu tự luận về tư vấn sản phẩm. Phần tự luận không tính điểm, bộ phận nhân sự sẽ xem xét riêng.'
)

# (câu hỏi, [A, B, C, D], đáp án đúng, căn cứ/giải thích)
MULTIPLE_CHOICE = [
    # ===================== KEO CHÀ RON GỐC XI MĂNG =====================
    ('Thành phần chính của keo chà ron gốc xi măng Bricon là:',
     ['Cát vàng sàng mịn, xi măng xám, vôi bột',
      'CaCO₃, xi măng trắng cao cấp, phụ gia đặc biệt',
      'Nhựa epoxy, chất đóng rắn và bột màu chịu UV cao',
      'Silica 200 mesh, nhựa acrylic, chất bảo quản'], 'B',
     'TDS: sản xuất từ CaCO₃, xi măng trắng cao cấp và phụ gia đặc biệt.'),
    ('Keo chà ron gốc xi măng Bricon đạt tiêu chuẩn nào?',
     ['TCVN 7899-1:2008', 'TCVN 12692:2020', 'TCVN 7899-3:2008', 'TCVN 6415:2016'], 'C',
     'TDS: đạt tiêu chuẩn TCVN 7899-3:2008.'),
    ('Định mức sử dụng keo chà ron gốc xi măng Bricon khoảng:',
     ['1 kg/m²', '1 kg/2 m²', '1 kg/10 m²', '1 kg/5 m²'], 'D',
     'TDS: định mức sử dụng ~1 kg/5 m².'),
    ('Độ rộng mạch ron phù hợp với keo chà ron gốc xi măng Bricon:',
     ['1–6 mm', 'Dưới 0,5 mm', '8–15 mm', 'Trên 15 mm'], 'A',
     'TDS: độ rộng mạch ron 1–6 mm.'),
    ('Sau khi pha, keo chà ron phải được trộn và sử dụng hết trong khoảng:',
     ['5 phút', '30 phút', '2 giờ', 'Trong cả ngày'], 'B',
     'TDS: thời gian trộn & sử dụng 30 phút.'),
    ('Sau khi chà ron xong, phải chờ ít nhất bao lâu mới đưa vào sử dụng hoặc lưu thông?',
     ['1 giờ', '6 giờ', '24 giờ', '7 ngày'], 'C',
     'TDS: chờ ít nhất 24 giờ trước khi đưa vào sử dụng hoặc lưu thông.'),
    ('Gạch vừa dán bằng keo dán gạch Bricon. Phải chờ ít nhất bao lâu mới được chà ron?',
     ['2 giờ', '24 giờ', '3 ngày', '7 ngày'], 'B',
     'TDS keo dán gạch: chờ ít nhất 24 giờ trước khi chà ron.'),
    ('Việc đầu tiên cần làm trước khi chà ron là:',
     ['Làm sạch và để khô mạch ron',
      'Tưới đẫm nước cho mạch ron thật ướt',
      'Quét một lớp chống thấm vào mạch',
      'Phủ dầu chống dính lên mặt gạch'], 'A',
     'TDS: làm sạch và để khô mạch ron trước khi thi công.'),
    ('Cách ép keo chà ron vào mạch đúng theo TDS:',
     ['Bay răng cưa, kéo dọc theo mạch gạch',
      'Chổi quét, quét vuông góc mạch gạch',
      'Tay đeo găng, miết dọc từng đoạn mạch',
      'Bay cao su, kéo chéo với mạch gạch'], 'D',
     'TDS: dùng bay cao su ép keo vào mạch ron theo đường chéo với mạch gạch.'),
    ('Keo chà ron thừa trên mặt gạch được loại bỏ bằng:',
     ['Giấy nhám khi keo đã khô', 'Axit tẩy rửa pha loãng',
      'Miếng xốp hoặc khăn ẩm', 'Để khô rồi cạo bằng dao'], 'C',
     'TDS: loại bỏ phần keo thừa bằng miếng xốp hoặc khăn ẩm.'),
    ('Lưu ý nào đúng khi pha keo chà ron?',
     ['Pha thật loãng cho keo dễ chảy sâu vào trong mạch',
      'Không pha quá loãng vì sẽ giảm chất lượng',
      'Pha thêm xi măng trắng để ron cứng hơn',
      'Pha sẵn từ hôm trước để keo ngấm đều'], 'B',
     'TDS: lưu ý không pha quá loãng sẽ làm giảm chất lượng sản phẩm.'),
    ('Keo chà ron Bricon cần được bảo quản thế nào?',
     ['Nơi khô ráo, tránh ánh nắng trực tiếp',
      'Để ngoài trời, che bạt để bao keo thoáng khí',
      'Nơi ẩm mát để keo không bị vón cục',
      'Trong tủ lạnh ở nhiệt độ thấp'], 'A',
     'TDS: bảo quản nơi khô ráo, tránh ánh nắng trực tiếp.'),
    ('Keo chà ron Nội thất (túi 1 kg) KHÔNG nên dùng cho khu vực nào?',
     ['Sàn phòng khách lát gạch men', 'Tường phòng ngủ ốp gạch mosaic',
      'Sàn nội thất chịu ẩm nhẹ', 'Khu thường xuyên tiếp xúc nước'], 'D',
     'TDS ron Nội thất: không sử dụng cho khu vực thường xuyên tiếp xúc nước hoặc yêu cầu chống thấm cao.'),
    ('Quy cách đóng gói của keo chà ron Nội thất và Ngoại thất Extra:',
     ['Túi 1 kg, thùng 24 túi', 'Túi 5 kg, thùng 4 túi',
      'Hộp 1 kg, thùng 30 hộp', 'Bao 25 kg, không có túi nhỏ'], 'A',
     'TDS: túi 1 kg – thùng 24 túi.'),
    ('Quy cách đóng gói của keo chà ron Hộp Nội & Ngoại thất:',
     ['Hộp 2 kg, thùng 12 hộp', 'Hộp 1 kg, thùng 30 hộp',
      'Túi 1 kg, thùng 24 túi', 'Hộp 5 kg, thùng 4 hộp'], 'B',
     'TDS: hộp 1 kg – thùng 30 hộp.'),
    ('Theo TDS, ron Ngoại thất Extra và ron Hộp Nội & Ngoại thất thích hợp cho:',
     ['Chỉ tường và sàn nội thất khô ráo, không ẩm',
      'Chỉ dùng chà ron gạch men, không dùng cho đá',
      'Hồ bơi, xông hơi, WC, kho lạnh, sân thượng',
      'Chỉ khu khô trong nhà, không chịu được ẩm cao'], 'C',
     'TDS: thích hợp cho hồ bơi, phòng xông hơi, WC, kho lạnh, sân thượng...'),
    ('Keo chà ron gốc xi măng Bricon dùng được cho những bề mặt nào?',
     ['Chỉ gạch men, không dùng cho gạch thẻ hay đá tự nhiên',
      'Gạch men, sứ, granite, mosaic, đá cẩm thạch',
      'Chỉ đá tự nhiên, không dùng cho gạch men',
      'Chỉ gạch mosaic kích thước nhỏ dưới 5 cm'], 'B',
     'TDS: gạch men, sứ, granite, gạch tàu, gạch khảm, mosaic, đá cẩm thạch và các loại đá tự nhiên.'),
    ('Tính năng của keo chà ron gốc xi măng Bricon theo TDS:',
     ['Kháng axit mạnh, chịu hóa chất công nghiệp',
      'Dùng được cho mạch ron rộng 10–20 mm',
      'Tự làm sạch, không cần lau keo thừa',
      'Độ mịn cao, ron bóng đẹp, chống nấm mốc'], 'D',
     'TDS: độ mịn cao, bề mặt ron bóng đẹp, chống nấm mốc, bám bẩn.'),
    ('Hạn sử dụng của keo chà ron Bricon tính từ ngày sản xuất là:',
     ['6 tháng', '12 tháng', '24 tháng', '36 tháng'], 'B',
     'Hạn sử dụng 12 tháng kể từ ngày sản xuất.'),
    ('So với ron Nội thất, ron Ngoại thất Extra khác ở điểm nào?',
     ['Chịu ẩm cao, dùng được ngoại thất, hồ bơi',
      'Thi công bằng súng bơm, tỉ lệ trộn 1:1',
      'Không cần chờ 24 giờ trước khi đưa vào lưu thông',
      'Dùng được cho mạch ron rộng đến 15 mm'], 'A',
     'TDS Extra: bám dính vượt trội, chịu mài mòn cao, dùng cho ngoại thất và khu vực chịu ẩm cao.'),
    ('Sàn 60 m², mạch ron 3 mm. Theo định mức TDS cần khoảng bao nhiêu kg keo chà ron?',
     ['6 kg', '12 kg', '30 kg', '60 kg'], 'B',
     'Định mức ~1 kg/5 m² → 60 ÷ 5 = 12 kg.'),

    # ===================== KEO CHÀ RON MÀU =====================
    ('Keo chà ron màu Bricon khác keo chà ron thường ở điểm nào?',
     ['Chỉ khác màu sắc, cách dùng như ron thường',
      'Có tỉ lệ trộn khác, phải pha nhiều nước hơn',
      'Phải thi công bằng súng bơm như Epoxy',
      'Định mức gấp đôi do có thêm bột màu'], 'A',
     'Ron màu chỉ khác màu sắc; thành phần, cách thi công, định mức, thời gian như ron thường.'),
    ('Định mức và thời gian chờ của keo chà ron màu là:',
     ['Định mức 1 kg/2 m², chờ 48 giờ mới lưu thông',
      'Như ron thường: ~1 kg/5 m², chờ 24 giờ',
      'Định mức 1 kg/10 m², lưu thông sau 6 giờ',
      'Tùy màu, màu đậm tốn keo gấp đôi màu nhạt'], 'B',
     'Ron màu thi công và định mức như ron thường: ~1 kg/5 m², chờ 24 giờ.'),
    ('Theo bảng mã màu, keo chà ron màu Bricon có bao nhiêu màu?',
     ['12 màu', '20 màu', '28 màu', '40 màu'], 'C',
     'Bảng màu gồm 28 mã, đánh số từ 3 đến 30.'),
    ('Keo chà ron màu Bricon đặc biệt phù hợp với loại gạch nào?',
     ['Gạch giả gỗ, vân đá, mosaic nhiều màu',
      'Chỉ gạch men trắng trơn ốp trong nhà tắm',
      'Chỉ đá granite đen bóng khổ lớn ngoài trời',
      'Chỉ khu ngoại thất sân vườn, không dùng trong nhà'], 'A',
     'Bảng màu: phù hợp cho gạch giả gỗ, vân đá, mosaic nhiều màu sắc.'),
    ('Keo chà ron màu Bricon dùng được ở khu vực nào?',
     ['Chỉ trong nhà, khu khô ráo', 'Chỉ ngoài trời, khu sân vườn',
      'Cả nội thất và ngoại thất', 'Chỉ khu ướt như hồ bơi, WC'], 'C',
     'Bảng màu: dùng cho khu vực nội và ngoại thất.'),
    ('Để màu ron sau khi khô đúng ý khách, nên làm gì trước khi chà cả công trình?',
     ['Thử trên gạch thừa, chờ khô rồi mới chọn màu',
      'Chọn theo ảnh màu trên điện thoại, không cần thử',
      'Pha thêm bột màu ngoài để màu đậm hơn',
      'Pha loãng hơn để màu ron sáng và đều hơn'], 'A',
     'Màu ron khi ướt và khi khô có thể khác nhau; thử trên gạch thừa để khách duyệt màu thật.'),
    ('Để màu ron đều nhau giữa các mẻ trộn, cần lưu ý:',
     ['Mỗi mẻ pha lượng nước khác nhau cho dễ trộn',
      'Trộn đều, giữ cùng tỉ lệ nước cho mọi mẻ',
      'Pha mẻ sau loãng hơn để dễ miết vào mạch',
      'Trộn lẫn các mã màu gần nhau cho đủ keo'], 'B',
     'Lượng nước khác nhau làm màu ron loang, không đều giữa các mẻ.'),
    ('Khách lát gạch giả gỗ tông nâu và muốn mạch ron "chìm", ít lộ. Bạn tư vấn:',
     ['Chọn màu ron tương phản mạnh, như trắng',
      'Chọn màu ron gần với tông nâu của gạch',
      'Bắt buộc dùng ron trắng nội thất',
      'Không cần chà ron cho gạch giả gỗ'], 'B',
     'Màu ron gần tông gạch giúp mạch ron chìm, bề mặt liền như sàn gỗ.'),

    # ===================== KEO CHÀ RON EPOXY =====================
    ('Keo chà ron Epoxy Bricon có quy cách và tỉ lệ trộn:',
     ['Túi 1 kg dạng bột, trộn với nước',
      'Hộp 1 kg, trộn tay theo tỉ lệ 3:1',
      'Tuýp 380 ml, 2 thành phần, tỉ lệ 1:1',
      'Lon 5 kg, pha thêm dung môi khi dùng'], 'C',
     'TDS Epoxy: dung tích 380 ml, 2 thành phần, tỉ lệ trộn 1:1.'),
    ('Ký hiệu "VOC Free" trên Epoxy Bricon có nghĩa là:',
     ['Không chứa hợp chất hữu cơ bay hơi độc hại',
      'Pha được với nước nên không có mùi hóa chất',
      'Không cần đeo găng tay khi thi công',
      'Có thể pha dung môi để giảm mùi'], 'A',
     'Tên sản phẩm: BRICON Epoxy Grout – VOC Free.'),
    ('Khi bắt đầu bơm Epoxy, vì sao phải bỏ khoảng 10 g keo đầu tiên?',
     ['Để tiết kiệm keo cho khe ron hẹp', 'Vì keo ở đầu vòi đã bị đông cứng',
      'Để làm ướt và làm sạch khe ron trước', 'Để hai thành phần được trộn đều'], 'D',
     'TDS Epoxy: thải bỏ khoảng 10 g keo đầu để đảm bảo trộn đều.'),
    ('Đang bơm Epoxy thì ngừng hơn 20 phút. Cần làm gì trước khi bơm tiếp?',
     ['Thay vòi trộn mới, keo trong vòi có thể đông',
      'Bơm mạnh tay hơn để đẩy keo cũ ra ngoài',
      'Pha thêm dung môi vào vòi cho keo loãng ra',
      'Không cần làm gì, keo trong vòi không bao giờ đông'], 'A',
     'TDS Epoxy: ngừng thi công trên 20 phút, keo trong vòi có thể đông – thay vòi mới.'),
    ('Thứ tự chuẩn bị tuýp Epoxy trước khi bơm:',
     ['Cắt đầu vòi, lắp vòi trộn, đặt vào súng bơm',
      'Đổ keo ra xô, trộn tay rồi múc vào khe',
      'Pha hai thành phần với nước rồi mới bơm vào',
      'Lắc mạnh tuýp keo rồi bóp trực tiếp'], 'A',
     'TDS Epoxy: cắt đầu vòi, lắp vòi trộn, đặt vào súng bơm.'),
    ('Khi bơm Epoxy vào khe ron, thao tác đúng là:',
     ['Bơm thật nhanh cho kịp, chấp nhận có bọt khí trong ron',
      'Bơm đều tay, tránh tạo bọt khí trong ron',
      'Bơm ngắt quãng, mỗi lần cách 30 phút',
      'Bơm đầy tràn mặt gạch rồi để khô'], 'B',
     'TDS Epoxy: bơm keo đều tay vào khe ron, tránh tạo bọt khí.'),
    ('Sau khi bơm và miết tạo hình ron Epoxy, khi nào tháo băng keo và vệ sinh?',
     ['Ngay sau khi bơm xong', 'Sau 4–5 giờ', 'Sau 24 giờ', 'Sau 3 ngày'], 'B',
     'TDS Epoxy: sau 4–5 giờ tháo băng và vệ sinh.'),
    ('Ron Epoxy đạt độ cứng tối đa sau bao lâu?',
     ['1 giờ', '6 giờ', '24 giờ', '7 ngày'], 'C',
     'TDS Epoxy: sau 24 giờ đạt độ cứng tối đa.'),
    ('Khe ron trước khi bơm Epoxy cần ở trạng thái nào?',
     ['Còn ướt để keo bám tốt hơn', 'Sạch và khô ráo',
      'Phủ một lớp dầu chống dính', 'Còn bụi cũng được, keo sẽ phủ'], 'B',
     'TDS Epoxy: làm sạch khe ron, khô ráo.'),
    ('Keo Epoxy dính lên mặt gạch khi còn ướt, xử lý thế nào?',
     ['Lau ngay bằng khăn sạch', 'Để khô rồi cạo bằng dao',
      'Tẩy bằng axit pha loãng', 'Lau bằng xăng thơm'], 'A',
     'TDS Epoxy: khi còn ướt lau ngay bằng khăn sạch.'),
    ('Keo Epoxy đã khô cứng trên mặt gạch, xử lý thế nào?',
     ['Tẩy bằng axit đậm đặc cho nhanh',
      'Lau bằng dung môi tẩy sơn chuyên dụng',
      'Để nguyên, keo sẽ tự bong theo thời gian',
      'Dụng cụ cơ học, máy mài, không hỏng gạch'], 'D',
     'TDS Epoxy: khi đã khô dùng dụng cụ cơ học, máy mài, không làm hỏng bề mặt gạch.'),
    ('Theo TDS, keo chà ron Epoxy Bricon dùng cho khu vực nào?',
     ['Nhà tắm, bếp, ban công, hồ bơi, thương mại',
      'Chỉ khu nội thất khô ráo như phòng ngủ, phòng khách',
      'Chỉ dùng cho gạch men, không dùng cho đá',
      'Chỉ dùng để dán gạch, không dùng chà ron'], 'A',
     'TDS Epoxy: tường và sàn nội, ngoại thất – nhà tắm, bếp, ban công, hồ bơi, khu thương mại.'),
    ('Keo chà ron Epoxy Bricon phù hợp với vật liệu nào?',
     ['Chỉ gạch men, không dùng cho đá', 'Gạch men, đá tự nhiên, mosaic',
      'Chỉ đá granite, không dùng mosaic', 'Chỉ gạch thẻ ốp ngoại thất'], 'B',
     'TDS Epoxy: phù hợp gạch men, đá tự nhiên, mosaic và nhiều vật liệu ốp lát khác.'),
    ('Cảnh báo an toàn đúng khi dùng Epoxy Bricon:',
     ['Tránh tiếp xúc mắt, da; để xa trẻ em',
      'An toàn tuyệt đối, không cần đồ bảo hộ khi thi công',
      'Có thể pha dung môi nếu keo quá đặc',
      'Rửa tay bằng xăng sau khi thi công'], 'A',
     'TDS Epoxy: tránh tiếp xúc mắt/da, không nuốt hoặc hít hơi/bụi, để xa tầm tay trẻ em; luôn đeo găng tay và bảo hộ.'),
    ('Khách hỏi vì sao Epoxy đắt hơn ron xi măng. Câu trả lời đúng nhất:',
     ['Vì Epoxy pha được nhiều nước nên dùng lâu hơn',
      'Vì Epoxy không thấm, kháng hóa chất, khó bám bẩn',
      'Vì Epoxy không cần làm sạch khe trước khi bơm',
      'Vì Epoxy dùng được cả để dán gạch lẫn chà ron gạch'], 'B',
     'TDS Epoxy: chống thấm vượt trội, không hóa chất, chống rêu mốc, màu bền, khó bám bẩn, độ bền cơ học cao.'),
    ('Bếp nhà hàng nhiều dầu mỡ và chất tẩy rửa. Nên tư vấn loại ron nào?',
     ['Ron Nội thất (túi)', 'Ron Ngoại thất Extra', 'Keo chà ron Epoxy', 'Xi măng trắng pha nước'], 'C',
     'Epoxy kháng hóa chất, khó bám bẩn, phù hợp bếp và khu thương mại.'),
]

# (câu hỏi, đáp án tham khảo cho HR)
ESSAYS = [
    ('Tự luận – Chọn đúng loại ron:\n'
     'Một khách xây nhà có 4 khu vực cần chà ron: (1) sàn phòng khách gạch men, (2) khu tắm đứng trong WC, '
     '(3) hồ bơi ngoài trời, (4) bếp nhà hàng. Với mỗi khu vực, bạn tư vấn loại keo chà ron Bricon nào và vì sao?',
     '(1) Phòng khách: ron Nội thất (túi) – khu nội thất khô ráo, tiết kiệm chi phí; có thể dùng ron màu nếu khách muốn hợp tông gạch.\n'
     '(2) Khu tắm đứng: ron Ngoại thất Extra hoặc Hộp N&N (TDS ghi dùng cho WC); nên tư vấn nâng cấp Epoxy vì không thấm, chống rêu mốc, khó bám bẩn. '
     'Không dùng ron Nội thất vì TDS ghi không dùng cho khu thường xuyên tiếp xúc nước.\n'
     '(3) Hồ bơi: ron Ngoại thất Extra / Hộp N&N (TDS ghi thích hợp hồ bơi) hoặc Epoxy (TDS có hồ bơi trong phạm vi dùng).\n'
     '(4) Bếp nhà hàng: Epoxy – kháng hóa chất, chịu dầu mỡ và chất tẩy rửa, khó bám bẩn.\n'
     'Gợi ý đánh giá: chọn đúng 4 khu, nêu được lý do bám theo TDS, biết tư vấn nâng cấp Epoxy ở khu ướt.'),
    ('Tự luận – Quy trình thi công Epoxy:\n'
     'Hãy trình bày từng bước thi công keo chà ron Epoxy Bricon từ lúc chuẩn bị đến khi hoàn thiện, '
     'và nêu ít nhất 3 lỗi thợ hay mắc khi thi công Epoxy.',
     'Các bước theo TDS:\n'
     '1) Làm sạch khe ron, để khô ráo (có thể dán băng keo bảo vệ mép gạch).\n'
     '2) Cắt đầu vòi, lắp vòi trộn, đặt tuýp vào súng bơm.\n'
     '3) Thải bỏ khoảng 10 g keo đầu để đảm bảo hai thành phần trộn đều.\n'
     '4) Bơm keo đều tay vào khe ron, tránh tạo bọt khí.\n'
     '5) Miết tạo hình ron; sau 4–5 giờ tháo băng và vệ sinh.\n'
     '6) Sau 24 giờ ron đạt độ cứng tối đa.\n'
     'Lỗi hay gặp: không bỏ keo đầu → ron không đông, loang màu; ngừng > 20 phút không thay vòi → keo đông trong vòi; '
     'pha dung môi (TDS cấm); bơm vào khe ướt, bẩn; không lau keo khi còn ướt → khô cứng trên mặt gạch, phải mài; '
     'không đeo găng tay, bảo hộ.'),
    ('Tự luận – Tư vấn keo chà ron màu:\n'
     'Khách lát sàn gạch giả gỗ cho phòng ngủ và ốp mosaic nhiều màu cho khu bếp, muốn dùng keo chà ron màu Bricon. '
     'Khách hỏi: "Ron màu có gì khác ron thường, có bền bằng không?" Hãy trả lời khách và tư vấn cách chọn màu, '
     'những lưu ý khi thi công để màu ron đẹp, đều.',
     'Trả lời: ron màu chỉ khác màu sắc; thành phần, độ bền, cách thi công, định mức (~1 kg/5 m², mạch 1–6 mm), '
     'thời gian sử dụng sau khi pha (30 phút) và thời gian chờ (24 giờ) giống ron thường. Bảng màu có 28 mã (số 3–30), '
     'phù hợp gạch giả gỗ, vân đá, mosaic nhiều màu, dùng được cả nội và ngoại thất.\n'
     'Chọn màu: gạch giả gỗ chọn màu gần tông gỗ để mạch ron chìm; mosaic nhiều màu chọn màu trung tính hoặc màu chủ đạo của mảng mosaic; '
     'cho khách xem bảng màu và thử trên gạch thừa, chờ khô rồi mới chốt vì màu khi ướt và khi khô có thể khác.\n'
     'Thi công: mạch sạch, khô; giữ cùng tỉ lệ nước cho mọi mẻ để màu đều; không pha quá loãng; bay cao su kéo chéo; '
     'lau keo thừa bằng xốp ẩm; mua đủ số lượng một lần cùng mã màu.'),
    ('Tự luận – Tính số lượng và quy cách mua:\n'
     'Căn hộ có sàn phòng khách và phòng ngủ tổng 90 m² (gạch 60×60, mạch ron 2 mm) và 2 phòng vệ sinh tổng 30 m² '
     '(sàn + tường). Hãy chọn loại keo chà ron Bricon cho từng khu, tính số lượng và quy đổi ra số túi/hộp/thùng cần mua.',
     'Phòng khách + phòng ngủ: ron Nội thất (túi 1 kg). 90 ÷ 5 = 18 kg → 18 túi; cộng hao hụt 5–10% → khoảng 19–20 túi '
     '(hoặc lấy 1 thùng 24 túi nếu khách muốn dư để sửa sau).\n'
     'Phòng vệ sinh: ron Ngoại thất Extra (túi 1 kg) hoặc ron Hộp N&N (hộp 1 kg). 30 ÷ 5 = 6 kg → 6 túi/hộp; cộng hao hụt → khoảng 7.\n'
     'Tư vấn thêm: khu tắm đứng có thể nâng cấp Epoxy; nếu dùng ron màu thì tính như ron thường và nên mua đủ một lần cùng mã màu.\n'
     'Điểm trừ: dùng ron Nội thất cho WC; tính sai định mức (định mức TDS ~1 kg/5 m²).'),
    ('Tự luận – Khách hàng thực tế:\n'
     'Một chủ nhà ghé cửa hàng đại lý, cầm túi keo chà ron Bricon và tuýp Epoxy Bricon lên xem. '
     'Theo bạn, khách hàng thường sẽ NÓI gì, HỎI gì và LÀM gì với sản phẩm? Hãy nêu ít nhất 6 tình huống '
     'và cách bạn trả lời / xử lý từng tình huống.',
     'Ví dụ các tình huống thực tế và cách xử lý:\n'
     '1) Hỏi: "Ron này có bị đen, ố như ron cũ nhà tôi không?" → Hỏi ron cũ ở khu nào; giải thích ron đen thường do dùng sai loại cho khu ẩm, '
     'pha loãng, vệ sinh kém; tư vấn đúng loại (Extra/Hộp cho WC, Epoxy cho khu ướt nhiều); ron Bricon chống nấm mốc, Epoxy khó bám bẩn.\n'
     '2) Nói: "Epoxy đắt quá, ron thường được không?" → Khu khô dùng ron thường cho tiết kiệm; khu tắm đứng, bếp nên dùng Epoxy vì không thấm, '
     'kháng hóa chất, màu bền – đỡ chi phí sửa về sau.\n'
     '3) Hỏi: "Màu thật có giống bảng màu không?" → Bảng màu in chỉ để tham khảo; cho xem mẫu thật nếu có, khuyên thử trên gạch thừa, chờ khô rồi chọn.\n'
     '4) Hỏi: "Nhà tôi cần mua bao nhiêu?" → Hỏi diện tích, khổ gạch, độ rộng mạch; tính theo định mức ~1 kg/5 m² (mạch 1–6 mm), cộng hao hụt; '
     'quy ra túi/hộp/thùng.\n'
     '5) Hỏi: "Tôi tự chà được không?" → Ron xi măng tự làm được nếu đúng bước (mạch sạch khô, pha đúng nước, bay cao su kéo chéo, lau xốp ẩm, chờ 24 giờ); '
     'Epoxy cần súng bơm và kỹ thuật, nên để thợ làm.\n'
     '6) Hỏi: "Ron cũ bị ố, chà đè lên được không?" → Không chà đè; phải cạo bỏ ron cũ, vệ sinh, để khô rồi mới chà.\n'
     '7) Làm: lật bao bì xem ngày sản xuất, hạn dùng → chỉ NSX in trên bao bì, HSD 12 tháng kể từ NSX.\n'
     '8) Làm: chụp ảnh gửi thợ quen, so giá với hãng khác, mặc cả → không chê hãng khác; nêu điểm mạnh có căn cứ (TCVN 7899-3, chống nấm mốc, '
     'Epoxy VOC Free); để lại thông tin, hướng dẫn thợ nếu cần.\n'
     '9) Hỏi: "Chà xong bao lâu thì dùng được?" → Ron xi măng chờ 24 giờ mới lưu thông; Epoxy cứng tối đa sau 24 giờ.\n'
     'Gợi ý đánh giá: nêu được tình huống sát thực tế, trả lời đúng thông số TDS, thái độ tư vấn chủ động, không chê đối thủ.'),
]


def seed(replace=False):
    existing = Quiz.query.filter_by(slug=QUIZ_SLUG).first()
    if existing:
        if not replace:
            print(f'⚠️  Đề "{QUIZ_SLUG}" đã tồn tại (id={existing.id}). '
                  f'Dùng --update để cập nhật nội dung hoặc --replace để xóa và tạo lại.')
            return
        db.session.delete(existing)
        db.session.commit()
        print(f'🗑️  Đã xóa đề cũ id={existing.id}')

    quiz = Quiz(
        title=QUIZ_TITLE,
        slug=QUIZ_SLUG,
        description=QUIZ_DESCRIPTION,
        duration_minutes=60,
        pass_score=70,
        show_correct_answers=False,  # Không lộ đáp án cho người làm sau; bật trong Admin nếu dùng để ôn tập
        shuffle_questions=False,     # Giữ thứ tự: ron xi măng → ron màu → Epoxy → tự luận
        shuffle_answers=True,
        category='San-pham',
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


def update():
    """
    Cập nhật nội dung đề đã có theo dữ liệu trong file này mà KHÔNG xóa kết quả đã làm.
    Ghép theo thứ tự câu hỏi và thứ tự đáp án (giữ nguyên id), nên chỉ dùng khi
    số câu, loại câu và vị trí đáp án đúng không đổi.
    """
    quiz = Quiz.query.filter_by(slug=QUIZ_SLUG).first()
    if not quiz:
        print(f'⚠️  Chưa có đề "{QUIZ_SLUG}". Chạy không kèm tham số để tạo đề.')
        return

    questions = quiz.questions.order_by(Question.order, Question.id).all()
    expected = [('multiple_choice', item) for item in MULTIPLE_CHOICE] + [('essay', item) for item in ESSAYS]
    if len(questions) != len(expected):
        print(f'❌ Đề hiện có {len(questions)} câu, dữ liệu mới có {len(expected)} câu. '
              f'Không cập nhật được – dùng --replace nếu chấp nhận xóa kết quả cũ.')
        return

    changed = 0
    for q, (qtype, item) in zip(questions, expected):
        if (q.question_type == 'essay') != (qtype == 'essay'):
            print(f'❌ Câu id={q.id} khác loại với dữ liệu mới. Dừng, không thay đổi gì.')
            db.session.rollback()
            return

        if qtype == 'essay':
            text, model_answer = item
            if (q.question_text, q.model_answer) != (text, model_answer):
                q.question_text, q.model_answer = text, model_answer
                changed += 1
            continue

        text, options, correct, explanation = item
        answers = q.answers.order_by(Answer.order, Answer.id).all()
        if len(answers) != len(options):
            print(f'❌ Câu id={q.id} có {len(answers)} đáp án, dữ liệu mới có {len(options)}. Dừng, không thay đổi gì.')
            db.session.rollback()
            return
        old_correct = next((i for i, a in enumerate(answers) if a.is_correct), None)
        if old_correct != 'ABCD'.index(correct):
            print(f'❌ Câu id={q.id}: vị trí đáp án đúng thay đổi – cập nhật sẽ làm sai kết quả cũ. Dừng.')
            db.session.rollback()
            return

        dirty = (q.question_text, q.explanation) != (text, explanation)
        q.question_text, q.explanation = text, explanation
        for a, opt in zip(answers, options):
            if a.answer_text != opt:
                a.answer_text = opt
                dirty = True
        changed += dirty

    db.session.commit()
    print(f'✅ Đã cập nhật {changed} câu của đề "{quiz.title}" (id={quiz.id}); kết quả đã làm được giữ nguyên.')


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        if '--update' in sys.argv:
            update()
        else:
            seed(replace='--replace' in sys.argv)
