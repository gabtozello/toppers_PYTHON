from flask import Flask, request, render_template, url_for, redirect
from flask_cors import CORS, cross_origin
import pandas as pd
import spacy


#Flask ------------------------------------------>
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
#Arquivo CSV para comparação --------------------->
file = "grupos-de-pesquisa.csv"
#Dicionario do Spacy ---------------------------->
nlp = spacy.load("pt_core_news_lg")

constructor = []

#Rota home ------------------------------------->
@app.route('/home')
@cross_origin()
def home():
    return render_template('xora_google.html')
#Rota run ------------------------------------->
@app.route('/', methods=['POST', 'GET'])
@cross_origin()
def run():
    if request.method == "POST":
        informacao = request.form['info']
        return redirect(url_for("informacao", info=informacao))
    else:
        return render_template('xora_google.html')

@app.route('/<info>', methods=['POST','GET'])
@cross_origin()
def informacao(info):
    ref = nlp(info.lower())
    arquivo = pd.read_csv(file, sep=";")
    arquivo['NOME DO GRUPO'] = arquivo['NOME DO GRUPO'].str.lower()
    arquivo.head()
    all_docs = [nlp(row) for row in arquivo['NOME DO GRUPO']]
    sims = []
    doc_id = []
    for i in range(len(all_docs)):
        sim = all_docs[i].similarity(ref)
        sims.append(sim)
        doc_id.append(i)
        sims_docs = pd.DataFrame(list(zip(doc_id, sims)), columns=['doc_id', 'sims'])
    sims_docs_sorted = sims_docs.sort_values(by='sims', ascending=False)
    top5_sim_docs = arquivo.iloc[sims_docs_sorted['doc_id'][0:5]]
    top_sim_scores = pd.concat([top5_sim_docs, sims_docs_sorted['sims'][0:5]], axis=1)
    constructor = []
    for (pergunta, sim,id) in zip(top_sim_scores['PERGUNTA'], top_sim_scores['sims']):
        data = {'Pergunta': pergunta,
                'Similaridade': sim}
        constructor.append(data)
    return f"<h1>{constructor}</h1>"

#Chamando rota ------------------------------------------------------->
if __name__ == "__main__":
    app.run(debug=True)