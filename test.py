import json
import svgwrite

def create_svg_from_json(json_file, output_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    dwg = svgwrite.Drawing(output_file, profile='tiny')

    for element in data:
        element_type = element['type']
        if element_type == 'circle':
            cx = element['cx']
            cy = element['cy']
            r = element['r']
            fill = element['fill']
            dwg.add(dwg.circle(center=(cx, cy), r=r, fill=fill))
        elif element_type == 'rectangle':
            x = element['x']
            y = element['y']
            width = element['width']
            height = element['height']
            fill = element['fill']
            dwg.add(dwg.rect(insert=(x, y), size=(width, height), fill=fill))
        elif element_type == 'line':
            x1 = element['x1']
            y1 = element['y1']
            x2 = element['x2']
            y2 = element['y2']
            stroke = element['stroke']
            stroke_width = element['stroke_width']
            dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), stroke=stroke, stroke_width=stroke_width))
        elif element_type == 'image':
            x = element['x']
            y = element['y']
            width = element['width']
            height = element['height']
            src = element['src']
            dwg.add(dwg.image(href=src, insert=(x, y), size=(width, height)))

    dwg.save()

# Example usage
json_file = 'diagram.json'
output_file = 'diagram.svg'
create_svg_from_json(json_file, output_file)

