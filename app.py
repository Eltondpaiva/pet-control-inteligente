from flask import Flask, render_template, request, send_file
import pandas as pd
import os
from services.analise import processar_dados

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    file = request.files['file']
    if not file: return "Nenhum arquivo enviado."
    
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # Detecta se é CSV ou Excel e processa
        df = pd.read_csv(filepath) if filepath.endswith('.csv') else pd.read_excel(filepath)
        resultado = processar_dados(df)
        
        output_path = os.path.join(UPLOAD_FOLDER, "relatorio_prospeccao.xlsx")
        resultado.to_excel(output_path, index=False)
        
        return render_template('index.html', tabela=resultado.to_html(classes='table table-striped', index=False))
    except Exception as e:
        return f"Erro técnico: {str(e)}"

@app.route('/download')
def download():
    return send_file(os.path.join(UPLOAD_FOLDER, "relatorio_prospeccao.xlsx"), as_attachment=True)

if __name__ == '__main__':
    app.run()
