# 🧾 Extrator de NFS-e - Brasil

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://extractornfse.streamlit.app)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sistema completo de extração, validação e consolidação de Notas Fiscais de Serviço Eletrônicas (NFS-e) brasileiras em planilhas Excel.

## 🌐 Aplicação Web

**Acesse a aplicação online:** [https://extractornfse.streamlit.app](https://extractornfse.streamlit.app)

✨ **Sem instalação necessária! Use direto no navegador!**

---

## 📋 Características

✨ **Extração Inteligente Multi-Padrão**
- Suporta layouts de diversos municípios brasileiros
- Detecta automaticamente padrões: Duque de Caxias (ISSNet Online), Rio de Janeiro (DANFSe Nacional), e modo genérico
- Extração de texto nativo de PDFs (sem OCR necessário para PDFs digitais)

🔍 **Validação Fiscal Automática**
- Valida cálculos de ISS, PIS, COFINS, CSLL, IRRF
- Verifica alíquotas dentro dos limites legais
- Identifica inconsistências em valores e totais
- Classifica problemas por severidade (Erro, Aviso, Info)

📊 **Consolidação em Excel**
- Planilha consolidada com todos os dados extraídos
- Relatório de validação detalhado
- Resumo executivo com totalizadores
- Formatação profissional pronta para uso

🖥️ **Interface Web (Streamlit)**
- Upload múltiplo de arquivos
- Interface intuitiva e responsiva
- Visualização de resultados em tempo real
- Download direto da planilha consolidada

---

## 🚀 Formas de Uso

### 1️⃣ **Aplicação Web Online (Recomendado)**

Acesse: **[https://extractornfse.streamlit.app](https://extractornfse.streamlit.app)**

1. Faça upload dos PDFs das notas fiscais
2. Clique em "Processar"
3. Visualize os resultados
4. Baixe a planilha Excel consolidada

✅ **Sem instalação | Sem configuração | 100% online**

---

### 2️⃣ **Execução Local (Interface Web)**

#### Requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

#### Instalação

```bash
# Clone o repositório
git clone https://github.com/RAFAELSOUZA280292/ExtractorNFSe.git
cd ExtractorNFSe

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação web
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

---

### 3️⃣ **Linha de Comando (CLI)**

```bash
# Processar um único PDF
python main.py nota_fiscal.pdf -o resultado.xlsx

# Processar todos os PDFs de uma pasta
python main.py ./pasta_com_notas/ -o consolidado.xlsx

# Desabilitar validação (mais rápido)
python main.py ./notas/ -o saida.xlsx --no-validation

# Modo verboso (mostra detalhes de processamento)
python main.py ./notas/ -o saida.xlsx -v

# Ver ajuda completa
python main.py --help
```

---

### 4️⃣ **Google Colab (Notebook Online)**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RAFAELSOUZA280292/ExtractorNFSe/blob/main/NFSe_Extractor_Colab.ipynb)

1. Clique no badge acima
2. Siga as instruções do notebook
3. Faça upload dos PDFs
4. Execute as células
5. Baixe a planilha gerada

---

## 📊 Estrutura do Excel Gerado

O arquivo Excel contém 3 planilhas:

### 1️⃣ **Dados NFS-e**
Planilha principal com todas as informações extraídas:

| Campo | Descrição |
|-------|-----------|
| **Identificação** | Número, datas, município, chave |
| **Prestador** | CNPJ, nome, inscrição municipal |
| **Tomador** | CNPJ, nome, inscrição municipal |
| **Valores** | Serviços, desconto, base de cálculo |
| **ISS** | Alíquota, valor, retenção, município |
| **Tributos Federais** | PIS, COFINS, CSLL, IRRF, INSS |
| **Totais** | Tributos retidos, valor líquido |
| **Extras** | Descrição, código atividade, origem |

### 2️⃣ **Validação**
Relatório de problemas encontrados em cada nota:
- Status geral (✅ Validado, ⚠️ Avisos, ❌ Erros)
- Quantidade de problemas por tipo
- Detalhamento de cada problema

### 3️⃣ **Resumo**
Totalizadores e estatísticas:
- Total de notas processadas
- Valores totais (serviços, líquido, tributos)
- Distribuição por município
- Top prestadores por valor

---

## 🏗️ Arquitetura do Sistema

```
ExtractorNFSe/
├── app.py                      # Aplicação Streamlit (Interface Web)
├── main.py                     # Script CLI (Linha de comando)
├── extractor.py                # Motor de extração de PDFs
├── validator.py                # Sistema de validação fiscal
├── consolidator.py             # Gerador de planilhas Excel
├── requirements.txt            # Dependências Python
├── .streamlit/
│   └── config.toml            # Configuração Streamlit
├── NFSe_Extractor_Colab.ipynb # Notebook Google Colab
├── README.md                   # Esta documentação
└── LICENSE                     # Licença MIT
```

---

## 🎯 Dados Extraídos

### Informações Principais
- ✅ Número da nota fiscal
- ✅ Datas (emissão e competência)
- ✅ Município emissor
- ✅ Chave de acesso

### Prestador e Tomador
- ✅ CNPJ/CPF
- ✅ Nome/Razão Social
- ✅ Inscrição Municipal

### Valores e Tributos
- ✅ Valor dos serviços
- ✅ Base de cálculo
- ✅ **ISS** (alíquota, valor, retenção, município)
- ✅ **PIS** (valor retido)
- ✅ **COFINS** (valor retido)
- ✅ **CSLL** (valor retido)
- ✅ **IRRF** (valor retido)
- ✅ **INSS** (valor retido)
- ✅ Outras retenções
- ✅ Valor líquido

### Extras
- ✅ Descrição dos serviços
- ✅ Código de atividade
- ✅ Arquivo de origem
- ✅ Padrão de layout identificado

---

## 🧪 Exemplo de Validação

O sistema valida automaticamente:

### ✅ Cálculos Corretos
```
Base de cálculo: R$ 3.000,00
Alíquota ISS: 5%
ISS calculado: R$ 150,00 ✓
```

### ⚠️ Avisos
```
⚠️ Alíquota de ISS fora da faixa usual
   Esperado: 2% a 5% | Encontrado: 6%
```

### ❌ Erros
```
❌ Valor do ISS não corresponde ao cálculo
   Esperado: R$ 150,00 | Encontrado: R$ 140,00
```

---

## 🌍 Municípios Suportados

### ✅ Suporte Completo
- Duque de Caxias - RJ (ISSNet Online)
- Rio de Janeiro - RJ (DANFSe Nacional v1.0)

### 🔄 Suporte Parcial (Modo Genérico)
Outros municípios funcionam com extração básica:
- Número da nota
- CNPJs (prestador e tomador)
- Valores principais

### 🔧 Adicionar Novo Município

Para adicionar suporte completo a um novo município, veja a [documentação de contribuição](CONTRIBUTING.md).

---

## 🚀 Deploy no Streamlit Cloud

### Passos para publicar sua própria versão:

1. **Fork este repositório**
2. **Acesse:** [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. **Clique em "New app"**
4. **Configure:**
   - Repository: `seu-usuario/ExtractorNFSe`
   - Branch: `main`
   - Main file path: `app.py`
5. **Clique em "Deploy"**

Sua aplicação estará disponível em: `https://seu-app.streamlit.app`

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Especialmente:

- 📍 Suporte para novos municípios
- 🐛 Correção de bugs
- 📚 Melhorias na documentação
- ✨ Novas funcionalidades

### Como Contribuir

1. Fork este repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

---

## 🆘 Problemas Comuns

### Erro: "Module not found"
```bash
pip install -r requirements.txt
```

### PDFs Escaneados (Imagem)
O sistema atual funciona com PDFs digitais (com texto). Para PDFs escaneados, será necessário adicionar OCR.

### Layout Não Reconhecido
O sistema usará o modo genérico. Para melhor precisão, solicite suporte para o município específico abrindo uma issue.

---

## 📞 Suporte

- 🐛 **Bugs**: Abra uma [issue no GitHub](https://github.com/RAFAELSOUZA280292/ExtractorNFSe/issues)
- 💡 **Sugestões**: Use as [discussions](https://github.com/RAFAELSOUZA280292/ExtractorNFSe/discussions)
- 📧 **Contato**: Crie uma issue com a tag [question]

---

## 🎓 Créditos

Desenvolvido por **Rafael Souza** para automatizar a validação e consolidação de notas fiscais brasileiras, facilitando o trabalho de contadores, auditores e profissionais financeiros.

---

## 📸 Screenshots

### Interface Web
![Interface Principal](https://via.placeholder.com/800x400?text=Interface+Principal)

### Resultados da Extração
![Resultados](https://via.placeholder.com/800x400?text=Resultados+da+Extra%C3%A7%C3%A3o)

### Planilha Excel Gerada
![Planilha](https://via.placeholder.com/800x400?text=Planilha+Excel)

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**

[![GitHub stars](https://img.shields.io/github/stars/RAFAELSOUZA280292/ExtractorNFSe.svg?style=social&label=Star)](https://github.com/RAFAELSOUZA280292/ExtractorNFSe)
