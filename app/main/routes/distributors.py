# app/main/routes/distributors.py
from flask import render_template, request, jsonify
from app.models.distributor import Distributor
from app.main import main_bp
from app import db


@main_bp.route('/dai-ly')
def distributors():
    """Trang danh sách đại lý"""
    return render_template('public/dai_ly/distributors.html')


@main_bp.route('/api/distributors')
def api_distributors():
    """API lấy danh sách đại lý (JSON)"""
    # Parameters
    search = request.args.get('search', '').strip()
    city = request.args.get('city', '')
    distributor_type = request.args.get('type', '')

    # Query
    query = Distributor.query.filter_by(is_active=True)

    # Filter theo search
    if search:
        query = query.filter(
            db.or_(
                Distributor.name.ilike(f'%{search}%'),
                Distributor.address.ilike(f'%{search}%'),
                Distributor.city.ilike(f'%{search}%'),
                Distributor.district.ilike(f'%{search}%')
            )
        )

    # Filter theo city
    if city:
        query = query.filter_by(city=city)

    # Filter theo type
    if distributor_type:
        query = query.filter_by(distributor_type=distributor_type)

    # Sắp xếp: featured trước, sau đó theo tên
    distributors = query.order_by(
        Distributor.is_featured.desc(),
        Distributor.name
    ).all()

    # Convert to dict
    results = [d.to_dict() for d in distributors]

    return jsonify({
        'success': True,
        'count': len(results),
        'distributors': results
    })


@main_bp.route('/api/distributors/cities')
def api_distributor_cities():
    """API lấy danh sách tỉnh/thành"""
    cities = Distributor.get_cities()
    return jsonify({
        'success': True,
        'cities': cities
    })


@main_bp.route('/api/distributors/<int:id>')
def api_distributor_detail(id):
    """API lấy chi tiết 1 đại lý"""
    distributor = Distributor.query.get_or_404(id)

    if not distributor.is_active:
        return jsonify({'success': False, 'message': 'Distributor not found'}), 404

    return jsonify({
        'success': True,
        'distributor': distributor.to_dict()
    })