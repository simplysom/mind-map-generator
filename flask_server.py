from flask import Flask, request, render_template
import main
import json
import requests
import urllib


app = Flask(__name__)
json_data = None
input_text = None

@app.route('/')
def simple_page():
    return "Please go to <a href='/page1'> INPUT PAGE</a>"


@app.route('/page1')
def input_page():
    return render_template('input.html')


@app.route('/wiki_text')
def wiki_test():
    base_url = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&exsentences=3&titles="
    input_text = request.args.get("title")
    parse_title = urllib.parse.quote(input_text)
    url = base_url + parse_title
    try:
        R = requests.get(url)
        ex = list(R.json()['query']['pages'].values())[0]['extract']
        return "" + ex
    except Exception:
        return ""
        pass
    # print(ex)


@app.route('/page2', methods=['POST', 'GET'])
def page2():
    global json_data, input_text
    if request.method == "POST":
        input_text = request.form["input-text"]
        return render_template('new-output.html')


@app.route('/juggad')
def juggad():
    global json_data, input_text
    threshold_value = request.args.get('threshhold_value')
    max_connections_value = request.args.get('max_connections_value')
    if threshold_value and max_connections_value:
        cytoscape_dict, processed_text = main.generate_structured_data_from_text(input_text,
                                                    threshold_value=float(threshold_value),
                                                    max_connections_value=int(max_connections_value))
        json_data = json.dumps(cytoscape_dict)
    else:
        cytoscape_dict, processed_text = main.generate_structured_data_from_text(input_text)
        json_data = json.dumps(cytoscape_dict)
    return json_data + "|split|" + processed_text



if __name__ == '__main__':
    app.run(debug=True)
