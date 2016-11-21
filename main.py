from __future__ import division
import os
import os.path
import copy
import collections as col
import gdxpds
import pandas as pd
import numpy as np
import bokeh.io as bio
import bokeh.layouts as bl
import bokeh.plotting as bp
import bokeh.models as bm
import bokeh.models.widgets as bmw
import bokeh.models.glyphs as bmg

#set globals
runs_path = 'C:/Users/mmowers/Bokeh/runs_test/'
#runs_path = '//nrelqnap01d/ReEDS/FY16-RenewableTaxCreditExtensions-MRM-019743a-v2016/scenarios/runs/'
#runs_path = '//nrelqnap01d/ReEDS/FY16-MissionInnovation-MRM-019743a-v2016/runs/nuclear 80 yr/runs/'

scenarios = os.walk(runs_path).next()[1]
scenario_colors = 5*['#5e4fa2', '#3288bd', '#66c2a5', '#abdda4', '#e6f598', '#ffffbf', '#fee08b', '#fdae61', '#f46d43', '#d53e4f', '#9e0142']
regions_full = {
    'n': ['p'+str(i) for i in range(1,136)],
}
techs_full = ['hydro', 'gas-ct', 'gas-cc', 'gas-cc-ccs', 'coaloldscr', 'coalolduns', 'coal-new', 'coal-igcc', 'coal-ccs', 'o-g-s', 'nuclear', 'geothermal', 'undisc', 'nf-egs', 'shallow-egs', 'deep-egs', 'biopower', 'cofirebiomass', 'cofireold', 'cofirenew', 'lfill-gas', 'ocean', 'current', 'wave', 'mhkwave', 'distpv', 'wind', 'wind-ons', 'wind-ofs', 'wind-ofm', 'wind-ofd', 'solar', 'csp', 'csp-ns', 'csp-ws', 'pv', 'upv', 'dupv', 'pumped-hydro', 'battery', 'one-hour-battery', 'caes', 'ice-storage', 'demand-response', 'gas-ct-nsp', 'gas-cc-nsp', 'coal-ccs-nsp', 'nuclear-nsp', 'reqt']
#techs_full = ['hydro', 'gas-ct', 'gas-cc', 'gas-cc-ccs', 'coaloldscr', 'coalolduns', 'coal-new', 'coal-igcc', 'coal-ccs', 'o-g-s', 'nuclear', 'geothermal', 'undisc', 'nf-egs', 'shallow-egs', 'deep-egs', 'biopower', 'cofirebiomass', 'cofireold', 'cofirenew', 'lfill-gas', 'ocean', 'current', 'wave', 'mhkwave', 'distpv', 'wind', 'wind-ons', 'wind-ofs', 'wind-ofm', 'wind-ofd', 'solar', 'csp', 'csp-ns', 'csp-ws', 'pv', 'upv', 'dupv', 'pumped-hydro', 'battery', 'one-hour-battery', 'caes', 'ice-storage', 'demand-response', 'transmission', 'il', 'canada', 'curtail', 'phev', 'excess', 'reqt', 'cofire-rebate', 'gas-ct-nsp', 'gas-cc-nsp', 'coal-ccs-nsp', 'nuclear-nsp']
display_techs = col.OrderedDict((
    ('Conv Coal', {'techs': ['coaloldscr', 'coalolduns', 'coal-new', 'coal-igcc',], 'color': '#5e4fa2'}),
    ('Coal CCS', {'techs': ['coal-ccs','coal-ccs-nsp'], 'color': '#3288bd'}),
    ('Gas CC', {'techs': ['gas-cc','gas-cc-nsp'], 'color': '#66c2a5'}),
    ('Gas CCS', {'techs': ['gas-cc-ccs',], 'color': '#abdda4'}),
    ('Oil/Gas Steam', {'techs': ['o-g-s',], 'color': '#e6f598'}),
    ('Comb Turbines', {'techs': ['gas-ct','gas-ct-nsp'], 'color': '#ffffbf'}),
    ('Nuclear', {'techs': ['nuclear','nuclear-nsp'], 'color': '#fee08b'}),
    ('Hydro', {'techs': ['hydro',], 'color': '#fdae61'}),
    ('Onshore Wind', {'techs': ['wind-ons',], 'color': '#f46d43'}),
    ('Offshore Wind', {'techs': ['wind-ofs', 'wind-ofm', 'wind-ofd',], 'color': '#f46d43'}),
    ('UPV', {'techs': ['upv', 'dupv',], 'color': '#d53e4f'}), #capacity needs to be divided by 1.1 to reflect AC capacity.
    ('distPV', {'techs': ['distpv',], 'color': '#d53e4f'}),
    ('CSP', {'techs': ['csp', 'csp-ns', 'csp-ws',], 'color': '#d53e4f'}),
    ('Biomass', {'techs': ['biopower', 'cofirebiomass', 'lfill-gas',], 'color': '#9e0142'}),
    ('Cofire', {'techs': ['cofireold', 'cofirenew',], 'color': '#5e4fa2'}),
    ('Geothermal', {'techs': ['geothermal', 'nf-egs', 'shallow-egs', 'deep-egs',], 'color': '#5e4fa2'}),
    ('Pumped-hydro', {'techs': ['pumped-hydro',], 'color': '#5e4fa2'}),
    ('Battery', {'techs': ['battery',], 'color': '#5e4fa2'}),
    ('CAES', {'techs': ['caes',], 'color': '#5e4fa2'}),
    ('Bus Bar Load', {'techs': ['reqt',], 'color': '#5e4fa2'}), #
))
display_techs_colors = {k:v['color'] for k,v in display_techs.iteritems()}
tech_map = {}
for name in display_techs:
    for raw_tech in display_techs[name]['techs']:
        tech_map[raw_tech] = name

