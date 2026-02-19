"""
Aplicação Streamlit para Extração de NFS-e
Interface web para processar múltiplas notas fiscais
"""

import streamlit as st
import pandas as pd
import tempfile
import os
from pathlib import Path
import io
from extractor import NFSeExtractor
from validator import NFSeValidator
from consolidator import NFSeConsolidator

# Configuração da página
st.set_page_config(
    page_title="Extrator de NFS-e Brasil",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🧾 Extrator de NFS-e - Brasil</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistema de Extração, Validação e Consolidação de Notas Fiscais</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/invoice.png", width=80)
    st.title("⚙️ Configurações")
    
    st.markdown("---")
    
    st.markdown("### 📋 Funcionalidades")
    st.markdown("""
    - ✅ Upload múltiplo de PDFs
    - ✅ Extração automática
    - ✅ Validação fiscal
    - ✅ Consolidação em Excel
    - ✅ Suporte multi-município
    """)
    
    st.markdown("---")
    
    enable_validation = st.checkbox("Habilitar Validação", value=True, help="Valida cálculos e consistência dos dados")
    
    st.markdown("---")
    
    st.markdown("### 🏛️ Municípios Suportados")
    st.markdown("""
    - ✅ Duque de Caxias - RJ
    - ✅ Rio de Janeiro - RJ
    - 🔄 Outros (modo genérico)
    """)
    
    st.markdown("---")
    
    st.markdown("### 📚 Documentação")
    st.markdown("[📖 README](https://github.com/RAFAELSOUZA280292/ExtractorNFSe)")
    st.markdown("[🐛 Reportar Bug](https://github.com/RAFAELSOUZA280292/ExtractorNFSe/issues)")

# Main content
tab1, tab2, tab3 = st.tabs(["📤 Upload e Processamento", "📊 Resultados", "ℹ️ Sobre"])

with tab1:
    st.markdown("## 📤 Upload das Notas Fiscais")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Selecione os arquivos PDF das NFS-e",
            type=['pdf'],
            accept_multiple_files=True,
            help="Você pode selecionar múltiplos arquivos PDF de uma vez (máx. 10 MB por arquivo)"
        )
        
        # Validação de tamanho de arquivo
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
        if uploaded_files:
            valid_files = []
            for file in uploaded_files:
                if file.size > MAX_FILE_SIZE:
                    st.error(f"❌ Arquivo {file.name} excede o tamanho máximo de 10 MB")
                else:
                    valid_files.append(file)
            uploaded_files = valid_files if valid_files else None
    
    with col2:
        st.info(f"""
        **Arquivos carregados:** {len(uploaded_files) if uploaded_files else 0}
        
        **Formatos aceitos:** PDF
        
        **Limite:** 10 MB por arquivo
        """)
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} arquivo(s) carregado(s) com sucesso!")
        
        # Mostra preview dos arquivos
        with st.expander("📋 Ver lista de arquivos"):
            for i, file in enumerate(uploaded_files, 1):
                st.text(f"{i}. {file.name} ({file.size / 1024:.2f} KB)")
        
        st.markdown("---")
        
        # Botão de processar
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            process_button = st.button("🚀 Processar Notas Fiscais", type="primary", use_container_width=True)
        
        if process_button:
            # Barra de progresso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Inicializa componentes
            extractor = NFSeExtractor()
            validator = NFSeValidator()
            consolidator = NFSeConsolidator()
            
            # Processa arquivos
            extracted_data = []
            errors = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                progress = (i + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.text(f"Processando {uploaded_file.name}...")
                
                tmp_path = None
                try:
                    # Salva arquivo temporário
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_path = tmp_file.name
                    
                    # Extrai dados
                    data = extractor.extract_from_pdf(tmp_path)
                    # Preserva o nome original do arquivo
                    data.arquivo_origem = uploaded_file.name
                    extracted_data.append(data)
                    
                except Exception as e:
                    errors.append(f"{uploaded_file.name}: {str(e)}")
                finally:
                    # Garante remoção do arquivo temporário
                    if tmp_path and os.path.exists(tmp_path):
                        try:
                            os.unlink(tmp_path)
                        except Exception:
                            pass  # Ignora erros ao remover arquivo temporário
            
            progress_bar.progress(1.0)
            status_text.text("✅ Processamento concluído!")
            
            # Armazena resultados na sessão
            st.session_state['extracted_data'] = extracted_data
            st.session_state['errors'] = errors
            st.session_state['enable_validation'] = enable_validation
            
            # Mensagem de sucesso
            if extracted_data:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown(f"### ✅ Extração Concluída!")
                st.markdown(f"**{len(extracted_data)} nota(s) processada(s) com sucesso**")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Erros
            if errors:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.markdown(f"### ⚠️ Avisos ({len(errors)} arquivo(s))")
                for error in errors[:5]:
                    st.text(f"• {error}")
                if len(errors) > 5:
                    st.text(f"... e mais {len(errors) - 5} erro(s)")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Redireciona para aba de resultados
            st.info("👉 Acesse a aba **'Resultados'** para visualizar os dados extraídos")

with tab2:
    st.markdown("## 📊 Resultados da Extração")
    
    if 'extracted_data' not in st.session_state or not st.session_state['extracted_data']:
        st.info("ℹ️ Nenhum dado processado ainda. Faça upload e processe os arquivos na aba 'Upload e Processamento'.")
    else:
        extracted_data = st.session_state['extracted_data']
        enable_validation = st.session_state.get('enable_validation', True)
        validator = NFSeValidator()
        
        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        total_valor = sum(float(d.valor_servicos) for d in extracted_data)
        total_iss = sum(float(d.iss_valor) for d in extracted_data)
        total_tributos = sum(float(d.total_tributos_retidos) for d in extracted_data)
        total_liquido = sum(float(d.valor_liquido) for d in extracted_data)
        
        with col1:
            st.metric("📄 Notas Processadas", len(extracted_data))
        with col2:
            st.metric("💰 Valor Total", f"R$ {total_valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        with col3:
            st.metric("🏛️ ISS Total", f"R$ {total_iss:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        with col4:
            st.metric("📊 Total Tributos", f"R$ {total_tributos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        st.markdown("---")
        
        # Validação
        if enable_validation:
            st.markdown("### 🔍 Validação dos Dados")
            
            validation_counts = {'ok': 0, 'warning': 0, 'error': 0}
            all_issues = []
            
            for data in extracted_data:
                issues = validator.validate(data)
                if any(i.severity == 'ERROR' for i in issues):
                    validation_counts['error'] += 1
                elif any(i.severity == 'WARNING' for i in issues):
                    validation_counts['warning'] += 1
                else:
                    validation_counts['ok'] += 1
                
                if issues:
                    all_issues.append((data.numero_nota, issues))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("✅ Validadas", validation_counts['ok'])
            with col2:
                st.metric("⚠️ Com Avisos", validation_counts['warning'])
            with col3:
                st.metric("❌ Com Erros", validation_counts['error'])
            
            # Mostra problemas
            if all_issues:
                with st.expander("🔍 Ver detalhes da validação"):
                    for nota_num, issues in all_issues[:10]:
                        st.markdown(f"**NF {nota_num}:**")
                        for issue in issues[:3]:
                            icon = {'ERROR': '❌', 'WARNING': '⚠️', 'INFO': 'ℹ️'}
                            st.text(f"  {icon.get(issue.severity, '•')} {issue.message}")
                        st.markdown("---")
        
        st.markdown("---")
        
        # Preview dos dados
        st.markdown("### 📋 Preview dos Dados Extraídos")
        
        # Cria DataFrame
        rows = []
        for data in extracted_data:
            rows.append({
                'NF': data.numero_nota,
                'Data': data.data_emissao,
                'Município': data.municipio,
                'Prestador': data.prestador_nome[:30] + '...' if len(data.prestador_nome) > 30 else data.prestador_nome,
                'CNPJ Prestador': data.prestador_cnpj,
                'Valor Serviços': f"R$ {float(data.valor_servicos):,.2f}",
                'ISS': f"R$ {float(data.iss_valor):,.2f}",
                'Valor Líquido': f"R$ {float(data.valor_liquido):,.2f}",
                'Padrão': data.padrao_layout
            })
        
        df_preview = pd.DataFrame(rows)
        st.dataframe(df_preview, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Download da planilha consolidada
        st.markdown("### 📥 Download da Planilha Consolidada")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📊 Gerar Planilha Excel", type="primary", use_container_width=True):
                with st.spinner("Gerando planilha..."):
                    # Cria arquivo temporário
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                        consolidator = NFSeConsolidator()
                        consolidator.consolidate_to_excel(
                            extracted_data,
                            tmp_file.name,
                            include_validation=enable_validation
                        )
                        
                        # Lê arquivo para download
                        with open(tmp_file.name, 'rb') as f:
                            excel_data = f.read()
                        
                        # Remove arquivo temporário
                        os.unlink(tmp_file.name)
                    
                    st.success("✅ Planilha gerada com sucesso!")
                    
                    st.download_button(
                        label="⬇️ Baixar Planilha Excel",
                        data=excel_data,
                        file_name="nfse_consolidado.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

with tab3:
    st.markdown("## ℹ️ Sobre o Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Funcionalidades
        
        Este sistema foi desenvolvido para automatizar a extração e validação de dados de Notas Fiscais de Serviço Eletrônicas (NFS-e) brasileiras.
        
        **Principais recursos:**
        - Extração automática de 30+ campos fiscais
        - Validação de cálculos e alíquotas
        - Suporte para múltiplos municípios
        - Consolidação em planilhas Excel
        - Processamento em lote
        - Detecção automática de padrões
        
        ### 📊 Dados Extraídos
        - Identificação completa da nota
        - Dados do prestador e tomador
        - Valores e base de cálculo
        - ISS (alíquota, valor, retenção)
        - Tributos federais (PIS, COFINS, CSLL, IRRF)
        - Descrição dos serviços
        """)
    
    with col2:
        st.markdown("""
        ### 🏛️ Municípios Suportados
        
        **Suporte Completo:**
        - ✅ Duque de Caxias - RJ (ISSNet Online)
        - ✅ Rio de Janeiro - RJ (DANFSe Nacional)
        
        **Suporte Parcial (Modo Genérico):**
        - 🔄 Outros municípios brasileiros
        
        ### 🔧 Tecnologias
        - **Python 3.8+**
        - **Streamlit** (Interface web)
        - **pdfplumber** (Extração de PDF)
        - **pandas** (Manipulação de dados)
        - **openpyxl** (Geração de Excel)
        
        ### 📚 Links Úteis
        - [📖 Documentação Completa](https://github.com/RAFAELSOUZA280292/ExtractorNFSe)
        - [🐛 Reportar Problemas](https://github.com/RAFAELSOUZA280292/ExtractorNFSe/issues)
        - [🤝 Contribuir](https://github.com/RAFAELSOUZA280292/ExtractorNFSe)
        
        ### 📝 Licença
        MIT License - Código aberto e gratuito
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 👨‍💻 Desenvolvedor
    **Rafael Souza**
    
    Sistema desenvolvido para facilitar o trabalho de contadores, auditores e profissionais financeiros no processamento de notas fiscais brasileiras.
    
    ---
    
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>💼 Extrator de NFS-e Brasil | Desenvolvido com ❤️ para a comunidade contábil brasileira</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    🧾 Extrator de NFS-e v1.0 | © 2026 Rafael Souza | 
    <a href="https://github.com/RAFAELSOUZA280292/ExtractorNFSe" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)
