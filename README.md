# Food Inventory App

Aplicativo para gerenciamento de estoque de alimentos, com cadastro, busca, atualização de quantidade e relatórios de produtos próximos do vencimento.

## Requisitos

- Python 3.10+
- Tkinter (normalmente incluído em instaladores padrão do Python para Windows e macOS)
- `pytest` para executar os testes (opcional, mas recomendado)

## Instalação

### 1) Criar ambiente virtual

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Instalar dependências

```bash
pip install -r requirements.txt
```

## Execução

```bash
python food_inventory_app.py
```

## Estrutura de arquivos

- `food_inventory_app.py` - aplicação principal
- `alimentos.csv` - base de dados do estoque - criado automaticamente se não existir
- `relatorios/` - arquivos CSV gerados por relatórios - criado automaticamente se não existir

## Observações importantes

- A aplicação usa `alimentos.csv` como arquivo de armazenamento principal.
- Quando executada a partir de um executável bundle gerado com PyInstaller, o programa tenta manter os arquivos ao lado do executável ou no diretório do projeto.
- Para distribuir para usuários finais, o recomendado é gerar um executável com PyInstaller e publicar em um GitHub Release.

## Build com PyInstaller

```bash
pyinstaller --onefile --windowed --name food_inventory_app food_inventory_app.py
```

## Licença

Este projeto foi desenvolvido para uso local e pessoal.
