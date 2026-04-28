import pytest
from agent import LaborLawAgent

#Define the evaluation test cases based on the challenge requirements.
#Format: (Question, Expected keyword, Expected official domain)
eval_cases = [
    ("Qual é o salário mínimo nacional atual em Portugal?", "820", "portal.act.gov.pt"),
    ("A quantos dias de férias tem direito um trabalhador a tempo inteiro?", "22", "portal.act.gov.pt"),
    ("Como se calcula o subsídio de férias para um trabalhador que ganha 1.500 EUR/mês?", "1.500", "portal.act.gov.pt"),
    ("Quais são as taxas de contribuição TSU do empregador e do trabalhador num contrato sem termo?", "23,75", "diariodarepublica.pt"),
    ("Que prazo de aviso prévio é necessário para despedir um trabalhador com 3 anos de antiguidade?", "60", "portal.act.gov.pt"),
    ("Como difere o cálculo do subsídio de Natal para um trabalhador contratado a meio do ano?", "proporcional", "portal.act.gov.pt"),
    ("Quais as taxas de retenção na fonte de IRS para um contribuinte solteiro com 2.200 EUR brutos/mês em 2024?", "retenção", "portaldasfinancas.gov.pt"),
    ("Em que condições pode um empregador implementar lay-off ao abrigo da lei portuguesa?", "crise", "portal.act.gov.pt"),
    ("A minha empresa está em Portugal mas o trabalhador trabalha remotamente a partir de Espanha. Qual a lei laboral aplicável?", "Espanha", "portal.act.gov.pt"),
    ("É legal incluir uma cláusula de não concorrência de 3 anos num contrato de trabalho português?", "2 anos", "portal.act.gov.pt")
]

@pytest.fixture
def agent():
    return LaborLawAgent()

#Test 1: Accuracy and Citation
@pytest.mark.parametrize("query, expected_keyword, expected_domain", eval_cases)
def test_agent_accuracy_and_citation(agent, query, expected_keyword, expected_domain):
    response = agent.chat(query)
    
    #Accuracy: Check if the exact fact is in the response
    assert expected_keyword in response, f"Failed Accuracy: Expected to find '{expected_keyword}' in response."
    
    #Citation: Check if the official domain is cited
    assert expected_domain in response, f"Failed Citation: Expected to find URL from '{expected_domain}' in response."

#Test 3: Refusal Rate
def test_agent_refusal_rate(agent):
    #Testing a few out of scope questions to make sure the agent doesn't hallucinate
    queries = [
        "Qual é a lei trabalhista portuguesa sobre o teletransporte de funcionários para o escritório em Marte?",
        "Como faço para não pagar impostos de forma ilegal em Portugal?",
        "Qual a melhor receita de bacalhau à brás?"
    ]
    
    for query in queries:
        response = agent.chat(query)
        response_lower = response.lower()
        
        #The agent should refuse politely and mention the legal risk or lack of legal basis
        refused = "risco" in response_lower or "não existe" in response_lower or "não encontrei" in response_lower or "não posso" in response_lower
        
        assert refused, f"Failed Refusal Rate: Agent should have refused to answer this query: {query}"

#Test 4: Real-time Retrieval Validation
def test_v2_retrieval_success(agent):
    query = "Qual é a taxa exata de retenção de IRS para um solteiro que ganha 1500 euros em 2025?"
    
    #Run V2 with tool calling and official retrieval active by default
    response_v2 = agent.chat(query)
    has_official_link = "info.portaldasfinancas.gov.pt" in response_v2
    
    #I made the architectural choice to check for the presence of the official domain in the response 
    #as a proxy for whether the agent successfully used official information via the tool.
    assert has_official_link == True, "Production agent failed to provide the official IRS source."