#! /usr/bin/env python3

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
import uuid

#####################################################
#####################################################
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../cerebrosphere.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Entity(db.Model):
    __tablename__ = 'entities'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = db.Column(db.String, nullable=False)
    properties = db.relationship('EntityProperty', backref='entity', cascade="all, delete-orphan")
    _private = db.Column(db.Boolean, default=False, nullable=False)

class EntityProperty(db.Model):
    __tablename__ = 'entity_properties'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = db.Column(db.String(36), db.ForeignKey('entities.id'), nullable=False)
    key = db.Column(db.String, nullable=False)
    value = db.Column(db.String)

class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_a = db.Column(db.String(36), db.ForeignKey('entities.id'), nullable=False)
    entity_b = db.Column(db.String(36), db.ForeignKey('entities.id'), nullable=False)
    link_type = db.Column(db.String, default='connected_to')  # Default to 'connected_to' if not provided

#####################################################
@app.route('/entities', methods=['POST'])
def create_entity():
    data = request.json
    entity = Entity(type=data['type'], _private=data.get('_private', False))
    db.session.add(entity)
    db.session.commit()
    for k, v in data.get('properties', {}).items():
        prop = EntityProperty(entity_id=entity.id, key=k, value=v)
        db.session.add(prop)
    db.session.commit()
    # Flatten properties into root
    response = {'id': entity.id, 'type': entity.type, '_private': entity._private}
    for p in entity.properties:
        response[p.key] = p.value
    return jsonify(response), 201

#####################################################
@app.route('/entities', methods=['GET'])
def list_entities():
    include_private = request.args.get('include_private', 'false').lower() == 'true'
    query = Entity.query
    if not include_private:
        query = query.filter_by(_private=False)
    entities = query.all()
    result = []
    for e in entities:
        obj = {'id': e.id, 'type': e.type, '_private': e._private}
        for p in e.properties:
            obj[p.key] = p.value
        result.append(obj)
    return jsonify(result)

#####################################################
@app.route('/entities/<entity_id>/links', methods=['GET'])
def get_linked_entities(entity_id):
    links = Link.query.filter((Link.entity_a == entity_id) | (Link.entity_b == entity_id)).all()
    linked_ids = [link.entity_b if link.entity_a == entity_id else link.entity_a for link in links]
    entities = Entity.query.filter(Entity.id.in_(linked_ids)).all()
    return jsonify([{'id': e.id, 'type': e.type} for e in entities])

#####################################################
@app.route('/links', methods=['POST'])
def create_link():
    data = request.json
    entity_a = data['entity_a']
    entity_b = data['entity_b']
    link_type = data.get('link_type', 'connected_to')
    link = Link(entity_a=entity_a, entity_b=entity_b, link_type=link_type)
    db.session.add(link)
    db.session.commit()
    return jsonify({'id': link.id, 'entity_a': entity_a, 'entity_b': entity_b, 'link_type': link.link_type}), 201

#####################################################
@app.route('/links', methods=['GET'])
def list_links():
    links = Link.query.all()
    return jsonify([
        {'id': l.id, 'entity_a': l.entity_a, 'entity_b': l.entity_b, 'link_type': l.link_type}
        for l in links
    ])

#####################################################
@app.route('/entities/<entity_id>', methods=['DELETE'])
def delete_entity(entity_id):
    entity = Entity.query.get(entity_id)
    if not entity:
        return jsonify({'error': 'Entity not found'}), 404
    # Delete all links where this entity is involved
    Link.query.filter((Link.entity_a == entity_id) | (Link.entity_b == entity_id)).delete(synchronize_session=False)
    db.session.delete(entity)
    db.session.commit()
    return jsonify({'result': 'Entity and related links deleted'})

#####################################################
@app.route('/entities/<entity_id>', methods=['GET'])
def get_entity(entity_id):
    include_private = request.args.get('include_private', 'false').lower() == 'true'
    entity = Entity.query.get(entity_id)
    if not entity or (entity._private and not include_private):
        return jsonify({'error': 'Entity not found'}), 404
    obj = {'id': entity.id, 'type': entity.type, '_private': entity._private}
    for p in entity.properties:
        obj[p.key] = p.value
    return jsonify(obj)

#####################################################
@app.route('/entities/<entity_id>', methods=['PATCH'])
def patch_entity_properties(entity_id):
    data = request.json
    entity = Entity.query.get(entity_id)
    if not entity:
        return jsonify({'error': 'Entity not found'}), 404
    updated = []
    for k, v in data.items():
        prop = next((p for p in entity.properties if p.key == k), None)
        if prop:
            prop.value = v
        else:
            prop = EntityProperty(entity_id=entity.id, key=k, value=v)
            db.session.add(prop)
        updated.append(k)
    db.session.commit()
    # Return updated entity in new format
    obj = {'id': entity.id, 'type': entity.type}
    for p in entity.properties:
        obj[p.key] = p.value
    return jsonify(obj)

#####################################################
@app.route('/')
def index():
    return 'Cerebrosphere API is running.'

if __name__ == "__main__":
    app.run(debug=True)
