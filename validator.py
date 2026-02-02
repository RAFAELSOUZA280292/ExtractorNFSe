"""
Módulo de Validação de Dados Fiscais
Valida cálculos, alíquotas e consistência das informações
"""

from typing import List, Dict, Tuple
from decimal import Decimal
from dataclasses import dataclass
from extractor import NFSeData


@dataclass
class ValidationIssue:
    """Representa um problema de validação"""
    severity: str  # 'ERROR', 'WARNING', 'INFO'
    field: str
    message: str
    expected: str = ""
    actual: str = ""


class NFSeValidator:
    """Validador de dados de NFS-e"""
    
    # Alíquotas de ISS por município (exemplos - expandir conforme necessário)
    ISS_ALIQUOTAS = {
        'Rio de Janeiro': {'min': 2.0, 'max': 5.0},
        'Duque de Caxias': {'min': 2.0, 'max': 5.0},
        'default': {'min': 2.0, 'max': 5.0}
    }
    
    # Alíquotas federais
    PIS_ALIQUOTA = Decimal("0.65")  # 0.65%
    COFINS_ALIQUOTA = Decimal("3.00")  # 3.00%
    CSLL_ALIQUOTA = Decimal("1.00")  # 1.00%
    IRRF_ALIQUOTA = Decimal("1.50")  # 1.50%
    
    def __init__(self):
        self.tolerance = Decimal("0.02")  # Tolerância de 2 centavos para arredondamentos
    
    def validate(self, data: NFSeData) -> List[ValidationIssue]:
        """
        Valida os dados de uma NFS-e
        
        Args:
            data: Dados da NFS-e a validar
            
        Returns:
            Lista de problemas encontrados
        """
        issues = []
        
        # Validações obrigatórias
        issues.extend(self._validate_required_fields(data))
        
        # Validações de cálculo
        issues.extend(self._validate_calculations(data))
        
        # Validações de alíquotas
        issues.extend(self._validate_tax_rates(data))
        
        # Validações de consistência
        issues.extend(self._validate_consistency(data))
        
        return issues
    
    def _validate_required_fields(self, data: NFSeData) -> List[ValidationIssue]:
        """Valida campos obrigatórios"""
        issues = []
        
        required_fields = {
            'numero_nota': 'Número da Nota',
            'data_emissao': 'Data de Emissão',
            'prestador_cnpj': 'CNPJ do Prestador',
            'tomador_cnpj': 'CNPJ do Tomador',
            'valor_servicos': 'Valor dos Serviços'
        }
        
        for field, label in required_fields.items():
            value = getattr(data, field)
            if not value or (isinstance(value, Decimal) and value == 0):
                issues.append(ValidationIssue(
                    severity='ERROR',
                    field=field,
                    message=f'{label} não informado ou inválido'
                ))
        
        return issues
    
    def _validate_calculations(self, data: NFSeData) -> List[ValidationIssue]:
        """Valida cálculos de impostos"""
        issues = []
        
        # Valida cálculo do ISS
        if data.base_calculo > 0 and data.iss_aliquota > 0:
            iss_calculado = (data.base_calculo * data.iss_aliquota / 100).quantize(Decimal("0.01"))
            
            if abs(data.iss_valor - iss_calculado) > self.tolerance:
                issues.append(ValidationIssue(
                    severity='ERROR',
                    field='iss_valor',
                    message='Valor do ISS não corresponde ao cálculo (Base x Alíquota)',
                    expected=f'R$ {iss_calculado}',
                    actual=f'R$ {data.iss_valor}'
                ))
        
        # Valida total de tributos retidos
        total_calculado = (
            data.iss_valor + data.pis + data.cofins + 
            data.csll + data.irrf + data.inss + data.outras_retencoes
        )
        
        if abs(data.total_tributos_retidos - total_calculado) > self.tolerance:
            issues.append(ValidationIssue(
                severity='WARNING',
                field='total_tributos_retidos',
                message='Total de tributos retidos diverge da soma individual',
                expected=f'R$ {total_calculado}',
                actual=f'R$ {data.total_tributos_retidos}'
            ))
        
        # Valida valor líquido
        if data.valor_servicos > 0:
            liquido_calculado = (data.valor_servicos - data.valor_desconto - total_calculado).quantize(Decimal("0.01"))
            
            if abs(data.valor_liquido - liquido_calculado) > self.tolerance:
                issues.append(ValidationIssue(
                    severity='WARNING',
                    field='valor_liquido',
                    message='Valor líquido diverge do cálculo (Serviços - Descontos - Tributos)',
                    expected=f'R$ {liquido_calculado}',
                    actual=f'R$ {data.valor_liquido}'
                ))
        
        return issues
    
    def _validate_tax_rates(self, data: NFSeData) -> List[ValidationIssue]:
        """Valida alíquotas de impostos"""
        issues = []
        
        # Valida alíquota de ISS
        if data.iss_aliquota > 0:
            municipio_key = data.municipio.split(' - ')[0] if ' - ' in data.municipio else 'default'
            aliquotas = self.ISS_ALIQUOTAS.get(municipio_key, self.ISS_ALIQUOTAS['default'])
            
            if data.iss_aliquota < Decimal(str(aliquotas['min'])) or data.iss_aliquota > Decimal(str(aliquotas['max'])):
                issues.append(ValidationIssue(
                    severity='WARNING',
                    field='iss_aliquota',
                    message=f'Alíquota de ISS fora da faixa usual para {municipio_key}',
                    expected=f'{aliquotas["min"]}% a {aliquotas["max"]}%',
                    actual=f'{data.iss_aliquota}%'
                ))
        
        # Valida cálculo de PIS (se informado)
        if data.pis > 0 and data.base_calculo > 0:
            pis_esperado = (data.base_calculo * self.PIS_ALIQUOTA / 100).quantize(Decimal("0.01"))
            if abs(data.pis - pis_esperado) > self.tolerance:
                issues.append(ValidationIssue(
                    severity='INFO',
                    field='pis',
                    message='Valor de PIS não corresponde à alíquota padrão de 0.65%',
                    expected=f'R$ {pis_esperado}',
                    actual=f'R$ {data.pis}'
                ))
        
        # Valida cálculo de COFINS (se informado)
        if data.cofins > 0 and data.base_calculo > 0:
            cofins_esperado = (data.base_calculo * self.COFINS_ALIQUOTA / 100).quantize(Decimal("0.01"))
            if abs(data.cofins - cofins_esperado) > self.tolerance:
                issues.append(ValidationIssue(
                    severity='INFO',
                    field='cofins',
                    message='Valor de COFINS não corresponde à alíquota padrão de 3.00%',
                    expected=f'R$ {cofins_esperado}',
                    actual=f'R$ {data.cofins}'
                ))
        
        return issues
    
    def _validate_consistency(self, data: NFSeData) -> List[ValidationIssue]:
        """Valida consistência dos dados"""
        issues = []
        
        # Valida CNPJ
        if data.prestador_cnpj and not self._validate_cnpj_format(data.prestador_cnpj):
            issues.append(ValidationIssue(
                severity='WARNING',
                field='prestador_cnpj',
                message='Formato de CNPJ do prestador pode estar inválido'
            ))
        
        if data.tomador_cnpj and not self._validate_cnpj_format(data.tomador_cnpj):
            issues.append(ValidationIssue(
                severity='WARNING',
                field='tomador_cnpj',
                message='Formato de CNPJ do tomador pode estar inválido'
            ))
        
        # Valida data de competência
        if data.data_emissao and data.data_competencia:
            try:
                emissao = self._parse_date(data.data_emissao)
                competencia = self._parse_date(data.data_competencia)
                
                if emissao < competencia:
                    issues.append(ValidationIssue(
                        severity='WARNING',
                        field='data_competencia',
                        message='Data de emissão anterior à data de competência'
                    ))
            except:
                pass
        
        # Valida retenção de ISS
        if data.iss_retido == "Sim":
            if data.iss_valor == 0:
                issues.append(ValidationIssue(
                    severity='ERROR',
                    field='iss_valor',
                    message='ISS marcado como retido mas valor não informado'
                ))
            
            if not data.municipio_retencao:
                issues.append(ValidationIssue(
                    severity='WARNING',
                    field='municipio_retencao',
                    message='ISS retido mas município de retenção não informado'
                ))
        
        # Valida se há impostos zerados quando deveria haver retenção
        if data.valor_servicos > 0 and data.base_calculo > 0:
            if data.iss_valor == 0 and data.iss_retido != "Sim":
                issues.append(ValidationIssue(
                    severity='INFO',
                    field='iss_valor',
                    message='ISS não calculado - verifique se é MEI ou imune'
                ))
        
        return issues
    
    def _validate_cnpj_format(self, cnpj: str) -> bool:
        """Valida formato básico de CNPJ"""
        # Remove pontuação
        cnpj_numbers = ''.join(filter(str.isdigit, cnpj))
        return len(cnpj_numbers) == 14
    
    def _parse_date(self, date_str: str) -> tuple:
        """Converte string de data para tupla (ano, mês, dia)"""
        parts = date_str.split('/')
        if len(parts) == 3:
            return (int(parts[2]), int(parts[1]), int(parts[0]))
        return (0, 0, 0)
    
    def generate_validation_report(self, issues: List[ValidationIssue]) -> str:
        """
        Gera relatório textual de validação
        
        Args:
            issues: Lista de problemas encontrados
            
        Returns:
            Relatório formatado
        """
        if not issues:
            return "✅ Nenhum problema encontrado"
        
        report = []
        
        errors = [i for i in issues if i.severity == 'ERROR']
        warnings = [i for i in issues if i.severity == 'WARNING']
        infos = [i for i in issues if i.severity == 'INFO']
        
        if errors:
            report.append("🔴 ERROS:")
            for issue in errors:
                report.append(f"  • {issue.message}")
                if issue.expected:
                    report.append(f"    Esperado: {issue.expected} | Encontrado: {issue.actual}")
        
        if warnings:
            report.append("\n⚠️  AVISOS:")
            for issue in warnings:
                report.append(f"  • {issue.message}")
                if issue.expected:
                    report.append(f"    Esperado: {issue.expected} | Encontrado: {issue.actual}")
        
        if infos:
            report.append("\nℹ️  INFORMAÇÕES:")
            for issue in infos:
                report.append(f"  • {issue.message}")
                if issue.expected:
                    report.append(f"    Esperado: {issue.expected} | Encontrado: {issue.actual}")
        
        return "\n".join(report)
    
    def get_validation_status(self, issues: List[ValidationIssue]) -> str:
        """Retorna status geral da validação"""
        if not issues:
            return "✅ Validado"
        
        errors = [i for i in issues if i.severity == 'ERROR']
        warnings = [i for i in issues if i.severity == 'WARNING']
        
        if errors:
            return f"❌ {len(errors)} erro(s)"
        elif warnings:
            return f"⚠️ {len(warnings)} aviso(s)"
        else:
            return "ℹ️ Com observações"
