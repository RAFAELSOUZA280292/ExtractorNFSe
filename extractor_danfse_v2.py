"""
Função melhorada de extração DANFSe v1.0
Abordagem baseada em linhas adjacentes para lidar com texto sem espaços
"""

import re
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass

@dataclass
class NFSeData:
    """Estrutura de dados para informações da NFS-e"""
    numero_nota: str = ""
    data_emissao: str = ""
    data_competencia: str = ""
    municipio: str = ""
    chave_acesso: str = ""
    
    # Prestador
    prestador_cnpj: str = ""
    prestador_nome: str = ""
    prestador_inscricao: str = ""
    
    # Tomador
    tomador_cnpj: str = ""
    tomador_nome: str = ""
    tomador_inscricao: str = ""
    
    # Valores
    valor_servicos: Decimal = Decimal("0.00")
    valor_desconto: Decimal = Decimal("0.00")
    base_calculo: Decimal = Decimal("0.00")
    
    # Impostos
    iss_aliquota: Decimal = Decimal("0.00")
    iss_valor: Decimal = Decimal("0.00")
    iss_retido: str = "Não"
    municipio_retencao: str = ""
    
    pis: Decimal = Decimal("0.00")
    cofins: Decimal = Decimal("0.00")
    csll: Decimal = Decimal("0.00")
    irrf: Decimal = Decimal("0.00")
    inss: Decimal = Decimal("0.00")
    outras_retencoes: Decimal = Decimal("0.00")
    
    # Totais
    total_tributos_retidos: Decimal = Decimal("0.00")
    valor_liquido: Decimal = Decimal("0.00")
    
    # Metadados
    descricao_servico: str = ""
    codigo_atividade: str = ""
    arquivo_origem: str = ""
    padrao_layout: str = ""


def _parse_decimal(value: str) -> Decimal:
    """Converte string monetária para Decimal"""
    if not value or value == '-' or value.strip() == '':
        return Decimal("0.00")
    
    # Remove pontos de milhar e substitui vírgula por ponto
    value = value.replace('.', '').replace(',', '.')
    
    try:
        return Decimal(value).quantize(Decimal("0.01"))
    except (ValueError, InvalidOperation):
        return Decimal("0.00")


