#!/usr/bin/env python
"""
Script para rodar apenas testes básicos (sem dependências de permissões)

Execute:
    python run_tests_basicos.py
"""

import subprocess
import sys

def run_command(cmd, description):
    """Roda comando e mostra resultado"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     TESTES BÁSICOS - Sprint 1 (CRUD Implementado)       ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    testes_ok = True

    # 1. Testes de Modelos (100% prontos)
    if not run_command(
        "pytest acoes/tests/test_models.py -v",
        "1. TESTES DE MODELOS (Acao, Inscricao, Notificacao)"
    ):
        testes_ok = False

    # 2. Testes de Formulários (100% prontos)
    if not run_command(
        "pytest acoes/tests/test_forms.py -v",
        "2. TESTES DE FORMULÁRIOS (AcaoForm)"
    ):
        testes_ok = False

    # Resumo
    print(f"\n{'='*60}")
    if testes_ok:
        print("✅ TODOS OS TESTES BÁSICOS PASSARAM!")
        print("📊 Total: ~37 testes")
        print("\n💡 Próximos passos:")
        print("   - Testar CRUD manualmente no navegador")
        print("   - Implementar sistema de permissões automático")
        print("   - Rodar todos os 120 testes")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("🔍 Verifique os erros acima")
        print("\n💡 Possíveis problemas:")
        print("   - Banco de dados não configurado (rode: python manage.py migrate)")
        print("   - Dependências faltando (rode: pip install -r requirements.txt)")
        print("   - URLs não configuradas corretamente")
    print(f"{'='*60}\n")

    return 0 if testes_ok else 1

if __name__ == '__main__':
    sys.exit(main())
