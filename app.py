from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from pymongo import MongoClient
from urllib.parse import quote_plus
from bson.objectid import ObjectId
import json
import jwt
from datetime import datetime, timedelta


app = Flask(__name__)

username = 'rajeevshrivastav525'
password = 'Rajeev@123'
host = 'cluster0.g1m7m6v.mongodb.net'
database = 'test'

uri = f"mongodb+srv://{quote_plus(username)}:{quote_plus(password)}@{host}/{database}?retryWrites=true&w=majority"

app.config['MONGO_URI'] = uri
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  
mongo = PyMongo(app)


@app.route('/protected', methods=['GET'])
def protected():
    print("asdfdkjsfoadsf")
    collection = mongo.db.collection_name  
    return jsonify({'message': 'Protected route'}), 200




@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')

    existing_user = mongo.db.users.find_one({'email': email})
    if existing_user:
        return jsonify({'message': 'Email already registered'})

    new_user = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': password
    }

    inserted_user = mongo.db.users.insert_one(new_user)
    new_user['_id'] = str(inserted_user.inserted_id)  

    return json.dumps(new_user), 200, {'Content-Type': 'application/json'}




@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = mongo.db.users.find_one({'email': email, 'password': password})
    if user:
        token = jwt.encode(
            {'email': email},
            app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        return jsonify({'access_token': token})

    return jsonify({'message': 'Invalid credentials'}), 401






def validate_token(token):
    try:
        decoded = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return decoded['email']
    except jwt.exceptions.InvalidTokenError:
        return None

@app.route('/template', methods=['POST'])
def create_template():
    data = request.get_json()
    template_name = data.get('template_name')
    subject = data.get('subject')
    body = data.get('body')

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401
    print(token)
    email = validate_token(token)
    print(email)
    if not email:
        return jsonify({'message': 'Invalid token'}), 401

    new_template = {
        'template_name': template_name,
        'subject': subject,
        'body': body
    }

    inserted_template = mongo.db.templates.insert_one(new_template)
    new_template['_id'] = str(inserted_template.inserted_id)  

    return jsonify(new_template), 200





@app.route('/getTemplate', methods=['GET'])
def get_all_templates():
    token = request.headers.get('Authorization')
    if not token:
     return jsonify({'message': 'Token is missing'}), 401
    email = validate_token(token)
    if not email:
        return jsonify({'message': 'Invalid token'}), 401
    templates = mongo.db.templates.find()

    template_list = []
    for template in templates:
        template['_id'] = str(template['_id'])
        template_list.append(template)

    return jsonify({'templates': template_list}), 200





@app.route('/templateById/<template_id>', methods=['GET'])
def get_template(template_id):
    token = request.headers.get('Authorization')
    if not token:
     return jsonify({'message': 'Token is missing'}), 401
    email = validate_token(token)
    if not email:
        return jsonify({'message': 'Invalid token'}), 401
    template = mongo.db.templates.find_one({'_id': ObjectId(template_id)})

    if template:
        template['_id'] = str(template['_id'])
        return jsonify({'template': template}), 200
    else:
        return jsonify({'message': 'Template not found'}), 404





@app.route('/updateTemplate/<template_id>', methods=['PUT'])
def update_template(template_id):
    token = request.headers.get('Authorization')
    if not token:
     return jsonify({'message': 'Token is missing'}), 401
    email = validate_token(token)
    if not email:
        return jsonify({'message': 'Invalid token'}), 401
    data = request.get_json()
    updated_fields = {}

    template = mongo.db.templates.find_one({'_id': ObjectId(template_id)})

    if not template:
        return jsonify({'message': 'Template not found'}), 404

    if 'template_name' in data:
        updated_fields['template_name'] = data['template_name']
    else:
        updated_fields['template_name'] = template['template_name']

    if 'subject' in data:
        updated_fields['subject'] = data['subject']
    else:
        updated_fields['subject'] = template['subject']

    if 'body' in data:
        updated_fields['body'] = data['body']
    else:
        updated_fields['body'] = template['body']

    result = mongo.db.templates.update_one(
        {'_id': ObjectId(template_id)},
        {'$set': updated_fields}
    )

    if result.modified_count > 0:
        return jsonify({'message': 'Template updated successfully'}), 200
    else:
        return jsonify({'message': 'Template not found'}), 404






@app.route('/deleteTemplate/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    token = request.headers.get('Authorization')
    if not token:
     return jsonify({'message': 'Token is missing'}), 401
    email = validate_token(token)
    if not email:
        return jsonify({'message': 'Invalid token'}), 401
    result = mongo.db.templates.delete_one({'_id': ObjectId(template_id)})

    if result.deleted_count > 0:
        return jsonify({'message': 'Template deleted successfully'}), 200
    else:
        return jsonify({'message': 'Template not found'}), 404





if __name__ == '__main__':
    app.run()