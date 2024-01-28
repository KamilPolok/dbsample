from matplotlib.patches import Rectangle

class Chart_ShaftViewer():
    def __init__(self, ax, canvas, toolbar):
        self._ax = ax
        self._canvas = canvas
        self._toolbar = toolbar
        self._toolbar.show_dimensions_checkbox.stateChanged.connect(self._draw_shaft_dimensions)
        
        self._active_sections = {}       # Dictionary to keep track of shaft sections
        
        self._axes_arrows = []                  # List to keep track of figure axes
        self._shaft_markers = []         # List to keep track of shaft markers
        self._shaft_coordinates = []     # List to keep track of shaft coordinates
        self._shaft_dimensions = []      # List to keep track of shaft dimensions

        self._shaft_attributes = {}      # List to keep track of current shaft attributes

        self._dimension_offset = 0

    def _set_axes_limits(self):
        """
        Set the axes limits for the plot based on the data.

        This method calculates the overall maximum and minimum values across all plots
        and sets the x and y axis limits accordingly.
        """
        # Set x and y axis limits
        shaft_length = self.points[-1]
        
        offset = 0.1 * shaft_length
        xmin = -offset
        xmax = shaft_length + offset
        ymin = -0.25 * shaft_length
        ymax = 0.25 * shaft_length

        self._ax.set_xlim(xmin, xmax)
        self._ax.set_ylim(ymin, ymax)

        # Display axes arrows
        for item in self._axes_arrows:
            item.remove()
        self._axes_arrows.clear()

        arrow_x_max = shaft_length + 0.5 * offset
       
        z_axis = self._ax.annotate(
            '', xy=(0, 0), xycoords='data',
            xytext=(arrow_x_max, 0), textcoords='data',
            arrowprops=dict(arrowstyle="<-", color='#1b5e20'),
            zorder=3
        )   
        self._axes_arrows.append(z_axis)

        z_axis_label = self._ax.text(arrow_x_max, 0, 'z [mm]', ha='left', va='center', color='#1b5e20', 
                                    fontsize=8, fontweight='bold',
                                    bbox=dict(alpha=0, zorder=3))
        
        self._axes_arrows.append(z_axis_label)

    def _draw_shaft_markers(self):
        """
        Draw the shaft characteristic points on the plot.

        This method adds markers and labels for significant points along the shaft,
        such as supports and eccentric positions.
        """        
        # Remove old markers
        for item in self._shaft_markers:
            item.remove()
        self._shaft_markers.clear()

        # Draw markers
        markers = self._ax.scatter(self.points, [0] * len(self.points), color='black', s=8, zorder=5)
        self._shaft_markers.append(markers)

        # Add labels for the markers
        for marker, label in zip(self.points, self.labels):
            annotation_labels = self._ax.annotate(label, (marker, 0), textcoords="offset points", xytext=(10, -15), ha='center', zorder=5)
            self._shaft_markers.append(annotation_labels)

        self._draw_shaft_coordinates()

        self._canvas.draw()

    def _draw_shaft_coordinates(self):
        # Remove old coordinates
        for item in self._shaft_coordinates:
            item.remove()
        self._shaft_coordinates.clear()

        if self._toolbar.show_dimensions_checkbox.isChecked():
            # Define characteristic shaft coordinates

            # Draw dimension lines between points
            dimensions_color = 'SkyBlue'
            for i in range(len(self.points) - 1):
                start, end = self.points[i], self.points[i + 1]
                mid_point = (start + end) / 2
                distance = "{:.1f}".format(end - start)
                y_position = -self._dimension_offset

                dimension = self._draw_dimension(distance, start, end, mid_point, y_position, y_position, y_position)

                self._shaft_coordinates.extend(dimension)
        
        self._canvas.draw()
    
    def _draw_shaft_dimensions(self):
        # Remove old dimenions
        for item in self._shaft_dimensions:
            item.remove()
        self._shaft_dimensions.clear()
        
        highest_diameter = 0

        if self._shaft_attributes and self._toolbar.show_dimensions_checkbox.isChecked():
            # Get the highest diameter of shaft
            for section_name, section in self._shaft_attributes.items():
                for subsection_number, subsection in section.items():
                        if subsection[-1] > highest_diameter:
                            highest_diameter = subsection[-1]

            self._dimension_offset = ((0.5 * highest_diameter ) * 1.2 + 5)

            # Draw new dimensions
            for section_name, section in self._shaft_attributes.items():
                for subsection_number, subsection in section.items():

                    # Draw length dimension
                    start = subsection[0]
                    length = subsection[1]
                    diameter = subsection[2]

                    start_z = start[0]
                    end_z = start[0] + length
                    y_position = self._dimension_offset
                    label_position = start_z + length * 0.5
                    text = "{:.1f}".format(length)

                    length_dimension = self._draw_dimension(text, start_z, end_z, label_position, y_position, y_position, y_position)
                    self._shaft_dimensions.extend(length_dimension)

                    # Draw diameter dimension
                    start_y = start[1]
                    end_y = start[1] + diameter
                    z_position = start_z + length * 0.75
                    y_position = start_y + diameter * 0.5
                    text = "Ø {:.1f}".format(diameter)

                    diameter_dimension = self._draw_dimension(text, z_position, z_position, z_position, start_y, end_y, y_position)
                    self._shaft_dimensions.extend(diameter_dimension)
        
        self._draw_shaft_coordinates()

        self._canvas.draw()

    def _draw_dimension(self, text, start_z, end_z, label_z_position, start_y=0, end_y=0, label_y_position=0):
        lines = []
        # Set dimensions color
        dimensions_color = '#c62828'

        # Draw dimension line
        dimension_line = self._ax.annotate(
            '', xy=(start_z, start_y), xycoords='data',
            xytext=(end_z, end_y), textcoords='data',
            arrowprops=dict(arrowstyle="<->", color=dimensions_color),
            zorder=3
        )
        lines.append(dimension_line)

        # Perfrom actions depending of dimension line orientation
        offset = 0.3
        if start_z == end_z:                # Vertical line
            ha, va = 'right', 'center'
            rotation = 90
            label_z_position -= offset            
        else:                               # Horizontal line
            ha, va = 'center', 'bottom'
            rotation = 0
            label_y_position += offset

            # draw reference lines for horizontal dimension lines
            for position in [start_z, end_z]:
                reference_line = self._ax.plot([position, position], [0, end_y], linestyle='-', color=dimensions_color, linewidth=0.5, zorder=0)
                lines.append(reference_line[0])

        # Add dimension labels
        dimension_label = self._ax.text(label_z_position, label_y_position, text, rotation=rotation, ha=ha, va=va, color=dimensions_color,
                                        fontsize=8,
                                        bbox=dict(alpha=0, zorder=3))
        lines.append(dimension_label)
        
        return lines

    def draw_shaft(self, shaft_subsections_drawing_attributes):
        self._shaft_attributes = shaft_subsections_drawing_attributes

        # Remove old sections
        for section in list(self._active_sections.keys()):
            self._active_sections[section].remove()
            del self._active_sections[section]

        # Draw new sections
        for section_name, section in self._shaft_attributes.items():
            for subsection_number, subsection in section.items():
                start = subsection[0]
                length = subsection[1]
                diameter = subsection[2]

                subsection_id = f"{section_name}_{subsection_number}"

                subsection_plot = Rectangle(start, length, diameter, color='grey', linewidth=2, fill=False)
                self._active_sections[subsection_id] = subsection_plot
                self._ax.add_patch(subsection_plot)
        
        # Draw shaft dimensions
        self._draw_shaft_dimensions()

        self._canvas.draw()

    def init_shaft(self, coordinates):
        shaft_points = [(0,0)] + coordinates
        self.labels = [coord[0] for coord in shaft_points]
        self.points = [coord[1] for coord in shaft_points]

        self._set_axes_limits()
        self._draw_shaft_markers()