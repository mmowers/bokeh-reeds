import os
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

#set globals
gdx_structure = col.OrderedDict((
    ('Capacity (GW)', {'file': 'CONVqn.gdx', 'param': 'CONVqnallyears', 'columns': ['tech', 'n', 'year', 'value'], 'unit': 'GW', 'mult': 0.001, 'reg': 'n'}),
    ('Generation (TWh)', {'file': 'CONVqn.gdx', 'param': 'CONVqmnallyears', 'columns': ['tech', 'n', 'year', 'value'], 'unit': 'TWh', 'mult': 0.000001, 'reg': 'n'}),
))

runs_path = 'C:\\Users\\mmowers\\Bokeh\\runs\\'
scenarios = os.walk(runs_path).next()[1]

regions_full = {
    'n': ['p'+str(i) for i in range(1,136)],
}
techs_full = ['hydro', 'gas-ct', 'gas-cc', 'gas-cc-ccs', 'coaloldscr', 'coalolduns', 'coal-new', 'coal-igcc', 'coal-ccs', 'o-g-s', 'nuclear', 'geothermal', 'undisc', 'nf-egs', 'shallow-egs', 'deep-egs', 'biopower', 'cofirebiomass', 'cofireold', 'cofirenew', 'lfill-gas', 'ocean', 'current', 'wave', 'mhkwave', 'distpv', 'wind', 'wind-ons', 'wind-ofs', 'wind-ofm', 'wind-ofd', 'solar', 'csp', 'csp-ns', 'csp-ws', 'pv', 'upv', 'dupv', 'pumped-hydro', 'battery', 'one-hour-battery', 'caes', 'ice-storage', 'demand-response', 'gas-ct-nsp', 'gas-cc-nsp', 'coal-ccs-nsp', 'nuclear-nsp']
#techs_full = ['hydro', 'gas-ct', 'gas-cc', 'gas-cc-ccs', 'coaloldscr', 'coalolduns', 'coal-new', 'coal-igcc', 'coal-ccs', 'o-g-s', 'nuclear', 'geothermal', 'undisc', 'nf-egs', 'shallow-egs', 'deep-egs', 'biopower', 'cofirebiomass', 'cofireold', 'cofirenew', 'lfill-gas', 'ocean', 'current', 'wave', 'mhkwave', 'distpv', 'wind', 'wind-ons', 'wind-ofs', 'wind-ofm', 'wind-ofd', 'solar', 'csp', 'csp-ns', 'csp-ws', 'pv', 'upv', 'dupv', 'pumped-hydro', 'battery', 'one-hour-battery', 'caes', 'ice-storage', 'demand-response', 'transmission', 'il', 'canada', 'curtail', 'phev', 'excess', 'reqt', 'cofire-rebate', 'gas-ct-nsp', 'gas-cc-nsp', 'coal-ccs-nsp', 'nuclear-nsp']
display_techs = col.OrderedDict((
    ('Conv Coal', {'techs': ['coaloldscr', 'coalolduns', 'coal-new', 'coal-igcc', 'cofireold', 'cofirenew',], 'color': '#5e4fa2'}),
    ('Coal CCS', {'techs': ['coal-ccs','coal-ccs-nsp'], 'color': '#3288bd'}),
    ('Gas CC', {'techs': ['gas-cc','gas-cc-nsp'], 'color': '#66c2a5'}),
    ('Gas CCS', {'techs': ['gas-cc-ccs',], 'color': '#abdda4'}),
    ('Oil/Gas Steam', {'techs': ['o-g-s',], 'color': '#e6f598'}),
    ('Comb Turbines', {'techs': ['gas-ct','gas-ct-nsp'], 'color': '#ffffbf'}),
    ('Nuclear', {'techs': ['nuclear','nuclear-nsp'], 'color': '#fee08b'}),
    ('Hydro', {'techs': ['hydro',], 'color': '#fdae61'}),
    ('Wind', {'techs': ['wind-ons', 'wind-ofs', 'wind-ofm', 'wind-ofd',], 'color': '#f46d43'}),
    ('Solar', {'techs': ['distpv',  'solar', 'csp', 'csp-ns', 'csp-ws', 'pv', 'upv', 'dupv',], 'color': '#d53e4f'}),
    ('Dedicated Bio', {'techs': ['biopower',], 'color': '#9e0142'}),
    ('Other Renew', {'techs': ['geothermal', 'nf-egs', 'shallow-egs', 'deep-egs', 'cofirebiomass', 'lfill-gas', 'ocean', 'current', 'wave', 'mhkwave',], 'color': '#5e4fa2'}),
))
tech_map = {}
for name in display_techs:
    for raw_tech in display_techs[name]['techs']:
        tech_map[raw_tech] = name

