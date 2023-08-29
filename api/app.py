from flask import Flask, request, Response, send_file
import generate_svg as generate_svg
app = Flask(__name__)

@app.route('/')
def get_svg():
    package_name = request.args.get('package_name')
    if not package_name:
        return "Missing package_name parameter", 400
    
    #svg_content = generate_svg.make_widget(package_name)
    
    # response = Response(svg_content, content_type='image/svg+xml')
    # return response
    return package_name
    # return send_file(f"{package_name}.svg", mimetype='image/svg+xml')
if __name__ == '__main__':
    app.run(debug=True)