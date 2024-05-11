from flask import Flask, render_template, request, send_file
import os
from osgeo import ogr

app = Flask(__name__)

# Specify the absolute path to the uploads folder
UPLOAD_FOLDER = r'C:\\Users\\manst\\Desktop\\Conv\\.venv\\uploads'

# Ensure that the uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Set the UPLOAD_FOLDER configuration
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def shp_to_kml(input_shp, output_kml):
    # Open the input Shapefile
    input_ds = ogr.Open(input_shp)

    # Create a KML driver
    kml_driver = ogr.GetDriverByName('KML')

    # Create the output KML file
    output_ds = kml_driver.CreateDataSource(output_kml)

    # Loop through each layer in the input Shapefile and copy it to the output KML file
    for i in range(input_ds.GetLayerCount()):
        layer = input_ds.GetLayerByIndex(i)
        output_layer = output_ds.CreateLayer(layer.GetName(), geom_type=layer.GetGeomType())
        output_layer.CreateFields(layer.schema)
        for feature in layer:
            output_layer.CreateFeature(feature)

    # Close the datasets
    input_ds = None
    output_ds = None

@app.route('/')
def upload_form():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return render_template('index.html', message='No file part')
    
    files = request.files.getlist('file')
    
    # Check if all required files are uploaded
    required_extensions = ['.shp', '.shx', '.dbf']
    for ext in required_extensions:
        if not any(file.filename.endswith(ext) for file in files):
            return render_template('index.html', message=f'Missing {ext} file')

    # Save the uploaded files
    uploaded_files = []
    for file in files:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        uploaded_files.append(file_path)
        
    # Get paths for input Shapefile and output KML file
    shp_path = os.path.join(app.config['UPLOAD_FOLDER'], [file for file in uploaded_files if file.endswith('.shp')][0])
    kml_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.splitext(os.path.basename(shp_path))[0] + '.kml')
    
    # Convert Shapefile to KML
    shp_to_kml(shp_path, kml_path)
    
    # Delete the uploaded shapefiles
    for file_path in uploaded_files:
        os.remove(file_path)
    
    # Return the KML file for download
    return send_file(kml_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
