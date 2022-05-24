from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_api import status
from safrs import SAFRSBase, SAFRSAPI
from flask_cors import cross_origin
import os

from auth import token_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.sqlite'  #typ sqlalchemy databaze

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    content = db.Column(db.Text)
    complete = db.Column(db.Boolean, default=True)
    #1


#@cross_origin() #allow xs request
@app.route('/task', methods=['POST'])
def create_task():
    data = request.get_json()

    new_task = Task(name=data['name'], content=data['content'], complete=False)

    db.session.add(new_task)
    db.session.commit()

    return make_response(jsonify("Nový task vytvořen!"), 200)



@app.route('/', methods=['GET'])
@token_required
def get_all_tasks():
    filters = {
        "ALL": "all",
        "COMPLETED": "completed",
        "NOT_COMPLETED": "not_completed"
    }
    
    filter = request.args.get('filter', None)

    if filter == filters["ALL"]:
        task_query = Task.query.all()

    elif filter == filters["COMPLETED"]:
        task_query = Task.query.filter_by(complete=True).all()

    elif filter == filters["NOT_COMPLETED"]:
        task_query = Task.query.filter_by(complete=False).all()

    else:
        return make_response(jsonify("Filtr nenalezen!"), 404)


    output = []

    for task in task_query:
        task_data = {}
        task_data['id'] = task.id
        task_data['name'] = task.name
        task_data['content'] = task.content
        task_data['complete'] = task.complete
        output.append(task_data)

    response = jsonify(
        {
            "items":
             output
        }
    )

    return response, status.HTTP_201_CREATED


@app.route('/task/<id>', methods=['PUT'])
def update_task(id):
    data = request.get_json()

    name = data.get('name', None)
    content = data.get('content', None)
    complete = data.get('complete', None)

    task = Task.query.filter_by(id=id).first()

    if not task:
        return make_response(jsonify("Task nenalezen."), 404)

    task.name = name
    task.content = content
    task.complete = complete

    db.session.commit()

    return make_response(jsonify("Úspěšně změněno."), 200)


@app.route('/task/<id>', methods=['GET'])
def get_one_task(id):
    task = Task.query.filter_by(id=id).first()

    if not task:
        return make_response(jsonify("id nenalezeeno"), 404)

    result = {}
    result["name"] = task.name
    result["content"] = task.content
    result["complete"] = task.complete

    return make_response(jsonify(result), 200)


@app.route("/task/<id>", methods=["DELETE"])
def delete_task(id):
    task = Task.query.filter_by(id=id).first()

    if not task:
        return make_response(jsonify("id tasku nenalezenbo"), 404)

    db.session.delete(task)
    db.session.commit()

    return make_response(jsonify("Smazáno!"), 200)

if __name__ == '__main__':
 
    
    api = SAFRSAPI(app, host="0.0.0.0", port=5000, prefix="/doc")
    print(f"Created API: http://0.0.0.0:5000/doc/")
    app.run(host="0.0.0.0", port=5000, debug=True)
    
    #host="0.0.0.0"
    #port=5000
    #api = SAFRSAPI(app, host=host, port=port, prefix="/doc")
    #api.expose_object(User)
    #api.expose_object(Book)
    #print(f"Created API: http://{host}:{port}/doc/")
    #app.run(debug=True, host=host, port=port,)

    