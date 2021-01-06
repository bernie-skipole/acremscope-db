

import os, pathlib, mimetypes, hashlib, uuid

import redis

from skipole import WSGIApplication, FailPage, GoTo, ValidateError, ServerError, use_submit_list, skis

# the framework needs to know the location of the projectfiles directory holding the project data
# and static files.

PROJECTFILES = os.path.dirname(os.path.realpath(__file__))
PROJECT = "servebackups"

# This service needs a redis connection to store cookies
rconn = redis.Redis(host='localhost', port=6379, db=0)

PROJ_DATA={"rconn":rconn,                                 # redis connection
           "serverfolder":"/home/bernard/backups",        # where backup files can be found
           "projurl":"/acremscope/backups",               # where this project is served
           "urlfolder":"/acremscope/backups/files",       # the url of the folder called when requesting a backup file
           "username":"sysadmin",                         # the username which must be used to log in
           "password": "2408af085311a5e19308f33260943d16bbc16e801c0f3006106eef01789d9e995b4d39b2709496711792f7f5e605322f099e80d278470e78a2d9c9d3048c3e48"
           }

# The password above is an hashed password, being the result of running
# python3 hashpassword.py, and copying the result here


def _is_user_logged_in(skicall):
    received_cookies = skicall.received_cookies
    if PROJECT not in received_cookies:
        return False
    # get cookie
    rconn = skicall.proj_data["rconn"]
    # the current cookiestring is stored in redis at key 'cookiestring'
    cookiestring = rconn.get('cookiestring').decode('utf-8')
    if received_cookies[PROJECT] != cookiestring:
        return False
    return True


def _hash_password(username, password):
    "Return hashed password, as a string, on failure return None"
    seed_password = username +  password
    hashed_password = hashlib.sha512(   seed_password.encode('utf-8')  ).hexdigest()
    return hashed_password

def _create_cookie(skicall):
    "Generates a random cookie, store it in redis, and return the cookie"
    rconn = skicall.proj_data["rconn"]
    # generate a cookie string
    cookiestring = uuid.uuid4().hex
    rconn.set('cookiestring', cookiestring)
    return cookiestring


def start_call(called_ident, skicall):
    "When a call is initially received this function is called."
    skicall.call_data['logged_in'] = _is_user_logged_in(skicall)
    # if not logged in, the only valid pages are the login page and check login
    if not skicall.call_data['logged_in']:
        if (called_ident == (PROJECT, 1)) or (called_ident == (PROJECT, 10)):
            # can go to the login page, or to the checklogin page
            return called_ident
        else:
            # go to login page
            return (PROJECT, 1)
            
    # all other pages can only be accessed with a valid cookie

    # if the login page or checklogin page is accessed, but the user is already logged in
    # go to the files page, as no point re-showing a login page
    if (called_ident == (PROJECT, 1)) or (called_ident == (PROJECT, 10)):
        return (PROJECT, 20)

    if called_ident is None:
        serverfolder = skicall.proj_data["serverfolder"]
        urlfolder = skicall.proj_data["urlfolder"]
        servedfile = skicall.map_url_to_server(urlfolder, serverfolder, mimetype="application/octet-stream")
        if servedfile:
            return servedfile
    return called_ident


# You may wish to apply the decorator '@use_submit_list' to the submit_data
# function below. See the skipole documentation for details.