leftovers = ['undisc', 'one-hour-battery', 'ice-storage', 'demand-response', 'ocean', 'current', 'wave', 'mhkwave', 'solar', 'pv']

years_full = range(2010, 2052, 2)

hierarchy_input = pd.read_csv('csv/hierarchy.csv')
hierarchy = copy.deepcopy(hierarchy_input)

region_boundaries = {}
for regtype in hierarchy.columns.values.tolist():
    filepath = 'csv/gis_' + regtype + '.csv'
    if os.path.isfile(filepath):
        region_boundaries[regtype] = pd.read_csv(filepath, sep=',')
        region_boundaries[regtype]['x'] = region_boundaries[regtype]['long']*53
        region_boundaries[regtype]['y'] = region_boundaries[regtype]['lat']*69

gdx_structure = col.OrderedDict((
    ('Capacity (GW)', {'file': 'CONVqn.gdx', 'param': 'CONVqnallyears', 'columns': ['tech', 'n', 'year', 'value'], 'unit': 'GW', 'mult': 0.001, 'reg': 'n', 'xaxis': 'year', 'series': 'tech', 'series_keys': display_techs.keys(), 'series_colors': display_techs_colors}),
    ('Generation (TWh)', {'file': 'CONVqn.gdx', 'param': 'CONVqmnallyears', 'columns': ['tech', 'n', 'year', 'value'], 'unit': 'TWh', 'mult': 0.000001, 'reg': 'n', 'xaxis': 'year', 'series': 'tech', 'series_keys': display_techs.keys(), 'series_colors': display_techs_colors}),
    ('CO2 (Million Tonnes)', {'file': 'Reporting.gdx', 'param': 'AnnualReport', 'columns': ['n', 'year', 'type','value'], 'unit': 'Million tonnes', 'mult': 0.000001, 'reg': 'n', 'filters': {'type': 'CO2'}, 'xaxis': 'year'}),
))

