"""
Extrator e Consolidador de NFS-e
Script principal para processar múltiplos PDFs de notas fiscais
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List
from extractor import NFSeExtractor
from validator import NFSeValidator
from consolidator import NFSeConsolidator


def find_pdf_files(directory: str) -> List[str]:
    """Encontra todos os arquivos PDF em um diretório"""
    pdf_files = []
    path = Path(directory)
    
    if path.is_file() and path.suffix.lower() == '.pdf':
        return [str(path)]
    
    if path.is_dir():
        for pdf_file in path.rglob('*.pdf'):
            pdf_files.append(str(pdf_file))
    
    return sorted(pdf_files)


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Extrator e Validador de Notas Fiscais de Serviço Eletrônicas (NFS-e)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  
  # Processar um único PDF
  python main.py nota.pdf -o relatorio.xlsx
  
  # Processar todos os PDFs de uma pasta
  python main.py ./notas_fiscais/ -o consolidado.xlsx
  
  # Processar sem validação
  python main.py ./notas/ -o resultado.xlsx --no-validation
  
  # Modo verboso
  python main.py ./notas/ -o saida.xlsx -v
        """
    )
    
    parser.add_argument(
        'input',
        help='Arquivo PDF ou diretório com PDFs de NFS-e'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='nfse_consolidado.xlsx',
        help='Arquivo Excel de saída (padrão: nfse_consolidado.xlsx)'
    )
    
    parser.add_argument(
        '--no-validation',
        action='store_true',
        help='Desabilita a validação de dados'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Modo verboso (exibe detalhes do processamento)'
    )
    
    args = parser.parse_args()
    
    # Banner
    print("="*70)
    print(" "*15 + "EXTRATOR DE NFS-e - Brasil")
    print(" "*10 + "Validação e Consolidação de Notas Fiscais")
    print("="*70)
    print()
    
    # Encontra arquivos PDF
    print(f"🔍 Buscando arquivos PDF em: {args.input}")
    pdf_files = find_pdf_files(args.input)
    
    if not pdf_files:
        print("❌ Nenhum arquivo PDF encontrado!")
        sys.exit(1)
    
    print(f"✅ Encontrados {len(pdf_files)} arquivo(s) PDF\n")
    
    # Inicializa extrator
    extractor = NFSeExtractor()
    validator = NFSeValidator()
    consolidator = NFSeConsolidator()
    
    # Processa cada PDF
    print("📄 Extraindo dados das notas fiscais...")
    extracted_data = []
    errors = []
    
    for i, pdf_path in enumerate(pdf_files, 1):
        filename = os.path.basename(pdf_path)
        
        try:
            if args.verbose:
                print(f"   [{i}/{len(pdf_files)}] Processando: {filename}")
            
            data = extractor.extract_from_pdf(pdf_path)
            extracted_data.append(data)
            
            if args.verbose:
                print(f"       ✓ NF {data.numero_nota} - R$ {data.valor_servicos}")
            
        except Exception as e:
            error_msg = f"Erro em {filename}: {str(e)}"
            errors.append(error_msg)
            if args.verbose:
                print(f"       ✗ {error_msg}")
    
    print(f"\n✅ Extraídos dados de {len(extracted_data)} nota(s) com sucesso")
    
    if errors:
        print(f"⚠️  {len(errors)} arquivo(s) com erro:")
        for error in errors[:5]:  # Mostra apenas os 5 primeiros
            print(f"    • {error}")
        if len(errors) > 5:
            print(f"    ... e mais {len(errors) - 5} erro(s)")
    
    if not extracted_data:
        print("\n❌ Nenhum dado foi extraído com sucesso!")
        sys.exit(1)
    
    # Validação
    if not args.no_validation:
        print("\n🔍 Validando dados extraídos...")
        validation_summary = {'errors': 0, 'warnings': 0, 'ok': 0}
        
        for data in extracted_data:
            issues = validator.validate(data)
            
            if any(i.severity == 'ERROR' for i in issues):
                validation_summary['errors'] += 1
            elif any(i.severity == 'WARNING' for i in issues):
                validation_summary['warnings'] += 1
            else:
                validation_summary['ok'] += 1
            
            if args.verbose and issues:
                print(f"\n   NF {data.numero_nota}:")
                for issue in issues[:3]:  # Mostra apenas 3 primeiros
                    icon = {'ERROR': '❌', 'WARNING': '⚠️', 'INFO': 'ℹ️'}
                    print(f"   {icon.get(issue.severity, '•')} {issue.message}")
        
        print(f"\n   ✅ Validadas: {validation_summary['ok']}")
        print(f"   ⚠️  Com avisos: {validation_summary['warnings']}")
        print(f"   ❌ Com erros: {validation_summary['errors']}")
    
    # Consolidação
    print(f"\n📊 Gerando planilha consolidada: {args.output}")
    
    try:
        output_path = consolidator.consolidate_to_excel(
            extracted_data,
            args.output,
            include_validation=not args.no_validation
        )
        
        print(f"✅ Planilha gerada com sucesso!")
        print(f"\n📁 Arquivo: {output_path}")
        
        # Resumo final
        total_valor = sum(float(d.valor_servicos) for d in extracted_data)
        total_iss = sum(float(d.iss_valor) for d in extracted_data)
        total_tributos = sum(float(d.total_tributos_retidos) for d in extracted_data)
        
        print("\n" + "="*70)
        print("RESUMO EXECUTIVO")
        print("="*70)
        print(f"Notas processadas:      {len(extracted_data)}")
        print(f"Valor total:            R$ {total_valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"ISS retido:             R$ {total_iss:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"Total tributos retidos: R$ {total_tributos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print("="*70)
        
    except Exception as e:
        print(f"❌ Erro ao gerar planilha: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
