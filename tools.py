import logging
#Import DDGS from duckduckgo search for performing searches
from duckduckgo_search import DDGS
#Import Basemodel and Field from pydantic for defining data models
from pydantic import BaseModel, Field

#Configure basic logging to INFO level 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#Here are the schemas, where the LLM knows where to extract the info for each tool.

class SearchACT(BaseModel):
    query: str = Field(..., 
        description="Precise search terms for the labor code. Extract only the main keywords from the legal issue (e.g. 'cálculo indemnização despedimento', 'prazo aviso prévio'). Do not pass full sentences or questions."
    )

class SearchIRS(BaseModel):
    brute_salary: float = Field(..., 
        description="Monthly brute salary value in euros. Convert to float. If user mentions an annual value, divide by 12. If the user doesn't mention salary, ask for it before calling the tool."
    )
    civil_status: str = Field(..., 
        description="Exact tax classification. Use only: 'solteiro', 'casado_unico_titular' or 'casado_dois_titulares'. If the user doesn't say, ask for this info before calling the tool."
    )
    legal_dependents: int = Field(default=0, 
        description="Number of dependents or beneficiaries (children, etc). Assume 0 if user doesn't mention, but prefer to ask if there's ambiguity."
    )

class SearchSegSocial(BaseModel):
    contract_type: str = Field(..., 
        description="Nature of the labor contract. Extract or infer the type (e.g. 'sem termo', 'a termo certo', 'independente'). If user doesn't mention, ask for it before calling the tool."
    )

#Search engines(DuckDuckGo + site: filter)

#This function perform official searches restricted to a domain and returns the content and source of the results
def official_search(query: str, domain: str) -> str:
    #This makes the search term with site filter, so that the search is restricted to the specified domain
    search_term = f"site:{domain} {query}"
    logger.info(f"Searching for: {search_term}")
    
    #I used DDGS to perform the search, specifying portuguese region and limiting to 4 results. 
    #Then i format the results to include content and source, and return them as a single string. 
    #If there are no results, i return a message indicating that. 
    #If there is an error during the search, i log the error and return an error message.
    try:
        results = DDGS().text(search_term, region='pt-pt', max_results=4)
        context = []

        for result in results:
            context.append(f"Content: {result['body']}\nSource: {result['href']}")
            
        if not context:
            return "No results found in this official source."
            
        return "\n\n".join(context)
    
    # Catch any exceptions
    except Exception as e:
        logger.error(f"Search error: {e}")
        return "Error accessing the source. Ask the user to rephrase the search."


#These next 2 functions follow the schemas defined above and call the official_search function with the appropriate queries and domains for each topic.

#This is a function to search the labor code at the ACT domain, using the function official_search with the appropriate query and domain.
def search_labor_code(query: str) -> str:
    return official_search(query, "portal.act.gov.pt")

#This is a function to search IRS tables at the Finance Portal, using the function official_search with the appropriate query and domain.
def search_tables_irs(brute_salary: float, civil_status: str) -> str:
    query = f"tabelas retenção IRS 2025 {brute_salary} euros {civil_status}"
    return official_search(query, "info.portaldasfinancas.gov.pt")

#This is a function to search social security
def search_social_security(contract_type: str) -> str:
    query = f"Taxa Social Única TSU Código dos Regimes Contributivos {contract_type}"
    return official_search(query, "diariodarepublica.pt")