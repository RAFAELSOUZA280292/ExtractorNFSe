# CHANGELOG - ExtractorNFSe v2.0

## [2.0.0] - 19/02/2026

### 🚀 Novidades Principais

#### Novo Padrão: Matinhos/PR
Implementado suporte completo para o layout específico da Prefeitura Municipal de Matinhos/PR.

**Características do padrão Matinhos:**
- Layout próprio da prefeitura (não segue DANFSe v1.0)
- Cabeçalho com dados do prestador
- Campos específicos: Número RPS, Série RPS, Situação, Tipo
- Códigos de serviço municipais
- Local de Prestação com código numérico
- Situação Tributária: TIST (Tributada Integralmente com Substituição Tributária), TI (Tributada Integralmente)
- ISSRF (ISS Retido na Fonte)
- Tributos federais separados: INSS, IR, CSLL, COFINS, PIS

### ✅ Melhorias Implementadas

#### 1. Novo Módulo: `extractor_matinhos.py`
Criado módulo especializado para extração de NFS-e de Matinhos/PR com:
- Detecção automática do padrão
- Extração de valores em linhas adjacentes
- Suporte para valores em formato de tabela
- Priorização de valores monetários (com vírgula)
- Cálculo automático de valor líquido

#### 2. Detecção Inteligente de Padrões
Atualizado `extractor.py` para detectar automaticamente:
- Matinhos/PR (via "PREFEITURA MUNICIPAL DE MATINHOS")
- DANFSe v1.0 (Curitiba, Rio de Janeiro, e outros municípios)
- Duque de Caxias (ISSNet Online)

#### 3. Extração de Valores em Tabelas
Implementada lógica robusta para capturar valores organizados em colunas:
- Linha de cabeçalho: `Serviço Local Prestação Alíquota Situação Trib. Valor Serviço Desc. Incondic. Valor Dedução Valor ISS`
- Linha de valores: `702 7963 2.0939% TIST 18.000,00 0,00 0,00 376,90`
- Prioriza valores com vírgula (formato monetário brasileiro)
- Filtra alíquotas percentuais (ex: 2.0939% não é confundido com valor)

#### 4. Campos Extraídos do Padrão Matinhos
- ✅ Número da NFS-e
- ✅ Data de Emissão e Data Fato Gerador
- ✅ CNPJ e Nome do Prestador
- ✅ Inscrição Municipal do Prestador
- ✅ CNPJ e Nome do Tomador
- ✅ Código de Serviço
- ✅ Local de Prestação
- ✅ Alíquota
- ✅ Situação Tributária
- ✅ Valor do Serviço
- ✅ Valor ISS / ISSRF (ISS Retido na Fonte)
- ✅ INSS, IR, CSLL, COFINS, PIS
- ✅ Valor Líquido (calculado automaticamente)

### 📊 Resultados dos Testes

Testados **37 novos PDFs** da pasta DHS INSS:
- **Taxa de sucesso: 100%** ✅
- **20 PDFs** - DANFSe v1.0 (Curitiba/PR e outros municípios)
- **17 PDFs** - Matinhos/PR (novo padrão)

**Todos os campos essenciais foram extraídos corretamente:**
- Número da NF ✓
- Data de Emissão ✓
- CNPJ Prestador e Tomador ✓
- Valor dos Serviços ✓
- Valor Líquido ✓
- ISS Retido ✓
- Tributos Federais ✓

### 🔧 Correções Técnicas

1. **Extração de valores em linhas adjacentes**
   - Problema: Valores estavam na linha seguinte ao cabeçalho
   - Solução: Implementada lógica para processar linha seguinte quando detectar cabeçalho

2. **Filtro de alíquotas percentuais**
   - Problema: Alíquota "2.0939%" era convertida para "20939.0"
   - Solução: Prioriza valores com vírgula (formato monetário)

3. **Detecção de ISSRF**
   - Problema: ISS Retido na Fonte não era identificado
   - Solução: Implementada detecção específica do campo ISSRF

4. **Cálculo de valor líquido**
   - Problema: Valor líquido não era calculado quando não informado
   - Solução: Cálculo automático: Valor Serviço - ISS - PIS - COFINS - IRRF - CSLL - INSS

### 📦 Arquivos Novos/Modificados

**Novos:**
- `extractor_matinhos.py` - Módulo especializado para Matinhos/PR

**Modificados:**
- `extractor.py` - Integração com novo módulo e detecção de padrão
- `CHANGELOG.md` - Documentação de mudanças

### 🎯 Cobertura de Municípios

O ExtractorNFSe agora suporta:
1. **Matinhos/PR** - Layout próprio ✅
2. **Curitiba/PR** - DANFSe v1.0 ✅
3. **Rio de Janeiro/RJ** - DANFSe v1.0 ✅
4. **Duque de Caxias/RJ** - ISSNet Online ✅
5. **Outros municípios** - DANFSe v1.0 (genérico) ✅

### 🚀 Próximos Passos Recomendados

1. Adicionar suporte para mais municípios do Paraná
2. Implementar validação cruzada de valores
3. Adicionar exportação em múltiplos formatos
4. Criar testes unitários automatizados

---

**Desenvolvido com excelência técnica e foco em resultados.**

*Última atualização: 19/02/2026*
