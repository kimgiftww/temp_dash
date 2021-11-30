from requirements import *

df = gpd.read_file('gadm36_THA_2.shp')
df['point'] = df['geometry'].to_crs(epsg=4326).centroid
df['lat'] = df.point.y
df['lon'] = df.point.x
# df['fw'] = 1
df = df.dropna(subset=['NL_NAME_2'])  # , inplace=True
df.loc[df.NAME_1.str.contains('Bangkok'), 'NL_NAME_1'] = 'กรุงเทพมหานคร'
df.loc[df.NAME_1.str.contains('Chaiyaphum'), 'NL_NAME_1'] = 'ชัยภูมิ'
df.loc[df.NL_NAME_2.str.contains('บางกะป'), 'NL_NAME_2'] = 'บางกะปิ'
df.loc[df.NL_NAME_2.str.contains('ทวีวัฒนา'), 'NL_NAME_2'] = 'ทวีวัฒนา'
df.loc[df.NL_NAME_2.str.contains('ธนบุร'), 'NL_NAME_2'] = 'ธนบุรี'
df.loc[df.NL_NAME_2.str.contains('หลักส'), 'NL_NAME_2'] = 'หลักสี่'
df.loc[df.NL_NAME_2.str.contains('บึงกาฬ'), 'NL_NAME_2'] = 'เมืองบึงกาฬ'
df.loc[df.NL_NAME_2.str.contains('เมืองยาง'), 'NL_NAME_2'] = 'เมืองยาง'
df.loc[df.NL_NAME_2.str.contains('สุขสำราญ'), 'NL_NAME_2'] = 'สุขสำราญ'
df.loc[df.NL_NAME_2.str.contains(
    'เฉลิมพระเกียรต'), 'NL_NAME_2'] = 'เฉลิมพระเกียรติ'
df.loc[df.NL_NAME_2.str.contains('ศรีนครินทร'), 'NL_NAME_2'] = 'ศรีนครินทร์'
df.loc[df.NL_NAME_2.str.contains('ปากพยูน'), 'NL_NAME_2'] = 'ปากพะยูน'
df.loc[df.NL_NAME_2.str.contains('ภูชาง'), 'NL_NAME_2'] = 'ภูซาง'
df.loc[df.NL_NAME_2.str.contains('วชิระบารมี'), 'NL_NAME_2'] = 'วชิรบารมี'
df.loc[df.NL_NAME_2.str.contains('บึงบูรณ์'), 'NL_NAME_2'] = 'บึงบูรพ์'
df.loc[df.NL_NAME_2.str.contains('เกาะพงัน'), 'NL_NAME_2'] = 'เกาะพะงัน'
df.loc[df.NL_NAME_2.str.contains('พิบูลรักษ์'), 'NL_NAME_2'] = 'พิบูลย์รักษ์'
df.loc[df.NL_NAME_2.str.contains('จุฬาภรณ'), 'NL_NAME_2'] = 'จุฬาภรณ์'
df.loc[df.NL_NAME_2.str.contains('หนองบุญนาก'), 'NL_NAME_2'] = 'หนองบุญมาก'
df.loc[df.NL_NAME_2.str.contains('โคกโพธิ์ชัย'), 'NL_NAME_2'] = 'โคกโพธิ์ไชย'
df.loc[df.NL_NAME_2.str.contains('กุฉินารายน์'), 'NL_NAME_2'] = 'กุฉินารายณ์'
df.loc[df.NL_NAME_2.str.contains('สนามชัยเขต'), 'NL_NAME_2'] = 'สนามชัย'
df.loc[df.NL_NAME_2.str.contains('ราชสาสน์'), 'NL_NAME_2'] = 'ราชสาส์น'

