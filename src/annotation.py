def build_annotation(ax):
    global annotation

    annotation = ax.annotate(
        text='',
        xy=(0, 0),
        xytext=(35, 35),
        textcoords='offset pixels',
        bbox={'boxstyle': 'round', 'fc': 'w'},
        arrowprops={'arrowstyle': '->'},
        color='black',
        fontfamily='Consolas'
    )
    annotation.set_visible(False)


def _on_hover(event, line_plot, fig, ax, xdata, ydata):
    if event.inaxes != ax:
        return
    
    is_contained, annotation_index = line_plot.contains(event)
    if is_contained:
        idx = annotation_index['ind'][0]
        data_point_location = (xdata[idx], ydata[idx])
        annotation.xy = data_point_location

        text_label = '({0:.2f}, {1:.2f})'.format(data_point_location[0], data_point_location[1])
        annotation.set_text(text_label)

        annotation.get_bbox_patch().set_facecolor("#ffffff")
        annotation.set_alpha(0.4)

        annotation.set_visible(True)
        fig.canvas.draw_idle()
    else:
        if annotation.get_visible():
            annotation.set_visible(False)
            fig.canvas.draw_idle()
