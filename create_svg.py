import os
import csv
from datetime import datetime, timedelta
from math import floor

axes = '''
    <rect  fill="white" x="0%" y="0%" width="100%" height="100%"/>

    <line x1="2%" y1="97%" x2="2%" y2="5%" stroke="black" stroke-width="0.5%" />
    <polygon points="13,30 27,30 20,15" fill="black" stroke="black" />
    <text text-anchor="middle" x="2.5%" y="2.5%" font-size="15">People</text>

    <line x1="1%" y1="95%" x2="92%" y2="95%" stroke="black" stroke-width="0.5%" />
    <polygon points="920,468 920,482 935,475" fill="black" stroke="black" />
    <text text-anchor="middle" x="95.5%" y="96%" font-size="15">Days</text>
'''


class CreateSVG:

    def __init__(self):
        self.axes = axes
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

    def extract_csv(self, file_path):
        with open(file_path) as csv_file:
            raw = csv.reader(csv_file,  delimiter=',')
            for index, day in enumerate(raw):
                if index != 0:
                    self.data.append(day)

    def get_first_day(self):
        return datetime.strptime(self.data[0][0], '%Y/%m/%d %H:%M')

    def get_last_day(self):
        return datetime.strptime(self.data[-1][0], '%Y/%m/%d %H:%M')

    @staticmethod
    def legend_rect(color, y, stroke):
        return f'<rect  fill="{color}" x="92%" y="{y}" width="7.5%" height="6%" stroke="{stroke}" stroke-width="0.2%"/>'

    @staticmethod
    def legend_text(text, y):
        return f'<text  text-anchor="middle" x="95.5%" y="{y}" font-size="15">{text}</text>'

    @staticmethod
    def path_format(color, draw):
        return f'<path fill="none" stroke="{color}" stroke-width="0.2%" d="{draw}"/>'

    @staticmethod
    def scale_format(x, y, num):
        return f'<text x="{x}" y="{y}" font-size="15">{num}</text>'

    def generate_legends(self):
        self.cases_legend["rect"] = self.legend_rect('yellow', '1%', 'black')
        self.cases_legend["text"] = self.legend_text('Cases', '5%')

        self.death_legend["rect"] = self.legend_rect('red', '8%', 'black')
        self.death_legend["text"] = self.legend_text('Deaths', '12%')

        self.recoveries_legend["rect"] = self.legend_rect('green', '15%', 'black')
        self.recoveries_legend["text"] = self.legend_text('Recoveries', '19%')

    def set_days_adjuster(self):
        first_day = self.get_first_day()
        last_day = self.get_last_day()
        seconds = (last_day - first_day).total_seconds()
        self.days_adjuster = (self.end[0] - self.origin[0]) / int(seconds)

    def set_people_adjuster(self):
        cases = self.data[-1][2]
        self.people_adjuster = (self.origin[1] - self.end[1]) / int(cases)

    def set_x_scale(self):
        day_final = self.get_last_day()
        day_one = self.get_first_day()
        seconds_in_day = 60*60*24
        num_days = int((day_final - day_one).total_seconds() / seconds_in_day)
        self.x_scale.append(day_final)
        self.x_scale.append(day_one)
        for day in range(num_days):
            new_day = day_one + timedelta(days=day)
            if int(new_day.strftime('%d')) % 5 == 0:
                self.x_scale.append(new_day)
        for index, day in enumerate(self.x_scale):
            self.x_scale[index] = (self.origin[0] +
                                   (day - day_one).total_seconds()*self.days_adjuster,
                                   day.strftime('%m/%d'))

    def set_y_scale(self):
        people_final = int(self.data[-1][2])
        people_one = min([int(self.data[0][i]) for i in range(2, 5)])
        people_mid = (people_final + people_one)/2
        self.y_scale.append(people_final)
        self.y_scale.append(people_one)
        self.y_scale.append(people_mid)
        self.y_scale.append((people_final + people_mid)/2)
        self.y_scale.append((people_mid + people_one)/2)

        for index, num in enumerate(self.y_scale):
            size = (len(str(int(num))) - 2)
            pot = 10**size
            formated_num = (num//pot)
            self.y_scale[index] = (self.origin[1] - pot*formated_num *
                                   self.people_adjuster,
                                   str(int(formated_num))+f'*10^{size}')

    def generate_scale(self):
        self.set_x_scale()
        self.set_y_scale()
        for scale, num in self.x_scale:
            self.scale.append(self.scale_format(scale, 498, num))
        for scale, num in self.y_scale:
            self.scale.append(self.scale_format(30, scale, num))

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
        svg_content = [self.cases_legend['rect'], self.cases_legend['text'],
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

    all_locations = {'world', 'brazil', 'india', 'italy', 'spain', 'us'}

    file_path = os.path.dirname(os.path.realpath(__file__))
    csv_dir = 'csv_data'
    local_path = os.getcwd()
    svg_dir = 'svg_countries_final'
    if not os.path.exists(os.path.join(local_path, svg_dir)):
        os.mkdir(os.path.join(local_path, svg_dir))

    for location in all_locations:
        csv_file = f'corona_{location}.csv'
        csv_path = os.path.join(file_path, csv_dir, csv_file)
        svg_file = f'corona_{location}.svg'
        svg_path = os.path.join(local_path, svg_dir, svg_file)

        svg_creator = CreateSVG()
        svg_creator.extract_csv(csv_path)
        svg_creator.generate_legends()
        svg_creator.generate_paths()
        svg_creator.generate_scale()
        svg_creator.create_svg(svg_path)
