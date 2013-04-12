# ~*~ coding: utf-8 ~*~

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from pmax.data.Constants import Constants
from pmax.logic.Device import Device, DeviceActions
from pmax.logic.Panel import Panel, PanelActions
from pmax.core.IpmpLog import IpmpLog


def main_page(request):
    return render_to_response('main.html')


def powerMaster10_page(request):
    response = __getResponseParams()
    response["type"] = Constants.POWER_MAX_10
    return render_to_response('PowerMaster.html', response)


def powerMaster30_page(request):
    response = __getResponseParams()
    response["type"] = Constants.POWER_MAX_30
    return render_to_response('PowerMaster.html', response)
	
	
	
def __getResponseParams():
    contacts_info = [Device(),Device(),Device()Device(),Device()]
    return {"contact_zones": Constants.CONTACT_ZONES,
            "contacts_info": contacts_info
            "motion_zones": Constants.MOTION_ZONES,
            "partitions": Constants.PARTITIONS,
            "zone_types": Constants.ZONE_TYPES,
            'locations': Constants.LOCATIONS,
            'device_buttons': DeviceActions,
            'panel_buttons':  PanelActions,
            'panel_custom_actions': ['', PanelActions.LOGIN_TO_INST, PanelActions.LOGIN_TO_USER]}


@csrf_exempt
def device_view(request):
    device = Device(request.POST)
    response = {"error": ""}
    try:
        device.InvokeAction()
    except Exception, e:
        response["error"] = e.message

    return HttpResponse(response)


# import contextlib
# import selenium.webdriver as webdriver
# import selenium.webdriver.support.ui as ui
# def aaa():
#     with contextlib.closing(webdriver.Firefox()) as driver:
#         driver.get('http://www.google.com')
#         wait = ui.WebDriverWait(driver, 10)
#         wait.until(lambda driver: driver.find_element_by_id("asdfsdfasdfszd"))
#         print(driver.title)


@csrf_exempt
def panel_view(request):
	panel = Panel(request.POST)
	if panel.Action is None:
		return HttpResponse(panel.GetScreen())
	else:
		panel.InvokeAction()
		response = json.dumps({ 'success': 'success' , 'error': ''})
		return HttpResponse(response)


# from pmax.core.Cache import GlobalStorage
# import time
# @csrf_exempt
# def ipmp_log_view(request):
    # time.sleep(1)
    # post = request.POST
    # lines = []
    # if post.get('action') == 'run':
        # if not GlobalStorage.IpmpLog:
            # GlobalStorage.IpmpLog = IpmpLog(post.get('IP'), post.get('user'), post.get('pass'))
        # log = GlobalStorage.IpmpLog
        # log.openSSHSession()
        # log.startLog()
        # lines = log.getLog()
    # else:
        # GlobalStorage.IpmpLog.closeSSHSession()
        # GlobalStorage.IpmpLog = None

    # response = json.dumps({ 'lines': lines })
    # return HttpResponse(response)


from django.core.cache import cache
import time
CACHE_KEY_IPMP_LOG = "IPMP_LOG"
@csrf_exempt
def ipmp_log_view(request):
    time.sleep(1)
    post = request.POST
    lines = []
    if post.get('action') == 'run':
        log = cache.get(CACHE_KEY_IPMP_LOG)
        if log is None:
            log = IpmpLog(post.get('IP'), post.get('user'), post.get('pass'))
            cache.set(CACHE_KEY_IPMP_LOG, log,)
        log.openSSHSession()
        log.startLog()
        lines = log.getLog()
    else:
        cache.get(CACHE_KEY_IPMP_LOG).closeSSHSession()
        cache.delete(CACHE_KEY_IPMP_LOG)

    response = json.dumps({ 'lines': lines })
    return HttpResponse(response)