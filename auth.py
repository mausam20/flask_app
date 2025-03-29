from functools import wraps
import jwt
from flask import request,g,current_app
import utils

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        response = None
        token = None
        data = None
        body = request.get_json()
        emp_id = body.get("emp_id")
        token = body.get("AK")
        mod_id = body.get("mod_id")
        auth_fail_resp = {
                "CODE" : 406,
                "message": "authentication failed"
            }
        if not token:
            response =  {
                "CODE":406,
                "message": "Authentication Token is missing!",
            }
        elif not emp_id :
            response =  {
            "CODE" : 406, 
            "message": "employee id is missing!",
            }
        #{'sub': '99602', 'exp': 1691486220, 'iat': 1691399820, 'iss': 'EMPLOYEE'}
        try:
            data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        except Exception as e:
            # logger.error(e)
            g.error = str(e)
            response =  auth_fail_resp
        if isinstance(emp_id,int) or emp_id.isnumeric():
            emp_id = int(emp_id)
        else:
            if  not response :
                response = {
                "CODE" : 406, 
                "message": "invalid employee id",
                }

        if not response:
            if int(data['sub'])!=emp_id:
                response =  auth_fail_resp
            elif not mod_id :
                response = {
                "CODE" : 406, 
                "message": "module id is missing!",
                }
            elif mod_id.lower() not in current_app.config["mod_id"]:
                response = auth_fail_resp

            elif data['iss']!='EMPLOYEE':
                response = {
                "CODE" : 406, 
                "message": "invalid token",
                }

        if response : 
            utils.print_application_log(request,response,0)
            return response
        print("employee validated successfuly")
        return f(*args, **kwargs)       

    return decorated
