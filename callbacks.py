from requirements import *
# from layout import ndfl
import plotly.express as px
import plotly.graph_objects as go
region_c = pd.read_pickle('data/hdg.pickle').region_c.dropna().unique()
region_c = np.sort(region_c)
region_cd = [{'label': i, 'value': i} for i in region_c]
# region_cd = region_cd + [{'label': 'All', 'value': 'All'}]
rcl = list(region_c)  # + ['All']
num = ['saleid', 'sum_premium', 'coveramount']


def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    return fig


def levelf(x):
    if x > 80:
        return 'Alert'
    elif x > 60:
        return 'Warning'
    else:
        return 'Safe'


def levelc(x):
    if x > 80:
        return 'red'
    elif x > 60:
        return 'yellow'
    else:
        return 'green'


def levelr(x):
    if x < 20:
        return '#F93154'
    elif x < 40:
        return '#FFA900'
    else:
        return '#00B74A'


ic = {
    'Alert': '#F93154',
    'Warning': '#FFA900',
    'Safe': '#00B74A',
    'Primary': '#0275d8',
    'Info': '#5bc0de',
    'Light': '#f7f7f7',
    '(?)': '#FBFBFB'
}


def drawSub(text, substr, cards_dd_col, nd):
    cn = 'm-0 p-0 border-0'  # border-info
    bm = '3px solid' if not cards_dd_col else 0
    if text == nd:
        cn = 'm-0 p-0 border-info'
    return dbc.Card([
        dbc.CardHeader(
            f'Sublimit {text}',
            className='p-0 m-0 border-0 bg-info text-white text-left font-weight-bold'),
        dbc.CardBody(
            substr,
            className='p-0 m-0 text-right font-weight-bold')
    ], className=cn, style={'border-left': '3px solid',
                            'border-bottom': bm,
                            'border-width': '3px', })


def drawSubdd(text, nd, dfm):
    dd_sublimit = dfm.loc[dfm.suppliercode == text][nd].sum()
    dd_quota = dfm.loc[dfm.suppliercode == text]['q_'+nd].sum()
    dd_percent = round((dd_sublimit/dd_quota)*100, 2)
    return dbc.Card([
        dbc.CardHeader(text, className='p-0 m-0 text-left'),  # bg-white
        dbc.CardBody([
            html.Small(f'{dd_sublimit:,.0f} THB ({dd_percent}%)')
        ], className='p-0 m-0 text-right')
    ], className='p-0 m-0 border-0')


