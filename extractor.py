"""
Módulo de Extração de Dados de NFS-e
Suporta múltiplos padrões de layout municipal
"""

import re
import os
import pdfplumber
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from decimal import Decimal, InvalidOperation

# Importa extratores especializados
from extractor_matinhos import extract_matinhos


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


class NFSeExtractor:
    """Extrator inteligente de dados de NFS-e"""
    
    def __init__(self):
        self.patterns = {
            'matinhos': extract_matinhos,
            'duque_caxias': self._extract_duque_caxias,
            'danfse_v1': self._extract_danfse_v1,
            'generic': self._extract_generic
        }
    
    def extract_from_pdf(self, pdf_path: str) -> NFSeData:
        """
        Extrai dados de um PDF de NFS-e
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            NFSeData com os dados extraídos
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            
            # Detecta o padrão do layout
            pattern_type = self._detect_pattern(text)
            
            # Extrai usando o padrão detectado
            extractor_func = self.patterns.get(pattern_type, self.patterns['generic'])
            data = extractor_func(text)
            
            # Define metadados
            data.arquivo_origem = pdf_path.split('/')[-1]
            data.padrao_layout = pattern_type
            
            return data
            
        except Exception as e:
            filename = os.path.basename(pdf_path)
            raise Exception(f"Erro ao processar PDF {filename}: {str(e)}")
    
    def _detect_pattern(self, text: str) -> str:
        """
        Detecta o padrão de layout da NFS-e.
        
        Padrões suportados:
        - duque_caxias: ISSNet Online (Duque de Caxias)
        - danfse_v1: DANFSe v1.0 (Nacional - múltiplos municípios)
        - matinhos: NFS-e Matinhos/PR (layout próprio)
        - generic: Fallback genérico
        """
        text_lower = text.lower()
        
        # Matinhos/PR - Layout próprio
        if 'prefeitura municipal de matinhos' in text_lower:
            return 'matinhos'
        
        # Duque de Caxias - ISSNet Online (padrão específico)
        elif 'duque de caxias' in text_lower and 'issnetonline' in text_lower:
            return 'duque_caxias'
        
        # DANFSe v1.0 - Padrão Nacional (usado por vários municípios)
        elif 'danfse' in text_lower or 'danfse v1.0' in text_lower:
            return 'danfse_v1'
        
        # Fallback genérico
        else:
            return 'generic'
    
    def _extract_duque_caxias(self, text: str) -> NFSeData:
        """Extrai dados do padrão Duque de Caxias (ISSNet Online)"""
        data = NFSeData()
        
        # Número da nota
        match = re.search(r'Número da Nota Fiscal\s*(\d+)', text, re.IGNORECASE)
        if match:
            data.numero_nota = match.group(1)
        
        # Datas
        match = re.search(r'Data de Geração da NFS-e\s*(\d{2}/\d{2}/\d{4})', text)
        if match:
            data.data_emissao = match.group(1)
        
        match = re.search(r'Data de Competência\s*(\d{2}/\d{2}/\d{4})', text)
        if match:
            data.data_competencia = match.group(1)
        
        data.municipio = "Duque de Caxias - RJ"
        
        # Chave de acesso
        match = re.search(r'Chave de acesso.*?(\d{52})', text)
        if match:
            data.chave_acesso = match.group(1)
        
        # Prestador
        match = re.search(r'CPF/CNPJ\s*[:\s]*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', text)
        if match:
            data.prestador_cnpj = match.group(1)
        
        match = re.search(r'Dados do Prestador.*?(?:CPF/CNPJ.*?\n)?(.*?)\n.*?Estrada|Rua|Avenida', text, re.DOTALL)
        if match:
            data.prestador_nome = match.group(1).strip()
        
        match = re.search(r'Inscrição Municipal\s*(\d+)', text)
        if match:
            data.prestador_inscricao = match.group(1)
        
        # Tomador
        match = re.search(r'CNPJ/CPF\s*:\s*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', text)
        if match:
            data.tomador_cnpj = match.group(1)
        
        match = re.search(r'Razão Social\s*:\s*([A-Z\s]+)', text)
        if match:
            data.tomador_nome = match.group(1).strip()
        
        match = re.search(r'IM\s*:\s*(\d+)', text)
        if match:
            data.tomador_inscricao = match.group(1)
        
        # Valores (abordagem baseada em linhas para capturar colunas)
        lines = text.split('\n')
        for i, line in enumerate(lines):
            # Linha de cabeçalho dos valores
            if 'Vl. Total dos Serviços' in line and i + 1 < len(lines):
                valores_line = lines[i + 1]
                # Extrai todos os valores R$
                valores = re.findall(r'R\$\s*([\d.,]+)', valores_line)
                if len(valores) >= 4:
                    data.valor_servicos = self._parse_decimal(valores[0])  # Vl. Total dos Serviços
                    data.base_calculo = self._parse_decimal(valores[3])    # Base de Cálculo
                # Verifica se ISS foi retido
                if 'Sim' in valores_line:
                    data.iss_retido = "Sim"
                elif 'Não' in valores_line:
                    data.iss_retido = "Não"
                break
        
        match = re.search(r'Alíquota\s*([\d.,]+)', text)
        if match:
            data.iss_aliquota = self._parse_decimal(match.group(1))
        
        match = re.search(r'Total do ISSQN.*?R\$\s*([\d.,]+)', text)
        if match:
            data.iss_valor = self._parse_decimal(match.group(1))
        
        match = re.search(r'ISSQN Retido.*?(Sim|Não)', text, re.IGNORECASE)
        if match:
            data.iss_retido = match.group(1).capitalize()
        
        # Vl. ISSQN Retido e Vl. Líquido (linha de tributos)
        for i, line in enumerate(lines):
            if 'Vl. ISSQN Retido' in line and 'Vl. Líquido da Nota Fiscal' in line and i + 1 < len(lines):
                valores_line = lines[i + 1]
                # Extrai todos os valores R$
                valores = re.findall(r'R\$\s*([\d.,]+)', valores_line)
                if len(valores) >= 8:
                    data.pis = self._parse_decimal(valores[0])
                    data.cofins = self._parse_decimal(valores[1])
                    data.inss = self._parse_decimal(valores[2])
                    data.irrf = self._parse_decimal(valores[3])
                    data.csll = self._parse_decimal(valores[4])
                    data.outras_retencoes = self._parse_decimal(valores[5])
                    data.iss_valor = self._parse_decimal(valores[6])  # Vl. ISSQN Retido
                    data.valor_liquido = self._parse_decimal(valores[7])  # Vl. Líquido
                    
                    if data.iss_valor > 0:
                        data.iss_retido = "Sim"
                break
        
        # Município de retenção (sempre o tomador para Duque de Caxias)
        match = re.search(r'Município Incidência\s*([^\n]+)', text)
        if match and data.iss_retido == "Sim":
            data.municipio_retencao = match.group(1).strip()
        
        # Tributos federais e valor líquido já extraídos acima na linha de valores
        
        # Calcula total de tributos retidos
        data.total_tributos_retidos = (
            data.iss_valor + data.pis + data.cofins + 
            data.csll + data.irrf + data.inss + data.outras_retencoes
        )
        
        # Descrição do serviço
        match = re.search(r'Descrição dos Serviços\s*([^\n]+(?:\n[^\n]+){0,3})', text)
        if match:
            data.descricao_servico = match.group(1).strip()
        
        # Código de atividade
        match = re.search(r'Atividade do Município\s*(\d+)', text)
        if match:
            data.codigo_atividade = match.group(1)
        
        return data
    
    def _extract_danfse_v1(self, text: str) -> NFSeData:
        """Wrapper para função melhorada"""
        from extractor_danfse_v2 import extract_danfse_v1_improved
        return extract_danfse_v1_improved(text)
    

    def _extract_generic(self, text: str) -> NFSeData:
        """Extração genérica para padrões não identificados"""
        data = NFSeData()
        data.padrao_layout = "generic"
        
        # Tenta extrair informações básicas com regex genéricos
        # Número da nota
        for pattern in [r'n[úu]mero.*?(\d+)', r'nota.*?n[°º]?\s*(\d+)', r'nfs-?e.*?(\d+)']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data.numero_nota = match.group(1)
                break
        
        # CNPJ
        cnpjs = re.findall(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', text)
        if len(cnpjs) >= 1:
            data.prestador_cnpj = cnpjs[0]
        if len(cnpjs) >= 2:
            data.tomador_cnpj = cnpjs[1]
        
        # Valores em R$
        valores = re.findall(r'R\$\s*([\d.,]+)', text)
        if valores:
            # O primeiro valor grande geralmente é o valor dos serviços
            for valor in valores:
                val = self._parse_decimal(valor)
                if val > 100:  # Filtra valores pequenos
                    data.valor_servicos = val
                    break
        
        return data
    
    def _parse_decimal(self, value: str) -> Decimal:
        """
        Converte string monetária para Decimal.
        
        Args:
            value: String contendo valor monetário (ex: "1.234,56")
            
        Returns:
            Valor convertido para Decimal com 2 casas decimais
        """
        if not value or value == '-':
            return Decimal("0.00")
        
        # Remove pontos de milhar e substitui vírgula por ponto
        value = value.replace('.', '').replace(',', '.')
        
        try:
            return Decimal(value).quantize(Decimal("0.01"))
        except (ValueError, InvalidOperation):
            # Retorna zero se não conseguir converter
            return Decimal("0.00")
    
    def extract_batch(self, pdf_paths: List[str]) -> List[NFSeData]:
        """
        Extrai dados de múltiplos PDFs
        
        Args:
            pdf_paths: Lista de caminhos para arquivos PDF
            
        Returns:
            Lista de NFSeData extraídos
        """
        results = []
        for pdf_path in pdf_paths:
            try:
                data = self.extract_from_pdf(pdf_path)
                results.append(data)
            except Exception as e:
                print(f"Erro ao processar {pdf_path}: {str(e)}")
        
        return results
