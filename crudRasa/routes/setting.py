from flask import request, jsonify, Blueprint

import utils
from app import db
from db import models

setting=Blueprint('setting', __name__)

@setting.route('/settings', methods=['GET'])
def settingsAll():
    try:
        settings=db.session.query(models.t_settings).all()
        return jsonify([models.Serializer\
            .serializeStatic(s) for s in settings])
    except Exception as e:
        return(str(e))



@setting.route('/settings/<setting_name>', methods=['GET', 'PUT'])
def settingsName(setting_name):
    if request.method=='PUT':
        try:
            data=request.get_json()
            setting=db.session.query(models.t_settings)\
                .filter_by(setting_name=setting_name).first_or_404()
            setting.setting_value=data['setting_value']
            db.session.commit()
            return utils.result('success', 'Inserted')
        except Exception as e:
            db.session.rollback()
            return(str(e))
        
    try:
        setting=db.session.query(models.t_settings)\
            .filter_by(setting_name=setting_name).first_or_404()
        return jsonify(models.Serializer.serializeStatic(setting))
    except Exception as e:
        return(str(e))