def prep_data(gb, nd, future, dd1, province, district, quota, level_district):

    ndfl = ['Flood', 'Storm', 'Hail', 'Quake']
    ndql = ['q_'+nd for nd in ndfl]
    ndl = ndfl+ndql
    col = gb+num+ndl
    dfm = pd.read_pickle('data/hdg.pickle')[col].fillna(0)  # +ndq
    dfm.future = dfm.future.astype(int)
    print('\ndfm unfiltered', len(dfm), dfm.columns, dfm.nunique())

    # filter
    # dd1 = [] if not dd1 else dd1
    dfm = dfm.loc[dfm.suppliercode.isin(dd1)]
    if level_district:
        # district = [] if not district else district
        dfm = dfm.loc[dfm.R_P_A.isin(district)]
        print('dfm.sum()', dfm.sum())
    else:
        fc = num + ndl + ['num_district']
        dfm = dfm.loc[dfm.R_P.isin(province)]
        dfm['num_district'] = 0
        dfm.loc[dfm.future == 0, 'num_district'] = 1
        dfm = dfm.groupby(gb[:5])[fc].sum().reset_index()
        # print('dfm.sum()', dfm.sum())
    print('\ndfm filtered', len(dfm), dfm.columns, dfm.nunique())
    # print('dfm.sum()', dfm.sum())
    # print('dfm.isna().sum()', dfm.isna().sum())
    # fc = ['future', 'saleid']
    # print('dfm', dfm[fc])
    # print('dfm0', dfm.loc[dfm.future == 0][fc])
    # print('dfm1', dfm.loc[dfm.future == 1][fc])
    active = f'{dfm.loc[dfm.future==0].saleid.sum():,.0f} Policies'
    inactive = f'{dfm.loc[dfm.future==1].saleid.sum():,.0f} Policies'

    # future
    print('future', future)
    fg = gb[1:] if level_district else gb[1:4]
    print('fg', fg)
    if len(future):
        if len(future) == 1:
            cf = fg + num + ndl if level_district else \
                fg + num + ndl + ['num_district']
            dfm = dfm.loc[dfm.future == future[0]
                          ][cf]
        else:
            cf = num + ndl if level_district else \
                num + ndl + ['num_district']
            dfm = dfm.groupby(
                fg)[cf].sum().reset_index()
    else:
        dfm = dfm.iloc[:0][fg + num + ndl]  # .loc[dfm.future == future]
    # print('dfm futured', len(dfm), dfm.columns, dfm.nunique())

    # Percent
    dfm['Percent'] = round((dfm[nd]/dfm['q_'+nd])*100, 2)
    dfm['Level'] = [levelf(x) for x in dfm.Percent]
    dfm['Count'] = 1

    # Quota Level
    dfm['Quota'] = 'Safe'
    dfm.loc[dfm.Percent > 60, 'Quota'] = 'Warning'
    dfm.loc[dfm.Percent > 80, 'Quota'] = 'Alert'
    dfm = dfm.loc[dfm.Quota.isin(quota)]

    # Summary / Sublimit / Insurer Cards
    sum_premium = f'{dfm.sum_premium.sum():,.0f} THB'
    coveramount = f'{dfm.coveramount.sum():,.0f} THB'

    return dfm, active, inactive, sum_premium, coveramount


