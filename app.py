# Copyright (c) 2021 Casmatt Co., Ltd.
# All rights reserved. No warranty, explicit or implicit, provided.

from requirements import *
from layout import init_dashboard
from requests.structures import CaseInsensitiveDict
import requests
headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/x-www-form-urlencoded"
url_tk = "https://api.line.me/oauth2/v2.1/token"
l_cid = '1656651377'
l_cs = 'ccb9032fa27887f799323c3170aa655b'
l_url_cb = "https://tqm.sum.insure/l"
d_state = 'dash_tqm'
d_url_login = f"https://access.line.me/oauth2/v2.1/authorize?client_id={l_cid}&scope=chat_message.write+openid+profile+email&state={d_state}&response_type=code&redirect_uri={l_url_cb}"


app = Flask(__name__)
app.secret_key = '0'


@app.route('/')
def home():
    return redirect('/tqm')


@app.route('/tqm')
def home_a():
    favicon = url_for('_dash_tqm_dash_assets.static', filename='favicon.ico')
    # return html
    return f"""<html><head>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css">
    <style>a:link {{text-decoration: none;}} .vertical-center {{ vertical-align:middle; text-align: center; margin: 0;
    position: absolute; width: 100%; top: 50%; -ms-transform: translateY(-50%); transform: translateY(-50%);}}</style>
    <link rel="shortcut icon" href="{favicon}"><title>Accumulation</title></head><body><div class=vertical-center>
    <h1><a href={d_url_login}><img src={favicon} width=100><span class="badge badge-pill badge-primary"><b>RMS</b></span></h1></a>
    </div></body></html>"""


@app.route('/l')
def login():

    if 'profile' in session:
        if 'tqm' in session['profile']['state']:
            return redirect('/dash_tqm')
        else:
            return redirect('/')

    rqs = str(request.query_string)
    print(rqs)
    if 'code' in rqs and 'state' in rqs:
        code = request.args['code']
        state = request.args['state']
        print(code, state)
        data = f"grant_type=authorization_code&redirect_uri={l_url_cb}&client_id={l_cid}&client_secret={l_cs}&code={code}"
        resp = requests.post(url_tk, headers=headers, data=data)
        print(resp, resp.text, resp.json()['id_token'])
        # , options={"verify_signature": False}
        userinfo = jwt.decode(resp.json()['id_token'],
                              l_cs, audience=l_cid, issuer='https://access.line.me', algorithms=['HS256'])
        print(userinfo)
        # state_ = 'dash_dark' if state == 'dash' else state
        session['jwt_payload'] = userinfo
        session['profile'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture'],
            'email': userinfo['email'],
            'state': state  # state_
        }
        print(session)
        return redirect(f'/{state}')
    else:
        return abort(404)


@app.route('/uploadpickle', methods=['POST'])
def uploadpickle():
    reset = request.args.get('reset')
    print(reset)
    f = request.files['upload_file']
    f.save('data/'+f.filename)
    hdgc = pd.read_pickle('data/hdgc.pickle', compression='gzip')
    gb = ['future', 'suppliercode',
          'region_c', 'PROVINCE', 'DISTRICT', 'R_P', 'R_P_A']  # , 'a_p', 'dpa' 'p_a', 'P_A',
    nd = ['Flood', 'Storm', 'Hail', 'Quake',
          'coveramount', 'sum_premium', 'saleid']
    cq = ['q_Flood', 'q_Storm', 'q_Hail', 'q_Quake']
    #   'qr_Flood', 'qr_Storm', 'qr_Hail', 'qr_Quake']
    print('reset', reset)
    if reset:
        sc = ['suppliercode', 'suppliername']
        hdgc.drop_duplicates(subset=sc)[sc].sort_values(
            by='suppliercode').reset_index(drop=True).to_pickle('data/sc.pickle')
        dfm = hdgc.groupby(gb[1:])[nd].sum().reset_index()
        dfm['future'] = 0
        # simulate 50 million THB quota in all district
        quota = 50000000
        dfm['q_Flood'] = quota
        dfm['q_Storm'] = quota
        dfm['q_Hail'] = quota
        dfm['q_Quake'] = quota
        hdg = dfm[gb+nd+cq]
    else:
        dfm = pd.read_pickle('data/hdg.pickle')
        hdg = dfm[gb+cq].merge(hdgc, left_on=gb, right_on=gb, how='outer')
    hdg.to_pickle('data/hdg.pickle')
    return jsonify(hdg.to_dict('record'))  # jsonify(task)


def requires_auth_dash(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            # print(f())
            # print(args)
            print('profile not in profile')
            return redirect('/')
        if 'tqm' not in session['profile']['state']:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated


# def requires_auth_dash_accumulation(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         if 'profile' not in session:
#             # print(f())
#             # print(args)
#             print('profile not in profile')
#             return redirect('/accumulation')
#         if 'dash_accumulation' not in session['profile']['state']:
#             return redirect('/accumulation')
#         return f(*args, **kwargs)
#     return decorated

page = 'dash_tqm'
app = init_dashboard(app, 'dash_tqm')
# app = init_dashboard(app, 'dash_accumulation')  # print(app, app.layout) #

app.view_functions['/dash_tqm/'] = requires_auth_dash(
    app.view_functions['/dash_tqm/'])

# app.view_functions['/dash_accumulation/'] = requires_auth_dash_accumulation(
#     app.view_functions['/dash_accumulation/'])

# f'/{page}/']
