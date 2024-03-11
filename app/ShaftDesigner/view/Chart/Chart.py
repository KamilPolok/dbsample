from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

import numpy as np

class Chart(FigureCanvas):
    """
    A class representing a chart widget in a PyQt application.

    This class is responsible for creating and managing the chart display,
    including the plot selection and updating the plot display.
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)        
        self.axes = self.figure.add_subplot(111)
        super(Chart, self).__init__(self.figure)
        self.setParent(parent)

        self._axes_arrows = []  # List to keep track of figure axes

        # Adjust subplot parameters to make the plot fill the figure canvas
        self.figure.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)

        # Set background color
        self._set_colors()

        # Remove axes spines, ticks and grid lines
        self._strip_canvas()

    def _set_colors(self):
        # Set background color
        self.background_color = '#212830'   # dark gray
        self.figure.set_facecolor( self.background_color)
        self.axes.set_facecolor( self.background_color)

        # Set other items colors
        self.shaft_color = '#89a0b0'        # bluey grey
        self.bearings_color = '#4d5ea8'     # bluey grey
        self.axes_color = '#ff073a'         # nenon red
        self.dimensions_color = '#1bfc06'   # neon green
        self.markers_color = '#ffffe4'      # off white

        # Set zorder - order of layers
        self.axes_layer = 1
        self.plots_layer = 2
        self.markers_layer = 3
        self.shaft_layer = 4
        self.dimensions_layer = 5

    def _strip_canvas(self):
        # Remove spines
        self.axes.spines[['right', 'top', 'bottom', 'left']].set_visible(False)

        # Remove x and y tick labels
        self.axes.set_xticks([])
        self.axes.set_yticks([])

        # Remove the ticks if desired
        self.axes.xaxis.set_ticks_position('none') 
        self.axes.yaxis.set_ticks_position('none')

        # Remove grid lines
        self.axes.grid(False)

        # Add zoom and pan functionality
        zoom_factory(self.axes)
        pan_factory(self.axes)

    def _draw_axes_arrows(self):
        '''
        Draw axes on the canvas.
        '''
        for item in self._axes_arrows:
            item.remove()
        self._axes_arrows.clear()

        xlim = self.axes.get_xlim()
        z_axis = self.axes.annotate('', xy=(xlim[1], 0), xytext=(xlim[0], 0),
                           arrowprops=dict(arrowstyle="->", color=self.axes_color, lw=1),
                           zorder=self.axes_layer,
                           annotation_clip=False)
        
        self._axes_arrows.append(z_axis)

        self.figure.canvas.draw_idle()

    def set_initial_axes_limits(self, xlim, ylim):
        '''
        Save initial axes limits.

        Args:
            xlim (tuple): tuple (min, max) of x axis limits.
            ylim (tuple): tuple (min, max) of y axis limits.
        '''
        self.initial_xlim = xlim
        self.initial_ylim = ylim

        self._draw_axes_arrows()

    def reset_initial_view(self):
        '''
        Reset the plot view to its original view.
        '''
        self.axes.set_xlim(self.initial_xlim)
        self.axes.set_ylim(self.initial_ylim)
        
        self.axes.figure.canvas.draw_idle()

    def get_controls(self):
        return (self.axes, self.figure.canvas)

def zoom_factory(axis, base_scale=1.5, min_zoom_range=0.1):
    """
    Returns zooming functionality to axis.
    """
    def zoom_fun(event):
        """Zoom when scrolling."""
        if event.inaxes == axis:
            cur_xlim = axis.get_xlim()
            cur_ylim = axis.get_ylim()
            xdata, ydata = event.xdata, event.ydata

            direction = np.sign(event.step)
            scale_factor = np.power(base_scale, direction)

            # Calculate proposed new limits
            new_xlim = [xdata - (xdata - cur_xlim[0]) * scale_factor,
                        xdata + (cur_xlim[1] - xdata) * scale_factor]
            new_ylim = [ydata - (ydata - cur_ylim[0]) * scale_factor,
                        ydata + (cur_ylim[1] - ydata) * scale_factor]

            # Enforce zoom-in limit
            if (new_xlim[1] - new_xlim[0]) < min_zoom_range or (new_ylim[1] - new_ylim[0]) < min_zoom_range:
                return  # Prevent zooming in beyond the limit

            # Apply the new limits
            axis.set_xlim(new_xlim)
            axis.set_ylim(new_ylim)

            axis.figure.canvas.draw_idle()

    fig = axis.get_figure()
    fig.canvas.mpl_connect('scroll_event', zoom_fun)

def pan_factory(axis):
    """
    Returns panning functionality to axis.
    """
    def on_press(event):
        """Callback for mouse button press."""
        if event.button == 3:  # Right mouse button
            axis._pan_start = (event.xdata, event.ydata)

    def on_release(event):
        """Callback for mouse button release."""
        axis._pan_start = None

    def on_motion(event):
        """Callback for mouse motion."""
        if event.button == 3 and axis._pan_start is not None:  # Right mouse button
            if event.xdata is not None and event.ydata is not None:
                xdata_start, ydata_start = axis._pan_start
                dx = event.xdata - xdata_start
                dy = event.ydata - ydata_start
                xlim = axis.get_xlim()
                ylim = axis.get_ylim()
                axis.set_xlim([xlim[0] - dx, xlim[1] - dx])
                axis.set_ylim([ylim[0] - dy, ylim[1] - dy])
                
                axis.figure.canvas.draw_idle()

    fig = axis.get_figure()
    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('button_release_event', on_release)
    fig.canvas.mpl_connect('motion_notify_event', on_motion)
