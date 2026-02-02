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
            'duque_caxias': self._extract_duque_caxias,
            'rio_danfse': self._extract_rio_danfse,
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
        """Detecta o padrão de layout da NFS-e"""
        text_lower = text.lower()
        
        if 'duque de caxias' in text_lower and 'issnetonline' in text_lower:
            return 'duque_caxias'
        elif 'danfse' in text_lower and 'rio de janeiro' in text_lower:
            return 'rio_danfse'
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
        
        # Valores
        match = re.search(r'Vl\.?\s*Total dos Serviços.*?R\$\s*([\d.,]+)', text, re.DOTALL)
        if match:
            data.valor_servicos = self._parse_decimal(match.group(1))
        else:
            # Tenta padrão alternativo
            match = re.search(r'Valor.*?Servi[çc]os?.*?R?\$?\s*([\d.,]+)', text, re.IGNORECASE)
            if match:
                data.valor_servicos = self._parse_decimal(match.group(1))
        
        match = re.search(r'Base de Cálculo.*?R\$\s*([\d.,]+)', text)
        if match:
            data.base_calculo = self._parse_decimal(match.group(1))
        
        match = re.search(r'Alíquota\s*([\d.,]+)', text)
        if match:
            data.iss_aliquota = self._parse_decimal(match.group(1))
        
        match = re.search(r'Total do ISSQN.*?R\$\s*([\d.,]+)', text)
        if match:
            data.iss_valor = self._parse_decimal(match.group(1))
        
        match = re.search(r'ISSQN Retido.*?(Sim|Não)', text, re.IGNORECASE)
        if match:
            data.iss_retido = match.group(1).capitalize()
        
        match = re.search(r'Vl\.\s*ISSQN Retido.*?R\$\s*([\d.,]+)', text)
        if match:
            iss_retido_valor = self._parse_decimal(match.group(1))
            if iss_retido_valor > 0:
                data.iss_retido = "Sim"
                data.iss_valor = iss_retido_valor
        
        # Município de retenção (sempre o tomador para Duque de Caxias)
        match = re.search(r'Município Incidência\s*([^\n]+)', text)
        if match and data.iss_retido == "Sim":
            data.municipio_retencao = match.group(1).strip()
        
        # Tributos federais
        match = re.search(r'PIS.*?R\$\s*([\d.,]+)', text)
        if match:
            data.pis = self._parse_decimal(match.group(1))
        
        match = re.search(r'COFINS.*?R\$\s*([\d.,]+)', text)
        if match:
            data.cofins = self._parse_decimal(match.group(1))
        
        match = re.search(r'CSLL.*?R\$\s*([\d.,]+)', text)
        if match:
            data.csll = self._parse_decimal(match.group(1))
        
        match = re.search(r'IRRF.*?R\$\s*([\d.,]+)', text)
        if match:
            data.irrf = self._parse_decimal(match.group(1))
        
        match = re.search(r'INSS.*?R\$\s*([\d.,]+)', text)
        if match:
            data.inss = self._parse_decimal(match.group(1))
        
        match = re.search(r'Outras Retenções.*?R\$\s*([\d.,]+)', text)
        if match:
            data.outras_retencoes = self._parse_decimal(match.group(1))
        
        # Valor líquido
        match = re.search(r'Vl\.\s*Líquido da Nota Fiscal\s*R\$\s*([\d.,]+)', text)
        if match:
            data.valor_liquido = self._parse_decimal(match.group(1))
        
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
    
    def _extract_rio_danfse(self, text: str) -> NFSeData:
        """Extrai dados do padrão Rio de Janeiro (DANFSe Nacional)"""
        data = NFSeData()
        
        # Número da nota
        match = re.search(r'Número da NFS-e\s*(\d+)', text, re.IGNORECASE)
        if match:
            data.numero_nota = match.group(1)
        
        # Datas
        match = re.search(r'Data e Hora da emiss[ãa]o da NFS-e\s*(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
        if match:
            data.data_emissao = match.group(1)
        else:
            # Tenta capturar apenas data sem hora
            match = re.search(r'emiss[ãa]o.*?(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
            if match:
                data.data_emissao = match.group(1)
        
        match = re.search(r'Competência da NFS-e\s*(\d{2}/\d{2}/\d{4})', text)
        if match:
            data.data_competencia = match.group(1)
        
        data.municipio = "Rio de Janeiro - RJ"
        
        # Chave de acesso
        match = re.search(r'Chave de Acesso da NFS-e\s*(\d+)', text)
        if match:
            data.chave_acesso = match.group(1)
        
        # Prestador
        match = re.search(r'EMITENTE.*?CNPJ.*?(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', text, re.DOTALL)
        if match:
            data.prestador_cnpj = match.group(1)
        
        match = re.search(r'Nome / Nome Empresarial\s*(?:\d+\.\d+\.\d+\s+)?([A-Z\s]+)', text)
        if match:
            data.prestador_nome = match.group(1).strip()
        
        # Tomador
        match = re.search(r'TOMADOR.*?CNPJ.*?(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', text, re.DOTALL)
        if match:
            data.tomador_cnpj = match.group(1)
        
        match = re.search(r'TOMADOR.*?Nome.*?([A-Z\s]+?)(?:\n|E-mail)', text, re.DOTALL)
        if match:
            nome = match.group(1).strip()
            # Remove números do CNPJ que podem vir junto
            nome = re.sub(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', '', nome).strip()
            data.tomador_nome = nome
        
        # Valores
        match = re.search(r'Valor do Serviço\s*R\$\s*([\d.,]+)', text)
        if match:
            data.valor_servicos = self._parse_decimal(match.group(1))
            data.base_calculo = data.valor_servicos  # Para MEI geralmente é o mesmo
        
        # ISS
        match = re.search(r'Retenção do ISSQN\s*(Não Retido|Retido)', text)
        if match:
            data.iss_retido = "Sim" if "Retido" in match.group(1) and "Não" not in match.group(1) else "Não"
        
        match = re.search(r'ISSQN Retido.*?R\$\s*([\d.,]+)', text)
        if match:
            data.iss_valor = self._parse_decimal(match.group(1))
            if data.iss_valor > 0:
                data.iss_retido = "Sim"
        
        match = re.search(r'Município de Incidência do ISSQN\s*([^\n]+)', text)
        if match and data.iss_retido == "Sim":
            data.municipio_retencao = match.group(1).strip()
        
        # Tributos federais (geralmente zero para MEI)
        match = re.search(r'IRRF.*?R\$\s*([\d.,]+)', text)
        if match:
            data.irrf = self._parse_decimal(match.group(1))
        
        match = re.search(r'PIS.*?R\$\s*([\d.,]+)', text)
        if match:
            data.pis = self._parse_decimal(match.group(1))
        
        match = re.search(r'COFINS.*?R\$\s*([\d.,]+)', text)
        if match:
            data.cofins = self._parse_decimal(match.group(1))
        
        match = re.search(r'CSLL.*?R\$\s*([\d.,]+)', text)
        if match:
            data.csll = self._parse_decimal(match.group(1))
        
        # Valor líquido
        match = re.search(r'Valor Líquido da NFS-e\s*R\$\s*([\d.,]+)', text)
        if match:
            data.valor_liquido = self._parse_decimal(match.group(1))
        
        # Calcula total de tributos
        data.total_tributos_retidos = (
            data.iss_valor + data.pis + data.cofins + 
            data.csll + data.irrf + data.inss + data.outras_retencoes
        )
        
        # Descrição do serviço
        match = re.search(r'Descrição do Serviço\s*([^\n]+(?:\n[^\n]+){0,5}?)(?:\n\n|TRIBUTAÇÃO)', text, re.DOTALL)
        if match:
            data.descricao_servico = match.group(1).strip()
        
        # Código de atividade
        match = re.search(r'Código de Tributação Nacional\s*([^\n]+)', text)
        if match:
            data.codigo_atividade = match.group(1)
        
        return data
    
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
