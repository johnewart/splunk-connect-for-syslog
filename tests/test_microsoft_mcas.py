# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

# 2020-05-15T13:25:05+00:00 HOSTNAME CEF:0|MCAS|SIEM_Agent|0.172.123|EVENT_CATEGORY_UPLOAD_DISCOVERY_FILE|Upload Cloud Discovery file|0|externalId=111005697_1589549105456_dc4b870227e1474f94cab2cb4d256d1c rt=1589549105456 start=1589549105456 end=1589549105456 msg=Upload Cloud Discovery file suser= destinationServiceName=Microsoft Cloud App Security dvc=111.222.18.21 requestClientApplication=Apache-HttpClient/4.5.10 (Java/1.8.0_222) cs1Label=portalURL cs1=https://companyname.portal.cloudappsecurity.com/#/audits?activity.id\=eq(111005697_1589549105456_dc4b870227e1474f94cab2cb4d256d1c,) cs2Label=uniqueServiceAppIds cs2=APPID_OFFICE,APPID_MCAS cs3Label=targetObjects cs3= cs4Label=policyIDs cs4= c6a1Label=“Device IPv6 Address” c6a1=
def test_microsoft_mcas(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ iso }} {{ host }} "
        + 'CEF:0|MCAS|SIEM_Agent|0.172.123|EVENT_CATEGORY_UPLOAD_DISCOVERY_FILE|Upload Cloud Discovery file|0|externalId=111005697_1589549105456_dc4b870227e1474f94cab2cb4d256d1c rt={{ epoch }} start={{ epoch }} end={{ epoch }} msg=Upload Cloud Discovery file suser= destinationServiceName=Microsoft Cloud App Security dvc=111.222.18.21 requestClientApplication=Apache-HttpClient/4.5.10 (Java/1.8.0_222) cs1Label=portalURL cs1=https://companyname.portal.cloudappsecurity.com/#/audits?activity.id\=eq(111005697_1589549105456_dc4b870227e1474f94cab2cb4d256d1c,) cs2Label=uniqueServiceAppIds cs2=APPID_OFFICE,APPID_MCAS cs3Label=targetObjects cs3= cs4Label=policyIDs cs4= c6a1Label="Device IPv6 Address" c6a1='
        + "\n"
    )
    message = mt.render(mark="<134>", iso=iso, host=host, epoch=epoch)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" source="microsoft:cas" sourcetype=cef'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
