from flask import request, jsonify, Blueprint, current_app,g
from models import BquerySession
from auth import token_required
from datetime import date, timedelta,datetime
import utils
import json
import logging.config
import time
import os

log_level = "DEBUG"
LOGFILENAME = "app.log"
class LoggerConfig:
    dictConfig = {
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] {%(pathname)s:%(funcName)s:%(lineno)d} %(levelname)s - %(message)s',
        }},
        'handlers': {'default': {
                    'level': 'DEBUG',
                    'formatter': 'default',
           
                     'class': 'logging.handlers.RotatingFileHandler',
                    'filename': LOGFILENAME,
                    'maxBytes': 5000000,
                    'backupCount': 10
                }},
        'root': {
            'level': log_level,
            'handlers': ['default']
        },
    }

main_bp = Blueprint('main_bp', __name__)

# # logging.basicConfig(filename='app.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
# logging.config.dictConfig(LoggerConfig.dictConfig)

try:
    config_data = json.loads(open("config.json").read())
    config_data = config_data.get(os.environ["environment"])
    bquery_ = BquerySession(config_data)

except Exception as e:
    print(e)



@main_bp.route('/get_seller_data', methods=['POST'])
@token_required
def get_log():
    try:
        request_time=0
        start = time.perf_counter()
        query_data = request.get_json()
        status,msg = utils.validate_schema("log",query_data)
        if status == "failure":
            return {
                "CODE": "401",
                "STATUS": "Faliure",
                "MESSAGE":msg,
            }
        glid = query_data.get('glid')
        current_date =date.today()
        filters = query_data.get('filters',{'time':{'start_time':(current_date-timedelta(days=7)),'end_time':current_date}})
        columns = query_data.get('columns',config_data.get("agg_columns"))
        result_data = bquery_.read_table(config_data, glid, columns, filters)
        if not result_data:
            result_data = "no records found"
        # current_app.logger.info("got user data")
        request_time = time.perf_counter() - start
        # current_app.logger.info(f"total request time {request_time}")
        response = {
                "CODE": "200",
                "STATUS": "Success",
                "records": result_data
            }

    except Exception as e:
        # current_app.logger.error(e)
        g.error = str(e)
        response = {
            "CODE": "503",
            "STATUS": "Failure",
            "MESSAGE": "API FAILURE"
        }
    utils.print_application_log(request,response,request_time)
    return response


@main_bp.route('/get_aggregate_count', methods=['POST'])
@token_required  
def get_aggregate():
    try:
        request_time = 0
        start = time.perf_counter()
        query_data = request.get_json()
        status,msg = utils.validate_schema("count",query_data)
        if status == "failure":
            return {
                "CODE": "401",
                "STATUS": "Faliure",
                "MESSAGE":msg
            }
        glid = query_data.get('glid')
        columns = query_data.get('columns',config_data.get("agg_columns"))
        agg_df = bquery_.get_last_year_count(glid,columns,config_data,"aggregate")
        if not agg_df:
            agg_df = "No records found"
        request_time = time.perf_counter() - start
        # current_app.logger.info(f"total request time {request_time}")
        response = {
                "CODE": "200",
                "STATUS": "Success",
                "records": agg_df
            }
    except Exception as e:
        # current_app.logger.error(e)
        g.error = str(e)
        response = {
                "CODE": "503",
                "STATUS": "Failure",
                "MESSAGE": "API FAILURE"
            }
    utils.print_application_log(request,response,request_time)
    return response

@main_bp.route('/get_risk_score', methods=['POST'])
@token_required    
def cal_risk_score():
    try:
        request_time=0
        start = time.perf_counter()
        query_data = request.get_json()
        status,msg = utils.validate_schema("risk_score",query_data)
        if status == "failure":
            return {
                "CODE": "401",
                "STATUS": "Faliure",
                "MESSAGE":msg,
            }
        glid = query_data.get('glid')
        columns = config_data.get("default_columns")
        agg_df = bquery_.get_last_year_count(glid,columns,config_data,"risk_score")
        if agg_df is None:
            data = 0,"no records found", {}
        else:
            print(agg_df)
            data = utils.calculate_risk_score(agg_df,config_data)
        request_time = time.perf_counter() - start
        # current_app.logger.info(f"total request time {request_time}")
        response = {
                "CODE": "200",
                "STATUS": "Success",
                "records": data
            }
    except Exception as e:
        # current_app.logger.error(e)
        g.error = str(e)
        response =  {
                "CODE": "503",
                "STATUS": "Failure",
                "MESSAGE": "API FAILURE"
            }
    utils.print_application_log(request,response,request_time)
    return response


    
@main_bp.route("/health")
def health_check(): 
    return jsonify({'Code' : 200, 'message' : 'Health check passed'})

    
@main_bp.app_errorhandler(404)
def invalid_route(e): 
    return jsonify({'errorCode' : 404, 'message' : 'Route not found'})

@main_bp.app_errorhandler(405)
def invalid_route(e): 
    return jsonify({
                "CODE":405,
                "message": "invalid input",
            })

@main_bp.app_errorhandler(400)
def invalid_route(e): 
    return jsonify({
                "CODE":400,
                "message": "invalid input",
            })