data_obj = {}
for result in gdx_structure.keys():
    data_obj[result] = {}
    data_obj[result]['scenarios'] = {}
    data_obj[result]['combined'] = {'dataframe': 0}
    for scenario in scenarios:
        data_obj[result]['scenarios'][scenario] = {'dataframe': 0}

plot_list = col.OrderedDict()
plot_list['scenarios'] = col.OrderedDict()
plot_list['combined'] = {}

map_list = col.OrderedDict()
for scenario in scenarios:
    map_list[scenario] = {'plot': 0, 'max_val': 0, 'glyphs':{}}
    for regtype in hierarchy.columns.values.tolist():
        map_list[scenario]['glyphs'][regtype] = {}
        for region in hierarchy[regtype].unique():
            map_list[scenario]['glyphs'][regtype][region] = {'groups': {}, 'value':0}

scenario_legend_string = '<div class="legend-header">Scenarios</div><div class="legend-body">'
for i, scenario in enumerate(scenarios):
    scenario_legend_string += '<div class="legend-entry"><span class="legend-color" style="background-color:' + scenario_colors[i] + ';"></span>'
    scenario_legend_string += '<span class="legend-text">' + scenario + '</span></div>'
scenario_legend_string += '</div>'

tech_legend_string = '<div class="legend-header">Techs</div><div class="legend-body">'
techs_reversed = display_techs.keys()
techs_reversed.reverse()
for tech in techs_reversed:
    tech_legend_string += '<div class="legend-entry"><span class="legend-color" style="background-color:' + display_techs[tech]['color'] + ';"></span>'
    tech_legend_string += '<span class="legend-text">' + tech + '</span></div>'
tech_legend_string += '</div>'

map_legend_steps = 5
def build_map_legend(max_value=200):
    map_legend_string = '<div class="legend-header">Map ranges</div><div class="legend-body">'
    for legend_index in range(map_legend_steps):
        map_legend_string += '<div class="legend-entry"><span class="legend-color" style="background-color:' + scenario_colors[legend_index] + ';"></span>'
        map_legend_string += '<span class="legend-text">' + str(int(legend_index*max_value/map_legend_steps)) + ' - ' + str(int((legend_index+1)*max_value/map_legend_steps)) +'</span></div>'
    map_legend_string += '</div>'
    return map_legend_string

widgets = col.OrderedDict((
    ('legends_heading', bmw.Div(text='Legends', id='legends_heading')),
    ('techs_legend', bmw.Div(text=tech_legend_string, id='techs_legend')),
    ('scenarios_legend', bmw.Div(text=scenario_legend_string, id='scenarios_legend')),
    ('maps_legend', bmw.Div(text=build_map_legend(), id='maps_legend')),
    ('show_heading', bmw.Div(text='Show', id='show_heading')),
    ('scenarios_compare', bmw.Select(value='Show All', options=['Show All','Show Difference with Base'], id='scenarios_compare')),
    ('result', bmw.Select(value=gdx_structure.keys()[0], options=gdx_structure.keys(), id='result')),
    ('format', bmw.Select(value='Chart', options=['Figure','Table','Map'], id='format')),
    ('charttype', bmw.Select(value='Stacked Area', options=['Stacked Area'], id='charttype')),
    ('set_axis_ranges_heading', bmw.Div(text='Set axis ranges', id='set_axis_ranges_heading')),
    ('set_x_min', bmw.TextInput(title='x min', value='', id='set_x_min')),
    ('set_x_max', bmw.TextInput(title='x max', value='', id='set_x_max')),
    ('set_y_min', bmw.TextInput(title='y min', value='', id='set_y_min')),
    ('set_y_max', bmw.TextInput(title='y max', value='', id='set_y_max')),
    ('set_map_max_heading', bmw.Div(text='Set map max', id='set_map_max_heading')),
    ('set_map_max', bmw.TextInput(title='max', value='', id='set_map_max')),
    ('filters_heading', bmw.Div(text='Filters', id='filters_heading')),
    ('scenarios_heading', bmw.Div(text='Scenarios', id='scenarios_heading')),
    ('scenarios', bmw.CheckboxGroup(labels=scenarios, active=range(len(scenarios)), id='scenarios')),
    ('techs_heading', bmw.Div(text='Techs', id='techs_heading')),
    ('techs', bmw.CheckboxGroup(labels=display_techs.keys(), active=range(len(display_techs.keys())), id='techs')),
    ('regtype', bmw.Select(value='country', options=hierarchy.columns.values.tolist(), id='regtype')),
    ('region', bmw.Select(value='USA', options=hierarchy['country'].unique().tolist(), id='region')),
    ('map_subregtype', bmw.Select(value='st', options=hierarchy.columns.values.tolist(), id='map_subregtype')),
    ('year', bmw.Select(value=str(2050), options=[str(x) for x in years_full], id='year')),
    ('timeslice', bmw.Select(value='All timeslices', options=['All timeslices','H1','H2','H3'], id='timeslice')),
    ('scale_axes', bmw.RadioButtonGroup(labels=['Sync Axes', 'Scale Independently'], id='scale_axes')),
    ('rerender', bmw.Button(label='Re-render', button_type='success', id='rerender')),
    ('download', bmw.Button(label='Download CSV', button_type='success', id='download')),
))

