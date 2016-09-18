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
runs_path = 'C:\\Users\\mmowers\\Bokeh\\runs\\'
scenarios = os.walk(runs_path).next()[1]
scenario_colors = 5*['#5e4fa2', '#3288bd', '#66c2a5', '#abdda4', '#e6f598', '#ffffbf', '#fee08b', '#fdae61', '#f46d43', '#d53e4f', '#9e0142']
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
    ('Biomass', {'techs': ['biopower', 'cofirebiomass', 'lfill-gas',], 'color': '#9e0142'}),
    ('Geothermal', {'techs': ['geothermal', 'nf-egs', 'shallow-egs', 'deep-egs',], 'color': '#5e4fa2'}),
))
display_techs_colors = [display_techs[key]['color'] for key in display_techs]
tech_map = {}
for name in display_techs:
    for raw_tech in display_techs[name]['techs']:
        tech_map[raw_tech] = name

leftovers = ['undisc', 'pumped-hydro', 'battery', 'one-hour-battery', 'caes', 'ice-storage', 'demand-response', 'ocean', 'current', 'wave', 'mhkwave',]

years_full = range(2010, 2052, 2)

hierarchy_input = pd.read_csv('hierarchy.csv', header=None)
hierarchy = copy.deepcopy(hierarchy_input)
hierarchy_column_names = ['i','n','r','rnew','rto','censusregions','st','in','country','custreg','readin']
hierarchy.columns = hierarchy_column_names

# tech_map_input = pd.read_csv('tech_map.csv', header=None)
# tech_map = copy.deepcopy(tech_map_input)
# tech_map_column_names = ['tech', 'grouped_tech']
# tech_map.columns = tech_map_column_names

gdx_structure = col.OrderedDict((
    ('Capacity (GW)',
        {'file': 'CONVqn.gdx',
        'param': 'CONVqnallyears',
        'columns': ['tech', 'n', 'year', 'value'],
        'reg': 'n',
        'default_xaxis': 'year',
        'default_series': 'tech',
        'default_yaxis': 'value',
        'default_aggregation': 'sum',
        'mult': 0.001,
        'unit': 'GW',
        'default_chart_type': 'stacked_area',
        'xaxis': 'year',
        'series': 'tech',
        'series_keys': display_techs.keys(),
        'series_colors': display_techs_colors}),
    ('Generation (TWh)',
        {'file': 'CONVqn.gdx',
        'param': 'CONVqmnallyears',
        'columns': ['tech', 'n', 'year', 'value'],
        'unit': 'TWh',
        'mult': 0.000001,
        'reg': 'n',
        'xaxis': 'year',
        'series': 'tech',
        'series_keys': display_techs.keys(),
        'series_colors': display_techs_colors}),
    ('CO2 (Million Tonnes)',
        {'file': 'Reporting.gdx',
        'param': 'AnnualReport',
        'columns': ['n', 'year', 'type','value'],
        'unit': 'Million tonnes',
        'mult': 0.000001,
        'reg': 'n',
        'filters': {'type': 'CO2'},
        'xaxis': 'year'}),
))
column_metadata = {
    'tech':{
        'type': 'string',
        'filter': 'single',
        'full_set': techs_full,
        'colors': display_techs_colors,
        'options': ['series'],
        'merge': tech_map,
    },
    'type':{
        'type': 'string',
        'full_set': ['CO2'],
        'grouping': display_techs,
        'colors': display_techs_colors,
    },
    'n':{
        'type': 'string',
        'full_set': regions_full['n'],
    },
    'year':{
        'type': 'number',
        'full_set': years_full,
    },
    'value':{
        'type': 'number',
    },
}

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

widgets = col.OrderedDict((
    ('legends_heading', bmw.Div(text='Legends', id='legends_heading')),
    ('techs_legend', bmw.Div(text=tech_legend_string, id='techs_legend')),
    ('scenarios_legend', bmw.Div(text=scenario_legend_string, id='scenarios_legend')),
    ('show_heading', bmw.Div(text='Show', id='show_heading')),
    ('scenarios_compare', bmw.Select(value='Show All', options=['Show All','Show Difference with Base'], id='scenarios_compare')),
    ('result', bmw.Select(value=gdx_structure.keys()[0], options=gdx_structure.keys(), id='result')),
    ('format', bmw.Select(value='Chart', options=['Figure','Table','Map'], id='format')),
    ('charttype', bmw.Select(value='Stacked Area', options=['Stacked Area'], id='charttype')),
    ('filters_heading', bmw.Div(text='Filters', id='filters_heading')),
    ('scenarios_heading', bmw.Div(text='Scenarios', id='scenarios_heading')),
    ('scenarios', bmw.CheckboxGroup(labels=scenarios, active=range(len(scenarios)), id='scenarios')),
    ('techs_heading', bmw.Div(text='Techs', id='techs_heading')),
    ('techs', bmw.CheckboxGroup(labels=display_techs.keys(), active=range(len(display_techs.keys())), id='techs')),
    ('regtype', bmw.Select(value='country', options=hierarchy_column_names, id='regtype')),
    ('region', bmw.Select(value='USA', options=hierarchy['country'].unique().tolist(), id='region')),
    ('year', bmw.Select(value='All years', options=['All years'] + [str(x) for x in years_full], id='year')),
    ('timeslice', bmw.Select(value='All timeslices', options=['All timeslices','H1','H2','H3'], id='timeslice')),
    ('scale_axes', bmw.RadioButtonGroup(labels=['Sync Axes', 'Scale Independently'], id='scale_axes')),
    ('rerender', bmw.Button(label='Re-render', button_type='success', id='rerender')),
))

