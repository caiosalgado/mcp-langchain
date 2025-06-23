#!/usr/bin/env python3
"""
Sales Analysis Chat - Simple Interactive Chat
Connects to the FastAPI sales insights API
"""
import requests
import json
import sys
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"
SALES_INSIGHTS_ENDPOINT = f"{API_BASE_URL}/sales-insights"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

def print_header():
    """Print the chat header"""
    print("\n🤖 Sales Analysis Chat - Ollama + MCP")
    print("=" * 50)
    print("Digite suas perguntas sobre vendas (ou 'sair' para terminar)")
    print()

def check_api_health() -> bool:
    """Check if the API is running and healthy"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API conectada - Modelo: {health_data.get('model', 'N/A')}")
            return True
        else:
            print(f"⚠️  API respondeu com status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        print("\n💡 Certifique-se de que os servidores estão rodando:")
        print("   1. uv run python mcp_server.py --port 8001")
        print("   2. uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False

def ask_question(question: str) -> Dict[str, Any]:
    """Send a question to the sales insights API"""
    try:
        print("🔍 Processando pergunta...")
        print("   ⏳ Aguardando resposta do LLM...")
        
        # Make the API call
        response = requests.get(
            SALES_INSIGHTS_ENDPOINT,
            params={"question": question},
            timeout=300  # Increased timeout for LLM processing
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            try:
                error_data = response.json()
                return {"error": error_data.get("detail", "Pergunta inválida")}
            except:
                return {"error": f"Erro 400: {response.text}"}
        else:
            return {"error": f"Erro na API ({response.status_code}): {response.text}"}
            
    except requests.exceptions.Timeout:
        return {"error": "Timeout - A pergunta demorou muito para ser processada (60s)"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro de conexão: {e}"}
    except Exception as e:
        return {"error": f"Erro inesperado: {e}"}

def format_response(result: Dict[str, Any]) -> str:
    """Format the API response for display"""
    if result is None:
        return "❌ Erro: Resposta vazia da API"
    
    if "error" in result and result["error"]:
        return f"❌ Erro: {result['error']}"
    
    answer = result.get("answer", "Sem resposta")
    tools_used = result.get("mcp_tools_used", [])
    model_used = result.get("model_used", "N/A")
    
    # Clean up answer (remove <think> tags if present)
    if answer and "<think>" in answer:
        # Extract only the part after </think>
        parts = answer.split("</think>")
        if len(parts) > 1:
            answer = parts[1].strip()
        else:
            # If no closing tag, remove the opening tag and everything before it
            parts = answer.split("<think>")
            if len(parts) > 1:
                answer = parts[-1].strip()
    
    # Remove any remaining think tags
    if answer:
        import re
        answer = re.sub(r'</?think[^>]*>', '', answer).strip()
    
    formatted = f"✅ Resposta:\n{answer}\n"
    
    if tools_used:
        formatted += f"\n🔧 Ferramentas usadas: {', '.join(tools_used)}"
    
    formatted += f"\n🤖 Modelo: {model_used}"
    
    return formatted

def main():
    """Main chat loop"""
    print_header()
    
    # Check API health
    if not check_api_health():
        sys.exit(1)
    
    print()
    
    while True:
        try:
            # Get user input
            question = input("💬 Você: ").strip()
            
            # Check for exit commands
            if question.lower() in ['sair', 'exit', 'quit', 'q']:
                print("\n👋 Até logo!")
                break
            
            # Skip empty questions
            if not question:
                continue
            
            # Show help
            if question.lower() in ['help', 'ajuda']:
                print("\n📋 Comandos disponíveis:")
                print("   • Digite qualquer pergunta sobre vendas")
                print("   • 'sair' - Para terminar o chat")
                print("   • 'help' - Para mostrar esta ajuda")
                print("\n💡 Exemplos de perguntas:")
                print("   • Qual foi o produto mais vendido?")
                print("   • Qual é o faturamento total?")
                print("   • Quantos clientes fizeram compras?")
                print("   • Qual categoria vendeu mais?")
                continue
            
            print(f"   • Conectando ao Ollama (qwen3:30b)")
            print(f"   • Consultando banco de dados via MCP")
            
            # Ask the question
            result = ask_question(question)
            
            # Display the response
            print("\n" + format_response(result))
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrompido. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main() 