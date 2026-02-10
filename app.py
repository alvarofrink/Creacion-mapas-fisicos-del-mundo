from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image, ImageDraw
import io
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'maps'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Map templates (preset regions)
MAP_TEMPLATES = {
    'south_america': {
        'name': 'South America',
        'width': 800,
        'height': 900,
        'bounds': {'north': 12, 'south': -56, 'west': -82, 'east': -34}
    },
    'europe': {
        'name': 'Europe',
        'width': 900,
        'height': 700,
        'bounds': {'north': 71, 'south': 35, 'west': -10, 'east': 40}
    },
    'africa': {
        'name': 'Africa',
        'width': 700,
        'height': 850,
        'bounds': {'north': 37, 'south': -35, 'west': -18, 'east': 52}
    },
    'asia': {
        'name': 'Asia',
        'width': 1000,
        'height': 700,
        'bounds': {'north': 77, 'south': -10, 'west': 26, 'east': 150}
    },
    'north_america': {
        'name': 'North America',
        'width': 800,
        'height': 700,
        'bounds': {'north': 83, 'south': 15, 'west': -170, 'east': -52}
    }
}

class PhysicalMap:
    def __init__(self, template_name='south_america', title='Physical Map'):
        self.template = MAP_TEMPLATES.get(template_name, MAP_TEMPLATES['south_america'])
        self.width = self.template['width']
        self.height = self.template['height']
        self.title = title
        
        # Create base image with light blue background (ocean)
        self.image = Image.new('RGB', (self.width, self.height), color='#E8F4F8')
        self.draw = ImageDraw.Draw(self.image, 'RGBA')
        
        # Add title
        self._draw_title()
        
        # Features to be drawn
        self.features = []
    
    def _draw_title(self):
        """Draw title at the top of the map"""
        title_y = 10
        # Using default font; for better results, you can load a custom font
        self.draw.text((self.width//2 - 100, title_y), self.title, fill='#000000')
    
    def add_mountain_range(self, name, points, color='#8B7355'):
        """Add a mountain range using brown/tan colors"""
        if len(points) > 1:
            # Draw triangular mountain peaks
            for i in range(0, len(points) - 1, 2):
                x1, y1 = points[i]
                x2, y2 = points[i + 1] if i + 1 < len(points) else points[i]
                peak_x = (x1 + x2) / 2
                peak_y = min(y1, y2) - 20
                triangle = [(x1, y1), (peak_x, peak_y), (x2, y2)]
                self.draw.polygon(triangle, fill=color, outline='#654321')
        
        self.features.append({'type': 'mountain', 'name': name, 'color': color})
    
    def add_river(self, name, points, color='#4A90E2', width=3):
        """Add a river as a line"""
        if len(points) > 1:
            for i in range(len(points) - 1):
                self.draw.line([points[i], points[i+1]], fill=color, width=width)
        
        self.features.append({'type': 'river', 'name': name, 'color': color})
    
    def add_lake(self, name, center, radius=15, color='#4A90E2'):
        """Add a lake as a circle"""
        x, y = center
        bbox = [x - radius, y - radius, x + radius, y + radius]
        self.draw.ellipse(bbox, fill=color, outline='#2E5C8A')
        
        self.features.append({'type': 'lake', 'name': name, 'color': color})
    
    def add_forest(self, name, points, color='#2D5016'):
        """Add forest areas using green"""
        if len(points) >= 3:
            self.draw.polygon(points, fill=color, outline='#1a3d0a')
        
        self.features.append({'type': 'forest', 'name': name, 'color': color})
    
    def add_desert(self, name, points, color='#F4D03F'):
        """Add desert areas using yellow/tan"""
        if len(points) >= 3:
            self.draw.polygon(points, fill=color, outline='#D4A017')
        
        self.features.append({'type': 'desert', 'name': name, 'color': color})
    
    def add_city(self, name, position, size=5, color='#FF0000'):
        """Add a city marker"""
        x, y = position
        bbox = [x - size, y - size, x + size, y + size]
        self.draw.ellipse(bbox, fill=color, outline='#8B0000')
        
        # Add city label
        self.draw.text((x + 8, y - 8), name, fill='#000000')
        
        self.features.append({'type': 'city', 'name': name, 'color': color})
    
    def add_coastline(self, name, points, color='#000000', width=2):
        """Add a coastline or border"""
        if len(points) > 1:
            self.draw.line(points, fill=color, width=width)
        
        self.features.append({'type': 'coastline', 'name': name})
    
    def add_legend(self):
        """Add a legend to the map"""
        legend_x = self.width - 200
        legend_y = 50
        box_height = len(self.features) * 25 + 20
        
        # Draw legend box
        self.draw.rectangle(
            [legend_x - 10, legend_y - 10, self.width - 10, legend_y + box_height],
            fill='#FFFFFF',
            outline='#000000'
        )
        
        # Draw legend entries
        self.draw.text((legend_x, legend_y), 'Legend', fill='#000000')
        for idx, feature in enumerate(self.features):
            y = legend_y + 25 + (idx * 20)
            # Draw color box
            self.draw.rectangle(
                [legend_x, y, legend_x + 15, y + 15],
                fill=feature.get('color', '#CCCCCC'),
                outline='#000000'
            )
            # Draw label
            self.draw.text((legend_x + 20, y), feature['name'][:20], fill='#000000')
    
    def save(self, filename=None):
        """Save the map to a file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"map_{timestamp}.png"
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        self.image.save(filepath)
        return filepath

# Flask Routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', templates=MAP_TEMPLATES)

@app.route('/api/create-map', methods=['POST'])
def create_map():
    """Create a new map with features"""
    data = request.json
    template = data.get('template', 'south_america')
    title = data.get('title', 'Physical Map')
    
    # Create map
    map_obj = PhysicalMap(template, title)
    
    # Add features from request
    features = data.get('features', [])
    for feature in features:
        feature_type = feature.get('type')
        
        if feature_type == 'mountain':
            map_obj.add_mountain_range(feature['name'], feature['points'], feature.get('color', '#8B7355'))
        elif feature_type == 'river':
            map_obj.add_river(feature['name'], feature['points'], feature.get('color', '#4A90E2'))
        elif feature_type == 'lake':
            map_obj.add_lake(feature['name'], tuple(feature['center']), feature.get('radius', 15), feature.get('color', '#4A90E2'))
        elif feature_type == 'forest':
            map_obj.add_forest(feature['name'], feature['points'], feature.get('color', '#2D5016'))
        elif feature_type == 'desert':
            map_obj.add_desert(feature['name'], feature['points'], feature.get('color', '#F4D03F'))
        elif feature_type == 'city':
            map_obj.add_city(feature['name'], tuple(feature['position']), feature.get('size', 5), feature.get('color', '#FF0000'))
    
    # Add legend
    map_obj.add_legend()
    
    # Save map
    filename = f"map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = map_obj.save(filename)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'url': f'/api/download-map/{filename}'
    })

@app.route('/api/download-map/<filename>')
def download_map(filename):
    """Download a created map"""
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/png', as_attachment=True)
    return jsonify({'error': 'Map not found'}), 404

@app.route('/api/preview-map', methods=['POST'])
def preview_map():
    """Preview a map before saving"""
    data = request.json
    template = data.get('template', 'south_america')
    title = data.get('title', 'Physical Map')
    
    map_obj = PhysicalMap(template, title)
    
    features = data.get('features', [])
    for feature in features:
        feature_type = feature.get('type')
        
        if feature_type == 'mountain':
            map_obj.add_mountain_range(feature['name'], feature['points'], feature.get('color', '#8B7355'))
        elif feature_type == 'river':
            map_obj.add_river(feature['name'], feature['points'], feature.get('color', '#4A90E2'))
        elif feature_type == 'lake':
            map_obj.add_lake(feature['name'], tuple(feature['center']), feature.get('radius', 15), feature.get('color', '#4A90E2'))
        elif feature_type == 'forest':
            map_obj.add_forest(feature['name'], feature['points'], feature.get('color', '#2D5016'))
        elif feature_type == 'desert':
            map_obj.add_desert(feature['name'], feature['points'], feature.get('color', '#F4D03F'))
        elif feature_type == 'city':
            map_obj.add_city(feature['name'], tuple(feature['position']), feature.get('size', 5), feature.get('color', '#FF0000'))
    
    map_obj.add_legend()
    
    # Save to bytes and return as base64
    img_io = io.BytesIO()
    map_obj.image.save(img_io, 'PNG')
    img_io.seek(0)
    
    import base64
    img_base64 = base64.b64encode(img_io.getvalue()).decode()
    
    return jsonify({
        'success': True,
        'image': f'data:image/png;base64,{img_base64}'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)