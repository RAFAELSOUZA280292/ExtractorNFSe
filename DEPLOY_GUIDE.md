# 🚀 Guia de Deploy no Streamlit Cloud

## Passo a Passo Completo

### 1️⃣ **Preparar Repositório no GitHub**

#### A. Fazer Upload dos Arquivos

1. Acesse: https://github.com/RAFAELSOUZA280292/ExtractorNFSe
2. Clique em **"Add file"** → **"Upload files"**
3. Arraste TODOS os arquivos da pasta `github-final`:
   ```
   ✅ app.py
   ✅ main.py
   ✅ extractor.py
   ✅ validator.py
   ✅ consolidator.py
   ✅ requirements.txt
   ✅ README.md
   ✅ LICENSE
   ✅ .gitignore
   ✅ NFSe_Extractor_Colab.ipynb
   ✅ .streamlit/config.toml (criar pasta .streamlit primeiro)
   ```

4. **IMPORTANTE:** Para a pasta `.streamlit/`:
   - Clique em **"Add file"** → **"Create new file"**
   - Nome do arquivo: `.streamlit/config.toml`
   - Cole o conteúdo do arquivo `config.toml`
   - Clique em **"Commit changes"**

5. Mensagem de commit sugerida:
   ```
   Initial commit: Sistema completo de extração de NFS-e
   
   - Aplicação Streamlit completa
   - Extração inteligente multi-padrão
   - Validação fiscal automática
   - Consolidação em Excel
   - Suporte CLI e Google Colab
   ```

6. Clique em **"Commit changes"**

#### B. Verificar Estrutura no GitHub

Certifique-se de que seu repositório tem esta estrutura:

```
ExtractorNFSe/
├── .gitignore
├── .streamlit/
│   └── config.toml
├── LICENSE
├── NFSe_Extractor_Colab.ipynb
├── README.md
├── app.py
├── consolidator.py
├── extractor.py
├── main.py
├── requirements.txt
└── validator.py
```

---

### 2️⃣ **Deploy no Streamlit Cloud**

#### A. Criar Conta no Streamlit Cloud

1. Acesse: https://streamlit.io/cloud
2. Clique em **"Sign in with GitHub"**
3. Autorize o Streamlit a acessar seus repositórios

#### B. Criar Nova Aplicação

1. No painel do Streamlit Cloud, clique em **"New app"**

2. Preencha as informações:
   - **Repository:** `RAFAELSOUZA280292/ExtractorNFSe`
   - **Branch:** `main` (ou `master`, dependendo do padrão do seu repo)
   - **Main file path:** `app.py`
   - **App URL (opcional):** `extractornfse` (ou outro nome de sua preferência)

3. Clique em **"Deploy!"**

#### C. Aguardar Deploy

- O Streamlit irá:
  1. ✅ Clonar seu repositório
  2. ✅ Instalar dependências do `requirements.txt`
  3. ✅ Iniciar a aplicação
  4. ✅ Gerar URL público

- Tempo estimado: 2-5 minutos

#### D. Acesse sua Aplicação

Após o deploy, sua app estará disponível em:
```
https://extractornfse.streamlit.app
```
(ou o nome personalizado que você escolheu)

---

### 3️⃣ **Configurações Avançadas (Opcional)**

#### Configurar Secrets (se necessário)

1. No painel do Streamlit Cloud, clique em **"Settings"**
2. Vá em **"Secrets"**
3. Adicione variáveis de ambiente (formato TOML):
   ```toml
   # Exemplo (não necessário para este projeto)
   [general]
   debug = false
   ```

#### Configurar Resources

1. No painel, clique em **"Settings"**
2. Vá em **"Resources"**
3. Ajuste se necessário:
   - CPU: 2 cores (padrão)
   - Memory: 800 MB (padrão)
   - Timeout: 10 min (padrão)

---

### 4️⃣ **Testar a Aplicação**

1. Acesse a URL da sua app
2. Faça upload de um PDF de teste
3. Clique em "Processar"
4. Verifique os resultados
5. Baixe a planilha Excel

---

### 5️⃣ **Atualizar a Aplicação**

Sempre que você fizer alterações no GitHub:

1. Faça commit das mudanças no GitHub
2. O Streamlit Cloud detecta automaticamente
3. A aplicação é atualizada automaticamente em ~1 minuto

**OU** manualmente:
1. Acesse o painel do Streamlit Cloud
2. Clique em **"Reboot app"** ou **"Manage app"** → **"Reboot"**

---

### 6️⃣ **Atualizar README com Link da App**

Após o deploy, edite o README.md no GitHub:

1. Localize a linha:
   ```markdown
   **Acesse a aplicação online:** [https://extractornfse.streamlit.app](https://extractornfse.streamlit.app)
   ```

2. Substitua pela URL real da sua app

3. Atualize também o badge:
   ```markdown
   [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://SEU-APP.streamlit.app)
   ```

---

## 🎯 Checklist Final

Antes de fazer o deploy, verifique:

- ✅ Todos os arquivos foram enviados para o GitHub
- ✅ A pasta `.streamlit/` existe com `config.toml`
- ✅ O arquivo `requirements.txt` está correto
- ✅ O `app.py` está na raiz do repositório
- ✅ Não há arquivos de teste ou PDFs no repositório
- ✅ O `.gitignore` está configurado

---

## 🐛 Solução de Problemas

### Erro: "ModuleNotFoundError"

**Causa:** Dependência faltando no `requirements.txt`

**Solução:**
1. Adicione a dependência no `requirements.txt`
2. Commit no GitHub
3. Aguarde atualização automática

### Erro: "File not found: app.py"

**Causa:** Nome ou localização incorreta do arquivo principal

**Solução:**
1. Verifique que `app.py` está na raiz do repositório
2. No Streamlit Cloud, corrija o "Main file path"
3. Reboot a aplicação

### App Muito Lenta

**Causa:** Processamento pesado ou muitos arquivos

**Solução:**
1. Limite o tamanho dos uploads
2. Otimize o código
3. Solicite upgrade de recursos no Streamlit

### Erro ao Fazer Upload de PDFs

**Causa:** Limite de tamanho excedido

**Solução:**
Já configurado em `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 200
```

---

## 📊 Monitoramento

### Logs da Aplicação

1. Acesse o painel do Streamlit Cloud
2. Clique em **"Manage app"**
3. Veja **"Logs"** para debugging

### Métricas de Uso

O Streamlit Cloud fornece:
- Número de visualizações
- Usuários ativos
- Tempo de execução
- Uso de recursos

---

## 🎉 Pronto!

Após seguir todos os passos, você terá:

✅ Repositório GitHub completo e organizado  
✅ Aplicação web online 24/7  
✅ URL pública para compartilhar  
✅ Deploy automático a cada commit  
✅ Sistema pronto para uso profissional

---

## 📞 Precisa de Ajuda?

- 📖 [Documentação Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- 💬 [Fórum Streamlit](https://discuss.streamlit.io/)
- 🐛 [Issues do Projeto](https://github.com/RAFAELSOUZA280292/ExtractorNFSe/issues)

---

**Boa sorte com o deploy! 🚀**
