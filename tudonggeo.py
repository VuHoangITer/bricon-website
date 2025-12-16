"""
Script dùng Nominatim (OpenStreetMap) để geocode - MIỄN PHÍ 100%
Ổn định hơn Google search và không bị block
"""

import re
import urllib.parse
from app import create_app, db
from app.models.distributor import Distributor
import requests
import time

# =====================================================
# CẤU HÌNH
# =====================================================
DRY_RUN = False
DELAY = 1.5

# =====================================================
# FUNCTIONS
# =====================================================

def extract_address_from_iframe(iframe_code):
    """Extract địa chỉ từ iframe"""
    if not iframe_code:
        return None

    # Pattern: ?q={address}
    match = re.search(r'\?q=([^&"]+)', iframe_code)
    if match:
        encoded = match.group(1)
        return urllib.parse.unquote(encoded)
    return None


def geocode_nominatim(address):
    """
    Dùng Nominatim (OpenStreetMap) để geocode
    Miễn phí, ổn định, không cần API key
    """
    if not address:
        return None

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'vn',  # Chỉ tìm ở Việt Nam
        'addressdetails': 1
    }

    headers = {
        'User-Agent': 'BriconWebsite/1.0 (distributor-geocoding)'  # Nominatim yêu cầu User-Agent
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if data and len(data) > 0:
                result = data[0]
                lat = float(result['lat'])
                lon = float(result['lon'])

                # Kiểm tra tọa độ Việt Nam
                if 8 <= lat <= 24 and 102 <= lon <= 110:
                    return (lat, lon)

    except Exception as e:
        print(f"   ❌ Nominatim error: {str(e)}")

    return None


def extract_coords_from_embed(iframe_code):
    """Extract tọa độ trực tiếp từ iframe nếu có"""
    if not iframe_code:
        return None

    patterns = [
        r'!3d(-?\d+\.?\d*)!4d(-?\d+\.?\d*)',
        r'!2d(-?\d+\.?\d*)!3d(-?\d+\.?\d*)',
        r'@(-?\d+\.?\d*),(-?\d+\.?\d*)',
    ]

    for i, pattern in enumerate(patterns):
        match = re.search(pattern, iframe_code)
        if match:
            if i == 1:  # Pattern !2d!3d (đảo ngược)
                coords = (float(match.group(2)), float(match.group(1)))
            else:
                coords = (float(match.group(1)), float(match.group(2)))

            if 8 <= coords[0] <= 24 and 102 <= coords[1] <= 110:
                return coords

    return None


def simplify_address(address):
    """
    Đơn giản hóa địa chỉ để dễ tìm hơn
    Loại bỏ số nhà chi tiết, giữ lại đường/xã/huyện/tỉnh
    """
    if not address:
        return address

    # Tách theo dấu phẩy
    parts = [p.strip() for p in address.split(',')]

    # Nếu có từ 3 phần trở lên, bỏ phần đầu (số nhà chi tiết)
    if len(parts) >= 3:
        # Giữ lại các phần có từ khóa địa lý
        keywords = ['Xã', 'Phường', 'Huyện', 'Quận', 'Thành phố', 'Tỉnh', 'TP']
        filtered = []

        for part in parts:
            if any(kw in part for kw in keywords):
                filtered.append(part)

        if filtered:
            return ', '.join(filtered)

    return address


def process_distributor(dist, index, total):
    """Xử lý 1 distributor"""
    print(f"\n[{index}/{total}] 📍 {dist.name}")
    print(f"   ID: {dist.id}")

    full_addr = dist.get_full_address()
    print(f"   Địa chỉ: {full_addr[:80]}")

    # Kiểm tra đã có tọa độ chưa
    if dist.latitude and dist.longitude:
        print(f"   ✅ Đã có tọa độ: {dist.latitude:.6f}, {dist.longitude:.6f}")
        return True

    if not dist.map_iframe:
        print("   ⚠️  Không có iframe")
        return False

    # Bước 1: Thử extract trực tiếp từ iframe
    coords = extract_coords_from_embed(dist.map_iframe)

    if coords:
        print(f"   ✅ Extract từ iframe: {coords[0]:.6f}, {coords[1]:.6f}")
        if not DRY_RUN:
            dist.latitude = coords[0]
            dist.longitude = coords[1]
            db.session.commit()
            print("   💾 Đã lưu")
        return True

    # Bước 2: Extract địa chỉ từ iframe
    address = extract_address_from_iframe(dist.map_iframe)

    if not address:
        address = full_addr

    if address:
        # Thử với địa chỉ đầy đủ
        print(f"   🔍 Nominatim (đầy đủ): {address[:60]}...")
        coords = geocode_nominatim(address)

        # Nếu không tìm thấy, thử địa chỉ đơn giản hơn
        if not coords:
            simple_addr = simplify_address(address)
            if simple_addr != address:
                print(f"   🔍 Nominatim (đơn giản): {simple_addr[:60]}...")
                coords = geocode_nominatim(simple_addr)

        if coords:
            print(f"   ✅ Tìm thấy: {coords[0]:.6f}, {coords[1]:.6f}")
            if not DRY_RUN:
                dist.latitude = coords[0]
                dist.longitude = coords[1]
                db.session.commit()
                print("   💾 Đã lưu")
            time.sleep(DELAY)
            return True
        else:
            print("   ❌ Không tìm thấy")
    else:
        print("   ❌ Không có địa chỉ")

    time.sleep(DELAY)
    return False


def main():
    """Main function"""
    app = create_app()

    with app.app_context():
        print("=" * 70)
        print("🗺️  EXTRACT TỌA ĐỘ DÙNG NOMINATIM (OpenStreetMap)")
        print("=" * 70)
        print(f"Chế độ: {'🔍 DRY RUN' if DRY_RUN else '💾 CẬP NHẬT THẬT'}")
        print(f"Delay: {DELAY}s giữa mỗi request")
        print("-" * 70)

        # Lấy distributors chưa có tọa độ
        query = Distributor.query.filter(
            db.or_(
                Distributor.latitude.is_(None),
                Distributor.longitude.is_(None)
            )
        )

        distributors = query.all()
        total = len(distributors)

        print(f"\n📊 Tìm thấy {total} nhà phân phối cần xử lý")

        if total == 0:
            print("✅ Tất cả đã có tọa độ!")
            return

        if DRY_RUN:
            print("\n⚠️  Đang chạy DRY RUN - chỉ xem không cập nhật")
            print("   Đổi DRY_RUN = False để cập nhật database\n")

            # Test với 5 cái đầu
            distributors = distributors[:5]
            print(f"   Test với {len(distributors)} nhà phân phối đầu tiên\n")

        # Process
        success = 0

        for i, dist in enumerate(distributors, 1):
            if process_distributor(dist, i, len(distributors)):
                success += 1

        # Summary
        print("\n" + "=" * 70)
        print("📊 KẾT QUẢ")
        print("=" * 70)
        print(f"✅ Thành công: {success}/{len(distributors)}")
        print(f"❌ Thất bại:   {len(distributors) - success}/{len(distributors)}")

        if success < len(distributors):
            print("\n💡 GỢI Ý:")
            print("   - Một số địa chỉ quá chi tiết, Nominatim không tìm thấy")
            print("   - Có thể cần Google Geocoding API để chính xác hơn")

        if DRY_RUN:
            print("\n⚠️  Chưa cập nhật database (DRY_RUN mode)")
            print("   Đổi DRY_RUN = False để cập nhật thực sự")
        else:
            print(f"\n💾 Đã cập nhật {success} records vào database")


if __name__ == '__main__':
    main()