from marshmallow import Schema, fields, ValidationError
from flask import g
import json
import re



class TimeFilterSchema(Schema):
    start_time = values=fields.Date()
    end_time = values=fields.Date()
    
class FilterSchema(Schema):
    time = fields.Nested(TimeFilterSchema)

class BaseSchema(Schema):
    glid = fields.Integer(required=True)
    emp_id = fields.Integer(required=True)
    mod_id = fields.String(required=True)
    AK = fields.String(required=True)
    columns = fields.List(fields.String())
    filters = fields.Nested(FilterSchema)


class CountSchema(Schema):
    glid = fields.Integer(required=True)
    emp_id = fields.Integer(required=True)
    AK = fields.String(required=True)
    mod_id = fields.String(required=True)
    columns = fields.List(fields.String())


def calculate_risk_score(data,config_data):
    values_range = config_data.get("risk_score_per_range")
    risk_profile = {}
    total_score = 0
    for param in data:
        param_range = values_range.get(param)
        if param_range:
            param_value = 0         
            count = data.get(param)
            if count>=param_range.get("low")[0] and count<= param_range.get("low")[1]:
                total_score+=param_range.get("low")[2]
                param_value = param_range.get("low")[2]
            elif count>= param_range.get("medium")[0] and count<= param_range.get("medium")[1]:
                total_score+=param_range.get("medium")[2]
                param_value = param_range.get("medium")[2]
            elif not param_range.get("very high") and count>= param_range.get("high")[0]:
                if param in ['pns_defaulter','nach_bounce']:
                    total_score+= count
                    param_value = count
                else:
                    total_score+=param_range.get("high")[1]
                    param_value = param_range.get("high")[1]
            elif param_range.get("very high"):
                if count>= param_range.get("high")[0] and count<= param_range.get("high")[1]:
                    total_score+=param_range.get("high")[2]
                    param_value = param_range.get("high")[2]
                elif count>= param_range.get("very high")[0]:
                    total_score+=param_range.get("very high")[1]
                    param_value = param_range.get("very high")[1]
            risk_profile.update({param:[count,param_value]})
  
    flag = None
    if total_score>=0 and total_score<=33:
        flag = "low"
    elif total_score>33 and total_score<=66:
        flag = "medium"
    else:
        flag = "high"

    if total_score>100:
        total_score = 100

    return round(total_score), flag, risk_profile



def validate_schema(func_name,query_data):
    
    attr_names = {"glid":"GL user ID",
    "emp_id":"employee ID",
    "mod_id":"module ID",
    "AK":"Authenication token",
    "columns":"Parameter name",
    "filters":"filters value"
    }
     
    schema=BaseSchema()
    if func_name in ["count","risk_score"]:
        schema = CountSchema()
    try:
        # Validate request body against schema data types
        result = schema.load(query_data)
        return "success","success"
    except ValidationError as msg:
        print(msg)
        # Return a nice message if validation fails
        mand_fields = ["emp_id","glid","AK"]
        err="invalid input"
        for mand_field in mand_fields:
            if mand_field not in query_data:
                return "failure","mandatory field missing %s"%attr_names[mand_field] 
            attr = re.findall(r'\{\'(.*?)\':',str(msg)) 
            if attr: 
                if attr_names.get(attr[0]):
                    err = "invalid input : %s"%attr_names[attr[0]]
                else:
                    err = "invalid filed : %s"%attr[0]
        return "failure",err

def print_application_log(request,response,request_time):
    request_body = request.get_json()
    app_log = {"request_body":request_body,"request_method":request.method,"api_endpoint":request.path,
    "response":response.get("CODE"),"request_ip":request.remote_addr,"api_response_time":request_time,"TAG":"application_log",
    "application":"flask_apis"}
    g_values = vars(g)
    for param in g_values:
        app_log.update({param: g_values.get(param)})
    print(json.dumps(app_log))
    
