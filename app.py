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
    # Verifica se o template existe antes de carregar
    if not os.path.exists("templates/index.html"):
        return "Erro Crítico: Pasta 'templates' ou arquivo 'index.html' não encontrados no GitHub."
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    if 'file' not in request.files:
        return "Erro: Nenhum campo de arquivo encontrado."
    
    file = request.files['file']
    if file.filename == '':
        return "Erro: Nenhum arquivo selecionado."

    try:
        # Tenta ler com diferentes codificações comuns em softwares brasileiros
        content = file.read()
        try:
            df = pd.read_csv(io.BytesIO(content), sep=None, engine='python', encoding='utf-8')
        except:
            df = pd.read_csv(io.BytesIO(content), sep=None, engine='python', encoding='iso-8859-1')

        # Chamada para a inteligência de análise
        resultado = processar_dados(df)
        
        output_path = os.path.join(UPLOAD_FOLDER, "relatorio_prospeccao.xlsx")
        resultado.to_excel(output_path, index=False)
        
        tabela_html = resultado.to_html(classes='table table-striped table-hover', index=False)
        return render_template('index.html', tabela=tabela_html)

    except KeyError as e:
        return f"Erro de Coluna: O sistema esperava a coluna {str(e)}, mas ela não foi encontrada no seu CSV. Verifique se exportou o relatório de 'Vendas por Produto/Serviço'."
    except Exception as e:
        return f"Erro Técnico: {str(e)}"

@app.route('/download')
def download():
    path = os.path.join(UPLOAD_FOLDER, "relatorio_prospeccao.xlsx")
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run()
