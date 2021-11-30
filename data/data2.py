from requirements import *

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
