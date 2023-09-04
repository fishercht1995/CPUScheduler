from flask import Flask, render_template, request, jsonify, send_file
from schedulers import simulate
from schedulers.workload import readWorkload
from schedulers.analyze import analyzeData, drawPlot
import os
from workloads import workload

app = Flask(__name__,template_folder='.')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_file():
    number = int(request.form.get("param1"))
    iat = int(request.form.get("param2"))

    outpath = './workloads/generated_workload.txt'
    workload.generateWorkload(number, iat, outpath)
    
    return send_file(outpath, as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    policies = ["rr", "fifo", "srtf", "seal", "sfs"]
    inputfiles = []
    uploaded_file = request.files['fileToUpload']
    cscost = int(request.form["cscost"])
    if uploaded_file:
        file_path = 'uploaded_files/' + uploaded_file.filename  # 保存到服务器的路径
        uploaded_file.save(file_path)
        for p in policies:
            w = readWorkload(file_path)

            if p == "sfs":
                period = 20
            else:
                period = 1000

            simulate.simulate(w, p, "./static/data/{}/".format(p), period = period, CScost = cscost)
            inputfiles.append("./static/data/{}/data.csv".format(p))
        processD = analyzeData(policies, inputfiles)
        drawPlot(policies, inputfiles)
        data = {
        "message": "数据处理成功",
        "processed_data": processD
    }
        return render_template('result.html', data = data)

    return 'No file uploaded.'

@app.route('/process-data', methods=['POST'])
def process_data():
    try:
        user_data = request.json.get("user_data")
        if user_data:

            return_data = []
            for row in user_data:
                processed_row = [item.strip() for item in row]
                return_data.append(processed_row)
            
            response_data = {"message": "数据已成功处理", "processed_data": return_data}
            return jsonify(response_data)
        else:
            return jsonify({"error": "未收到有效数据"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        os.exit()