display_techs_w_color = [name+':'+display_techs[name]['color'] for name in display_techs]
display_techs_w_color.reverse()

leftovers = ['undisc', 'pumped-hydro', 'battery', 'one-hour-battery', 'caes', 'ice-storage', 'demand-response']

years_full = range(2010, 2052, 2)

hierarchy_input = pd.read_csv('hierarchy.csv', header=None)
hierarchy = copy.deepcopy(hierarchy_input)
hierarchy_column_names = ['i','n','r','rnew','rto','censusregions','st','in','country','custreg','readin']
hierarchy.columns = hierarchy_column_names

colors = ['#5e4fa2', '#3288bd', '#66c2a5', '#abdda4', '#e6f598', '#ffffbf', '#fee08b', '#fdae61', '#f46d43', '#d53e4f', '#9e0142']
colors = colors*10

data_obj = {}
for result in gdx_structure.keys():
    data_obj[result] = {}
    for scenario in scenarios:
        data_obj[result][scenario] = {'dataframe': 0}

plot_list = []

widgets = col.OrderedDict((
    ('scenarios_heading', bmw.Div(text='Select Scenarios', id='scenarios_heading')),
    ('scenarios', bmw.CheckboxGroup(labels=scenarios, active=range(len(scenarios)), id='scenarios')),
    ('scenarios_compare', bmw.Select(value='Show All', options=['Show All','Show Difference with Base'], id='scenarios_compare')),
    ('result', bmw.Select(value=gdx_structure.keys()[0], options=gdx_structure.keys(), id='result')),
    ('format', bmw.Select(value='Chart', options=['Figure','Table','Map'], id='format')),
    ('charttype', bmw.Select(value='Stacked Area', options=['Stacked Area'], id='charttype')),
    ('xaxis', bmw.Select(title='X-axis: ', value='year', options=['year', 'tech'], id='xaxis')),
    ('series', bmw.Select(title='Series: ', value='tech', options=['tech', 'year'], id='series')),
    ('filters_heading', bmw.Div(text='Select Filters:', id='filters_heading')),
    ('tech', bmw.Select(value='All techs', options=['All techs']+display_techs_w_color, id='tech')),
    ('regtype', bmw.Select(value='country', options=hierarchy_column_names, id='regtype')),
    ('region', bmw.Select(value='USA', options=hierarchy['country'].unique().tolist(), id='region')),
    ('year', bmw.Select(value='All years', options=['All years'] + [str(x) for x in years_full], id='year')),
    ('timeslice', bmw.Select(value='All timeslices', options=['All timeslices','H1','H2','H3'], id='timeslice')),
    ('scale_axes', bmw.RadioButtonGroup(labels=["Sync Axes", "Scale Independently"])),
))

def initialize():
    for scenario_name in scenarios:
        result = widgets['result'].value
        df_base = get_dataframe(scenario_name, result)

        #save data
        data_obj[result][scenario_name]['dataframe'] = df_base

        #build plots
        plot = {
            'figure': bp.Figure(toolbar_location='right', tools='save,pan,box_zoom,reset', width=250, height=250),
            'series': [],
            'xmin': 0,
            'xmax': 0,
            'ymin': 0,
            'ymax': 0,
        }
        plot['figure'].title.text = scenario_name
        plot['figure'].xaxis.major_label_orientation = 'vertical'
        plot['figure'].xaxis.major_label_standoff = 25
        plot_list.append(plot)
    fill_plots()

def fill_plots():
    for scenario in scenarios:
        fill_plot(scenario)

def fill_plot(scenario):
    result = widgets['result'].value
    df_base = data_obj[result][scenario]['dataframe']
    if type(df_base) is int:
        df_base = get_dataframe(scenario, result)
        data_obj[result][scenario]['dataframe'] = df_base
    df = filter_dataframe(df_base)
    if widgets['charttype'].value == 'Stacked Area':
        fill_stacked_areas(df, scenario)

