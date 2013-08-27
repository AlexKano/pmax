# ~*~ coding: utf-8 ~*~

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from pmax.data.Constants import Constants
from pmax.logic.Device import *
from pmax.logic.Panel import *
from pmax.core.IpmpLog import IpmpLog


def main_page(request):
    return render_to_response('main.html')


def powerMaster_page(request, panel_type):
    panel = Panel(panel_type)
    cachedPanel = Panel.GetByType(panel.Type)
    if cachedPanel is None:
        CONTACT_ZONES = [1, 2, 3, 4, 5]
        MOTION_ZONES = [6, 7]
        contacts = __getZonesInfo(CONTACT_ZONES, DeviceType.CONTACT)
        motions = __getZonesInfo(MOTION_ZONES, DeviceType.MOTION)

        panel.Devices.extend(contacts)
        panel.Devices.extend(motions)
        Panel.SetByType(panel)
    else:
        panel = cachedPanel

    response = __getResponseParams()
    response["contacts_info"] = [d for d in panel.Devices if d.Type == DeviceType.CONTACT]
    response["motions_info"] = [d for d in panel.Devices if d.Type == DeviceType.MOTION]
    response["panel"] = panel

    return render_to_response('PowerMaster.html', response, context_instance=RequestContext(request))


def __getZonesInfo(zones_numbers, zone_type):
    zones_info = []
    for i in zones_numbers:
        newDevice = Device(i, i - 1, i - 1, 0, zone_type)
        zones_info.append(newDevice)
    return zones_info


def __getResponseParams():
    return {"partitions": Constants.PARTITIONS,
            "zone_types": Constants.ZONE_TYPES,
            'locations': Constants.LOCATIONS,
            'device_buttons': DeviceActions,
            'panel_buttons':  PanelActions,
            'panel_custom_actions': ['', PanelActions.LOGIN_TO_INST, PanelActions.LOGIN_TO_USER]}


@csrf_exempt
def device_view(request, panel_type):
    panel = Panel.GetByType(panel_type)
    device = panel.GetDeviceByZone(int(request.POST.get("zone", 0)))

    response = {"error": ""}
    action = request.POST.get("action")
    if action is not None and action != 'undefined':
        try:
            device.Action = action
            device.InvokeAction()
        except Exception, e:
            response["error"] = e.message
    else:
        device.Update(request.POST)
    return HttpResponse(json.dumps(response))


@csrf_exempt
def panel_view(request, panel_type):
    panel = Panel.GetByType(panel_type)
    panel.Action = request.POST.get('action', None)
    panel.CustomAction = request.POST.get('custom_action', None)

    if panel.Action is None:
        #return HttpResponse(panel.GetScreen())
        return HttpResponse(json.dumps( {'screen' : panel.GetScreen()} ))
    else:
        response = {'error': ''}
        try:
            panel.InvokeAction()
        except Exception, e:
            response["error"] = e.message
        return HttpResponse(json.dumps(response))


@csrf_exempt
def ipmp_log_view(request):
    post = request.POST
    IP = post.get('IP')

    log = IpmpLog.GetByIP(IP)
    if log is None:
        log = IpmpLog(IP, post.get('user'), post.get('pass'))
        IpmpLog.SetByIP(log)

    resp = {'error': ''}
    lines = []
    if post.get('action') == 'run':
        log.openSSHSession()
        log.startLog()
        lines = log.getLog()
        resp['lines'] = lines
    else:   # stop read log from ipmp
        log.closeSSHSession()

    response = json.dumps(resp)
    return HttpResponse(response)