def init_callback(dashapp):

    # login

    @dashapp.callback([Output('test', 'children'), Output('img', 'src')], Input('location', 'pathname'))
    def test(path):
        if session:
            print(session, path)
            x = session['profile']
            return x['email'], x['picture']
        return None, None

    # logout

    @dashapp.callback(Output('location', 'pathname'), Input('logout', 'n_clicks'))
    def click_logout(nc):
        if nc:
            session.clear()
            print(session)  # ; redirect('/')#; layout = layout0
            return '/tqm'

    # add callback for toggling the collapse on small screens

    @dashapp.callback(Output("sidebar", "className"), [Input("sidebar-toggle", "n_clicks")], [State("sidebar", "className")])
    def toggle_classname(n, classname):
        if n and classname == "":
            return "collapsed"
        return ""

    @dashapp.callback(Output("collapse", "is_open"), [Input("navbar-toggle", "n_clicks")], [State("collapse", "is_open")])
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    @dashapp.callback(Output("navbar-collapse", "is_open"), [Input("navbar-toggler", "n_clicks")], [State("navbar-collapse", "is_open")])
    def toggle_navbar_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    # save

    @dashapp.callback(Output("toast", "is_open"), Input("savebtn", "n_clicks"), State('radio_nd', 'value'), State('table1', 'data'))
    def click_save(ncs, nd, datatable):
        print('ncs', ncs)
        if ncs:
            q = 'q_'+nd
            print(q)
            gb = ['suppliercode', 'region_c', 'PROVINCE', 'DISTRICT']
            dfs = pd.DataFrame(datatable).set_index(gb)[[q]]
            dfs[q] = dfs[q].astype(int)
            print(type(dfs), dfs.columns, dfs.shape)
            print(dfs)
            print(len(dfs))
            print(dfs[q])  # .sum()
            hdg = pd.read_pickle('data/hdg.pickle')
            hdg = hdg.loc[hdg.future == 0]
            hdg = hdg.set_index(gb)
            print(len(hdg))
            print(hdg[q].sum())
            hdg.update(dfs)
            hdg.reset_index().to_pickle('hdg.pickle')
            print('save success')
            print(len(hdg))
            print(hdg[q].sum())
            return True
        else:
            return False

    # popover_insurer

    @dashapp.callback(Output("popover_insurer", "is_open"), Output("popover_insurer", "children"), Input("Insurer", "n_clicks"), State("dd1", "value"))
    def popover_insurer(test, dd1):
        if test:
            # print('dd1', dd1, len(dd1))
            sc = pd.read_pickle('data/sc.pickle')

            sc = sc.loc[sc.suppliercode.isin(dd1)]
            # print('dd2', len(sc))
            sc = dbc.Table.from_dataframe(sc,
                                          striped=True, bordered=True, hover=True,
                                          style={'background-color': 'white',
                                                 'width': '385px'},
                                          id='sc')
            return True, sc  # , 'info' , Output('sc','color')
        else:
            return False, None

    # hide btn

    @ dashapp.callback(Output("btn_col", "is_open"), Input("radio_layout", "value"), Input('level_district', 'is_open'))
    def hide_cards(radio_layout, is_open):
        if radio_layout == 'Table' and is_open:
            return True
        else:
            return False

    # hide summary

    @ dashapp.callback(Output("cc", "is_open"),
                       Output("heatmap_si", "style"),
                       Output("heatmap_nd", "style"),
                       #    Input('radio_layout', 'value'),
                       Input('summary', 'value'))
    def hide_summary(summary):
        hopen = {
            'height': 'calc(100vh - 109px)'}  # if radio_layout == 'Map' else None
        hclose = {
            'height': 'calc(100vh - 50px)'}  # if radio_layout == 'Map' else None
        # h = hopen if summary else hclose
        if summary:
            return True, hopen, hopen
        else:
            return False, hclose, hclose

    # hide insurer_col

    @ dashapp.callback(Output("cards_dd_col", "is_open"),
                       Input('insurer_col', 'value'), Input('dd1', 'value'))
    def hide_insurer(insurer_col, dd1):
        if insurer_col:
            if len(dd1) > 1:
                return True
            else:
                return False
        else:
            return False

    # hide district

    @ dashapp.callback(Output("level_district_click", "color"), Output("level_district", "is_open"), Output("level_district_c", "is_open"), Output('level_district_click', 'n_clicks'),
                       Input('level_district_click', 'n_clicks'), State('level_district', 'is_open'))
    def hide_district(ncs, is_open):
        not_open = not is_open
        not_color = 'primary' if not_open else 'secondary'
        if ncs:
            return not_color, not_open, not_open, 0
        else:
            return 'secondary', False, False, 0

    # dynamic checkbox

    @dashapp.callback(Output("province", "options"),  # Output("province", "value"),
                      #   Output("region", "value"),
                      Input("region", "value"), State("region", "value"))  # , Input("province", "value")
    def dynamic_ckl_p(region, regions):  # , province
        # region = regions if not region else region
        # print('region', region, regions)
        dfm = pd.read_pickle('data/gi.pickle')[['region_c', 'R_P']]
        provincel = dfm.loc[dfm.region_c.isin(region), 'R_P'].unique()
        provincel = np.sort(provincel)
        provinced = [{'label': i, 'value': i} for i in provincel]
        # print('provinced', provinced)
        # changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        # if 'province' in changed_id:
        #     provincev = province
        # else:
        #     provincev = provincel
        # provincev = [] if not provincev else provincev
        return provinced  # , provincev,

    @ dashapp.callback(Output("district", "options"),  # Output("district", "value"),
                       Input("province", "value"))  # , Input("district", "value")
    def dynamic_ckl_d(province):  # , district
        dfm = pd.read_pickle('data/gi.pickle')[['R_P', 'R_P_A']]
        # province = [] if not province else province # Is this line important?
        districtl = dfm.loc[dfm.R_P.isin(province), 'R_P_A']
        districtl = np.sort(districtl)
        districtd = [{'label': i, 'value': i} for i in districtl]
        # changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        # if 'district' in changed_id:
        #     districtv = district
        # else:
        #     districtv = districtl
        # districtv = [] if not districtv else districtv
        # print('districtv', districtv)
        return districtd  # , districtv

    # all
    opa = [Output("region", "value"),
           Output("province", "value"), Output("district", "value")]
    ipa = [Input("all_region", "value"),
           Input("all_province", "value"), Input("all_district", "value")]
    spa = [State("region", "value"),
           State("province", "value"), State("province", "options"),
           State("district", "value"), State("district", "options")]

    @dashapp.callback(opa, ipa, spa)
    def all_chk(all_region, all_province, all_district,
                region, province, provinceo, district, districto):

        print('all_chk', all_region, all_province, all_district,
              region, province, provinceo, district, districto)

        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        # provincel = [p['value'] for p in provinceo]
        # districtl = [d['value'] for d in districto]
        print('changed_id', changed_id)
        if 'all_region' in changed_id:
            if all_region:
                return rcl, province, district
            else:
                return [], [], []
        elif 'all_province' in changed_id:
            provincel = [p['value'] for p in provinceo]
            if all_province:
                return region, provincel, district
            else:
                return region, [], district
        elif 'all_district' in changed_id:
            districtl = [d['value'] for d in districto]
            if all_district:
                return region, province, districtl
            else:
                return region, province, []
        elif changed_id == '.':
            return rcl, pd.read_pickle('data/gi.pickle').R_P.unique(), []
        else:
            return region, province, district

