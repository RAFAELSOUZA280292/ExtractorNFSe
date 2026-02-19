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
        
        # Número da NFS-e (pode estar na mesma linha ou próxima)
        if 'Número da NFS-e' in line:
            # Tenta extrair da mesma linha primeiro
            match = re.search(r'Número da NFS-e\s+(\d+)', line)
            if match:
                data.numero_nota = match.group(1)
            # Se não encontrou, procura na próxima linha
            # Evita pegar número de endereço (precedido por "-")
            elif i + 1 < len(lines):
                # Procura números isolados (não precedidos por "-" ou ",")
                match = re.search(r'(?<![-,])\s+(\d{1,5})(?=\s|$)', lines[i + 1])
                if match:
                    data.numero_nota = match.group(1)
                # Fallback: pega o último número da linha (geralmente é o correto)
                else:
                    numeros = re.findall(r'\b(\d{1,5})\b', lines[i + 1])
                    if numeros:
                        data.numero_nota = numeros[-1]
        
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
        
        # Linha com Valor Total Desc. Incondicional Dedução Base de Cálculo ISSQN (layout novo)
        # Exemplo: 7.000,00 0,00 0,00 7.000,00 0,00
        if 'Valor Total' in line and 'Base de Cálculo' in line and 'ISSQN' in line:
            # Cabeçalho, valores estão na próxima linha
            if i + 1 < len(lines):
                valores = re.findall(r'([\d.,]+)', lines[i + 1])
                if len(valores) >= 5:
                    # Ordem: Valor Total, Desc. Incond., Dedução, Base Cálculo, ISSQN
                    data.valor_servicos = _parse_decimal(valores[0])
                    # Desc. Incondicional (valores[1]) - pode ser armazenado se necessário
                    # Dedução (valores[2])
                    data.base_calculo = _parse_decimal(valores[3])
                    # ISSQN (valores[4]) - geralmente 0 quando há ISSRF
        
        # Valor Total (layout antigo)
        elif 'Valor Total' in line:
            match = re.search(r'([\d.,]+)', line)
            if match:
                valor_total = _parse_decimal(match.group(1))
                if valor_total > 0:
                    data.valor_servicos = valor_total
        
        # Linha com ISSRF IR INSS CSLL COFINS (layout novo)
        # Exemplo: 350,00 0,00 770,00 0,00 0,00
        if 'ISSRF' in line and 'IR' in line and 'INSS' in line and 'CSLL' in line and 'COFINS' in line:
            # Cabeçalho, valores estão na próxima linha
            if i + 1 < len(lines):
                valores = re.findall(r'([\d.,]+)', lines[i + 1])
                if len(valores) >= 5:
                    # Ordem: ISSRF, IR, INSS, CSLL, COFINS
                    data.iss_valor = _parse_decimal(valores[0])
                    if data.iss_valor > 0:
                        data.iss_retido = "Sim"
                    data.irrf = _parse_decimal(valores[1])
                    data.inss = _parse_decimal(valores[2])
                    data.csll = _parse_decimal(valores[3])
                    data.cofins = _parse_decimal(valores[4])
        
        # ISSRF (ISS Retido na Fonte) - linha separada (layout antigo)
        elif line.strip() == 'ISSRF' or re.match(r'^ISSRF\s', line):
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
        
        # INSS (layout antigo - evita cabeçalho e CEI)
        if (line.strip() == 'INSS' or ('INSS' in line and 'ISSRF' not in line and 'IR' not in line and 'CEI' not in line and 'Cadastro' not in line)):
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
        
        # CSLL (layout antigo - evita cabeçalho)
        if (line.strip() == 'CSLL' or ('CSLL' in line and 'ISSRF' not in line and 'COFINS' not in line)):
            if i + 1 < len(lines):
                match = re.search(r'([\d.,]+)', lines[i + 1])
                if match:
                    data.csll = _parse_decimal(match.group(1))
            else:
                match = re.search(r'CSLL\s+([\d.,]+)', line)
                if match:
                    data.csll = _parse_decimal(match.group(1))
        
        # COFINS (layout antigo - evita cabeçalho)
        if (line.strip() == 'COFINS' or ('COFINS' in line and 'ISSRF' not in line and 'CSLL' not in line)):
            if i + 1 < len(lines):
                match = re.search(r'([\d.,]+)', lines[i + 1])
                if match:
                    data.cofins = _parse_decimal(match.group(1))
            else:
                match = re.search(r'COFINS\s+([\d.,]+)', line)
                if match:
                    data.cofins = _parse_decimal(match.group(1))
        
        # Linha com PIS Outras Retenções Total Trib. Federais Desc. Condicional Valor Líquido (layout novo)
        # Exemplo: 0,00 0,00 770,00 0,00 5.880,00
        if 'PIS' in line and 'Outras Retenções' in line and 'Total Trib. Federais' in line and 'Valor Líquido' in line:
            # Cabeçalho, valores estão na próxima linha
            if i + 1 < len(lines):
                valores = re.findall(r'([\d.,]+)', lines[i + 1])
                if len(valores) >= 5:
                    # Ordem: PIS, Outras Ret., Total Trib. Fed., Desc. Cond., Valor Líquido
                    data.pis = _parse_decimal(valores[0])
                    data.outras_retencoes = _parse_decimal(valores[1])
                    # Total Trib. Federais (valores[2]) - não armazenamos separadamente
                    # Desc. Condicional (valores[3]) - não armazenamos
                    data.valor_liquido = _parse_decimal(valores[4])
        
        # PIS (layout antigo)
        elif line.strip() == 'PIS' or re.match(r'^PIS\s', line):
            if i + 1 < len(lines):
                match = re.search(r'([\d.,]+)', lines[i + 1])
                if match:
                    data.pis = _parse_decimal(match.group(1))
            else:
                match = re.search(r'PIS\s+([\d.,]+)', line)
                if match:
                    data.pis = _parse_decimal(match.group(1))
        
        # Valor Líquido (layout antigo)
        elif 'Valor Líquido' in line or 'Valor Liquido' in line:
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
