import json

python_obj = {
    "name": "John Doe",
    "age": 30,
    "city": "New York",
    "is_student": False,
    "courses": ["Math", "Science", "History"],
    "address": {
        "street": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip": "10001"
    }
}

json_str = json.dumps(python_obj, indent=4)
print(json_str)


python_obj_converted = json.loads(json_str)
print(python_obj_converted)