# svg_coronavirus
create a line graph in svg with csv information

create_svg.py expects a csv with columns:
date, location, cases, deaths, recoveries
with the first line not taken into account

## how to execute
in terminal run create_svg.py script giving the csv and svg paths as arguments.
You can give the location name as a third argument if you want(it will be in the graph legend)

ex: python3 create_svg.py /home/usr/the/csv/path.csv /home/usr/the/svg/path.svg

ex2: python3 create_svg.py /home/usr/the/csv/path.csv /home/usr/the/svg/path.svg Location_Here

obs: the entire csv path must exist and the svg dir too (in the exemples /home/usr/the/csv/path.csv and /home/usr/the/svg must exist)


## create_svg.py
this script has the class CreateSVG

their functions are __init__, extract_csv, get_first_day, get_last_day, legend_rect, legend_text, path_format, scale_format, generate_legends, set_days_adjuster, set_people_adjuster, set_x_scale, set_y_scale, generate_scale, draw_path, generate_paths, create_svg

### extract_csv
this function asks for the csv file path, reads the file with the csv module and saves all lines(except for the first) inside the instance list variable "data"

### get_first_day
gets the date from the first list in data, formating as datetime and returning it

### get_last_day
gets the date from the last list in data, formating as datetime and returning it

### legend_rect
asks for the rectangle color, y location and stroke, returning a rect svg element with these informations (all rectangles are displayed in x = 92%)

### legend_text
asks for the legend text and y location, returning a text svg element with these informations (all legend texts are middle anchored in x = 95.5%)

### path_format
asks for the path stroke color and draw("d" attribute), returning a path svg element with these informations

### scale_format
asks for the scale x, y and number to be displayed(it could be any text too), returning a text svg element with this information

### generate_legends
useses the legend_rect and legend_text functions to create a legend for cases, deaths and recoveries, saving them inside the instance dictionary varibles cases_legend, death_legend and recoveries_legend(each of these dictionaries have the keys rect and text)

### set_days_adjuster
divide the number of pixels the graph has by the number of seconds between the first and last date, saving it in the instance variable days_adjuster(this actually is a coefficient that when multiplied by a number(seconds) returns its location in the x axis )

### set_people_adjuster
divide the number of pixels the graph has by the number of cases, saving it in the instance variable people_adjuster (this actually is a coefficient that when multiplied by a number(number of people) returns its location in the y axis )

### set_x_scale
generates a tuple in the format (day_graph_location, month/day) for the first day, last day and all days divisible by 5, saving the x_scale instance variable

### set_y_scale
generates a tuple in the format (people_graph_location, people_scientific_notation) for the points that you get reparting the y axis by 5, saving the y_scale instance variable

### generate_scale
first it executes the set_x_scale and set_y_scale functions, sending the x_scale and y_scale informations to the scale_format function and appending the returns to the instance list variable scale

### draw_path
it asks for the state(index of data where the state info is)
after doing that executes the set_days_adjuster and set_people_adjuster functions, geting the day and number of people in the state, multpling them by the adjusters and calculating the position of every information in the graph, generating a "d" svg path element that goes thoroug all those points

### generate_paths
uses the draw_path with the path_format function to generate cases, feaths, and recoveries paths, saving them inside the instance variables cases_path, death_path, recoveries_path

### create_svg
asks fot the svg file path
after it creates a list called svg_content that contains all the lines from the svg files(except for the first, last, and axes lines).
And then opens the svg file in the file_path writing all the information