# select table / graph

    nmo = [Output('active', 'children'), Output('inactive', 'children'),
           Output('sum_premium', 'children'), Output('coveramount', 'children')]
    ndfl = ['Flood', 'Storm', 'Hail', 'Quake']
    # sfo = [Output(f'{o}_footer', 'children') for o in ndfl]
    # sbo = [Output(f'{o}_body', 'children') for o in ndfl]
    # sho = [Output(f'{0}_header', 'children') for o in ndfl]
    cgo = [Output('cards_sublimit', 'children'),
           Output('cards_dd_col', 'children'), ]
    #    Output('cards_chart', 'children')]
    ipl = [Input('radio_layout', 'value'),  Input('radio_nd', 'value'),
           Input('future', 'value'), Input('dd1', 'value'),
           Input('province', 'value'), Input('district', 'value'),
           Input('quota', 'value'),
           Input("cc", "is_open"), Input("level_district", "is_open"), Input("cards_dd_col", "is_open")]

    @ dashapp.callback([Output('main', 'children')]+nmo+cgo, ipl)
    def select_content(layout, nd, future, dd1, province, district, quota,
                       cc_is_open, level_district, cards_dd_col):

        # print(future, dd1, district, nd)
        gb = ['future', 'suppliercode',
              'region_c', 'PROVINCE', 'R_P',
              'DISTRICT', 'R_P_A']
        dfm, active, inactive, sum_premium, coveramount = prep_data(
            gb, nd, future, dd1, province, district, quota, level_district)

        s, p, quota = {}, {}, {}
        for ndf in ndfl:
            s[ndf] = dfm[ndf].sum()
            quota[ndf] = dfm["q_"+ndf].sum()
            p[ndf] = round((s[ndf]/quota[ndf])*100, 2)
            s[ndf] = f'{s[ndf]:,.0f} THB ({p[ndf]:,.2f}%)'

        s = [drawSub(ndf, s[ndf], cards_dd_col, nd) for ndf in ndfl]
        cdd = dbc.Card(
            dbc.CardGroup([drawSubdd(dd, nd, dfm) for dd in dd1]),
            className='p-0 m-0 border-info', style={'border-width': '3px'})

        ndl = [nd, 'q_'+nd]
        if layout == 'Table':
            from table import table
            if level_district:
                tc = gb[1:]+num+ndl+['Percent']
                main = table(dfm[tc], cc_is_open, nd)
            else:
                tc = gb[1:4]+['num_district']+num+ndl+['Percent']
                # dbct = dfm[tc].groupby('PROVINCE')[tc]

                def dbc_table(ql, color):
                    dfm_dbct = dfm[tc].loc[dfm.Quota == ql].copy()
                    dfm_dbct = dfm_dbct.sort_values(
                        by='Percent', ascending=False)
                    dfm_dbct.Percent = dfm_dbct.Percent.astype(str) + '%'
                    dfm_dbct.saleid = [
                        f'{x:,.0f}' for x in dfm_dbct.saleid]
                    dfm_dbct.sum_premium = [
                        f'{x:,.0f}' for x in dfm_dbct.sum_premium]
                    dfm_dbct.coveramount = [
                        f'{x:,.0f}' for x in dfm_dbct.coveramount]
                    dfm_dbct[nd] = [f'{x:,.0f}' for x in dfm_dbct[nd]]
                    dfm_dbct['q_' +
                             nd] = [f'{x:,.0f}' for x in dfm_dbct['q_'+nd]]
                    cd = {'suppliercode': 'Insurer',
                          'region_c': 'Region',
                          'PROVINCE': 'Province',
                          'num_district': 'Total Districts',
                          'saleid': 'Total Policies',
                          'sum_premium': 'Total Premiums',
                          'coveramount': 'Total Sum Insured',
                          nd: 'Sublimit ' + nd,
                          'q_'+nd: 'Quota Sublimit ' + nd}
                    dfm_dbct.rename(columns=cd, inplace=True)
                    return dbc.Card(
                        dbc.Table.from_dataframe(
                            dfm_dbct,
                            className='p-0 m-0 text-right',
                            striped=True,
                            bordered=True,
                            hover=True),
                        className=f'p-0 m-0 border-{color}',
                        style={'border-width': '3px'})

                main = html.Div([
                    dbc_table('Alert', 'danger'),
                    dbc_table('Warning', 'warning'),
                    dbc_table('Safe', 'success'),
                    # html.Br(), html.Br()
                ], style={'padding-bottom': '55px'})
                # style={'background-color': 'white'})
                # main = dbc.table(dfm[tc], cc_is_open, nd)

        elif layout == 'Chart':
            def ccp(label, v, ct, path):
                if ct == 'blind':
                    # w = 'w-25'
                    fig = px.sunburst(dfm, path=path, values=v, height=400)
                elif ct == 'color':
                    # w = 'w-25'
                    print(dfm.Level)

                    fig = px.sunburst(dfm, path=path, values=v, height=400,
                                      color='Level', color_discrete_map=ic)
                # if ct == 'bar':
                else:
                    # w = 'w-50'
                    x = 'DISTRICT' if path else 'PROVINCE'
                    # n = dfm.suppliercode.nunique() * dfm[x].nunique()
                    dfm5 = dfm.sort_values(
                        by='Percent', ascending=False).iloc[:20].copy()
                    dfm5.loc[dfm5.PROVINCE.str.contains(
                        'Ayutthaya'), 'PROVINCE'] = 'Ayutthaya'
                    dfm5['X'] = dfm5.suppliercode + '_' + dfm5[x]
                    # dfm5['Color'] = '#1266F1'  # 'Allocated' #00B74A
                    dfm5['Color'] = [levelc(x) for x in dfm5.Percent]
                    print('color', dfm5['Percent'], dfm5['Color'])
                    dfm5r = dfm5.copy()
                    dfm5r.Percent = 100 - dfm5r.Percent
                    # dfm5r['Color'] = '#1266F1' # '#39C0ED'  # 'Remaning
                    dfm5r['Color'] = [levelr(x) for x in dfm5r.Percent]
                    col = ['Color', 'Percent', 'X', 'suppliercode']
                    dfm5c = pd.concat([dfm5[col], dfm5r[col]])
                    fig = px.bar(dfm5c, x='X', y='Percent', color_discrete_map='identity',  # color_discrete_sequence=dfm5c['Color'].unique(),
                                 # ['#1266F1', '#39C0ED'],  # facet_col='suppliercode',
                                 color='Color', barmode='stack', text='Percent', height=500)
                    fig.update_xaxes(title=dict(text=''),
                                     tickangle=75, matches=None)
                    fig.update_yaxes(visible=False)  # title=dict(text=''),
                    fig.update_layout(legend=dict(title='', orientation="h",
                                                  yanchor="top", y=0.999, xanchor="left", x=0.4),
                                      #   uniformtext_minsize=8, uniformtext_mode='hide',
                                      autosize=True, dragmode=False, plot_bgcolor='white')  # , bargap=0.1
                    fig.update_traces(
                        texttemplate='%{text:.2f}%', textposition='outside', textangle=0)

                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0, pad=0))
                return dbc.Card([
                    dbc.CardHeader(
                        label,
                        className='p-0 m-0 border-0 text-center', style={'background': 'white'}),
                    dbc.CardBody(
                        dcc.Graph(figure=fig, responsive=True,
                                  config=dict(displaylogo=False, autosizable=True)),
                        className='p-0 m-0')  # d-flex justify-content-center align-items-center
                ], className='p-0 m-0 border-0')  # '+w)

            zc2 = zip(
                [
                    'Region by Insurer',
                    'Sublimit by Quota',
                ],
                [nd, nd],
                ['blind', 'color'],
                [
                    ['suppliercode', 'region_c'],
                    ['Level', 'suppliercode'],
                ])

            path = [
                px.Constant("all"),
                'Quota',
                'suppliercode',
                'region_c', 'PROVINCE'
            ]
            tree = px.treemap(dfm, path=path, values=nd, # height=1000,
                              color='Quota', color_discrete_map=ic)
            tree.update_layout(margin=dict(t=25, b=0, l=0, r=0, pad=0))

            # Unable to sort by Quota .sort_values(by='Quota', ascending=True)
            # print(tree)
            # # print(tree['data'][0]['ids'])
            # # print(tree['data'][0]['labels'])
            # # print(tree['data'][0]['parents'])
            # # print(tree['data'][0]['values'])
            # vwxyz = zip(
            #     tree['data'][0]['ids'],
            #     tree['data'][0]['marker']['colors'],
            #     tree['data'][0]['labels'],
            #     tree['data'][0]['parents'],
            #     tree['data'][0]['values']
            # )
            # tree_sorted = [(v, w, x, y, z) for v, w, x, y, z in vwxyz]
            # print('original', tree_sorted)
            # tree_sorted.sort(key=lambda y: y[3])
            # print('\nsorted', tree_sorted)
            # tree['data'][0]['ids'] = [v for v, w, x, y, z in tree_sorted]
            # tree['data'][0]['marker'] = {'colors': [w for v, w, x, y, z in tree_sorted]}
            # tree['data'][0]['labels'] = [x for v, w, x, y, z in tree_sorted]
            # tree['data'][0]['parents'] = [y for v, w, x, y, z in tree_sorted]
            # tree['data'][0]['values'] = [z for v, w, x, y, z in tree_sorted]

            # main = [
            #     dbc.Card(
            #         dbc.Row([
            #             dbc.Col(
            #                 [ccp(c[0], c[1], c[2], c[3]) for c in zc2],
            #                 width=3
            #             ),
            #             dbc.Col(
            #                 ccp('Top 15 %Quota by Province/District',
            #                     nd, 'bar', level_district),
            #                 width=9
            #             )
            #         ], no_gutters=True),
            #         style={'border-width': '3px'}),  # calc(100vh - 500px)
            #     dbc.Card(
            #         dcc.Graph(figure=tree),  # , style={}
            #         style={'border-width': '3px', 'padding-bottom': '55px'}
            #     )
            # ]

            pies = [dbc.Col(ccp(c[0], c[1], c[2], c[3]), width=6) for c in zc2]

            main = [
                dbc.Card(
                    ccp('Top 20 %Quota by Province/District',
                        nd, 'bar', level_district),
                    style={'border-width': '3px'}
                ),
                dbc.Card(
                    dbc.Row(pies),
                    style={'border-width': '3px'}
                ),
                dbc.Card(
                    dcc.Graph(figure=tree, responsive=True,
                              config=dict(displaylogo=False, autosizable=True)),
                    style={'border-width': '3px'} #, 'border-bottom': 0
                ),
                dbc.Card('Copyright © 2021 Cassmatt Co., Ltd',
                className='p-0 m-0 border-0 d-flex justify-content-end align-items-center',
                style={'height':55})
            ]
