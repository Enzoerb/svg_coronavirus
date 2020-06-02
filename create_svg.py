import os
import sys
import csv
from datetime import datetime, timedelta
from math import floor

axes = '''
    <rect  fill="white" x="0%" y="0%" width="100%" height="100%"/>
    <text text-anchor="middle" x="50%" y="2.5%" font-size="15">COVID-19</text>

    <line x1="2%" y1="97%" x2="2%" y2="5%" stroke="black" stroke-width="0.5%" />
    <polygon points="13,30 27,30 20,15" fill="black" stroke="black" />
    <text text-anchor="middle" x="2.5%" y="2.5%" font-size="15">People</text>

    <line x1="1%" y1="95%" x2="92%" y2="95%" stroke="black" stroke-width="0.5%" />
    <polygon points="920,468 920,482 935,475" fill="black" stroke="black" />
    <text text-anchor="middle" x="95.5%" y="96%" font-size="15">Days</text>
'''


class CreateSVG:

    def __init__(self, country=''):
        self.axes = axes
        self.country = country
        self.data = list()
        self.x_scale = list()
        self.y_scale = list()
        self.scale = list()
        self.cases_legend = {"rect": "", "text": ""}
        self.death_legend = {"rect": "", "text": ""}
        self.recoveries_legend = {"rect": "", "text": ""}
        self.cases_path = ''
        self.death_path = ''
        self.recoveries_path = ''
        self.origin = (20, 475)
        self.end = (920, 25)
        self.people_adjuster = 1
        self.days_adjuster = 1

    @property
    def country_text(self):
        text = f'<text text-anchor="middle" x="50%" y="5.5%" font-size="15">{self.country}</text>'
        return text

    def extract_csv(self, file_path):
        with open(file_path) as csv_file:
            raw = csv.reader(csv_file,  delimiter=',')
            for index, day in enumerate(raw):
                if index != 0:
                    self.data.append(day)

    def get_first_day(self):
        first_day = datetime.strptime(self.data[0][0], '%Y/%m/%d %H:%M')
        return first_day

    def get_last_day(self):
        last_day = datetime.strptime(self.data[-1][0], '%Y/%m/%d %H:%M')
        return last_day

    @staticmethod
    def legend_rect(color, y, stroke):
        rect_element = f'<rect  fill="{color}" x="92.3%" y="{y}" width="7.5%" height="6%" stroke="{stroke}" stroke-width="0.2%"/>'
        return rect_element

    @staticmethod
    def legend_text(text, y):
        text_element = f'<text  text-anchor="middle" x="96%" y="{y}" font-size="15">{text}</text>'
        return text_element

    @staticmethod
    def path_format(color, draw):
        path_element = f'<path fill="none" stroke="{color}" stroke-width="0.2%" d="{draw}"/>'
        return path_element

    @staticmethod
    def scale_format(x, y, number):
        scale_number_text = f'<text x="{x}" y="{y}" font-size="15">{number}</text>'
        return scale_number_text

    def generate_legends(self):
        self.cases_legend["rect"] = self.legend_rect('yellow', '0.5%', 'black')
        self.cases_legend["text"] = self.legend_text('Cases', '4.5%')

        self.death_legend["rect"] = self.legend_rect('red', '7.5%', 'black')
        self.death_legend["text"] = self.legend_text('Deaths', '11.5%')

        self.recoveries_legend["rect"] = self.legend_rect('green', '14.5%', 'black')
        self.recoveries_legend["text"] = self.legend_text('Recoveries', '18.5%')

    def set_days_adjuster(self):
        first_day = self.get_first_day()
        last_day = self.get_last_day()
        number_of_pixels = self.end[0] - self.origin[0]
        seconds = (last_day - first_day).total_seconds()
        self.days_adjuster = number_of_pixels / int(seconds)

    def set_people_adjuster(self):
        cases = self.data[-1][2]
        number_of_pixels = self.origin[1] - self.end[1]
        self.people_adjuster = number_of_pixels / int(cases)

    def set_x_scale(self):
        day_final = self.get_last_day()
        day_one = self.get_first_day()
        num_seconds = (day_final - day_one).total_seconds()
        seconds_in_day = 60*60*24
        num_days = int(num_seconds / seconds_in_day)
        self.x_scale.append(day_final)
        self.x_scale.append(day_one)
        for day in range(num_days):
            new_day = day_one + timedelta(days=day)
            if int(new_day.strftime('%d')) % 5 == 0:
                self.x_scale.append(new_day)
        for index, day in enumerate(self.x_scale):
            seconds_till_day = (day - day_one).total_seconds()
            day_graph_location = seconds_till_day*self.days_adjuster
            self.x_scale[index] = (self.origin[0] +
                                   day_graph_location,
                                   day.strftime('%m/%d'))

    def set_y_scale(self):
        people_final = int(self.data[-1][2])
        people_one = min([int(self.data[0][i]) for i in range(2, 5)])
        people_mid = (people_final + people_one)/2
        people_mid_high = (people_final + people_mid)/2
        people_mid_low = (people_mid + people_one)/2
        self.y_scale.append(people_final)
        self.y_scale.append(people_one)
        self.y_scale.append(people_mid)
        self.y_scale.append(people_mid_high)
        self.y_scale.append(people_mid_low)

        for index, people_number in enumerate(self.y_scale):
            size_number = len(str(int(people_number)))
            size_potence = size_number - 2
            ten_potence = 10**(size_potence)
            formated_people_number = (people_number//ten_potence)
            ronded_people_number = ten_potence*formated_people_number
            poeple_graph_location = ronded_people_number*self.people_adjuster

            self.y_scale[index] = (self.origin[1] - poeple_graph_location,
                                   f'{formated_people_number}*10^{size_potence}')

    def generate_scale(self):
        self.set_x_scale()
        self.set_y_scale()

        for x_location, date in self.x_scale:
            y_location = 498
            self.scale.append(self.scale_format(x_location, y_location, date))

        for y_location, people_number in self.y_scale:
            x_location = 30
            self.scale.append(self.scale_format(x_location, y_location, people_number))

    def draw_path(self, state):
        self.set_days_adjuster()
        self.set_people_adjuster()

        first_day = self.get_first_day()
        first_y = self.origin[1] - (int(self.data[0][state]) * self.people_adjuster)
        draw = f"M {self.origin[0]} {first_y}"
        for index in range(1, len(self.data)):
            time = datetime.strptime(self.data[index][0], '%Y/%m/%d %H:%M')
            time_second = (time - first_day).total_seconds()
            x = self.origin[0] + (time_second * self.days_adjuster)
            y = self.origin[1] - (int(self.data[index][state]) * self.people_adjuster)
            draw += f' L {x} {y}'

        return draw

    def generate_paths(self):
        self.cases_path = self.path_format('yellow', self.draw_path(2))
        self.death_path = self.path_format('red', self.draw_path(3))
        self.recoveries_path = self.path_format('green', self.draw_path(4))

    def create_svg(self, file_path):
        svg_content = [self.country_text,
                       self.cases_legend['rect'], self.cases_legend['text'],
                       self.death_legend['rect'], self.death_legend['text'],
                       self.recoveries_legend['rect'], self.recoveries_legend['text'],
                       self.cases_path, self.death_path, self.recoveries_path]
        svg_content += [scale for scale in self.scale]

        with open(file_path, 'w') as svg:
            svg.write('<svg width="1000" height="500">\n')
            svg.write(f'    {self.axes}')
            svg.write('\n\n')
            for element in svg_content:
                svg.write(f'    {element}')
                svg.write('\n')
            svg.write('\n')
            svg.write('</svg>')


if __name__ == '__main__':

    country = ''
    if len(sys.argv) == 4:
        country = sys.argv[3]

    if len(sys.argv) > 2:
        csv_path = sys.argv[1]
        svg_path = sys.argv[2]
        check = True
        if not os.path.exists(csv_path):
            print('csv path does not exist')
            check = False
        if not os.path.exists(os.path.dirname(svg_path)):
            print('svg dir path does not exist')
            check = False
        if check:
            svg_creator = CreateSVG(country)
            svg_creator.extract_csv(csv_path)
            svg_creator.generate_legends()
            svg_creator.generate_paths()
            svg_creator.generate_scale()
            svg_creator.create_svg(svg_path)
    else:
        print('you need to give the csv and svg paths as arguments')