def initialize():
    for scenario_name in scenarios:
        #build plots
        plot = {
            'figure': bp.Figure(toolbar_location='right', tools='save,pan,box_zoom,reset', width=250, height=225),
            'series': [],
            'xmin': 0,
            'xmax': 0,
            'ymin': 0,
            'ymax': 0,
        }
        plot['figure'].title.text = scenario_name
        plot['figure'].xaxis.major_label_orientation = 'vertical'
        plot['figure'].xaxis.major_label_standoff = 25
        plot_list['scenarios'][scenario_name] = plot
        
        #build maps
        map_plot = bm.Plot(x_range=bm.DataRange1d(), y_range=bm.DataRange1d(), plot_width=450, plot_height=250, toolbar_location=None)
        map_plot.title.text = scenario_name
        map_list[scenario_name]['plot']= map_plot
    
    combined_plot = {
        'figure': bp.Figure(toolbar_location='right', tools='save,pan,box_zoom,reset', width=250, height=225),
        'series': [],
    }
    combined_plot['figure'].title.text = 'Combined'
    combined_plot['figure'].xaxis.major_label_orientation = 'vertical'
    combined_plot['figure'].xaxis.major_label_standoff = 25
    plot_list['combined'] = combined_plot

    build_plots()
    build_maps()

def build_plots():
    result = widgets['result'].value
    for scenario in scenarios:
        build_plot(scenario, result)
    build_combined_chart(result)

def build_plot(scenario, result):
    df_base = data_obj[result]['scenarios'][scenario]['dataframe']
    if isinstance(df_base, int):
        df_base = get_dataframe(scenario, result)
        data_obj[result]['scenarios'][scenario]['dataframe'] = df_base
    df = filter_dataframe(df_base, regtype=widgets['regtype'].value, region=widgets['region'].value)
    if widgets['charttype'].value == 'Stacked Area':
        build_stacked_area_chart(df, scenario, result)

def build_combined_chart(result):
    df_base = data_obj[result]['combined']['dataframe']
    if isinstance(df_base, int):
        df_base = get_combined_dataframe(result)
        data_obj[result]['combined']['dataframe'] = df_base
    df = filter_dataframe(df_base, regtype=widgets['regtype'].value, region=widgets['region'].value, combined=True)
    build_combined_line_chart(df)


