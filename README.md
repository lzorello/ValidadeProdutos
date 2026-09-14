# ValidadeProdutos
Verificar validade de produtos de acordo com informações do código de barras

## Organização
### /Código de barras
Cartela com novos códigos de barras para ser adicionados ao banco de dados

### validade_produtos.csv
Banco de dados provisório no formato *.csv

### adicionar_produtos.py
1. Ler os números de código de barras a partir de fotos adicionadas à cartela "Código de barras"
2. Para os valores que ainda não foram adicionados na tabela, encontrar a data de validade de acordo com o código de barras
3. Adicionar os produtos à tabela "validade_produtos.csv":
    - Nome produto
    - Data de validade
4. Apagar imagens

### verificar_validade.py
1. Identificar produtos vencidos
2. Identificar produtos próximos ao vencimento