def submit_data(skicall):
    "This function is called when a Responder wishes to submit data for processing in some manner"
    if skicall.ident_list[-1] == (PROJECT, 10):
        # this call is to checklogin from the login page
        skicall.call_data['authenticate'] = False
        username = skicall.proj_data["username"]
        if (("login", "input_text1") in skicall.call_data) and (skicall.call_data["login", "input_text1"] == username):
            if ("login", "input_text2") in skicall.call_data:
                password = skicall.call_data["login", "input_text2"]
                hashed = _hash_password(username, password)
                if hashed == skicall.proj_data["password"]:
                    skicall.call_data['authenticate'] = True
        if skicall.call_data['authenticate']:
            return
        else:
            raise FailPage("Invalid input")
    if skicall.ident_list[-1] == (PROJECT, 20):
        # this call is to populate the showfiles page
        serverfolder = skicall.proj_data["serverfolder"]
        if not serverfolder:
            skicall.page_data['nothingfound', 'show'] = True
            skicall.page_data['filelinks', 'show'] = False
            return
        serverpath = pathlib.Path(serverfolder)
        serverfiles = [f.name for f in serverpath.iterdir() if f.is_file()]
        if not serverfiles:
            skicall.page_data['nothingfound', 'show'] = True
            skicall.page_data['filelinks', 'show'] = False
            return
        skicall.page_data['nothingfound', 'show'] = False
        skicall.page_data['filelinks', 'show'] = True

        # The widget has links formed from a list of lists
        # 0 : The url, label or ident of the target page of the link
        # 1 : The displayed text of the link
        # 2 : If True, ident is appended to link even if there is no get field
        # 3 : The get field data to send with the link

        serverfiles.sort(reverse=True)
        filelinks = []
        urlfolder = skicall.proj_data["urlfolder"] + "/"
        for sf in serverfiles:
            # create a link to urlfolder/sf
            filelinks.append([ urlfolder + sf, sf, False, ""])
        skicall.page_data['filelinks', 'nav_links'] = filelinks
        return
    if skicall.ident_list[-1] == (PROJECT, 30):
        # this call is to log out
        skicall.call_data['logout'] = True
    return


def end_call(page_ident, page_type, skicall):
    """This function is called at the end of a call prior to filling the returned page with skicall.page_data,
       it can also return an optional session cookie string."""
    if ('authenticate' in skicall.call_data) and skicall.call_data['authenticate']:
        # a user has logged in, set a cookie
        return _create_cookie(skicall)
    if ('logout' in skicall.call_data) and skicall.call_data['logout']:
        # a user has been logged out, set a new random cookie in redis, and an invalid cookie in the client
        _create_cookie(skicall)
        return "xxxxxxxx"
    return


# The above functions are required as arguments to the skipole.WSGIApplication object
# and will be called as required.

# create the wsgi application
application = WSGIApplication(project=PROJECT,
                              projectfiles=PROJECTFILES,
                              proj_data=PROJ_DATA,
                              start_call=start_call,
                              submit_data=submit_data,
                              end_call=end_call,
                              url=PROJ_DATA["projurl"])


# The 'skis' application serves javascript and the w3.css files required by
# the framework widgets.

# The skis package, contains the function makeapp() - which returns a
# WSGIApplication object which is then appended to your own project

skis_application = skis.makeapp()
application.add_project(skis_application, url=PROJ_DATA["projurl"] + '/lib')


if __name__ == "__main__":

    # If called as a script, this portion runs the python waitress server
    # and serves the project.

    ###############################################################################
    #
    # you could add the 'skiadmin' sub project
    # which can be used to develop pages for your project
    #
    ############################### THESE LINES ADD SKIADMIN ######################
    #                                                                             #
    #set_debug(True)                                                               #
    #from skipole import skiadmin                                                  #
    #skiadmin_application = skiadmin.makeapp(editedprojname=PROJECT)               #
    #application.add_project(skiadmin_application, url='/test/skiadmin')           #
    #                                                                             #
    ###############################################################################

    # if using the waitress server
    from waitress import serve

    # or the skilift development server
    # from skipole import skilift

    # serve the application, note host 0.0.0.0 rather than
    # 127.0.0.1 - so this will be available externally

    host = "0.0.0.0"
    port = 8000

    # using waitress
    serve(application, host=host, port=port)

    # or skilift
    # print("Serving %s on port %s" % (PROJECT, port))
    # skilift.development_server(host, port, application)