# , fillFrame=True
            # 'width': '100', , style={'height': 'auto'}
        else:
            main = None

        return main, active, inactive, sum_premium, coveramount, s, cdd

    # Map

    @ dashapp.callback(Output('sim', 'children'), ipl)
    def map_sum_insure(layout, nd, future, dd1, province, district, quota,
                       cc_is_open, level_district, cards_dd_col):

        # print(future, dd1, district, nd)
        if layout == 'Map':
            ndl = ['coveramount']
            gb = ['future', 'suppliercode',
                  'region_c', 'PROVINCE', 'R_P',
                  'DISTRICT', 'R_P_A']
            dfm, active, inactive, sum_premium, coveramount = prep_data(
                gb, nd, future, dd1, province, district, quota, level_district)

            if level_district:
                from heatmap import dfmm, nation, heatmap
                dfmms = dfmm(dfm[['R_P_A']+ndl], ndl)
                dfmms = nation(dfmms, ndl, level_district)
                fig = heatmap(dfmms, 'coveramount', cc_is_open,
                              'color', 'text',  'colorscale', 'colorclasses', 'Sum Insured')

            else:
                dfmp = dfm[['PROVINCE', 'coveramount']].groupby(
                    'PROVINCE').sum().reset_index()
                dfmp.loc[dfmp.PROVINCE.str.contains('Bangkok'), 'PROVINCE'] =\
                    'Bangkok Metropolis'

                # Percent
                # dfm['Percent'] = round((dfm[nd]/dfm['q_'+nd])*100, 2)
                # dfm['Level'] = [levelf(x) for x in dfm.Percent]
                # dfm['Count'] = 1

                # Quota Level
                dfmp['color'] = '<0.5 Billion THB'
                # dfmp.loc[dfmp.coveramount > 100000000, 'color'] = 'Safe'
                dfmp.loc[dfmp.coveramount > 500000000,
                         'color'] = '>0.5 Billion THB'
                dfmp.loc[dfmp.coveramount > 1000000000,
                         'color'] = '>1.0 Billion THB'
                dfmp.loc[dfmp.coveramount > 2500000000,
                         'color'] = '>2.5 Billion THB'
                dfmp.loc[dfmp.coveramount > 5000000000,
                         'color'] = '>5.0 Billion THB'
                # dfm = dfm.loc[dfm.Quota.isin(quota)]

                purl = 'https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json'
                labels = {
                    'coveramount': 'Sum Insured',
                    #    'PROVINCE': 'Province',
                }
                hd = {
                    'coveramount': ':,.0f',
                    'PROVINCE': False,
                    'color': False
                }

                icb = {
                    '>5.0 Billion THB': '#F93154',
                    '>2.5 Billion THB': '#FFA900',
                    '>1.0 Billion THB': '#0275d8',
                    '>0.5 Billion THB': '#5bc0de',
                    '<0.5 Billion THB': '#f7f7f7',
                    # '(?)': '#FBFBFB'
                }

                fig = px.choropleth_mapbox(dfmp.sort_values(by='coveramount'), geojson=purl,
                                           featureidkey="properties.name", locations='PROVINCE',
                                           color='color', color_discrete_map=icb,
                                           mapbox_style="carto-positron",
                                           zoom=5, center=dict(lat=13.149, lon=101.493),
                                           opacity=0.5,
                                           hover_name='PROVINCE',
                                           hover_data=hd,
                                           labels=labels
                                           )
                fig.update_layout(legend=dict(title='',  # xx='d', # traceorder=icb.keys(), # orientation="h",
                                              yanchor="top", y=1, xanchor="left", x=0),
                                  margin={"r": 0, "t": 0, "l": 0, "b": 0})
            return dcc.Graph(figure=fig, id='heatmap_si', responsive=True,
                             config=dict(displaylogo=False, autosizable=True))
        else:
            return None

    @ dashapp.callback(Output('sim', 'width'), Output('slm', 'width'),
                       Output('heatmap_nd', 'figure'), Output(
                           'slm_col', 'is_open'),
                       ipl+[Input('map', 'value')])
    def map_sublimit_quota(layout, nd, future, dd1, province, district, quota,
                           cc_is_open, level_district, cards_dd_col, mckl):

        # print(future, dd1, district, nd)
        if layout == 'Map':
            if mckl:
                ndl = [nd, 'q_'+nd]
                gb = ['future', 'suppliercode',
                      'region_c', 'PROVINCE', 'R_P',
                      'DISTRICT', 'R_P_A']
                dfm, active, inactive, sum_premium, coveramount = prep_data(
                    gb, nd, future, dd1, province, district, quota, level_district)

                if level_district:
                    from heatmap import dfmm, nation, heatmap
                    dfmms = dfmm(dfm[['R_P_A']+ndl], ndl)
                    dfmms = nation(dfmms, ndl, level_district)
                    fig = heatmap(dfmms, nd, cc_is_open,
                                  'qcolor', 'qtext', 'cs', 'colorp', '%Quota')

                else:
                    dfmp = dfm[['PROVINCE']+ndl].groupby(
                        'PROVINCE').sum().reset_index()
                    dfmp.loc[dfmp.PROVINCE.str.contains(
                        'Bangkok'), 'PROVINCE'] = 'Bangkok Metropolis'
                    dfmp['Percent'] = round((dfmp[nd]/dfmp['q_'+nd])*100, 2)

                    def levelp(x):
                        if x > 80:
                            return '>80%'
                        elif x > 60:
                            return '>60%'
                        else:
                            return '<60%'

                    dfmp['Level'] = [levelp(x) for x in dfmp.Percent]

                    purl = 'https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json'
                    # labels = {
                    #     'coveramount': 'Sum Insured',
                    #     #    'PROVINCE': 'Province',
                    # }
                    hd = {
                        nd: ':,.0f',
                        'PROVINCE': False,
                        'Percent': True,
                        'Level': False
                    }
                    icb = {
                        '>80%': '#F93154',
                        '>60%': '#FFA900',
                        '<60%': '#5cb85c ',
                    }

                    fig = px.choropleth_mapbox(dfmp.sort_values(by='Percent'), geojson=purl,
                                               featureidkey="properties.name", locations='PROVINCE',
                                               color='Level', color_discrete_map=ic,
                                               mapbox_style="carto-positron",
                                               zoom=5, center=dict(lat=13.149, lon=101.493),
                                               opacity=0.5,
                                               hover_name='PROVINCE',
                                               hover_data=hd,
                                               # labels=labels
                                               )
                    fig.update_layout(legend=dict(title='',  # xx='d', # traceorder=icb.keys(), # orientation="h",
                                                  yanchor="top", y=1, xanchor="left", x=0),
                                      margin={"r": 0, "t": 0, "l": 0, "b": 0})

                return 6, 6, fig, True
            else:
                return 12, None, blank_fig(), False
        else:
            return 12, None, blank_fig(), False
