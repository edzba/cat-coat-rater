# Classificador de gatos-do-mato

Versao simples de um app Streamlit para avaliar imagens de gatos-do-mato.

## Como usar

1. Coloque imagens na pasta `images/`.

Formatos aceitos:

- `jpg`
- `jpeg`
- `png`
- `webp`

Opcional: coloque uma imagem de referencia em `reference/reference.png`. Se ela existir, o app mostrara essa imagem no topo para ajudar a comparar padroes mais pintados e mais rosetados.

2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Rode o app:

```bash
streamlit run app.py
```

4. No navegador:

- informe o nome do avaliador;
- escolha o numero de rodadas, que comeca em 3 por padrao;
- veja a imagem exibida;
- escolha uma nota de 0 a 100 no slider ou no campo numerico;
- escolha a confianca de 1 a 5;
- clique em `Submeter`.

Cada resposta sera salva no arquivo `ratings.csv`.

Uma rodada significa que cada imagem aparece uma vez. Se voce escolher 3 rodadas, cada imagem aparecera 3 vezes no total. O app tambem salva quanto tempo a pessoa demorou para classificar cada imagem.

## Arquivos

- `app.py`: codigo do app Streamlit.
- `requirements.txt`: dependencias do projeto.
- `README.md`: instrucoes para rodar localmente.
- `images/`: pasta onde voce deve colocar as imagens.
- `reference/`: pasta opcional para a imagem `reference.png`.

## Observacao

Se a pasta `images/` estiver vazia, o app mostrara uma mensagem avisando que e preciso adicionar imagens.