def build_stacked_area_chart(df, scenario, result):
    x_values = np.hstack((df.index, df.index[::-1])).tolist()
    y_values = stack_lists(df.transpose().values.tolist())
    save_axis_ranges(scenario, x_values, y_values)
    if 'series_colors' in gdx_structure[result]:
        series_color_base = gdx_structure[result]['series_colors']
        colors = [series_color_base[tech] for tech in df.columns]
    else:
        colors = ['#3288bd']*len(y_values)
    plot = plot_list['scenarios'][scenario]
    for plot_series in plot['series']:
        plot_series.glyph.visible = False
    for j in range(len(y_values)):
        if j < len(plot['series']):
            plot['series'][j].data_source.data['y'] = y_values[j]
            plot['series'][j].glyph.fill_color = colors[j]
        else:
            plot['series'].append(plot['figure'].patch(x_values, y_values[j], alpha = 0.8, fill_color = colors[j], line_color = None, line_width = None))
        plot['series'][j].glyph.visible = True

def build_combined_line_chart(df):
    x_values = df.index.tolist()
    y_values = df.transpose().values.tolist()

    y_shown = []
    plot = plot_list['combined']
    for j in range(len(y_values)):
        if j < len(plot['series']):
            plot['series'][j].data_source.data['y'] = y_values[j]
        else:
            plot['series'].append(plot['figure'].line(x_values, y_values[j], alpha = 0.8, color = scenario_colors[j], line_width = 2))
        if j in widgets['scenarios'].active:
            y_shown.append(y_values[j])
            plot['series'][j].glyph.visible = True
        else:
            plot['series'][j].glyph.visible = False
    plot['figure'].x_range.start = min(x_values)
    plot['figure'].x_range.end = max(x_values)
    plot['figure'].y_range.start = min([min(a) for a in y_shown]+[0])
    plot['figure'].y_range.end = max([max(a) for a in y_shown])

def save_axis_ranges(scenario, x_values, y_values):
    plot = plot_list['scenarios'][scenario]
    plot['x_min'] = min(x_values)
    plot['x_max'] = max(x_values)
    plot['y_min'] = min([min(a) for a in y_values]+[0])
    plot['y_max'] = max([max(a) for a in y_values])


def get_dataframe(scenario, result):
    gdx_result = gdx_structure[result]
    df = gdxpds.to_dataframe(runs_path + scenario + '\\gdxfiles\\' + gdx_result['file'], gdx_result['param'])[gdx_result['param']]
    df.columns = gdx_result['columns']
    if 'filters' in gdx_result:
        for key in gdx_result['filters']:
            df = df[df[key].isin([gdx_result['filters'][key]])]
            df = df.drop(key, 1)
    multi_index_iterables = []
    multi_index_names = []
    if 'tech' in df.columns:
        df['tech'] = df['tech'].str.lower()
        df = df.replace({'tech': tech_map})
        df = df[df['tech'].isin(display_techs.keys())]
        multi_index_iterables.append(display_techs.keys())
        multi_index_names.append('tech')
    if 'reg' in gdx_result:
        multi_index_iterables.append(regions_full[gdx_result['reg']])
        multi_index_names.append(gdx_result['reg'])
    if 'year' in df.columns:
        df['year'] = df['year'].apply(pd.to_numeric)
        multi_index_iterables.append(years_full)
        multi_index_names.append('year')
    if 'value' in df.columns:
        df['value'] = df['value']* gdx_result['mult']

    #sum over duplicates of the desired index (e.g. from techs that are grouped into one)
    df = df.groupby(multi_index_names, as_index=False, sort=False)['value'].sum()

    #now to fill up the missing values with 0:
    df_index = pd.MultiIndex.from_product(multi_index_iterables, names=multi_index_names)
    df = df.set_index(multi_index_names).reindex(df_index).reset_index()
    df = df.fillna(0)
    return df

def get_combined_dataframe(result):
    comb_df = pd.DataFrame()
    for scenario in scenarios:
        df = data_obj[result]['scenarios'][scenario]['dataframe']
        df['scenario'] = scenario
        comb_df = pd.concat([comb_df, df])
    return comb_df

