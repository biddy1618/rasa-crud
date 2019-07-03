from flask import request, jsonify, Blueprint

from app import db
from models import models, utils

setting=Blueprint('setting', __name__)

@setting.route('/settings', methods=['GET'])
def settingsAll():
    try:
        settings=db.session.query(models.Setting).all()
        return jsonify([s.serialize() for s in settings])
    except Exception as e:
        return(str(e))



@setting.route('/settings/<setting_name>', methods=['GET', 'PUT'])
def settingsName(setting_name):
    if request.method=='PUT':
        try:
            data=request.get_json()
            setting=db.session.query(models.Setting)\
                .filter_by(setting_name=setting_name).first_or_404()
            setting.setting_value=data['setting_value']
            db.session.commit()
            return utils.result('success', 'Inserted')
        except Exception as e:
            db.session.rollback()
            return(str(e))
        
    try:
        setting=db.session.query(models.Setting)\
            .filter_by(setting_name=setting_name).first_or_404()
        return jsonify(setting.serialize())
    except Exception as e:
        return(str(e))