def initialize():
    for scenario_name in scenarios:
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
        plot_list['scenarios'][scenario_name] = plot
    
    combined_plot = {
        'figure': bp.Figure(toolbar_location='right', tools='save,pan,box_zoom,reset', width=250, height=250),
        'series': [],
    }
    combined_plot['figure'].title.text = 'Combined'
    combined_plot['figure'].xaxis.major_label_orientation = 'vertical'
    combined_plot['figure'].xaxis.major_label_standoff = 25
    plot_list['combined'] = combined_plot

    build_plots()

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
    df = filter_dataframe(df_base)
    if widgets['charttype'].value == 'Stacked Area':
        build_stacked_area_chart(df, scenario, result)

def build_combined_chart(result):
    df_base = data_obj[result]['combined']['dataframe']
    if isinstance(df_base, int):
        df_base = get_combined_dataframe(result)
        data_obj[result]['combined']['dataframe'] = df_base
    df = filter_dataframe(df_base, combined=True)
    build_combined_line_chart(df)

def build_stacked_area_chart(df, scenario, result):
    x_values = np.hstack((df.index, df.index[::-1])).tolist()
    y_all = df.transpose().values.tolist()
    if 'series_colors' in gdx_structure[result]:
        colors_all = gdx_structure[result]['series_colors']
    else:
        colors_all = ['#3288bd']*len(y_all)
    if 'series' in gdx_structure[result] and gdx_structure[result]['series'] == 'tech':
        active_techs = widgets['techs'].active
        y_filtered = []
        colors = []
        for i, y in enumerate(y_all):
            if i in active_techs:
                y_filtered.append(y)
                colors.append(colors_all[i])
        y_values = stack_lists(y_filtered)
    else:
        y_values = stack_lists(y_all)
        colors = colors_all
    save_axis_ranges(scenario, x_values, y_values)
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
    gdx_result = gdx_structure[result]
    grouped_cols = [gdx_result['reg'], 'year']
    for scenario in scenarios:
        df = data_obj[result]['scenarios'][scenario]['dataframe']
        df = df.groupby(grouped_cols, as_index=False, sort=False)['value'].sum()
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

def filter_dataframe(df_base, combined=False):
    gdx_result = gdx_structure[widgets['result'].value]
    hier = hierarchy.drop_duplicates(gdx_result['reg'])
    df = pd.merge(df_base, hier, how='left', on=gdx_result['reg'])
    df = df[df[widgets['regtype'].value].isin([widgets['region'].value])]
    if not combined:
        if 'series' in gdx_result:
            df = df.groupby([gdx_result['series'], gdx_result['xaxis']], as_index=False, sort=False)['value'].sum()
            df = df.pivot(index=gdx_result['xaxis'], columns=gdx_result['series'], values='value')
            df = df[gdx_result['series_keys']] #to order the columns properly
        else:
            df = df.groupby([gdx_result['xaxis']], sort=False)['value'].sum()
    else:
        df = df.groupby(['scenario', gdx_result['xaxis']], as_index=False, sort=False)['value'].sum()
        df = df.pivot(index=gdx_result['xaxis'], columns='scenario', values='value')
    if not isinstance(df, pd.DataFrame):
        df = df.to_frame()
    return df

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

def general_filter_update(attrname, old, new):
    build_plots()

def update_regtype(attrname, old, new):
    widgets['region'].options = hierarchy[widgets['regtype'].value].unique().tolist()
    widgets['region'].value = widgets['region'].options[0]

def scale_axes(new):
    if new == 0: sync_axes()
    elif new == 1: scale_axes_independently()

def rerender():
    build_plots()
    scale_axes(widgets['scale_axes'].active)

widgets['scenarios'].on_change('active', general_filter_update)
widgets['techs'].on_change('active', general_filter_update)
widgets['result'].on_change('value', general_filter_update)
widgets['region'].on_change('value', general_filter_update)
widgets['regtype'].on_change('value', update_regtype)
widgets['scale_axes'].on_click(scale_axes)
widgets['rerender'].on_click(rerender)

initialize()
plots = [p['figure'] for p in plot_list['scenarios'].values()]
plots.append(plot_list['combined']['figure'])
filters = bl.widgetbox(widgets.values(), width=300, id='widgets_section')
plots_display = bl.column(plots, width=1000, id='plots_section')
bio.curdoc().add_root(bl.row([filters, plots_display]))