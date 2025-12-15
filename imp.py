# scripts/import_distributors_with_maps.py
import pandas as pd
import requests
import time
from app import create_app, db
from app.models.distributor import Distributor


def get_google_maps_data(address, api_key=None):
    """
    Lấy tọa độ và iframe từ địa chỉ
    Nếu không có API key, tạo iframe đơn giản
    """
    if not address:
        return None, None, None, None

    # Tạo Google Maps URL
    encoded_address = requests.utils.quote(address)
    map_url = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"

    # Nếu có API key, dùng Geocoding API để lấy tọa độ chính xác
    if api_key:
        try:
            geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
            response = requests.get(geocode_url, timeout=5)
            data = response.json()

            if data['status'] == 'OK':
                location = data['results'][0]['geometry']['location']
                lat = location['lat']
                lng = location['lng']

                # Tạo iframe với tọa độ chính xác
                map_iframe = f'<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3919.5!2d{lng}!3d{lat}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zM!5e0!3m2!1svi!2s!4v1234567890" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy"></iframe>'

                return lat, lng, map_iframe, map_url
        except Exception as e:
            print(f"  ⚠️  Lỗi API: {e}")

    # Fallback: Tạo iframe đơn giản (không có tọa độ chính xác)
    map_iframe = f'<iframe src="https://www.google.com/maps?q={encoded_address}&output=embed" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy"></iframe>'

    return None, None, map_iframe, map_url


def import_distributors_from_excel(file_path, google_api_key=None, delay=0.5):
    """
    Import nhà phân phối từ Excel với tự động tạo Google Maps

    Args:
        file_path: Đường dẫn file Excel
        google_api_key: Google Maps API key (optional, để lấy tọa độ chính xác)
        delay: Delay giữa các request (giây) để tránh rate limit
    """

    app = create_app()

    with app.app_context():
        print(f"\n📂 Đọc file: {file_path}")
        df = pd.read_excel(file_path)

        # Đổi tên cột
        df.columns = ['name', 'phone', 'address', 'city']

        count_success = 0
        count_error = 0
        count_skip = 0

        total = len(df)

        print(f"📊 Tổng số dòng: {total}")
        print(f"{'=' * 60}")

        for index, row in df.iterrows():
            try:
                # Skip dòng trống
                if pd.isna(row['name']) or str(row['name']).strip() == '':
                    count_skip += 1
                    continue

                # Clean data
                name = str(row['name']).strip()
                phone = str(row['phone']).strip() if pd.notna(row['phone']) else None
                address = str(row['address']).strip() if pd.notna(row['address']) else None
                city = str(row['city']).strip() if pd.notna(row['city']) else None

                print(f"\n[{index + 2}/{total + 1}] {name}")

                # Kiểm tra trùng lặp
                existing = Distributor.query.filter(
                    (Distributor.name == name) | (Distributor.phone == phone)
                ).first()

                if existing:
                    print(f"  ⚠️  Đã tồn tại")
                    count_skip += 1
                    continue

                # Lấy Google Maps data
                full_address = f"{address}, {city}" if address and city else (address or city)
                lat, lng, map_iframe, map_url = get_google_maps_data(full_address, google_api_key)

                if lat and lng:
                    print(f"  📍 Tọa độ: {lat:.6f}, {lng:.6f}")
                else:
                    print(f"  📍 Tạo iframe cơ bản")

                # Tạo distributor
                distributor = Distributor(
                    name=name,
                    phone=phone,
                    address=address,
                    city=city,
                    latitude=lat,
                    longitude=lng,
                    map_iframe=map_iframe,
                    map_url=map_url,
                    is_active=True,
                    is_featured=False
                )

                db.session.add(distributor)
                count_success += 1
                print(f"  ✅ Thành công")

                # Delay để tránh rate limit
                if google_api_key:
                    time.sleep(delay)

            except Exception as e:
                count_error += 1
                print(f"  ❌ Lỗi: {str(e)}")
                continue

        # Commit
        try:
            db.session.commit()
            print(f"\n{'=' * 60}")
            print(f"🎉 IMPORT HOÀN TẤT!")
            print(f"{'=' * 60}")
            print(f"✅ Thành công: {count_success}")
            print(f"⚠️  Bỏ qua: {count_skip}")
            print(f"❌ Lỗi: {count_error}")
            print(f"📊 Tổng: {count_success + count_skip + count_error}")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ LỖI KHI COMMIT: {str(e)}")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("📌 Cách 1 (Không có API key - iframe cơ bản):")
        print("   python scripts/import_distributors_with_maps.py data.xlsx")
        print("\n📌 Cách 2 (Có API key - lấy tọa độ chính xác):")
        print("   python scripts/import_distributors_with_maps.py data.xlsx YOUR_API_KEY")
        print("\n💡 Lấy API key miễn phí tại: https://console.cloud.google.com/")
        sys.exit(1)

    file_path = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None

    if api_key:
        print(f"🔑 Sử dụng Google Maps API")
    else:
        print(f"ℹ️  Không có API key - chỉ tạo iframe cơ bản")

    import_distributors_from_excel(file_path, api_key)