#!/usr/bin/env python3
#
# Copyright (c) 2020 Roberto Riggio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

"""MAC PRB Utilization Reports."""

from construct import Struct, Int16ub, Int32ub

import empower.managers.ranmanager.vbsp as vbsp

from empower.managers.ranmanager.vbsp.lteworker import ELTEWorker
from empower.core.app import EVERY

PT_MAC_PRB_UTILIZATION_SERVICE = 0x04

TLV_MAC_PRB_UTILIZATION = 0x0A

MAC_PRB_UTILIZATION_SERVICE_REPORT = Struct(
    "prb" / Int16ub,
    "dl_prb_counter" / Int32ub,
    "ul_prb_counter" / Int32ub,
    "pci" / Int16ub,
)
MAC_PRB_UTILIZATION_SERVICE_REPORT.name = "mac_prb_utilization_report"


class MACPrbUtilization(ELTEWorker):
    """MAC PRB Utilization Reports.

    Collect the MAC level PRB utilization reports

    Parameters:
        every: the loop period in ms (optional, default 2000ms)

    Example:
        POST /api/v1/projects/52313ecb-9d00-4b7d-b873-b55d3d9ada26/apps
        {
            "name": "empower.workers.macprbutilization.macprbutilization",
            "params": {
                "every": 2000
            }
        }
    """

    def __init__(self, context, service_id, every=EVERY):

        super().__init__(context=context,
                         service_id=service_id,
                         every=every)

        # Register messages
        parser = (vbsp.PACKET, "mac_prb_utilization_service")
        vbsp.register_message(PT_MAC_PRB_UTILIZATION_SERVICE, parser)

        # Last seen time
        self.last = None

    def loop(self):
        """Periodic loop."""

        for vbs in self.vbses.values():

            if not vbs.is_online():
                continue

            vbs.connection.send_message(action=PT_MAC_PRB_UTILIZATION_SERVICE,
                                        msg_type=vbsp.MSG_TYPE_REQUEST,
                                        crud_result=vbsp.OP_RETRIEVE,
                                        tlvs=[],
                                        callback=self.handle_response)

    def handle_response(self, msg, vbs, request):
        """Handle an incoming UE_MEASUREMENTS message."""

        # parse TLVs
        for tlv in msg.tlvs:

            if tlv.type != TLV_MAC_PRB_UTILIZATION:
                self.log.warning("Unknown options %u", tlv.type)
                continue

            parser = MAC_PRB_UTILIZATION_SERVICE_REPORT
            option = parser.parse(tlv.value)

            self.log.debug("Processing options %s", parser.name)

            print(option)


def launch(context, service_id, every=EVERY):
    """ Initialize the module. """

    return MACPrbUtilization(context=context, service_id=service_id,
                             every=every)