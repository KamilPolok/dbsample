import mplcursors
class Chart_Plotter():
    def __init__(self, ax, canvas, toolbar):
        self._ax = ax
        self._canvas = canvas
        self._toolbar = toolbar
        self._toolbar.plots_selector.stateChanged.connect(self._refresh_selected_plots)

        # Create and store the cursor object for interactive data display
        self._cursor = mplcursors.cursor(self._ax, hover=False)

        self._plots = {}            # Dictionary to keep track of plots
        self._active_plots = {}     # Dictionary to keep track of active plots

    def add_plot_functions(self, functions):
        """
        Prepare and set the data for each plot based on the input data.

        This method appends plots to the toolbar selector 
        """
        for key, function in functions.items():
            if key not in self._plots:
                self._toolbar.add_plot(key, function[0])
            if function[3] is not None:
                self._plots[key] = function
                self._toolbar.plots_selector.enableItem(key, True)
            else:
                self._toolbar.plots_selector.enableItem(key, False)
        
            self._reset_plots()
            
    def _reset_plots(self):
        # Remove any active plots so they can be properly redrawn
        for plot_name in list(self._active_plots.keys()):
            for line in self._active_plots[plot_name]:
                line.remove()
            del self._active_plots[plot_name]

        self._refresh_selected_plots()

    def _refresh_selected_plots(self):
        """
        Switch the current plots based on the selected plots.
        """
        # Determine which plots are selected
        selected_plots = [plot[0] for plot in self._toolbar.plots_selector.currentOptions()]

        # Remove plots that are not selected
        for plot_name in list(self._active_plots.keys()):
            if plot_name not in selected_plots:
                for element in self._active_plots[plot_name]:
                    element.remove()
                del self._active_plots[plot_name]
    
        # Add new selected plots
        for plot_name in selected_plots:
            if plot_name not in self._active_plots:
                y = self._plots[plot_name][len(self._plots[plot_name]) - 1]
                color = self._plots[plot_name][2]
                if  plot_name.lower().startswith('d'):
                    d_half_above_axis = y / 2
                    d_half_below_axis = [-d for d in d_half_above_axis]

                    above, = self._ax.plot(self._z, d_half_above_axis, linewidth = 1, color=color)
                    below, = self._ax.plot(self._z, d_half_below_axis, linewidth = 1, color=color)
                    plot_elements = [above, below]
                else:
                    plot, = self._ax.plot(self._z, y, linewidth = 1, color=color)
                    filling = self._ax.fill_between(self._z, y, alpha=0.3, color=color)
                    plot_elements = [plot, filling]
                self._active_plots[plot_name] = plot_elements
        
        self._refresh_cursor()

        self._canvas.draw()

    def _refresh_cursor(self):
        """
        Refresh the mplcursors cursor for interactive data display.
        """
        # Remove the previous cursor if it exists
        if hasattr(self, '_cursor') and self._cursor:
            self._cursor.remove()

        # Collect all current plot lines
        current_lines = [line for lines in self._active_plots.values() for line in lines if hasattr(line, 'get_xdata')]

        # Create a new cursor if there are plots
        if current_lines:
            self._cursor = mplcursors.cursor(current_lines, hover=False)
            self._cursor.connect("add", lambda sel: self._annotate_cursor(sel))
        else:
            self._cursor = None  # Reset cursor if there are no plots

    def _annotate_cursor(self, sel):
        """
        Annotate the cursor based on the selected plot.
        """
        # Check if the current artist (plot) is a diameter plot
        plot_color = 'black'
        plot_key = None
        is_diameter_plot = False

        # Determine the type and key of the plot that is currently selected by the cursor
        # and key the plot label 
        for key, lines in self._active_plots.items():
            if sel.artist in lines:
                plot_label = self._plots[key][0]
                plot_color = self._plots[key][2]
                if key.startswith('d'):
                    is_diameter_plot = True
                break

        # Set the annotation text based on the plot type
        if is_diameter_plot:
            # For diameter plots, use absolute value for y-coordinate
            text = f'z: {sel.target[0]:.2f}, {plot_label}/2: {abs(sel.target[1]):.2f}'
        else:
            # For other types of plots, use the original y-coordinate
            text = f'z: {sel.target[0]:.2f}, {plot_label}: {sel.target[1]:.2f}'

        # Set annotation properties
        sel.annotation.set(
            text=text,
            fontsize=8,
            fontweight='bold',
            color='black',
            backgroundcolor=plot_color,
            alpha=0.7
        )

        # Customize the border and arrow colors
        sel.annotation.get_bbox_patch().set_edgecolor(plot_color)
        sel.annotation.arrow_patch.set_color(plot_color)

    def init_plots(self, z, functions):
        """
        Create and store plot data from the provided data dictionary.

        :param z: Numpy array containing the z arguments
        :param functions: Dictionary containing the functions arrays for the plots.
        """
        self._z = z

        self.add_plot_functions(functions)