# Changelog - ExtractorNFSe

## [1.1.0] - 2026-02-02

### 🔧 Correções para Deploy no Streamlit Cloud

#### Adicionado
- **`.streamlit/config.toml`**: Arquivo de configuração do Streamlit com tema personalizado e limites de upload
- **`.python-version`**: Especifica Python 3.11 para compatibilidade com Streamlit Cloud
- **`packages.txt`**: Lista de dependências do sistema (poppler-utils) necessárias para processamento de PDFs
- **Validação de tamanho de arquivo**: Limite de 10 MB por arquivo PDF para prevenir sobrecarga do servidor

#### Corrigido
- **Versionamento de dependências** (`requirements.txt`): Todas as bibliotecas agora têm versões específicas para garantir estabilidade
  - `pdfplumber==0.11.4`
  - `pandas==2.2.3`
  - `openpyxl==3.1.5`
  - `streamlit==1.40.2`

- **Tratamento de arquivos temporários** (`app.py`):
  - Implementado bloco `finally` para garantir remoção de arquivos temporários mesmo em caso de erro
  - Previne vazamento de espaço em disco e exposição de dados sensíveis

- **Exposição de informações sensíveis** (`extractor.py`):
  - Mensagens de erro agora mostram apenas o nome do arquivo, não o caminho completo
  - Previne vazamento de informações sobre estrutura de diretórios

- **Tratamento de exceções** (`extractor.py`):
  - Substituído `except:` genérico por `except (ValueError, InvalidOperation)` específico
  - Adicionado import de `InvalidOperation` do módulo `decimal`
  - Melhora depuração e previne mascaramento de erros

- **Divisão por zero** (`consolidator.py`):
  - Adicionada validação antes de calcular percentuais
  - Previne crash ao gerar relatório sem dados

- **Configuração do Streamlit** (`.streamlit/config.toml`):
  - Corrigido conflito entre `enableCORS` e `enableXsrfProtection`
  - `enableCORS` agora é `true` para compatibilidade com proteção CSRF

#### Melhorado
- **Documentação de código**: Docstrings expandidas com exemplos e descrição de parâmetros
- **Segurança**: Múltiplas correções de segurança aplicadas (ver análise de falhas)
- **Experiência do usuário**: Mensagens de erro mais claras e informativas

---

## [1.0.0] - 2026-02-01

### Lançamento Inicial
- Extração de dados de NFS-e de múltiplos municípios
- Validação fiscal automática
- Consolidação em planilhas Excel
- Interface web com Streamlit
- Suporte para Duque de Caxias-RJ e Rio de Janeiro-RJ
