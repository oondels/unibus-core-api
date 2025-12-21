"""
Script de teste para validar integração ViaCEP
"""

import httpx
import asyncio


async def test_viacep_integration():
    """Testa a integração completa com ViaCEP"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testando Integração ViaCEP + Student Validation API\n")
    
    # Teste 1: CEP válido + Email institucional válido
    print("1️⃣  Teste: CEP válido (20040-020) + Email institucional (@aluno.puc.br)")
    student_valid = {
        "name": "Maria Silva",
        "email": "maria.silva@aluno.puc.br",
        "cep": "20040-020"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/students", json=student_valid)
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                data = response.json()
                print(f"   ✅ Estudante criado com sucesso!")
                print(f"   📍 Cidade: {data['city']}")
                print(f"   🏛️  IBGE: {data['city_ibge_code']}")
                print(f"   📮 CEP: {data['cep']}\n")
            else:
                print(f"   ❌ Erro: {response.json()}\n")
        except Exception as e:
            print(f"   ❌ Erro de conexão: {e}\n")
    
    # Teste 2: CEP inválido
    print("2️⃣  Teste: CEP inválido (99999-999)")
    student_invalid_cep = {
        "name": "João Santos",
        "email": "joao.santos@aluno.ufrj.br",
        "cep": "99999-999"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/students", json=student_invalid_cep)
            print(f"   Status: {response.status_code}")
            if response.status_code == 400:
                print(f"   ✅ Rejeitado corretamente: {response.json()['detail']}\n")
            else:
                print(f"   ❌ Esperado HTTP 400, recebeu {response.status_code}\n")
        except Exception as e:
            print(f"   ❌ Erro de conexão: {e}\n")
    
    # Teste 3: CEP válido + Email não institucional
    print("3️⃣  Teste: CEP válido (01310-100) + Email comum (@gmail.com)")
    student_invalid_email = {
        "name": "Pedro Oliveira",
        "email": "pedro.oliveira@gmail.com",
        "cep": "01310-100"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/students", json=student_invalid_email)
            print(f"   Status: {response.status_code}")
            if response.status_code == 400:
                print(f"   ✅ Rejeitado corretamente: {response.json()['detail']}\n")
            else:
                print(f"   ❌ Esperado HTTP 400, recebeu {response.status_code}\n")
        except Exception as e:
            print(f"   ❌ Erro de conexão: {e}\n")
    
    # Teste 4: CEP sem hífen
    print("4️⃣  Teste: CEP válido sem hífen (01310100) + Email institucional")
    student_cep_no_hyphen = {
        "name": "Ana Costa",
        "email": "ana.costa@estudante.edu.br",
        "cep": "01310100"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/students", json=student_cep_no_hyphen)
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                data = response.json()
                print(f"   ✅ Estudante criado com sucesso!")
                print(f"   📍 Cidade: {data['city']}")
                print(f"   🏛️  IBGE: {data['city_ibge_code']}")
                print(f"   📮 CEP: {data['cep']}\n")
            else:
                print(f"   ❌ Erro: {response.json()}\n")
        except Exception as e:
            print(f"   ❌ Erro de conexão: {e}\n")
    
    # Teste 5: Listar estudantes
    print("5️⃣  Teste: Listar todos os estudantes")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/students")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                students = response.json()
                print(f"   ✅ Total de estudantes: {len(students)}")
                for student in students:
                    print(f"      - {student['name']} ({student['city']}) - {student['email']}")
                print()
            else:
                print(f"   ❌ Erro ao listar estudantes\n")
        except Exception as e:
            print(f"   ❌ Erro de conexão: {e}\n")
    
    print("=" * 70)
    print("✅ Testes concluídos!\n")
    print("📝 Observações:")
    print("   - Certifique-se de que a validation-api está rodando em localhost:8001")
    print("   - CEPs válidos para teste: 20040-020 (RJ), 01310-100 (SP), 30190-001 (BH)")
    print("   - Emails institucionais devem conter @aluno ou .edu.br")


if __name__ == "__main__":
    asyncio.run(test_viacep_integration())
