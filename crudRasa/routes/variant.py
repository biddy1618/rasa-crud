from flask import request, jsonify, Blueprint

from app import db
from orm import models, utils

variant=Blueprint('variant', __name__)

@variant.route('/synonyms_variants/<synonyms_ids>', methods=['GET'])
def variantsSynonyms(synonyms_ids):
    try:
        params = utils.makeList(synonyms_ids)

        variants=models.SynonymVariant.query.filter(\
            models.SynonymVariant.synonym_id.in_(params)).all()
        return jsonify([v.serialize() for v in variants])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)


@variant.route('/synonyms/<synonym_id>/variants', methods=['GET'])
def variantSynonym(synonym_id):
    try:
        variants=models.SynonymVariant.query.filter_by(\
            synonym_id=synonym_id).all()
        return jsonify([v.serialize() for v in variants])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)


@variant.route('/variants/<variant_id>', methods=['GET', 'DELETE'])
def variantID(variant_id):
    if request.method=='DELETE':
        try:
            db.session.query(models.SynonymVariant)\
                .filter_by(synonym_variant_id=variant_id).delete()
            db.session.commit()
            return utils.result('success', f'Removed variant {variant_id}')
        except Exception as e:
            db.session.rollback()
            return(f"Internal server error: {str(e)}", 500)
    
    try:
        variant=models.SynonymVariant.query.filter_by(\
            synonym_variant_id=variant_id).first_or_404()
        return jsonify(variant.serialize())
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)


@variant.route('/synonymvariants', methods=['GET'])
def variantAll():
    '''
    The query is as follows:
    "SELECT synonym_reference AS value, '[' || string_agg('\'' || synonym_value || '\'', ', ') || ']' 
    AS synonyms FROM entity_synonym_variants GROUP BY 1"
    '''
    try:
        sql_statement=(
            "SELECT synonym_reference AS value, '[' || string_agg('\'' || synonym_value || '\'', ', ') || ']'"
            "AS synonyms FROM entity_synonym_variants GROUP BY 1"
        )
        results=db.session.execute(sql_statement)
        
        return jsonify([{
            'value': e[0],
            'synonyms': e[1]
        } for e in results])
    except Exception as e:
        return(f"Internal server error: {str(e)}", 500)
    


@variant.route('/variants', methods=['POST'])
def variantCreate():
    try:
        data=request.get_json()
        db.session.add(models.SynonymVariant(
            synonym_id=data['synonym_id'],
            synonym_value=data['synonym_value']
        ))
        db.session.commit()
        return utils.result('success', 'Inserted')
    except Exception as e:
        db.session.rollback()
        return(f"Internal server error: {str(e)}", 500)


@variant.route('/synonyms/<synonym_id>/variants', methods=['DELETE'])
def variantSynonymRemove(synonym_id):
    try:
        db.session.query(models.SynonymVariant)\
            .filter_by(synonym_id=synonym_id).delete()
        db.session.commit()
        return utils.result('success', f'Removed variants of synonym {synonym_id}')
    except Exception as e:
        db.session.rollback()
        return(f"Internal server error: {str(e)}", 500)