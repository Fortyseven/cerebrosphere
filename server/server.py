#! /usr/bin/env python3

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../cerebrosphere.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Entity(db.Model):
    __tablename__ = 'entities'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = db.Column(db.String, nullable=False)
    properties = db.relationship('EntityProperty', backref='entity', cascade="all, delete-orphan")

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
    entity = Entity(type=data['type'])
    db.session.add(entity)
    db.session.commit()
    for k, v in data.get('properties', {}).items():
        prop = EntityProperty(entity_id=entity.id, key=k, value=v)
        db.session.add(prop)
    db.session.commit()
    return jsonify({'id': entity.id}), 201

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
@app.route('/')
def index():
    return 'Cerebrosphere API is running.'

if __name__ == "__main__":
    app.run(debug=True)