def extract_danfse_v1_improved(text: str) -> NFSeData:
    """
    Extração melhorada para DANFSe v1.0
    Usa abordagem baseada em linhas adjacentes
    """
    data = NFSeData()
    data.padrao_layout = "danfse_v1"
    
    lines = text.split('\n')
    
    # Processa linha por linha
    for i, line in enumerate(lines):
        line_clean = line.strip()
        
        # Número da NFS-e (linha seguinte após o cabeçalho)
        if 'NúmerodaNFS-e' in line or 'Número da NFS-e' in line:
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # Primeira palavra/número é o número da nota
                match = re.search(r'^(\d+)', next_line)
                if match:
                    data.numero_nota = match.group(1)
                
                # Extrai também competência e data de emissão
                dates = re.findall(r'(\d{2}/\d{2}/\d{4})', next_line)
                if len(dates) >= 2:
                    data.data_competencia = dates[0]
                    data.data_emissao = dates[1]
                elif len(dates) == 1:
                    data.data_emissao = dates[0]
        
        # Chave de acesso
        if 'ChavedeAcessodaNFS-e' in line or 'Chave de Acesso da NFS-e' in line:
            if i + 1 < len(lines):
                chave = lines[i + 1].strip()
                if chave.isdigit() and len(chave) > 30:
                    data.chave_acesso = chave
        
        # Município
        if 'Prefeitura' in line:
            # Extrai município do cabeçalho
            # Padrão: PrefeituradaCidadedoRiode ou Prefeitura Municipal de Magé
            match = re.search(r'Prefeitura(?:Municipal|daCidade)?(?:de|do)([A-Z][a-záéíóúãõç]+)', line)
            if match:
                mun = match.group(1)
                # Adiciona espaços em nomes compostos (ex: Riode -> Rio de)
                mun = re.sub(r'([a-z])([A-Z])', r'\1 \2', mun)
                # Casos especiais
                if mun == 'Riode':
                    mun = 'Rio de Janeiro'
                data.municipio = f"{mun} - RJ"
            else:
                # Tenta padrão com espaços
                match = re.search(r'Prefeitura.*?(?:de|do)\s+([A-Z][a-záéíóúãõç]+(?:\s+[a-z]+)?)', line, re.IGNORECASE)
                if match:
                    data.municipio = match.group(1).strip() + " - RJ"
        
        # Prestador - CNPJ (linha com "PrestadordoServiço" ou "Prestador do Serviço")
        if 'Prestador' in line and 'Serviço' in line:
            match = re.search(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', line)
            if match:
                data.prestador_cnpj = match.group(1)
        
        # Prestador - Nome (linha após "Nome/NomeEmpresarial")
        if 'Nome/NomeEmpresarial' in line or 'Nome / Nome Empresarial' in line:
            if 'EMITENTE' in lines[max(0, i-5):i+1][-1] or 'EMITENTE' in ''.join(lines[max(0, i-3):i+1]):
                if i + 1 < len(lines):
                    nome_line = lines[i + 1].strip()
                    # Remove CNPJ e números soltos no início
                    nome = re.sub(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', '', nome_line)
                    nome = re.sub(r'^[\d\.]+', '', nome)
                    # Remove email
                    nome_parts = nome.split()
                    nome_clean = ' '.join([p for p in nome_parts if '@' not in p and not p.replace('.', '').isdigit()])
                    # Adiciona espaços em nomes grudados (ex: CELIOSOARESDASILVA -> CELIO SOARES DA SILVA)
                    if nome_clean and ' ' not in nome_clean:
                        # Adiciona espaço antes de maiúsculas
                        nome_clean = re.sub(r'([a-záéíóúãõç])([A-Z])', r'\1 \2', nome_clean)
                        # Adiciona espaço antes de "DA", "DE", "DO", "DOS", "DAS"
                        nome_clean = re.sub(r'([A-ZÁÉÍÓÚÃÕÇ])(DA|DE|DO|DOS|DAS)([A-Z])', r'\1 \2 \3', nome_clean)
                    if nome_clean:
                        data.prestador_nome = nome_clean
            
            # Tomador - Nome
            elif 'TOMADOR' in ''.join(lines[max(0, i-3):i+1]):
                if i + 1 < len(lines):
                    nome_line = lines[i + 1].strip()
                    if nome_line and nome_line != '-':
                        # Remove CNPJ
                        nome = re.sub(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', '', nome_line)
                        nome_parts = nome.split()
                        nome_clean = ' '.join([p for p in nome_parts if '@' not in p and p != '-'])
                        # Adiciona espaços em nomes grudados
                        if nome_clean and ' ' not in nome_clean:
                            nome_clean = re.sub(r'([a-záéíóúãõç])([A-Z])', r'\1 \2', nome_clean)
                            nome_clean = re.sub(r'([A-ZÁÉÍÓÚÃÕÇ])(DA|DE|DO|DOS|DAS)([A-Z])', r'\1 \2 \3', nome_clean)
                        if nome_clean:
                            data.tomador_nome = nome_clean
        
        # Tomador - CNPJ
        if 'TOMADORDOSERVIÇO' in line or 'TOMADOR DO SERVIÇO' in line:
            match = re.search(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', line)
            if match:
                data.tomador_cnpj = match.group(1)
            # Se não estiver na mesma linha, procura na próxima
            elif i + 1 < len(lines):
                match = re.search(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', lines[i + 1])
                if match:
                    data.tomador_cnpj = match.group(1)
        
        # Valor do Serviço
        if 'ValordoServiço' in line or 'Valor do Serviço' in line:
            match = re.search(r'R\$\s*([\d.,]+)', line)
            if match:
                data.valor_servicos = _parse_decimal(match.group(1))
            # Se não estiver na mesma linha, procura na próxima
            elif i + 1 < len(lines):
                match = re.search(r'R\$\s*([\d.,]+)', lines[i + 1])
                if match:
                    data.valor_servicos = _parse_decimal(match.group(1))
        
        # BC ISSQN
        if 'BCISSQN' in line or 'BC ISSQN' in line:
            match = re.search(r'([\d.,]+)', line)
            if match and match.group(1) != '-':
                data.base_calculo = _parse_decimal(match.group(1))
        
        # Alíquota
        if 'AlíquotaAplicada' in line or 'Alíquota Aplicada' in line:
            match = re.search(r'([\d.,]+)%?', line)
            if match and match.group(1) != '-':
                data.iss_aliquota = _parse_decimal(match.group(1))
        
        # Retenção do ISSQN
        if 'RetençãodoISSQN' in line or 'Retenção do ISSQN' in line:
            if 'NãoRetido' in line or 'Não Retido' in line:
                data.iss_retido = "Não"
            elif 'Retido' in line:
                data.iss_retido = "Sim"
        
        # ISSQN Retido (valor)
        if 'ISSQNRetido' in line or 'ISSQN Retido' in line:
            match = re.search(r'R\$\s*([\d.,]+)', line)
            if not match:
                match = re.search(r'([\d.,]+)', line)
            if match and match.group(1) != '-':
                valor = _parse_decimal(match.group(1))
                if valor > 0:
                    data.iss_valor = valor
                    data.iss_retido = "Sim"
        
        # Valor Líquido
        if 'ValorLíquidodaNFS-e' in line or 'Valor Líquido da NFS-e' in line:
            match = re.search(r'R\$\s*([\d.,]+)', line)
            if match:
                data.valor_liquido = _parse_decimal(match.group(1))
        
        # Contribuição Previdenciária - Retida (variação de INSS)
        # Formato: IRRF ContribuiçãoPrevidenciária-Retida ContribuiçõesSociais-Retidas
        # Valores:  -    R$557,73                           -
        if 'ContribuiçãoPrevidenciária-Retida' in line or 'Contribuição Previdenciária - Retida' in line:
            if i + 1 < len(lines):
                valores_line = lines[i + 1]
                # Split por espaços
                partes = valores_line.split()
                
                # Primeira parte: IRRF
                if len(partes) >= 1 and partes[0] != '-':
                    match = re.search(r'([\d.,]+)', partes[0])
                    if match:
                        data.irrf = _parse_decimal(match.group(1))
                
                # Segunda parte: Contribuição Previdenciária (INSS)
                if len(partes) >= 2 and partes[1] != '-':
                    match = re.search(r'([\d.,]+)', partes[1])
                    if match:
                        data.inss = _parse_decimal(match.group(1))
                        if data.inss > 0:
                            # Marca como retido se houver valor
                            pass  # INSS retido é diferente de ISS retido
                
                # Terceira parte: Contribuições Sociais (PIS/COFINS)
                if len(partes) >= 3 and partes[2] != '-':
                    match = re.search(r'([\d.,]+)', partes[2])
                    if match:
                        total = _parse_decimal(match.group(1))
                        if total > 0:
                            data.pis = total * Decimal("0.178")
                            data.cofins = total * Decimal("0.822")
        
        # Seção VALOR TOTAL DA NFS-E (valores em colunas)
        # Formato: IRRF,CP,CSLL-Retidos PIS/COFINSRetidos ValorLíquidodaNFS-e
        # Valores:  R$0,00              -                 R$3.450,00
        elif 'IRRF,CP,CSLL-Retidos' in line or 'IRRF, CP, CSLL - Retidos' in line:
            if i + 1 < len(lines):
                valores_line = lines[i + 1]
                # Split por espaços
                partes = valores_line.split()
                
                # Primeira parte: IRRF,CP,CSLL-Retidos
                if len(partes) >= 1 and partes[0] != '-':
                    match = re.search(r'([\d.,]+)', partes[0])
                    if match:
                        total = _parse_decimal(match.group(1))
                        if total > 0:
                            data.irrf = total / 3
                            data.csll = total / 3
                            data.inss = total / 3
                
                # Segunda parte: PIS/COFINSRetidos
                if len(partes) >= 2 and partes[1] != '-':
                    match = re.search(r'([\d.,]+)', partes[1])
                    if match:
                        total = _parse_decimal(match.group(1))
                        if total > 0:
                            data.pis = total * Decimal("0.178")
                            data.cofins = total * Decimal("0.822")
                
                # Terceira parte: ValorLíquidodaNFS-e
                if len(partes) >= 3 and partes[2] != '-':
                    match = re.search(r'([\d.,]+)', partes[2])
                    if match:
                        data.valor_liquido = _parse_decimal(match.group(1))
        
        # ISSQNRetido na seção VALOR TOTAL (linha anterior)
        # Formato: ValordoServiço DescontoCondicionado DescontoIncondicionado ISSQNRetido
        # Valores:  R$3.450,00   R$                    R$                     -
        if 'ValordoServiço' in line and 'ISSQNRetido' in line:
            if i + 1 < len(lines):
                valores_line = lines[i + 1]
                # Split por espaços
                partes = valores_line.split()
                
                # Última parte é ISSQNRetido
                if partes:
                    iss_texto = partes[-1]
                    if iss_texto != '-':
                        # Tenta extrair valor
                        match = re.search(r'([\d.,]+)', iss_texto)
                        if match:
                            iss_val = _parse_decimal(match.group(1))
                            if iss_val > 0:
                                data.iss_valor = iss_val
                                data.iss_retido = "Sim"
        
        # Descrição do Serviço
        if 'DescriçãodoServiço' in line or 'Descrição do Serviço' in line:
            # Captura linhas seguintes até encontrar "TRIBUTAÇÃO"
            desc_lines = []
            for j in range(i + 1, min(i + 10, len(lines))):
                if 'TRIBUTAÇÃO' in lines[j]:
                    break
                desc_lines.append(lines[j].strip())
            if desc_lines:
                data.descricao_servico = '\n'.join(desc_lines)
        
        # Código de Tributação
        if 'CódigodeTributaçãoNacional' in line or 'Código de Tributação Nacional' in line:
            match = re.search(r'([\d\.]+)', line)
            if match:
                data.codigo_atividade = match.group(1)
    
    # Calcula base de cálculo se não informada
    if data.base_calculo == 0 and data.valor_servicos > 0:
        data.base_calculo = data.valor_servicos
    
    # Calcula valor líquido se não informado
    if data.valor_liquido == 0 and data.valor_servicos > 0:
        data.valor_liquido = data.valor_servicos - data.iss_valor - data.pis - data.cofins - data.irrf - data.csll - data.inss
    
    # Calcula total de tributos
    data.total_tributos_retidos = (
        data.iss_valor + data.pis + data.cofins + 
        data.csll + data.irrf + data.inss + data.outras_retencoes
    )
    
    return data
