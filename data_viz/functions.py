
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches



def barplot_frequency(data, x_col, y_col, xlabel, ylabel, title, figsize=(30, 15), fontsize=15, label_fontsize=30, title_fontsize=None, x_ticks_rotation=True, ylim=None, legend=None, color='#ADD8E6', ci=None, colored_xticks=False, color_col=None, hue=None, palette='Set2', grid=False):
    plt.figure(figsize=figsize)
    chart = sns.barplot(x=x_col, y=y_col, data=data, color=color, ci=ci, hue=hue, palette=palette, edgecolor='black')

    for p in chart.patches:
        chart.annotate("{:,.2f}".format(p.get_height()), (p.get_x() + p.get_width() / 2, p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=fontsize)

    plt.xlabel(xlabel, fontsize=label_fontsize, labelpad=12)
    plt.ylabel(ylabel, fontsize=label_fontsize)
    if grid:
        plt.grid(alpha=0.2)

    if title_fontsize is not None:
        plt.title(title, fontsize=title_fontsize, loc='center', pad=20)
    else:
        plt.title(title, fontsize=30, loc='center', pad=20)

    if x_ticks_rotation:
        plt.xticks(rotation=45, fontsize=15)
        plt.yticks(fontsize=15)
    else:
        plt.xticks(fontsize=12, weight='semibold')
        plt.yticks(fontsize=10, weight='semibold')

    if ylim is not None:
        plt.ylim(0, ylim)

    if colored_xticks and color_col:
        unique_values = data[color_col].unique()
        color_palette = ['green', 'blue', 'tomato', 'yellow', 'brown', 'black'] #sns.color_palette("Paired", len(unique_values))
        color_map = dict(zip(unique_values, color_palette))

        for i, tick in enumerate(chart.get_xticklabels()):
            tick.set_color(color_map[data[color_col].iloc[i]])

    if legend is not None and hue:
        hue_legend = plt.legend(title=legend, fontsize=15, fancybox=True, framealpha=1, shadow=True, borderpad=1, loc='best', bbox_to_anchor=(1, 1))

    if legend is not None and colored_xticks and color_col:
        patch_list = []
        for key, value in color_map.items():
            patch_list.append(mpatches.Patch(color=value, label=key))
        xtick_legend = plt.legend(handles=patch_list, title="Function", loc=1, fontsize=15, fancybox=True, framealpha=1, shadow=True, borderpad=1)
        plt.gca().add_artist(hue_legend)
        plt.show()
        
    plt.tight_layout()
    plt.show()


def donut_chart(ax, data, title, title_fontsize, startangle, label_color_map):
    if isinstance(label_color_map, dict):
        label_color_map = [label_color_map[label] for label in data.keys()]
    ax.pie(x=data, autopct="%.1f%%", labels=data.keys(), pctdistance=0.5, startangle=startangle, colors=label_color_map)
    ax.axis('equal')
    ax.set_title(title, fontsize=title_fontsize, fontweight='bold', pad=5)

    circle = plt.Circle(xy=(0,0), radius=.65, facecolor='white')
    ax.add_artist(circle)