"""
Extrator para NFS-e de Matinhos/PR
Layout específico da Prefeitura Municipal de Matinhos
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
    if not value or value == '-' or value.strip() == '' or value == 'SIMPLES NACIONAL':
        return Decimal("0.00")
    
    # Remove pontos de milhar e substitui vírgula por ponto
    value = value.replace('.', '').replace(',', '.')
    
    try:
        return Decimal(value).quantize(Decimal("0.01"))
    except (ValueError, InvalidOperation):
        return Decimal("0.00")


def extract_matinhos(text: str) -> NFSeData:
    """
    Extrai dados do padrão NFS-e Matinhos/PR
    
    Características:
    - Layout próprio da Prefeitura Municipal de Matinhos
    - Cabeçalho com dados do prestador
    - Campos: Número RPS, Série RPS, Situação, Tipo
    - Códigos de serviço específicos
    - Local de Prestação com código numérico
    - Situação Tributária: TIST, TI
    - ISSRF (ISS Retido na Fonte)
    """
    data = NFSeData()
    data.padrao_layout = "matinhos"
    data.municipio = "Matinhos - PR"
    
    lines = text.split('\n')
    
    # Processa linha por linha
    for i, line in enumerate(lines):
        line_clean = line.strip()
        
        # Número da NFS-e
        if 'Número da NFS-e' in line:
            if i + 1 < len(lines):
                match = re.search(r'(\d+)', lines[i + 1])
                if match:
                    data.numero_nota = match.group(1)
        
        # Situação
        if 'Situação' in line and 'Emitida' in ''.join(lines[i:i+3]):
            # Situação pode ser: Emitida, Preenchido, Importado, etc
            pass  # Não precisamos armazenar por enquanto
        
        # Número RPS e Série RPS
        if 'Número RPS:' in line:
            match = re.search(r'Número RPS:\s*(\d+)', line)
            if match:
                # Podemos armazenar em metadados se necessário
                pass
        
        # Data Fato Gerador e Data/Hora Emissão
        if 'Data Fato Gerador' in line:
            if i + 1 < len(lines):
                match = re.search(r'(\d{2}/\d{2}/\d{4})', lines[i + 1])
                if match:
                    data.data_competencia = match.group(1)
        
        if 'Data/Hora Emissão' in line or 'Data e Hora Emissão' in line:
            if i + 1 < len(lines):
                match = re.search(r'(\d{2}/\d{2}/\d{4})', lines[i + 1])
                if match:
                    data.data_emissao = match.group(1)
        
        # Prestador - CNPJ (no cabeçalho)
        if 'CNPJ:' in line and i < 10:  # Primeiras linhas
            match = re.search(r'CNPJ:\s*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', line)
            if match:
                data.prestador_cnpj = match.group(1)
        
        # Prestador - Nome (linha após CNPJ no cabeçalho)
        if data.prestador_cnpj and not data.prestador_nome:
            # Procura nome nas primeiras linhas
            for j in range(max(0, i-5), min(i+5, len(lines))):
                if 'CNPJ' not in lines[j] and 'CEP' not in lines[j] and 'Município' not in lines[j]:
                    nome_line = lines[j].strip()
                    if len(nome_line) > 5 and not nome_line.isdigit():
                        # Remove caracteres especiais
                        nome_clean = re.sub(r'[*]+', '', nome_line)
                        if nome_clean and len(nome_clean) > 3:
                            data.prestador_nome = nome_clean
                            break
        
        # Insc. Municipal (prestador)
        if 'Insc. Municipal:' in line and i < 15:
            match = re.search(r'Insc\. Municipal:\s*(\d+)', line)
            if match:
                data.prestador_inscricao = match.group(1)
        
        # Tomador - CNPJ/CPF
        if 'CPF/CNPJ' in line and 'TOMADOR' in ''.join(lines[max(0, i-5):i+1]):
            if i + 1 < len(lines):
                match = re.search(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', lines[i + 1])
                if match:
                    data.tomador_cnpj = match.group(1)
        
        # Tomador - Nome/Razão Social
        if 'Nome/Razão Social' in line:
            if i + 1 < len(lines):
                nome = lines[i + 1].strip()
                if nome and nome != '-':
                    data.tomador_nome = nome
        
        # Serviço - Código
        if 'Serviço' in line and i + 1 < len(lines):
            match = re.search(r'(\d+)', lines[i + 1])
            if match:
                data.codigo_atividade = match.group(1)
        
        # Valor Serviço (cabeçalho na linha atual, valores na próxima)
        if 'Valor Serviço' in line or 'Valor Servico' in line:
            # Verifica se é a linha de cabeçalho (tem "Serviço" e "Local")
            if 'Serviço' in line and 'Local' in line and i + 1 < len(lines):
                # Processa a próxima linha com os valores
                valores_line = lines[i + 1]
                valores = re.findall(r'([\d.,]+)', valores_line)
                if len(valores) >= 4:
                    # Formato: Serviço Local Alíquota Situação Valor Desc Dedução ValorISS
                    # Exemplo: 702 7963 2.0939% TIST 18.000,00 0,00 0,00 376,90
                    # Prioriza valores com vírgula (formato monetário brasileiro)
                    valores_com_virgula = [v for v in valores if ',' in v]
                    if valores_com_virgula:
                        # Pega o primeiro valor com vírgula que seja > 100
                        for v in valores_com_virgula:
                            val = _parse_decimal(v)
                            if val > 100:
                                data.valor_servicos = val
                                # O último valor com vírgula é o Valor ISS
                                if len(valores_com_virgula) > 1:
                                    data.iss_valor = _parse_decimal(valores_com_virgula[-1])
                                break
            else:
                # Linha única com valor
                valores = re.findall(r'([\d.,]+)', line)
                if len(valores) == 1:
                    data.valor_servicos = _parse_decimal(valores[0])
        
        # Valor ISS (pode estar na mesma linha que Valor Serviço)
        if 'Valor ISS' in line:
            valores = re.findall(r'([\d.,]+)', line)
            if len(valores) >= 4:  # Linha com múltiplos valores
                # Prioriza valores com vírgula
                valores_com_virgula = [v for v in valores if ',' in v]
                if valores_com_virgula:
                    # O último valor com vírgula é geralmente o Valor ISS
                    data.iss_valor = _parse_decimal(valores_com_virgula[-1])
                else:
                    data.iss_valor = _parse_decimal(valores[-1])
            elif len(valores) == 1 and 'SIMPLES' not in line:
                data.iss_valor = _parse_decimal(valores[0])
        
        # Alíquota
        if 'Alíquota' in line and 'Situação' not in line:
            match = re.search(r'([\d.,]+)%?', line)
            if match and 'SIMPLES' not in line:
                data.iss_aliquota = _parse_decimal(match.group(1))
        
        # Valor Total
        if 'Valor Total' in line:
            match = re.search(r'([\d.,]+)', line)
            if match:
                valor_total = _parse_decimal(match.group(1))
                if valor_total > 0:
                    data.valor_servicos = valor_total
        
        # ISSRF (ISS Retido na Fonte) - linha separada
        if line.strip() == 'ISSRF' or re.match(r'^ISSRF\s', line):
            # Procura valor na mesma linha ou próxima
            valores = re.findall(r'([\d.,]+)', line)
            if valores:
                issrf = _parse_decimal(valores[0])
                if issrf > 0:
                    data.iss_valor = issrf
                    data.iss_retido = "Sim"
            elif i + 1 < len(lines):
                match = re.search(r'([\d.,]+)', lines[i + 1])
                if match:
                    issrf = _parse_decimal(match.group(1))
                    if issrf > 0:
                        data.iss_valor = issrf
                        data.iss_retido = "Sim"
        
        # INSS
        if line.strip() == 'INSS' or 'INSS' in line:
            if i + 1 < len(lines):
                match = re.search(r'([\d.,]+)', lines[i + 1])
                if match:
                    data.inss = _parse_decimal(match.group(1))
            else:
                match = re.search(r'INSS\s+([\d.,]+)', line)
                if match:
                    data.inss = _parse_decimal(match.group(1))
        
        # IR (IRRF)
        if line.strip() == 'IR' or re.match(r'^IR\s', line):
            if i + 1 < len(lines):
                match = re.search(r'([\d.,]+)', lines[i + 1])
                if match:
                    data.irrf = _parse_decimal(match.group(1))
            else:
                match = re.search(r'IR\s+([\d.,]+)', line)
                if match:
                    data.irrf = _parse_decimal(match.group(1))
        
        # CSLL
        if line.strip() == 'CSLL' or 'CSLL' in line:
            if i + 1 < len(lines):
                match = re.search(r'([\d.,]+)', lines[i + 1])
                if match:
                    data.csll = _parse_decimal(match.group(1))
            else:
                match = re.search(r'CSLL\s+([\d.,]+)', line)
                if match:
                    data.csll = _parse_decimal(match.group(1))
        
        # COFINS
        if line.strip() == 'COFINS' or 'COFINS' in line:
            if i + 1 < len(lines):
                match = re.search(r'([\d.,]+)', lines[i + 1])
                if match:
                    data.cofins = _parse_decimal(match.group(1))
            else:
                match = re.search(r'COFINS\s+([\d.,]+)', line)
                if match:
                    data.cofins = _parse_decimal(match.group(1))
        
        # PIS
        if line.strip() == 'PIS' or re.match(r'^PIS\s', line):
            if i + 1 < len(lines):
                match = re.search(r'([\d.,]+)', lines[i + 1])
                if match:
                    data.pis = _parse_decimal(match.group(1))
            else:
                match = re.search(r'PIS\s+([\d.,]+)', line)
                if match:
                    data.pis = _parse_decimal(match.group(1))
        
        # Valor Líquido
        if 'Valor Líquido' in line or 'Valor Liquido' in line:
            match = re.search(r'([\d.,]+)', line)
            if match:
                data.valor_liquido = _parse_decimal(match.group(1))
        
        # Descrição do Serviço
        if 'Descrição do Serviço' in line or 'Descrição de Serviço' in line:
            if i + 1 < len(lines):
                desc_lines = []
                for j in range(i + 1, min(i + 5, len(lines))):
                    if 'Valor Total' in lines[j] or 'ISSRF' in lines[j]:
                        break
                    desc_lines.append(lines[j].strip())
                if desc_lines:
                    data.descricao_servico = ' '.join(desc_lines)
    
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