def stack_lists(raw_lists):
    last_stack = [0]*len(raw_lists[0])
    stacked_lists = []
    for next_list in raw_lists:
        next_stack = [x + y for x, y in zip(last_stack, next_list)]
        stacked_lists.append(last_stack+next_stack[::-1])
        last_stack = next_stack
    return stacked_lists

def filter_dataframe(df_base, regtype, region, combined=False):
    gdx_result = gdx_structure[widgets['result'].value]
    if 'series_keys' in gdx_result: 
        series_keys = gdx_result['series_keys']
    hier = hierarchy.drop_duplicates(gdx_result['reg'])
    df = pd.merge(df_base, hier, how='left', on=gdx_result['reg'])
    df = df[df[regtype].isin([region])]
    if 'tech' in gdx_result['columns']:
        active_techs = [widgets['techs'].labels[i] for i in widgets['techs'].active]
        df = df[df['tech'].isin(active_techs)]
        if 'series' in gdx_result and gdx_result['series'] == 'tech':
            series_keys = [key for key in series_keys if key in active_techs]
    if not combined:
        if 'series' in gdx_result:
            df = df.groupby([gdx_result['series'], gdx_result['xaxis']], as_index=False, sort=False)['value'].sum()
            df = df.pivot(index=gdx_result['xaxis'], columns=gdx_result['series'], values='value')
            df = df[series_keys] #to order the columns properly
        else:
            df = df.groupby([gdx_result['xaxis']], sort=False)['value'].sum()
    else:
        df = df.groupby(['scenario', gdx_result['xaxis']], as_index=False, sort=False)['value'].sum()
        df = df.pivot(index=gdx_result['xaxis'], columns='scenario', values='value')
    if not isinstance(df, pd.DataFrame):
        df = df.to_frame()
    return df

def build_maps():
    build_maps_glyphs()
    set_maps_values()
    shade_maps()

def build_maps_glyphs():
    for scenario in scenarios:
        build_map_glyphs(scenario)
def build_map_glyphs(scenario):
    #get current map
    plot = map_list[scenario]['plot']

    #get selected region and subregion type
    regtype = widgets['regtype'].value
    region = widgets['region'].value
    subregtype = widgets['map_subregtype'].value

    #get all subregions of selected region
    #first get all regions associated with selected region 
    associated_regions = hierarchy[hierarchy[regtype].isin([region])]
    #then filter by the subregion type
    subregions = associated_regions[subregtype].unique()

    #get the boundaries of the subregion type
    df_subregtype_boundaries = region_boundaries[subregtype]

    #get max and min coordinates for all subregions, and use to set width of plot
    df_subregion_boundaries = df_subregtype_boundaries[df_subregtype_boundaries['id'].isin(subregions)]
    min_x = df_subregion_boundaries['x'].min()
    max_x = df_subregion_boundaries['x'].max()
    min_y = df_subregion_boundaries['y'].min()
    max_y = df_subregion_boundaries['y'].max()
    plot.x_range.start = min_x
    plot.y_range.start = min_y
    plot_aspect = plot.plot_width/plot.plot_height
    glyphs_aspect = (max_x - min_x)/(max_y - min_y)
    if glyphs_aspect > plot_aspect:
        plot.x_range.end = max_x
        plot.y_range.end = min_y + (max_x - min_x)/plot_aspect
    else:
        plot.y_range.end = max_y
        plot.x_range.end = min_x + (max_y - min_y)*plot_aspect

    #Hide all glyphs in this map  
    for subregtype_iter in map_list[scenario]['glyphs'].values():
        for subreg_iter in subregtype_iter.values():
            for glyph in subreg_iter['groups'].values():
                glyph.visible = False

    #Set the glyphs for each subregion
    for subreg in subregions:
        #check if glyphs exist and, if not, make glyphs
        if not map_list[scenario]['glyphs'][subregtype][subreg]['groups']:
            #get the x,y coordinates and groups of this subregion
            df_map_subreg = df_subregtype_boundaries[df_subregtype_boundaries['id'] == subreg]
            #for each group, draw glyph
            for subreg_group in df_map_subreg['group'].unique():
                df_map_subreg_group = df_map_subreg[df_map_subreg['group'] == subreg_group]
                source = bm.ColumnDataSource(dict(x=df_map_subreg_group['x'], y=df_map_subreg_group['y']))
                glyph = bmg.Patch(x="x", y="y", fill_color="#a6cee3")
                plot.add_glyph(source, glyph)
                map_list[scenario]['glyphs'][subregtype][subreg]['groups'][subreg_group] = glyph
        #if glyphs already exist, we need to show them, because we hid them above
        else:
            for glyph in map_list[scenario]['glyphs'][subregtype][subreg]['groups'].values():
                glyph.visible = True

