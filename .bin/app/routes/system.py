# routes/system.py
from flask import Blueprint, request, jsonify, render_template
import os
import json
from android_tv_rc.logger import Logger
from functools import wraps
import platform
import psutil

from Server import ServerMonitorAndRemoteControl, auth

system_bp = Blueprint('System', __name__, url_prefix='/api')

if platform.system() == "Windows":
    Server_Monitor = ServerMonitorAndRemoteControl()

@system_bp.route("/system")
@auth.login_required
def monitor_dashboard():
    return render_template("system.html")


@system_bp.route("/system", methods=["GET"])
@auth.login_required
def return_system_info():
    try:
        system_info = {
            "cpu": Server_Monitor.get_cpu(),
            "ram": Server_Monitor.get_ram(),
            "disk": Server_Monitor.get_disk_usage(),
            "net_sent": Server_Monitor.net_sent,
            "net_recv": Server_Monitor.net_recv,
            "volume":Server_Monitor.get_volume(),
            "battery":Server_Monitor.get_battery(),
            "uptime":Server_Monitor.get_uptime()
        }
        return jsonify(system_info)
    
    except TypeError as e:
        Logger.error(f"400 Bad request: {e}")
        return jsonify({"response": f"Bad Request: {e}"}), 400

    except ConnectionError as e:
        Logger.error(f"503 Service Unavailable: {e}")
        return jsonify({"response": f"Service Unavailable: {e}"}), 503

    except KeyError as e:
        Logger.error(f"400 Missing field: {e}")
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /system: {e}")
        return jsonify({"response": "Internal Server Error"}), 500


@system_bp.route("/system/actions/sleep", methods=["POST"])
@auth.login_required
def sleep_api():
    try:
        data = request.json
        if data.get("action") == "sleep":
            Server_Monitor.sleep_pc()
        return jsonify({"message": "ok", "status": 200})
        
    except TypeError as e:
        Logger.error(f"400 Bad request: {e}")
        return jsonify({"response": f"Bad Request: {e}"}), 400

    except ConnectionError as e:
        Logger.error(f"503 Service Unavailable: {e}")
        return jsonify({"response": f"Service Unavailable: {e}"}), 503

    except KeyError as e:
        Logger.error(f"400 Missing field: {e}")
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /system/actions/sleep: {e}")
        return jsonify({"response": "Internal Server Error"}), 500

@system_bp.route("/system/actions/volume", methods=["GET","POST"])
@auth.login_required
def volume_api():
    if request.method == "GET":
        try:
            return jsonify({"volume":int(Server_Monitor.get_volume())})
         
        except TypeError as e:
            return jsonify({"response": f"Bad Request: {e}"}), 400 
    
        except ConnectionError as e:
            return jsonify({"response": f"Service Unavailable: {e}"}), 503
        
        except KeyError as e:
            return jsonify({"response": f"Missing field: {e}"}), 400
        
        except Exception as e:
            Logger.error(f"Unexpected error in /ai: {e}")
            return jsonify({"response": "Internal Server Error"}), 500
        
    else:
        try:
            data = request.json
            if data.get("action") == "increase":
                Server_Monitor.increase_volume()
            else:
                Server_Monitor.decrease_volume()
            return jsonify({"message": "ok", "status": 200})
        
        except TypeError as e:
            return jsonify({"response": f"Bad Request: {e}"}), 400 
    
        except ConnectionError as e:
            return jsonify({"response": f"Service Unavailable: {e}"}), 503
        
        except KeyError as e:
            return jsonify({"response": f"Missing field: {e}"}), 400
        
        except Exception as e:
            Logger.error(f"Unexpected error in /system/actions/volume: {e}")
            return jsonify({"response": "Internal Server Error"}), 500


@system_bp.route("/system/actions/shutdown", methods=["POST"])
@auth.login_required
def shutdown_api():
    try:
        data = request.json
        if data.get("action") == "shutdown":
            Server_Monitor.shutdown_pc()
        return jsonify({"message": "ok", "status": 200})
    
    except TypeError as e:
        Logger.error(f"400 Bad request: {e}")
        return jsonify({"response": f"Bad Request: {e}"}), 400

    except ConnectionError as e:
        Logger.error(f"503 Service Unavailable: {e}")
        return jsonify({"response": f"Service Unavailable: {e}"}), 503

    except KeyError as e:
        Logger.error(f"400 Missing field: {e}")
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /system/actions/shutdown: {e}")
        return jsonify({"response": "Internal Server Error"}), 500


@system_bp.route("/system/actions/restart", methods=["POST"])
@auth.login_required
def restart_api():
    try:
        data = request.json
        if data.get("action") == "restart":
            Server_Monitor.restart_pc()
        return jsonify({"message": "ok", "status": 200})
        
    except TypeError as e:
        Logger.error(f"400 Bad request: {e}")
        return jsonify({"response": f"Bad Request: {e}"}), 400

    except ConnectionError as e:
        Logger.error(f"503 Service Unavailable: {e}")
        return jsonify({"response": f"Service Unavailable: {e}"}), 503

    except KeyError as e:
        Logger.error(f"400 Missing field: {e}")
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /system/actions/restart: {e}")
        return jsonify({"response": "Internal Server Error"}), 500


@system_bp.route("/system/processes", methods=["GET"])
@auth.login_required
def get_processes():
    try:
        processes = []
        for proc in psutil.process_iter():
            with proc.oneshot():
                try:
                    mem = proc.memory_info().rss / (1024 * 1024)
                    processes.append({
                        "pid": proc.pid,
                        "name": proc.name(),
                        "mem": round(mem, 2)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        top_procs = sorted(processes, key=lambda x: x['mem'], reverse=True)[:10]
        return jsonify(top_procs)
    
    except TypeError as e:
        Logger.error(f"400 Bad request: {e}")
        return jsonify({"response": f"Bad Request: {e}"}), 400

    except ConnectionError as e:
        Logger.error(f"503 Service Unavailable: {e}")
        return jsonify({"response": f"Service Unavailable: {e}"}), 503

    except KeyError as e:
        Logger.error(f"400 Missing field: {e}")
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /system/processes: {e}")
        return jsonify({"response": "Internal Server Error"}), 500

