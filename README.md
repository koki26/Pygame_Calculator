### Pygame Drawing Calculator
Overview
A simple drawing application built with Pygame that allows users to create various shapes and generate the corresponding Pygame code. The tool is designed to help visualize and quickly prototype Pygame drawings.

Features
Shape Creation: Draw rectangles, circles, ellipses, lines, polygons, and arcs

Customization:

Choose colors from a palette

Adjust line width

Toggle filled/unfilled shapes

Editing:

Move shapes by dragging

Resize shapes using handles

Delete shapes with Delete key

Grid: Toggle grid display for precise alignment

Code Generation: Automatically generate Pygame code for your drawing

Installation
Ensure you have Python 3.x installed

Install Pygame:

bash
pip install pygame
Download or clone this repository

Usage
Run the application:

bash
python main.py
Toolbar Controls:

Left panel contains all drawing tools

Select shape type (rectangle, circle, etc.)

Choose color from the palette

Adjust line width using the slider

Toggle filled/unfilled shapes

Toggle grid visibility

Clear all shapes

Generate Pygame code

Drawing:

Click and drag to create shapes (except polygons)

For polygons:

Left-click to add points

Right-click or press Enter to complete

Select shapes by clicking on them

Drag selected shapes to move them

Use resize handles to adjust size

Keyboard Shortcuts:

Delete: Remove selected shape

Enter: Complete polygon drawing

Code Generation:

Click "Generate Code" to create a Python file

The code will be saved as generated_drawing.py

File Structure
pygame-drawing-calculator/
├── main.py          # Main application code
├── README.md        # This documentation
└── generated_drawing.py  # Output file (created when generating code)
Customization
You can modify the following constants in the code:

DEFAULT_WIDTH, DEFAULT_HEIGHT: Initial window size

MIN_WINDOW_SIZE: Minimum window size

COLOR_*: Color definitions

BUTTON_HEIGHT, PADDING: UI element sizes

SHAPE_TYPES: Available shape types

TOOLBAR_WIDTH: Width of the control panel

Requirements
Python 3.x

Pygame 2.x