def set_maps_values():
    result = widgets['result'].value
    regtype = widgets['regtype'].value
    region = widgets['region'].value
    subregtype = widgets['map_subregtype'].value
    year = widgets['year'].value

    #get all subregions of selected region
    #first get all regions associated with selected region 
    associated_regions = hierarchy[hierarchy[regtype].isin([region])]
    #then filter by the subregion type
    subregions = associated_regions[subregtype].unique()
    for scenario in scenarios:
        #get relevant data for this result and scenario
        df_base = data_obj[result]['scenarios'][scenario]['dataframe']
        #Set the values (for shading)
        for subreg in subregions:
            #Set the value for this subregion, which will be used for shading
            df_subreg = filter_dataframe(df_base, regtype=subregtype, region=subreg, combined=True)
            value = df_subreg[scenario][int(year)]
            map_list[scenario]['glyphs'][subregtype][subreg]['value'] = value
        #update the maximum values for each scenario map
        map_list[scenario]['max_val'] = max([map_list[scenario]['glyphs'][subregtype][subreg]['value'] for subreg in subregions])

def shade_maps():
    user_max = widgets['set_map_max'].value
    regtype = widgets['regtype'].value
    region = widgets['region'].value
    subregtype = widgets['map_subregtype'].value

    max_value = float(user_max) if user_max else max([a['max_val'] for a in map_list.values()])
    widgets['maps_legend'].text = build_map_legend(max_value)

    #get all subregions of selected region
    #first get all regions associated with selected region 
    associated_regions = hierarchy[hierarchy[regtype].isin([region])]
    #then filter by the subregion type
    subregions = associated_regions[subregtype].unique()
    for scenario in scenarios:
        for subreg in subregions:
            value = map_list[scenario]['glyphs'][subregtype][subreg]['value']
            bin_index = int(map_legend_steps*value/max_value)
            if bin_index >= map_legend_steps: bin_index = map_legend_steps - 1
            for glyph in map_list[scenario]['glyphs'][subregtype][subreg]['groups'].values():
                glyph.fill_color = scenario_colors[bin_index]

def sync_axes():
    scenario_plots = plot_list['scenarios'].values()
    x_min = min([a['x_min'] for a in scenario_plots])
    x_max = max([a['x_max'] for a in scenario_plots])
    y_min = min([a['y_min'] for a in scenario_plots])
    y_max = max([a['y_max'] for a in scenario_plots])
    for plot in scenario_plots:
        plot['figure'].x_range.start = x_min
        plot['figure'].x_range.end = x_max
        plot['figure'].y_range.start = y_min
        plot['figure'].y_range.end = y_max

def scale_axes_independently():
    for plot in plot_list['scenarios'].values():
        plot['figure'].x_range.start = plot['x_min']
        plot['figure'].x_range.end = plot['x_max']
        plot['figure'].y_range.start = plot['y_min']
        plot['figure'].y_range.end = plot['y_max']

def update_scenarios(attrname, old, new):
    build_plots()

def update_techs(attrname, old, new):
    build_plots()
    set_maps_values()
    shade_maps()

