# Applicativo ValidadeProdutos

Aplicativo para gerenciamento de estoque de alimentos, com cadastro, busca, atualização de quantidade e relatórios de produtos próximos do vencimento.

O executável se encontra na pasta `/dist`.

## Funcionalidades
* Buscar produto: procura um produto no database de acordo com a marca e tipo de produto. Caso o produto exista, uma tabela com os produtos aparecerá na área "Status do estoque"
* Registrar novo produto: permite cadastrar um novo produto. Caso o produto com mesma marca, tipo e validade já exista no estoque, a quantidade no estoque será apenas atualizada. Informações que podem ser adicionadas são:
     * Marca (obrigatório)
     * Tipo de produto (obrigatório)
     * Quantidade (obrigatório)
     * Unidade (obrigatório)
     * Categoria (opcional)
     * Localização (opcional)
     * Data de validade (obrigatório)
     * Comentários (opcional)
* Adicionar ou remover quantidades de um produto selecionado: ao selecionar um produto na tabela de "Status do estoque", é possível adicionar ou remover unidades desse produto ao clicar nos botões "Adicionar" ou "Remover", respectivamente
* Criar relatórios: mostra o relatório de todos os produtos em estoque, produtos próximos ao vencimento (<30 dias), e produtos vencidos.
* Exportar relatórios: caso existam produtos próximos ao vencimento e/ou produtos vencidos, cada relatório poderá ser exportado separadamente. Os relatórios serão exportados em formato csv na cartela "Relatórios".



## Estrutura de arquivos

- `food_inventory_app.py` - aplicação principal
- `alimentos.csv` - base de dados do estoque - criado automaticamente se não existir
- `relatorios/` - arquivos CSV gerados por relatórios - criado automaticamente se não existir
- `dist/` - executável Windows


## Requisitos para desenvolvimento

- Python 3.10+
- Tkinter (normalmente incluído em instaladores padrão do Python para Windows e macOS)


## Execução

```bash
python food_inventory_app.py
```

## Observações importantes

- A aplicação usa `alimentos.csv` como arquivo de armazenamento principal.
- Quando executada a partir de um executável bundle gerado com PyInstaller, o programa tenta manter os arquivos ao lado do executável ou no diretório do projeto.
- Para distribuir para usuários finais, o recomendado é gerar um executável com PyInstaller e publicar em um GitHub Release.

## Build com PyInstaller

```
pip install --upgrade pyinstaller
pyinstaller --onefile --windowed --name food_inventory_app food_inventory_app.py
```

## Licença

Este projeto foi desenvolvido para uso local e pessoal.
