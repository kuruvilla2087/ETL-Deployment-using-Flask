import sys
import os
import json
from Pre_process import read_csv,etl_preprocess
from app import app
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','csv'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def process_file():
    if request.method == 'POST':
        # check if the post request has the files part
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            #Process Fles
                output_path = sys.argv[2]
                input_path = app.config['UPLOAD_FOLDER']
                print(input_path)
                df = read_csv(input_path)
            df_final = etl_preprocess(df[0], df[1])

            export_csv = df_final.to_csv(os.path.join(output_path, 'export_dataframe.csv'), index=None, header=True)

            response = app.response_class(
                    response=json.dumps({'Output File': output_path,'Success' : 'File sucessfully processed'}),
                    status=200,
                    mimetype='application/json'
                )

            return response


if __name__ == "__main__":
    app.run(debug=True)