def update_result(attrname, old, new):
    build_plots()
    set_maps_values()
    shade_maps()

def update_region(attrname, old, new):
    build_plots()
    build_maps()

def update_regtype(attrname, old, new):
    widgets['region'].options = hierarchy[widgets['regtype'].value].unique().tolist()
    widgets['region'].value = widgets['region'].options[0]

def update_year(attrname, old, new):
    set_maps_values()
    shade_maps()

def update_map_subregtype(attrname, old, new):
    build_maps()

def update_x_min(attrname, old, new):
    for plot in plot_list['scenarios'].values():
        plot['figure'].x_range.start = float(new)
    plot_list['combined']['figure'].x_range.start = float(new)

def update_x_max(attrname, old, new):
    for plot in plot_list['scenarios'].values():
        plot['figure'].x_range.end = float(new)
    plot_list['combined']['figure'].x_range.end = float(new)

def update_y_min(attrname, old, new):
    for plot in plot_list['scenarios'].values():
        plot['figure'].y_range.start = float(new)
    plot_list['combined']['figure'].y_range.start = float(new)

def update_y_max(attrname, old, new):
    for plot in plot_list['scenarios'].values():
        plot['figure'].y_range.end = float(new)
    plot_list['combined']['figure'].y_range.end = float(new)

def update_map_max(attrname, old, new):
    shade_maps()

def scale_axes(new):
    if new == 0: sync_axes()
    elif new == 1: scale_axes_independently()

def rerender():
    build_plots()
    scale_axes(widgets['scale_axes'].active)

def download():
    result = widgets['result'].value
    df_base = data_obj[result]['combined']['dataframe']
    gdx_result = gdx_structure[result]
    hier = hierarchy.drop_duplicates(gdx_result['reg'])
    df = pd.merge(df_base, hier, how='left', on=gdx_result['reg'])
    df = df[df[widgets['regtype'].value].isin([widgets['region'].value])]
    if 'tech' in gdx_result['columns']:
        active_techs = [widgets['techs'].labels[i] for i in widgets['techs'].active]
        df = df[df['tech'].isin(active_techs)]
    if 'series' in gdx_result:
        df = df.groupby(['scenario', gdx_result['xaxis'], gdx_result['series']], as_index=False, sort=False)['value'].sum()
    else:
        df = df.groupby(['scenario', gdx_result['xaxis']], as_index=False, sort=False)['value'].sum()
    if not isinstance(df, pd.DataFrame):
        df = df.to_frame()
    df.to_csv('../../downloads/out.csv', index=False)


widgets['scenarios'].on_change('active', update_scenarios)
widgets['techs'].on_change('active', update_techs)
widgets['result'].on_change('value', update_result)
widgets['region'].on_change('value', update_region)
widgets['regtype'].on_change('value', update_regtype)
widgets['year'].on_change('value', update_year)
widgets['map_subregtype'].on_change('value', update_map_subregtype)
widgets['set_x_min'].on_change('value', update_x_min)
widgets['set_x_max'].on_change('value', update_x_max)
widgets['set_y_min'].on_change('value', update_y_min)
widgets['set_y_max'].on_change('value', update_y_max)
widgets['set_map_max'].on_change('value', update_map_max)
widgets['scale_axes'].on_click(scale_axes)
widgets['rerender'].on_click(rerender)
widgets['download'].on_click(download)

initialize()
filters = bl.widgetbox(widgets.values(), width=300, id='widgets_section')
charts = [p['figure'] for p in plot_list['scenarios'].values()]
charts.append(plot_list['combined']['figure'])
charts_display = bl.column(charts, width=1000, id='charts_section')
maps = [p['plot'] for p in map_list.values()]
maps_display = bl.column(maps, width=1000, id='maps_section')
plots_display = bl.column(charts_display, maps_display)
bio.curdoc().add_root(bl.row([filters, plots_display]))