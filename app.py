from flask import Flask, render_template, request, send_file
import pandas as pd
import os
import io
from services.analise import processar_dados

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    file = request.files.get('file')
    if not file: return "Arquivo não enviado."

    try:
        # Lê o CSV usando ponto-e-vírgula e ignora erros de encoding
        df = pd.read_csv(file, sep=';', encoding='latin1')
        
        resultado = processar_dados(df)
        
        output_path = os.path.join(UPLOAD_FOLDER, "relatorio_gerado.xlsx")
        resultado.to_excel(output_path, index=False)
        
        tabela_html = resultado.to_html(classes='table table-striped table-hover', index=False)
        return render_template('index.html', tabela=tabela_html)
    except Exception as e:
        return f"Erro de Processamento: {str(e)}. Verifique se o CSV é o de 'Vendas por Produto/Serviço'."

@app.route('/download')
def download():
    return send_file(os.path.join(UPLOAD_FOLDER, "relatorio_gerado.xlsx"), as_attachment=True)

if __name__ == '__main__':
    app.run()
