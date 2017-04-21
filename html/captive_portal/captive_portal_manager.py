import datetime
import user_agents
from flask import Flask, redirect, render_template, request, Response
from werkzeug.contrib.fixers import ProxyFix

WELCOME_TEMPLATE = "welcome.html"
_client_map = {}
_dhcp_lease_secs = -1
DHCP_FALLBACK_LEASE_SECS = 300
REAL_HOST_REDIRECT_URL = "/to-hostname"


def cp_entry_point():
    source_ip = request.headers["X-Forwarded-For"]
    if is_authorised_client(source_ip):
        return redirect(REAL_HOST_REDIRECT_URL)
    else:
        register_client(source_ip)
        return render_template(WELCOME_TEMPLATE)


def get_dhcp_lease_secs():
    """Extract lease time from /etc/dnsmasq.conf

    dhcp-range=10.129.0.2,10.129.0.250,255.255.255.0,300
    """
    global _dhcp_lease_secs
    if _dhcp_lease_secs <= 0:
        # So we have a valid lease time if we can't parse the file for
        #  some reason (this shouldn't ever be necessary)
        _dhcp_lease_secs = DHCP_FALLBACK_LEASE_SECS
        with open("/etc/dnsmasq.conf") as f:
            for line in f:
                if line[:10] == "dhcp_range":
                    _dhcp_lease_secs = int(line.split(",")[-1])
    return _dhcp_lease_secs


def is_authorised_client(ip_address_str):
    diff_client_recency_criteria = \
            datetime.timedelta(seconds=get_dhcp_lease_secs())
    last_registered_time = _client_map.get(ip_address_str)
    if last_registered_time:
        time_since_reg = datetime.datetime.now() - last_registered_time
        return time_since_reg < diff_client_recency_criteria
    return False


def authorise_client():
    source_ip = request.headers["X-Forwarded-For"]
    register_client(source_ip)
    user_agent = user_agents.parse(request.headers.get("User-agent", ""))
    show_url_as_href = 0
    # iOS 9 can open links from the captive portal agent in the browser
    if user_agent.os.family == "iOS" and \
       user_agent.os.version[0] == 9:
        show_url_as_href = 1

    return render_template("connected.html",
                           show_url_as_href=show_url_as_href)


def register_client(ip_address_str):
    _client_map[ip_address_str] = datetime.datetime.now()


def welcome_or_serve_template(template):
    source_ip = request.headers["X-Forwarded-For"]
    if is_authorised_client(source_ip):
        return render_template(template)
    else:
        return render_template(WELCOME_TEMPLATE)


def welcome_or_return_status_code(status_code):
    source_ip = request.headers["X-Forwarded-For"]
    if is_authorised_client(source_ip):
        return Response(status=status_code)
    else:
        return render_template(WELCOME_TEMPLATE)


def cp_check_ios_macos_pre_yosemite():
    """Captive Portal Check for iOS and MacOS pre-yosemite

    See: https://forum.piratebox.cc/read.php?9,8927
    No need to check for user agent, because the default server does not serve
    the connectbox interface, so we don't need to avoid name clashes.
    """
    return welcome_or_serve_template("success.html")


def cp_check_macos_post_yosemite():
    """Captive portal check for MacOS Yosemite and later

    # noqa (ignore line length check for URLs)

    See: https://apple.stackexchange.com/questions/45418/how-to-automatically-login-to-captive-portals-on-os-x
    No need to check for user agent, because the default server does not serve
    the connectbox interface, so we don't need to avoid name clashes.
    """
    return welcome_or_serve_template("hotspot-detect.html")


def cp_check_status_no_content():
    """Captive Portal Check for devices and apps wanting a 204

    # noqa (ignore line length check for URLs)

    generate_204 is a standard Android check
    See: https://www.chromium.org/chromium-os/chromiumos-design-docs/network-portal-detection

    gen_204 is a fallback method introduced in Android 7
    See: https://android.googlesource.com/platform/frameworks/base/+/master/services/core/java/com/android/server/connectivity/NetworkMonitor.java#92

    /mobile/status.php satisfies facebook messenger connectivity check
    """
    return welcome_or_return_status_code(204)


def cp_check_amazon_kindle_fire():
    """Captive portal check for Amazon Kindle Fire
    """
    return welcome_or_serve_template("wifistub.html")


def cp_check_windows():
    """Captive portal check for Windows

    See: https://technet.microsoft.com/en-us/library/cc766017(v=ws.10).aspx
    """
    return welcome_or_serve_template("ncsi.txt")


def forget_client():
    """Forgets that a client has been seen recently to allow running tests"""
    source_ip = request.headers["X-Forwarded-For"]
    if source_ip in _client_map:
        del _client_map[source_ip]

    # Is this an acceptable status code?
    return Response(status=204)


app = Flask(__name__)
app.add_url_rule('/',
                 'index', cp_entry_point)
app.add_url_rule('/success.html',
                 'success', cp_check_ios_macos_pre_yosemite)
# iOS from captive portal
app.add_url_rule('/library/test/success.html',
                 'success', cp_check_ios_macos_pre_yosemite)
app.add_url_rule('/hotspot-detect.html',
                 'hotspot-detect', cp_check_macos_post_yosemite)
app.add_url_rule('/generate_204',
                 'generate_204', cp_check_status_no_content)
app.add_url_rule('/gen_204',
                 'gen_204', cp_check_status_no_content)
app.add_url_rule('/mobile/status.php',
                 'status', cp_check_status_no_content)
app.add_url_rule('/kindle-wifi/wifistub.html',
                 'kindle-wifi', cp_check_amazon_kindle_fire)
app.add_url_rule('/ncsi.txt',
                 'ncsi', cp_check_windows)
app.add_url_rule('/_authorise_client',
                 'auth', authorise_client, methods=['POST'])
app.add_url_rule('/_forget_client',
                 'forget', forget_client)
app.wsgi_app = ProxyFix(app.wsgi_app)


@app.errorhandler(404)
def default_view(_):
    """Handle all URLs and send them to the welcome page"""
    return cp_entry_point()


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