df.NL_NAME_2 = df.NL_NAME_2.str.replace('กิ่ง', '')
df.NL_NAME_2 = df.NL_NAME_2.str.replace('อำเภอ', '')
df.NL_NAME_1 = df.NL_NAME_1.str.replace('จังหวัด', '')
df.NL_NAME_1 = df.NL_NAME_1.str.replace('อำเภอเมือง', '')
df['p_a'] = df.NL_NAME_1 + '_' + df.NL_NAME_2
df['P_A'] = df.NAME_1 + '_' + df.NAME_2

fw = pd.read_csv('district.csv', header=None)[0]
print('fw_data', fw)
df.loc[df.NL_NAME_2.isin(fw)  # df.NL_NAME_2.str.contains('|'.join(fw))
       | df.p_a.str.contains('พิษณุโลก_วังทอง')
       | df.p_a.str.contains('สระบุรี_เฉลิมพระเกียรติ')
       | df.p_a.str.contains('พระนครศรีอยุธยา_เสนา'),
       'symbol'] = 'swimming'
fw = df.loc[df.symbol == 'swimming']['p_a'].unique()
print('fw_data', fw)

dfm = pd.read_pickle('hdg.pickle')
print('dfm from hdg.pickle', len(dfm), dfm.columns)
region = np.sort(dfm.region.dropna().unique())
regiond = [{'label': i, 'value': i}
           for i in region] + [{'label': 'น้ำท่วม', 'value': 'FLOOD'}]
region_c = np.sort(dfm.region_c.dropna().unique())
region_cd = [{'label': i, 'value': i}
           for i in region_c] + [{'label': 'FLOOD', 'value': 'FLOOD'}]
suppliername = np.sort(dfm.suppliername.unique())
suppliercode = np.sort(dfm.suppliercode.unique())

# gb = ['region', 'p_a']  # gb = ['provincename','district_c']
cj = ['CC_2', 'geometry', 'point', 'NL_NAME_2', 'NL_NAME_1',
      'NAME_2', 'NAME_1', 'HASC_2', 'p_a', 'P_A', 'symbol', 'lat', 'lon']
ndmap = {'น้ำท่วม': 'flood', 'พายุ': 'storm',
         'ลูกเห็บ': 'snow', 'แผ่นดินไหว': 'quake'}


def dfmm(dfm, nd, *region_c):
    ndq = [nd, 'q_'+ndmap[nd], 'qr_'+ndmap[nd]]
    if region_c:
        gb = ['region_c', 'P_A']
        dfmg = dfm.groupby(gb)[ndq].sum().reset_index()
        dfmg[nd] = dfmg[nd].astype(int)
        dfmg['qp_'+ndmap[nd]] = (dfmg[nd] / dfmg['q_'+ndmap[nd]])*100
        dfmg['text'] = dfmg.P_A + '<br>' + dfmg[nd].apply(lambda x: f'{x:,.0f}')
        dfmg['qtext'] = dfmg.P_A + '<br>' + \
            dfmg['qp_'+ndmap[nd]].apply(lambda x: f'{x:,.0f}%')
        dfmm = df[cj].merge(dfmg, left_on='P_A', right_on='P_A', how='left')
        dfmm = dfmm.dropna(subset=[nd]).rename(columns={'P_A': 'name'})
    else:
        gb = ['region', 'p_a']
        dfmg = dfm.groupby(gb)[ndq].sum().reset_index()
        dfmg[nd] = dfmg[nd].astype(int)
        dfmg['qp_'+ndmap[nd]] = (dfmg[nd] / dfmg['q_'+ndmap[nd]])*100
        dfmg['text'] = dfmg.p_a + '<br>' + dfmg[nd].apply(lambda x: f'{x:,.0f}')
        dfmg['qtext'] = dfmg.p_a + '<br>' + \
            dfmg['qp_'+ndmap[nd]].apply(lambda x: f'{x:,.0f}%')
        dfmm = df[cj].merge(dfmg, left_on='p_a', right_on='p_a', how='left')
        dfmm = dfmm.dropna(subset=[nd]).rename(columns={'p_a': 'name'})
    return dfmm