def fill_stacked_areas(df, scenario):
    i = scenarios.index(scenario)
    x_values = np.hstack((df.index, df.index[::-1])).tolist()
    y_values = stack_lists(df.transpose().values.tolist())
    get_axis_ranges(scenario, x_values, y_values)

    for j, series_name in enumerate(df.columns.values.tolist()):
        if j < len(plot_list[i]['series']):
            plot_list[i]['series'][j].data_source.data['y'] = y_values[j]
        else:
            plot_list[i]['series'].append(plot_list[i]['figure'].patch(x_values, y_values[j], alpha = 0.8, color = display_techs[series_name]['color'], line_color = None, line_width = None, name = series_name))

def get_axis_ranges(scenario, x_values, y_values):
    i = scenarios.index(scenario)
    plot_list[i]['x_min'] = min(x_values)
    plot_list[i]['x_max'] = max(x_values)
    plot_list[i]['y_min'] = min([min(a) for a in y_values])
    plot_list[i]['y_max'] = max([max(a) for a in y_values])


def get_dataframe(scenario, result_type):
    gdx_result = gdx_structure[result_type]
    df = gdxpds.to_dataframe(runs_path + scenario + '\\gdxfiles\\' + gdx_result['file'], gdx_result['param'])[gdx_result['param']]
    df.columns = gdx_result['columns']
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
        hier = hierarchy.drop_duplicates(gdx_result['reg'])
    if 'year' in df.columns:
        df['year'] = df['year'].apply(pd.to_numeric)
        multi_index_iterables.append(years_full)
        multi_index_names.append('year')
    if 'value' in df.columns:
        df['value'] = df['value']* gdx_result['mult']
    
    df = df.groupby(multi_index_names, as_index=False, sort=False)['value'].sum()
    df_index = pd.MultiIndex.from_product(multi_index_iterables, names=multi_index_names)
    df = df.set_index(multi_index_names).reindex(df_index).reset_index()
    df = df.fillna(0)
    
    if 'reg' in gdx_result:
        df = pd.merge(df, hier, how='left', on=gdx_result['reg'])
    return df

def stack_lists(raw_lists):
    last_stack = [0]*len(raw_lists[0])
    stacked_lists = []
    for next_list in raw_lists:
        next_stack = [x + y for x, y in zip(last_stack, next_list)]
        stacked_lists.append(last_stack+next_stack[::-1])
        last_stack = next_stack
    return stacked_lists

def filter_dataframe(df_base):
    df = df_base[df_base[widgets['regtype'].value].isin([widgets['region'].value])]
    df = df.groupby([widgets['series'].value, widgets['xaxis'].value], as_index=False, sort=False)['value'].sum()
    df = df.pivot(index=widgets['xaxis'].value, columns=widgets['series'].value, values='value')
    df = df[display_techs.keys()]
    return df

def sync_axes():
    x_min = min([a['x_min'] for a in plot_list])
    x_max = max([a['x_max'] for a in plot_list])
    y_min = min([a['y_min'] for a in plot_list])
    y_max = max([a['y_max'] for a in plot_list])
    for plot in plot_list:
        plot['figure'].x_range.start = x_min
        plot['figure'].x_range.end = x_max
        plot['figure'].y_range.start = y_min
        plot['figure'].y_range.end = y_max

def scale_axes_independently():
    for plot in plot_list:
        plot['figure'].x_range.start = plot['x_min']
        plot['figure'].x_range.end = plot['x_max']
        plot['figure'].y_range.start = plot['y_min']
        plot['figure'].y_range.end = plot['y_max']

def general_filter_update(attrname, old, new):
    fill_plots()
    widgets['scale_axes'].active = None

def update_regtype(attrname, old, new):
    widgets['region'].options = hierarchy[widgets['regtype'].value].unique().tolist()
    widgets['region'].value = widgets['region'].options[0]

def scale_axes(new):
    if new == 0: sync_axes()
    elif new == 1: scale_axes_independently()

widgets['result'].on_change('value', general_filter_update)
widgets['region'].on_change('value', general_filter_update)
widgets['regtype'].on_change('value', update_regtype)
widgets['scale_axes'].on_click(scale_axes)

initialize()
plots = [p['figure'] for p in plot_list]
filters = bl.widgetbox(widgets.values(), width=300, id='widgets_section')
plots_display = bl.column(plots, width=1000, id='plots_section')
bio.curdoc().add_root(bl.row([filters, plots_display]))